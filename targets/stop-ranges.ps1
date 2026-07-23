# ============================================================
# Reasonix 靶场 — 停止脚本
# ============================================================
# 用法: .\targets\stop-ranges.ps1
#       .\targets\stop-ranges.ps1 -Reset   # 停止并清除所有数据
# ============================================================

param(
    [switch]$Reset = $false
)

$COMPOSE_DIR = "$PSScriptRoot"
Set-Location $COMPOSE_DIR

if ($Reset) {
    Write-Host "[!] 即将停止并清除所有靶场数据！" -ForegroundColor Red
    Write-Host "    这将删除所有数据库和用户进度。" -ForegroundColor Yellow
    $confirm = Read-Host "    输入 YES 确认"
    if ($confirm -ne "YES") {
        Write-Host "[-] 已取消" -ForegroundColor Gray
        exit 0
    }
    Write-Host "[*] 正在停止并清除数据..." -ForegroundColor Yellow
    docker compose down -v
    Write-Host "[OK] 靶场已停止，数据已清除" -ForegroundColor Green
}
else {
    Write-Host "[*] 正在停止靶场..." -ForegroundColor Yellow
    docker compose down
    Write-Host "[OK] 靶场已停止（数据保留）" -ForegroundColor Green
}
