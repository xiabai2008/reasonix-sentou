# ============================================================
# Reasonix 靶场 — 启动脚本
# ============================================================
# 用法: .\targets\start-ranges.ps1 [target]
#   .\targets\start-ranges.ps1            # 启动所有靶场
#   .\targets\start-ranges.ps1 dvwa        # 仅启动 DVWA
#   .\targets\start-ranges.ps1 juiceshop   # 仅启动 Juice Shop
#   .\targets\start-ranges.ps1 webgoat     # 仅启动 WebGoat
#   .\targets\start-ranges.ps1 vampi       # 仅启动 VAmPI
# ============================================================

param(
    [string]$Target = "all"
)

$ErrorActionPreference = "Stop"
$COMPOSE_DIR = "$PSScriptRoot"

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  Reasonix 渗透靶场启动" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# 检查 Docker 状态
$dockerInfo = docker info 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "[!] Docker Desktop 未运行！请先启动 Docker Desktop。" -ForegroundColor Red
    Write-Host "    启动后重新运行此脚本。" -ForegroundColor Yellow
    exit 1
}
Write-Host "[OK] Docker 运行中" -ForegroundColor Green

# 启动服务
Set-Location $COMPOSE_DIR

if ($Target -eq "all") {
    Write-Host ""
    Write-Host "[*] 正在启动全部 4 个靶场..." -ForegroundColor Yellow
    docker compose up -d
    Write-Host ""
    Write-Host "[OK] 全部靶场已启动" -ForegroundColor Green
}
else {
    $services = @("dvwa", "dvwa-db", "juiceshop", "webgoat", "vampi")
    if ($Target -in @("dvwa", "juiceshop", "webgoat", "vampi")) {
        Write-Host "[*] 正在启动: $Target" -ForegroundColor Yellow
        if ($Target -eq "dvwa") {
            docker compose up -d dvwa-db dvwa
        } else {
            docker compose up -d $Target
        }
        Write-Host "[OK] $Target 已启动" -ForegroundColor Green
    }
    else {
        Write-Host "[!] 未知靶场: $Target" -ForegroundColor Red
        Write-Host "    可用: dvwa, juiceshop, webgoat, vampi" -ForegroundColor Yellow
        exit 1
    }
}

# 等待服务就绪（部分镜像首次拉取较慢）
Write-Host ""
Write-Host "[*] 等待服务就绪..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

# 显示状态
Write-Host ""
docker compose ps --format "table {{.Name}}\t{{.Status}}\t{{.Ports}}"

# 显示访问地址
Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  靶场访问地址" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "  DVWA       http://localhost:8080" -ForegroundColor White
Write-Host "             默认账号: admin / password" -ForegroundColor DarkGray
Write-Host ""
Write-Host "  Juice Shop http://localhost:3000" -ForegroundColor White
Write-Host "             注册账号即可开始" -ForegroundColor DarkGray
Write-Host ""
Write-Host "  WebGoat    http://localhost:8081/WebGoat" -ForegroundColor White
Write-Host "             WebWolf: http://localhost:9090/WebWolf" -ForegroundColor DarkGray
Write-Host "             注册账号即可开始" -ForegroundColor DarkGray
Write-Host ""
Write-Host "  VAmPI      http://localhost:5000" -ForegroundColor White
Write-Host "             Swagger: http://localhost:5000/ui/" -ForegroundColor DarkGray
Write-Host "             注册后获取 JWT Token" -ForegroundColor DarkGray
Write-Host ""
Write-Host "  [提示] 首次启动会拉取镜像，需等待 3-5 分钟" -ForegroundColor Yellow
Write-Host "  [提示] 使用 .\targets\stop-ranges.ps1 停止" -ForegroundColor Yellow
Write-Host ""
