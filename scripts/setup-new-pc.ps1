<#
.SYNOPSIS
    Reasonix 渗透助手 — 新电脑一键部署脚本
.DESCRIPTION
    把整个项目文件夹复制到新电脑后，运行此脚本即可自动配置环境。
    包括：WSL Kali Linux 安装、渗透工具安装、Python 依赖、PATH 配置、路径替换。
.PARAMETER ProjectPath
    项目在新电脑上的完整路径（默认：脚本所在目录的上一级）
.EXAMPLE
    # 从项目根目录运行
    .\scripts\setup-new-pc.ps1
    
    # 指定新路径
    .\scripts\setup-new-pc.ps1 -ProjectPath "D:\reasonix渗透助手"
#>

param(
    [string]$ProjectPath = ""
)

# 如果未指定路径，自动检测脚本所在位置
if (-not $ProjectPath) {
    $ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
    $ProjectPath = Split-Path -Parent $ScriptDir
}

Write-Host "╔══════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║    Reasonix 渗透助手 — 新电脑部署工具         ║" -ForegroundColor Cyan
Write-Host "╚══════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host "项目路径: $ProjectPath" -ForegroundColor Yellow
Write-Host ""

# ============================================================
# 步骤1：检查项目完整性
# ============================================================
Write-Host "[1/7] 检查项目完整性..." -ForegroundColor Green

$RequiredDirs = @("config", "bin", "tools", "skills", "scripts")
$MissingDirs = @()
foreach ($dir in $RequiredDirs) {
    $path = Join-Path $ProjectPath $dir
    if (-not (Test-Path $path)) {
        $MissingDirs += $dir
    }
}

if ($MissingDirs.Count -gt 0) {
    Write-Host "  ⚠ 缺少目录: $($MissingDirs -join ', ')" -ForegroundColor Yellow
    Write-Host "  请确认完整复制了整个项目文件夹" -ForegroundColor Red
} else {
    Write-Host "  ✅ 项目结构完整" -ForegroundColor Green
}

# ============================================================
# 步骤2：替换 AGENTS.md 中的旧路径
# ============================================================
Write-Host "[2/7] 更新项目路径配置..." -ForegroundColor Green

$AgentsFile = Join-Path $ProjectPath "AGENTS.md"
if (Test-Path $AgentsFile) {
    $content = Get-Content $AgentsFile -Raw
    # 替换旧路径（兼容 C:\Users\xxx\reasonix渗透助手 格式）
    $oldPattern = 'C:\\Users\\[^\\]+\\reasonix渗透助手'
    $newPath = $ProjectPath -replace '\\', '\\'
    if ($content -match $oldPattern) {
        $content = $content -replace $oldPattern, $newPath
        Set-Content $AgentsFile $content
        Write-Host "  ✅ AGENTS.md 路径已更新" -ForegroundColor Green
    } else {
        Write-Host "  ℹ AGENTS.md 无需更新路径" -ForegroundColor Gray
    }
}

# ============================================================
# 步骤3：检查 Python 并安装依赖
# ============================================================
Write-Host "[3/7] 检查 Python 环境..." -ForegroundColor Green

$python = Get-Command "python" -ErrorAction SilentlyContinue
if (-not $python) {
    $python = Get-Command "python3" -ErrorAction SilentlyContinue
}

if ($python) {
    Write-Host "  ✅ Python 已安装: $($python.Source)" -ForegroundColor Green
    
    Write-Host "  正在安装 Python 依赖..." -ForegroundColor Yellow
    $pipResult = & $python.Source -m pip install ddddocr requests -q 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  ✅ ddddocr, requests 已安装" -ForegroundColor Green
    } else {
        Write-Host "  ⚠ pip 安装失败，请手动执行:" -ForegroundColor Yellow
        Write-Host "     pip install ddddocr requests" -ForegroundColor White
    }
} else {
    Write-Host "  ❌ Python 未安装！请先安装 Python 3.8+" -ForegroundColor Red
    Write-Host "     下载: https://www.python.org/downloads/" -ForegroundColor White
}

# ============================================================
# 步骤4：添加 bin/ 到 PATH
# ============================================================
Write-Host "[4/7] 配置环境变量 PATH..." -ForegroundColor Green

$BinPath = Join-Path $ProjectPath "bin"
$currentPath = [Environment]::GetEnvironmentVariable("Path", "User")
if ($currentPath -like "*$BinPath*") {
    Write-Host "  ✅ bin/ 已在 PATH 中" -ForegroundColor Green
} else {
    $newPath = $currentPath + ";" + $BinPath
    [Environment]::SetEnvironmentVariable("Path", $newPath, "User")
    # 同时设置当前会话
    $env:Path += ";" + $BinPath
    Write-Host "  ✅ bin/ 已加入 PATH（当前会话 + 永久）" -ForegroundColor Green
}

# ============================================================
# 步骤5：检查/安装 WSL Kali Linux
# ============================================================
Write-Host "[5/7] 检查 WSL Kali Linux..." -ForegroundColor Green

$wsl = Get-Command "wsl" -ErrorAction SilentlyContinue
if (-not $wsl) {
    Write-Host "  ❌ WSL 未安装！请先安装 WSL" -ForegroundColor Red
    Write-Host "     以管理员身份运行: wsl --install" -ForegroundColor White
} else {
    $kaliInstalled = & wsl -l -v 2>&1 | Select-String "kali"
    if ($kaliInstalled) {
        Write-Host "  ✅ Kali Linux WSL 已安装" -ForegroundColor Green
    } else {
        Write-Host "  ⏳ Kali Linux WSL 未安装，正在安装..." -ForegroundColor Yellow
        Write-Host "  这需要一些时间下载，请耐心等待..." -ForegroundColor Yellow
        & wsl --install -d kali-linux 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Host "  ✅ Kali Linux WSL 安装成功！" -ForegroundColor Green
        } else {
            Write-Host "  ⚠ Kali 安装失败，可稍后手动安装:" -ForegroundColor Yellow
            Write-Host "     wsl --install -d kali-linux" -ForegroundColor White
        }
    }
}

# ============================================================
# 步骤6：在 Kali 中安装工具
# ============================================================
$kaliInstalled = & wsl -l -v 2>&1 | Select-String "kali"
if ($kaliInstalled) {
    Write-Host "[6/7] 在 Kali 中安装渗透工具..." -ForegroundColor Green
    
    # 先设置 Kali 密码
    & wsl -d kali-linux sh -c "echo 'kali:kali' | sudo /usr/sbin/chpasswd" 2>$null
    
    Write-Host "  正在更新 apt 源..." -ForegroundColor Yellow
    & wsl -d kali-linux sh -c "sudo apt update" 2>&1 | Out-Null
    
    Write-Host "  正在安装工具（约 260MB 下载）..." -ForegroundColor Yellow
    & wsl -d kali-linux sh -c "sudo apt install -y nmap masscan hydra john crunch gobuster dirsearch wfuzz whatweb nikto proxychains4 netcat-openbsd" 2>&1
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  ✅ Kali 渗透工具全部安装成功！" -ForegroundColor Green
    } else {
        Write-Host "  ⚠ 部分工具安装失败，可稍后手动执行:" -ForegroundColor Yellow
        Write-Host "     wsl -d kali-linux sudo apt install -y nmap masscan hydra" -ForegroundColor White
    }
}

# ============================================================
# 步骤7：最终验证
# ============================================================
Write-Host "[7/7] 最终验证..." -ForegroundColor Green

$CheckPassed = 0
$CheckFailed = 0

# 检查 Windows 工具
$ToolsToCheck = @{
    "config/brute.py" = "爆破工具";
    "config/merge-dicts.py" = "字典管理";
    "tools/fscan.exe" = "fscan 端口扫描";
    "tools/naabu.exe" = "naabu 端口扫描";
    "tools/nuclei.exe" = "nuclei 漏洞扫描";
}
foreach ($tool in $ToolsToCheck.Keys) {
    $path = Join-Path $ProjectPath $tool
    if (Test-Path $path) {
        Write-Host "  ✅ $($ToolsToCheck[$tool])" -ForegroundColor Green
        $CheckPassed++
    } else {
        Write-Host "  ⚠ $($ToolsToCheck[$tool]) 未找到" -ForegroundColor Yellow
        $CheckFailed++
    }
}

# 检查 Kali 工具（如果安装了）
if ($kaliInstalled) {
    $KaliTools = @("nmap", "hydra", "gobuster", "masscan")
    foreach ($kt in $KaliTools) {
        $result = & wsl -d kali-linux sh -c "which $kt" 2>$null
        if ($result) {
            Write-Host "  ✅ Kali: $kt" -ForegroundColor Green
            $CheckPassed++
        } else {
            Write-Host "  ⚠ Kali: $kt 未安装" -ForegroundColor Yellow
            $CheckFailed++
        }
    }
}

# ============================================================
Write-Host ""
Write-Host "╔══════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║                    部署完成                      ║" -ForegroundColor Cyan
Write-Host "╚══════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""
Write-Host "✅ 通过: $CheckPassed   ⚠ 需注意: $CheckFailed" -ForegroundColor Yellow
Write-Host ""

if ($CheckFailed -gt 0) {
    Write-Host "📋 后续手动操作建议:" -ForegroundColor White
    Write-Host "  1. Wireshark 需自行安装（分析 pcap 用）" -ForegroundColor White
    Write-Host "  2. Python 包: pip install ddddocr requests" -ForegroundColor White
    Write-Host "  3. Kali 工具: wsl -d kali-linux sudo apt install -y nmap masscan hydra" -ForegroundColor White
}

Write-Host ""
Write-Host "💡 现在可以开始使用了！打开新终端输入 nmap / hydra / fscan 等命令即可" -ForegroundColor Green
