# start-all-ranges.ps1
# One-click launcher for all local pentest ranges used to validate 破晓 (Reasonix Sentou) capabilities.
# Validates: JYso (log4shell / fastjson / Spring4Shell), SSTImap (Flask SSTI),
#            dalfox (DVWA / Juice Shop XSS), PEASS-ng (in-container privesc).
#
# Usage:
#   .\start-all-ranges.ps1                 # start everything (auto-clone vulhub if missing)
#   .\start-all-ranges.ps1 -WhatIf         # show what would run, change nothing
#   .\start-all-ranges.ps1 -SkipDockerImages   # vulhub only
#   .\start-all-ranges.ps1 -VulhubRoot D:\vulhub

[CmdletBinding()]
param(
    [string]$VulhubRoot = "C:/Tools/vulhub",
    [switch]$SkipVulhubClone,
    [switch]$SkipDockerImages,
    [switch]$WhatIf
)

$ErrorActionPreference = "Stop"

$ScriptDir   = Split-Path -Parent $MyInvocation.MyCommand.Definition
$ProjectRoot = $ScriptDir
$ScopeCheck  = Join-Path $ProjectRoot "scripts/check-scope.py"

function Write-Step($m){ Write-Host "`n==> $m" -ForegroundColor Cyan }
function Write-Ok($m){ Write-Host "    [OK]   $m" -ForegroundColor Green }
function Write-Warn($m){ Write-Host "    [WARN] $m" -ForegroundColor Yellow }
function Write-Err($m){ Write-Host "    [ERR]  $m" -ForegroundColor Red }
function Test-Command($c){ return (Get-Command $c -ErrorAction SilentlyContinue) -ne $null }

# ---------------------------------------------------------------------------
# 1. Pre-flight: Docker
# ---------------------------------------------------------------------------
Write-Step "Pre-flight: Docker"
if (-not (Test-Command docker)) {
    Write-Err "Docker not found. Install Docker Desktop first:"
    Write-Host "        winget install -e --id Docker.DockerDesktop" -ForegroundColor White
    Write-Host "    Then reboot, launch Docker Desktop, and verify with:" -ForegroundColor White
    Write-Host "        docker run --rm hello-world" -ForegroundColor White
    exit 1
}
try { docker info | Out-Null }
catch {
    Write-Err "Docker daemon is not running. Launch Docker Desktop (system tray icon) and wait for it to start."
    exit 1
}
Write-Ok "Docker daemon is running"

# Resolve compose command (plugin 'docker compose' preferred over legacy 'docker-compose')
if (Test-Command "docker") {
    $probe = docker compose version 2>$null
    if ($LASTEXITCODE -eq 0) { $Compose = "plugin" }
    elseif (Test-Command "docker-compose") { $Compose = "legacy" }
    else { Write-Err "No docker compose available (neither 'docker compose' nor 'docker-compose')."; exit 1 }
}
Write-Ok "Compose: $Compose"

function Start-Compose($dir) {
    $file = $null
    if (Test-Path "$dir/docker-compose.yml")       { $file = "docker-compose.yml" }
    elseif (Test-Path "$dir/docker-compose.yaml")  { $file = "docker-compose.yaml" }
    else { Write-Warn "No docker-compose file in $dir"; return $false }

    if ($WhatIf) { Write-Host "    [WhatIf] compose up -d  ($dir/$file)"; return $true }
    if ($Compose -eq "plugin") { docker compose -f "$dir/$file" up -d 2>&1 | Select-Object -Last 4 }
    else                       { docker-compose -f "$dir/$file" up -d 2>&1 | Select-Object -Last 4 }
    return $true
}

# ---------------------------------------------------------------------------
# 2. Pre-flight: vulhub
# ---------------------------------------------------------------------------
Write-Step "Pre-flight: vulhub root = $VulhubRoot"
if (-not (Test-Path $VulhubRoot)) {
    if ($SkipVulhubClone) {
        Write-Warn "Vulhub root missing and -SkipVulhubClone set; vulhub targets will be skipped."
    }
    else {
        Write-Host "    Cloning vulhub (shallow)..." -ForegroundColor White
        if (-not $WhatIf) {
            git clone --depth 1 https://github.com/vulhub/vulhub.git $VulhubRoot 2>&1 | Select-Object -Last 3
        }
    }
}
else {
    Write-Ok "Vulhub root present"
}

# ---------------------------------------------------------------------------
# 3. vulhub-based targets  (relative paths under $VulhubRoot)
# ---------------------------------------------------------------------------
$vulhubTargets = @(
    @{ name = "log4shell  CVE-2021-44228  (-> JYso)";         path = "log4j/CVE-2021-44228";  port = 8983 }
    @{ name = "fastjson   1.2.24-rce       (-> JYso)";         path = "fastjson/1.2.24-rce";   port = 8090 }
    @{ name = "Spring4Shell CVE-2022-22965 (-> JYso)";         path = "spring/CVE-2022-22965";  port = 8080 }
    @{ name = "Flask SSTI                  (-> SSTImap)";       path = "flask/ssti";            port = 8000 }
)

$allUrls = @()

Write-Step "Starting vulhub targets"
foreach ($t in $vulhubTargets) {
    $dir = Join-Path $VulhubRoot $t.path
    $url = "http://127.0.0.1:" + $t.port
    $allUrls += $url
    if (-not (Test-Path $dir)) {
        Write-Warn "Skip $($t.name): path not found -> $dir"
        continue
    }
    Write-Step "Start $($t.name)  ->  $url"
    Start-Compose $dir | Out-Null
}

# ---------------------------------------------------------------------------
# 4. standalone docker-image targets (auto-pulled)
# ---------------------------------------------------------------------------
$dockerImageTargets = @(
    @{ name = "DVWA       (-> dalfox XSS)";   image = "vulnerables/web-dvwa";    hostPort = 8088; ctrPort = 80;   cname = "dvwa";  target = "http://127.0.0.1:8088" }
    @{ name = "Juice Shop (-> dalfox+logic)"; image = "bkimminich/juice-shop";   hostPort = 3000; ctrPort = 3000; cname = "juice"; target = "http://127.0.0.1:3000" }
)

if (-not $SkipDockerImages) {
    Write-Step "Starting docker-image targets"
    foreach ($t in $dockerImageTargets) {
        $allUrls += $t.target
        Write-Step "Start $($t.name)  ->  $($t.target)"
        $existing = docker ps -a --filter "name=$($t.cname)" -q 2>$null
        if ($existing) {
            Write-Ok "Container '$($t.cname)' already exists; ensuring it is running"
            if (-not $WhatIf) { docker start $t.cname 2>&1 | Out-Null }
            continue
        }
        if ($WhatIf) {
            Write-Host "    [WhatIf] docker run -d -p $($t.hostPort):$($t.ctrPort) --name $($t.cname) --restart unless-stopped $($t.image)"
            continue
        }
        docker run -d -p "$($t.hostPort):$($t.ctrPort)" --name $t.cname --restart unless-stopped $t.image 2>&1 | Select-Object -Last 2
    }
}

# ---------------------------------------------------------------------------
# 5. Scope validation (config/scope.yaml)
# ---------------------------------------------------------------------------
Write-Step "Validate targets against config/scope.yaml"
if (Test-Path $ScopeCheck) {
    foreach ($url in $allUrls) {
        if (Test-Command python) {
            $res = python $ScopeCheck $url 2>&1 | Select-Object -Last 1
            Write-Host "    $url -> $res"
        }
        else {
            Write-Warn "python not found; skipping scope check for $url"
        }
    }
}
else {
    Write-Warn "scope checker not found at $ScopeCheck; skipping validation"
}

# ---------------------------------------------------------------------------
# 6. Summary
# ---------------------------------------------------------------------------
Write-Step "Summary - 破晓 targets (all on localhost, pre-authorized in scope.yaml)"
Write-Host ("    {0,-42} {1}" -f "Capability", "URL") -ForegroundColor White
Write-Host ("    {0,-42} {1}" -f "---------", "---") -ForegroundColor White
$summary = @(
    @{ c = "JYso  (log4shell)";     u = "http://127.0.0.1:8983" }
    @{ c = "JYso  (fastjson)";      u = "http://127.0.0.1:8090" }
    @{ c = "JYso  (Spring4Shell)";  u = "http://127.0.0.1:8080" }
    @{ c = "SSTImap (Flask SSTI)";  u = "http://127.0.0.1:8000" }
    @{ c = "dalfox (DVWA XSS)";     u = "http://127.0.0.1:8088" }
    @{ c = "dalfox+logic (Juice)";  u = "http://127.0.0.1:3000" }
)
foreach ($s in $summary) {
    Write-Host ("    {0,-42} {1}" -f $s.c, $s.u) -ForegroundColor Green
}
Write-Host ""
Write-Host "    DVWA: open http://127.0.0.1:8088 , login admin/password, click 'Create / Reset Database'." -ForegroundColor Yellow
Write-Host "    Juice Shop: open http://127.0.0.1:3000 ." -ForegroundColor Yellow
Write-Host "    PEASS-ng: get a low-priv shell inside any container, then run linpeas.sh." -ForegroundColor Yellow
Write-Host ""
Write-Host "    Run 破晓 against a target, e.g.:" -ForegroundColor White
Write-Host "        reasonix scan http://127.0.0.1:8983" -ForegroundColor White

