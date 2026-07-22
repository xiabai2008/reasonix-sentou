#!/bin/bash
# WSL 渗透工具安装脚本
# 在 WSL Ubuntu 中执行: bash /mnt/c/Tools/reasonix_sentou/scripts/wsl-setup.sh

set -e

echo "============================================"
echo "  WSL 渗透工具安装脚本"
echo "============================================"

# 1. 基础工具
echo ""
echo "[1/4] 安装基础工具 (nmap, masscan, hydra, john)..."
sudo apt-get update -qq
sudo apt-get install -y -qq \
    nmap \
    masscan \
    hydra \
    john \
    proxychains4 \
    p7zip-full \
    libimage-exiftool-perl \
    foremost \
    wget \
    curl \
    git \
    2>&1 | tail -3
echo "  ✅ 基础工具安装完成"

# 2. Metasploit
echo ""
echo "[2/4] 安装 Metasploit Framework..."
if ! which msfconsole 2>/dev/null; then
    cd /tmp
    curl -sL https://raw.githubusercontent.com/rapid7/metasploit-omnibus/master/config/templates/metasploit-framework-wrappers/msfupdate.erb -o msfinstall
    chmod 755 msfinstall
    sudo ./msfinstall 2>&1 | tail -5
    echo "  ✅ Metasploit 安装完成"
else
    echo "  ⏭️ Metasploit 已存在"
fi

# 3. Python 工具
echo ""
echo "[3/4] 安装 Python 安全工具..."
pip3 install --user --break-system-packages \
    oneforall \
    2>&1 | tail -3 || true
echo "  ✅ Python 工具安装完成"

# 4. 配置环境变量
echo ""
echo "[4/4] 配置环境..."
echo 'export PATH=$PATH:$HOME/.local/bin' >> ~/.bashrc
echo "  ✅ PATH 已更新"

echo ""
echo "============================================"
echo "  🎉 安装完成！可用工具清单："
echo "============================================"
echo ""
echo "  nmap          $(nmap --version 2>&1 | head -1)"
echo "  masscan       $(masscan --version 2>&1 | head -1)"
echo "  hydra         $(hydra -h 2>&1 | head -1)"
echo "  john          $(john --help 2>&1 | head -1)"
echo "  proxychains4  $(which proxychains4)"
echo "  msfconsole    $(which msfconsole 2>/dev/null || echo '需重启终端')"
echo ""
echo "Windows 端已就绪的工具："
echo "  amass, ysoserial, JNDI-Injection-Exploit"
echo "  CDK, CloudToolkit, stegoveritas"
echo ""
echo "请重启 WSL 终端或执行: source ~/.bashrc"
