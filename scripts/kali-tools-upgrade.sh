#!/usr/bin/env bash
# Kali WSL 渗透工具补充安装脚本
# 在 Kali WSL 中运行: bash /mnt/c/Tools/reasonix_sentou/scripts/kali-tools-upgrade.sh
# 或者在 Windows 中运行: wsl -d kali-linux -e bash /mnt/c/Tools/reasonix_sentou/scripts/kali-tools-upgrade.sh

set -e

echo "==========================================="
echo "  Kali WSL 渗透工具补充安装"
echo "==========================================="
echo ""

# 确保 apt 最新
echo "[1/4] 更新 apt 源..."
sudo apt update -qq

# 安装核心渗透工具
echo "[2/4] 安装核心渗透工具..."
sudo apt install -y \
  metasploit-framework \
  bloodhound \
  responder \
  impacket-scripts \
  crackmapexec \
  evil-winrm \
  kerberoast \
  smbmap \
  seclists \
  wordlists \
  iproute2 \
  ncat \
  socat \
  tmux \
  jq \
  ffuf \
  gobuster \
  wfuzz \
  dirbuster \
  zaproxy \
  wireshark \
  tcpdump

# 安装 Python 工具
echo "[3/4] 安装 Python 工具..."
sudo apt install -y \
  python3-pip \
  python3-venv \
  python3-ldap \
  python3-ldapdomaindump \
  python3-dnspython \
  python3-scapy

# 通过 pip 安装额外工具
pip3 install --user \
  mitmproxy \
  shodan \
  pypykatz \
  lsassy \
  bloodhound-py \
  certipy-ad \
  dploot \
  donpapi \
  coercer \
  targeted-kerberoast \
  kerbrute

# 下载更新 wordlist
echo "[4/4] 下载额外字典..."
if [ -d "/usr/share/seclists" ]; then
  cd /usr/share/seclists
  git pull 2>/dev/null || true
fi

echo ""
echo "==========================================="
echo "  安装完成！"
echo "==========================================="
echo ""
echo "已安装工具清单："
echo "  - MSF (metasploit)    - BloodHound        - Responder"
echo "  - CrackMapExec        - Evil-WinRM        - Impacket"
echo "  - Kerberoast          - SMBMap            - SecLists"
echo "  - TMUX                - Ncat/Socat        - JQ"
echo "  - Certipy-ad          - Coercer           - Kerbrute"
echo "  - Shodan/PyPyKatz/Mitmproxy (via pip)"
echo ""
echo "启动指南："
echo "  msfconsole            - MSF 进入交互模式"
echo "  sudo bloodhound       - 启动 BloodHound (需 neo4j)"
echo "  responder -I eth0     - 启动 Responder"
echo "  crackmapexec smb target - 内网扫描"
