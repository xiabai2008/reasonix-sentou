<#
.SYNOPSIS
    下载恢复 Reasonix 渗透工作台所需的所有工具二进制和字典库
.DESCRIPTION
    git clone 后运行此脚本，自动从各工具官方源下载最新版本。
    工具清单见 config/tools-manifest.json
.EXAMPLE
    .\scripts\download-tools.ps1
    .\scripts\download-tools.ps1 -Force   # 强制重新下载
#>

param([switch]$Force)

$ErrorActionPreference = "Continue"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectDir = Split-Path -Parent $ScriptDir
$ToolsDir = Join-Path $ProjectDir "tools"
$DictDir = Join-Path $ProjectDir "config\dictionaries"

Write-Host "╔══════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║     Reasonix 渗透工作台 — 工具下载恢复      ║" -ForegroundColor Cyan
Write-Host "╚══════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# 确保目录存在
@($ToolsDir, $DictDir) | ForEach-Object {
    if (-not (Test-Path $_)) { New-Item -ItemType Directory -Path $_ -Force | Out-Null }
}

# ============================================================
# Step 0: 检查依赖
# ============================================================
Write-Host "[Preflight] 检查依赖..." -ForegroundColor Green
$ghOk = Get-Command "gh" -ErrorAction SilentlyContinue
if (-not $ghOk) {
    Write-Host "  [ERROR] 未找到 GitHub CLI (gh)。请安装: winget install GitHub.cli" -ForegroundColor Red
    Write-Host "  或从 https://cli.github.com 下载" -ForegroundColor Red
    exit 1
}
Write-Host "  [OK] GitHub CLI 可用" -ForegroundColor Green

# ============================================================
# Step 1: 下载工具二进制
# ============================================================
Write-Host ""
Write-Host "[Step 1/3] 下载 Windows 工具二进制..." -ForegroundColor Yellow

$tools = @(
    @{repo="projectdiscovery/nuclei";    name="nuclei";    bin="nuclei.exe"},
    @{repo="projectdiscovery/naabu";     name="naabu";     bin="naabu.exe"},
    @{repo="projectdiscovery/httpx";     name="httpx";     bin="httpx.exe"},
    @{repo="projectdiscovery/subfinder"; name="subfinder"; bin="subfinder.exe"},
    @{repo="projectdiscovery/katana";    name="katana";    bin="katana.exe"},
    @{repo="projectdiscovery/dnsx";      name="dnsx";      bin="dnsx.exe"},
    @{repo="projectdiscovery/tlsx";      name="tlsx";      bin="tlsx.exe"},
    @{repo="shadow1ng/fscan";            name="fscan";     bin="fscan.exe"},
    @{repo="ffuf/ffuf";                  name="ffuf";      bin="ffuf.exe"},
    @{repo="lc/gau";                     name="gau";       bin="gau.exe"},
    @{repo="jqlang/jq";                  name="jq";        bin="jq.exe"},
    @{repo="hahwul/dalfox";              name="dalfox";    bin="dalfox.exe"}
)

$downloaded = 0; $skipped = 0; $failed = 0

foreach ($tool in $tools) {
    $dest = Join-Path $ToolsDir $tool.bin
    if (Test-Path $dest -and -not $Force) {
        Write-Host "  [SKIP] $($tool.name) 已存在" -ForegroundColor Gray
        $skipped++
        continue
    }

    Write-Host "  [DOWNLOAD] $($tool.name) from $($tool.repo)..." -ForegroundColor Yellow -NoNewline
    
    try {
        # 获取最新 release 信息
        $releaseJson = gh release view --repo $tool.repo --json tagName,assets 2>&1 | Out-String
        if ($LASTEXITCODE -ne 0) { throw "无法获取 release 信息" }
        
        $release = $releaseJson | ConvertFrom-Json
        if (-not $release) { throw "JSON 解析失败" }
        
        # 匹配 Windows amd64 资产
        $asset = $release.assets | Where-Object { 
            $_.name -match "windows.*amd64" -and ($_.name -match "\.zip$" -or $_.name -match "\.exe$") 
        } | Select-Object -First 1
        
        if (-not $asset) {
            # 放宽匹配：只要含 exe 或 zip
            $asset = $release.assets | Where-Object { 
                $_.name -match "\.exe$" -or $_.name -match "\.zip$"
            } | Select-Object -First 1
        }
        
        if (-not $asset) { throw "未找到匹配的 Windows 资产" }
        
        $assetUrl = $asset.url
        $assetName = $asset.name
        
        # 下载
        $tmpFile = Join-Path $env:TEMP $assetName
        gh release download --repo $tool.repo --pattern $assetName --dir $env:TEMP 2>&1 | Out-Null
        
        if ($LASTEXITCODE -ne 0) { throw "下载失败" }
        
        # 解压或移动
        if ($assetName -match "\.zip$") {
            Expand-Archive -Path $tmpFile -DestinationPath $ToolsDir -Force
            # 如果解压后 .exe 不在 tools/ 根目录，查找并移动
            $exe = Get-ChildItem $ToolsDir -Recurse -Filter "$($tool.bin)" | Select-Object -First 1
            if ($exe -and (Split-Path $exe.FullName -Parent) -ne $ToolsDir) {
                Move-Item $exe.FullName $dest -Force
            }
            Remove-Item $tmpFile -Force
        } else {
            Move-Item $tmpFile $dest -Force
        }
        
        Write-Host " [OK]" -ForegroundColor Green
        $downloaded++
    } catch {
        Write-Host " [FAIL] $_" -ForegroundColor Red
        $failed++
    }
}

Write-Host "  完成: 下载 $downloaded / 跳过 $skipped / 失败 $failed" -ForegroundColor Yellow

# ============================================================
# Step 1.5: 克隆源码工具
# ============================================================
Write-Host ""
Write-Host "[Step 1.5/3] 克隆源码工具..." -ForegroundColor Yellow

$clonedTools = @(
    @{repo="carlospolop/PEASS-ng";  dir="peass-ng";  desc="Linux/Windows提权辅助"},
    @{repo="vladko312/SSTImap";     dir="sstimap";    desc="SSTI自动检测利用"},
    @{repo="LiChaser/SpiderX";      dir="spiderx";    desc="前端JS加密绕过"},
    @{repo="ReaJason/MemShellParty"; dir="MemShellParty"; desc="Java内存马注入"},
    @{repo="qi4L/JYso";             dir="JYso";       desc="JNDI+反序列化工具"}
)

foreach ($ct in $clonedTools) {
    $dest = Join-Path $ToolsDir $ct.dir
    if (Test-Path $dest -and -not $Force) {
        Write-Host "  [SKIP] $($ct.dir) ($($ct.desc)) 已存在" -ForegroundColor Gray
        $skipped++
        continue
    }
    
    Write-Host "  [CLONE] $($ct.repo) -> $($ct.dir) ($($ct.desc))..." -ForegroundColor Yellow -NoNewline
    
    try {
        if (Test-Path $dest) { Remove-Item $dest -Recurse -Force }
        git clone --depth 1 "https://github.com/$($ct.repo).git" $dest 2>&1 | Out-Null
        if ($LASTEXITCODE -eq 0) {
            Write-Host " [OK]" -ForegroundColor Green
            $downloaded++
        } else {
            Write-Host " [FAIL] git clone error" -ForegroundColor Red
            $failed++
        }
    } catch {
        Write-Host " [FAIL] $_" -ForegroundColor Red
        $failed++
    }
}

# MemShellParty 特殊处理：如果 README 说明需要编译，提示用户
$mspDir = Join-Path $ToolsDir "MemShellParty"
if (Test-Path $mspDir) {
    Write-Host "  [INFO] MemShellParty 需要 Maven 编译。参照 $mspDir/README.md" -ForegroundColor Gray
}
# SpiderX 特殊处理：安装 Python 依赖
$spxDir = Join-Path $ToolsDir "spiderx"
if (Test-Path $spxDir) {
    Write-Host "  [INFO] SpiderX Python依赖安装请参照 $spxDir/README.md" -ForegroundColor Gray
}

# ============================================================
# Step 2: 下载字典库
# ============================================================
Write-Host ""
Write-Host "[Step 2/4] 下载字典库..." -ForegroundColor Yellow

$dicts = @(
    @{repo="danielmiessler/SecLists";       dir="SecLists"},
    @{repo="CrackerCat/SuperWordlist";       dir="SuperWordlist"},
    @{repo="NS-Sp4ce/Dict";                  dir="Dict"},
    @{repo="R0B1NL1N/SaiDict";               dir="SaiDict"},
    @{repo="rootm0s/S-BlastingDictionary";    dir="S-BlastingDictionary"}
)

foreach ($dict in $dicts) {
    $dest = Join-Path $DictDir $dict.dir
    if (Test-Path $dest -and -not $Force) {
        Write-Host "  [SKIP] $($dict.dir) 已存在" -ForegroundColor Gray
        continue
    }
    
    Write-Host "  [CLONE] $($dict.repo) -> $($dict.dir)..." -ForegroundColor Yellow -NoNewline
    
    try {
        git clone --depth 1 "https://github.com/$($dict.repo).git" $dest 2>&1 | Out-Null
        if ($LASTEXITCODE -eq 0) {
            Write-Host " [OK]" -ForegroundColor Green
        } else {
            Write-Host " [FAIL]" -ForegroundColor Red
            $failed++
        }
    } catch {
        Write-Host " [FAIL] $_" -ForegroundColor Red
        $failed++
    }
}

# ============================================================
# Step 3: 生成自建字典
# ============================================================
Write-Host ""
Write-Host "[Step 3/4] 生成自建字典..." -ForegroundColor Yellow

$genScript = Join-Path $ProjectDir "config\generate-dicts.py"
$mergeScript = Join-Path $ProjectDir "config\merge-dicts.py"

if (Test-Path $genScript) {
    Write-Host "  运行 generate-dicts.py..." -ForegroundColor Gray
    python $genScript 2>&1 | Out-Null
}
if (Test-Path $mergeScript) {
    Write-Host "  运行 merge-dicts.py..." -ForegroundColor Gray
    python $mergeScript 2>&1 | Out-Null
}

# ============================================================
# 报告
# ============================================================
Write-Host ""
Write-Host "╔══════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║                下载完成                       ║" -ForegroundColor Cyan
Write-Host "╚══════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""
Write-Host "  工具: 成功 $downloaded / 跳过 $skipped / 失败 $failed" -ForegroundColor Yellow
Write-Host ""
if ($failed -gt 0) {
    Write-Host "  [WARN] 部分下载失败。可重新运行本脚本重试。" -ForegroundColor Yellow
    Write-Host "  也可手动从各工具 GitHub Releases 页面下载。" -ForegroundColor White
}

Write-Host ""
Write-Host "  [NEXT] 运行环境配置: .\scripts\setup-new-pc.ps1" -ForegroundColor Green
