<#
.SYNOPSIS
    下载恢复 Reasonix 渗透工作台所需的所有工具二进制和字典库
.DESCRIPTION
    git clone 后运行此脚本，自动从各工具官方源下载最新版本。
    工具清单来自 config/tools-manifest.json，修改工具列表只需编辑该文件。
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
$ManifestPath = Join-Path $ProjectDir "config\tools-manifest.json"

Write-Host "╔══════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║     Reasonix 渗透工作台 — 工具下载恢复      ║" -ForegroundColor Cyan
Write-Host "╚══════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# 确保目录存在
@($ToolsDir, $DictDir) | ForEach-Object {
    if (-not (Test-Path $_)) { New-Item -ItemType Directory -Path $_ -Force | Out-Null }
}

# ============================================================
# Step 0: 检查依赖 + 加载 manifest
# ============================================================
Write-Host "[Preflight] 检查依赖..." -ForegroundColor Green
$ghOk = Get-Command "gh" -ErrorAction SilentlyContinue
if (-not $ghOk) {
    Write-Host "  [ERROR] 未找到 GitHub CLI (gh)。请安装: winget install GitHub.cli" -ForegroundColor Red
    Write-Host "  或从 https://cli.github.com 下载" -ForegroundColor Red
    exit 1
}
Write-Host "  [OK] GitHub CLI 可用" -ForegroundColor Green

if (-not (Test-Path $ManifestPath)) {
    Write-Host "  [ERROR] 未找到工具清单: $ManifestPath" -ForegroundColor Red
    exit 1
}
Write-Host "  [OK] 工具清单: config/tools-manifest.json" -ForegroundColor Green

$manifest = Get-Content $ManifestPath -Raw -Encoding UTF8 | ConvertFrom-Json

$downloaded = 0; $skipped = 0; $failed = 0

# ============================================================
# Step 1: 下载工具二进制（gh release download）
# ============================================================
Write-Host ""
Write-Host "[Step 1/3] 下载 Windows 工具二进制 (gh release)..." -ForegroundColor Yellow

$toolCount = 0
foreach ($name in $manifest.tools.PSObject.Properties.Name) {
    $toolCount++
}
$toolIndex = 0

foreach ($name in $manifest.tools.PSObject.Properties.Name) {
    $toolIndex++
    $t = $manifest.tools.$name
    $dest = Join-Path $ToolsDir $t.bin
    $tmpFile = $null

    Write-Host "  [$toolIndex/$toolCount] " -NoNewline

    if (Test-Path $dest -and -not $Force) {
        Write-Host "[SKIP] $name 已存在" -ForegroundColor Gray
        $skipped++
        continue
    }

    Write-Host "[DOWNLOAD] $name from $($t.repo)..." -NoNewline

    try {
        # 获取最新 release 信息
        $releaseJson = gh release view --repo $t.repo --json tagName,assets 2>&1 | Out-String
        if ($LASTEXITCODE -ne 0) { throw "无法获取 release 信息" }

        $release = $releaseJson | ConvertFrom-Json
        if (-not $release) { throw "JSON 解析失败" }

        # 优先用 manifest 中的 asset_pattern 精确匹配
        $asset = $null
        if ($t.asset_pattern) {
            $asset = $release.assets | Where-Object {
                $_.name -match $t.asset_pattern
            } | Select-Object -First 1
        }

        # Fallback: 宽松匹配 Windows amd64 zip/exe
        if (-not $asset) {
            $asset = $release.assets | Where-Object {
                $_.name -match "windows.*amd64" -and ($_.name -match "\.zip$" -or $_.name -match "\.exe$")
            } | Select-Object -First 1
        }

        # 再次 fallback: 任意 zip/exe
        if (-not $asset) {
            $asset = $release.assets | Where-Object {
                $_.name -match "\.exe$" -or $_.name -match "\.zip$"
            } | Select-Object -First 1
        }

        if (-not $asset) { throw "未找到匹配的 Windows 资产" }

        $assetName = $asset.name
        $tmpFile = Join-Path $env:TEMP $assetName

        # 下载
        gh release download --repo $t.repo --pattern $assetName --dir $env:TEMP 2>&1 | Out-Null
        if ($LASTEXITCODE -ne 0) { throw "下载失败" }

        # 解压或移动
        if ($assetName -match "\.zip$") {
            Expand-Archive -Path $tmpFile -DestinationPath $ToolsDir -Force
            # 如果解压后 .exe 不在 tools/ 根目录，查找并移动
            $exe = Get-ChildItem $ToolsDir -Recurse -Filter "$($t.bin)" | Select-Object -First 1
            if ($exe -and (Split-Path $exe.FullName -Parent) -ne $ToolsDir) {
                Move-Item $exe.FullName $dest -Force
            }
            Remove-Item $tmpFile -Force -ErrorAction SilentlyContinue
        } elseif ($assetName -match "\.tar\.gz$") {
            # tar.gz 解压
            tar -xzf $tmpFile -C $ToolsDir 2>&1 | Out-Null
            $exe = Get-ChildItem $ToolsDir -Recurse -Filter "$($t.bin)" | Select-Object -First 1
            if ($exe -and (Split-Path $exe.FullName -Parent) -ne $ToolsDir) {
                Move-Item $exe.FullName $dest -Force
            }
            Remove-Item $tmpFile -Force -ErrorAction SilentlyContinue
        } else {
            # 直接移动（exe 或其他单文件）
            Move-Item $tmpFile $dest -Force
        }

        Write-Host " [OK]" -ForegroundColor Green
        $downloaded++
    } catch {
        Write-Host " [FAIL] $_" -ForegroundColor Red
        $failed++
        # 清理可能的残留临时文件
        if ($tmpFile -and (Test-Path $tmpFile)) { Remove-Item $tmpFile -Force -ErrorAction SilentlyContinue }
    }
}

Write-Host "  完成: 下载 $downloaded / 跳过 $skipped / 失败 $failed" -ForegroundColor Yellow

# ============================================================
# Step 2: 克隆源码工具（git clone）
# ============================================================
Write-Host ""
Write-Host "[Step 2/3] 克隆源码工具 (git clone)..." -ForegroundColor Yellow

$cloneCount = 0
foreach ($name in $manifest.cloned_tools.PSObject.Properties.Name) {
    $cloneCount++
}
$cloneIndex = 0

foreach ($name in $manifest.cloned_tools.PSObject.Properties.Name) {
    $cloneIndex++
    $ct = $manifest.cloned_tools.$name
    # target 格式: "tools/xxx" -> 相对于 ProjectDir
    $dest = Join-Path $ProjectDir $ct.target

    Write-Host "  [$cloneIndex/$cloneCount] " -NoNewline

    if (Test-Path $dest -and -not $Force) {
        Write-Host "[SKIP] $name ($($ct.target)) 已存在" -ForegroundColor Gray
        $skipped++
        continue
    }

    $desc = if ($ct.note) { $ct.note } else { $name }
    Write-Host "[CLONE] $($ct.repo) -> $($ct.target) ($desc)..." -NoNewline

    try {
        # 确保父目录存在
        $parentDir = Split-Path $dest -Parent
        if (-not (Test-Path $parentDir)) { New-Item -ItemType Directory -Path $parentDir -Force | Out-Null }

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
    Write-Host "  [INFO] SpiderX Python 依赖安装请参照 $spxDir/README.md" -ForegroundColor Gray
}

# ============================================================
# Step 3: 下载字典库 + 生成自建字典
# ============================================================
Write-Host ""
Write-Host "[Step 3/3] 下载字典库 + 生成自建字典..." -ForegroundColor Yellow

# 3a: 从 manifest 克隆字典库
$dictCount = 0
foreach ($name in $manifest.dictionaries.PSObject.Properties.Name) {
    $dictCount++
}
$dictIndex = 0

foreach ($name in $manifest.dictionaries.PSObject.Properties.Name) {
    $dictIndex++
    $d = $manifest.dictionaries.$name
    # target 格式: "config/dictionaries/xxx" -> 相对于 ProjectDir
    $dest = Join-Path $ProjectDir $d.target

    Write-Host "  [$dictIndex/$dictCount] " -NoNewline

    if (Test-Path $dest -and -not $Force) {
        Write-Host "[SKIP] $name 已存在" -ForegroundColor Gray
        continue
    }

    Write-Host "[CLONE] $($d.repo) -> $($d.target)..." -NoNewline

    try {
        # 确保父目录存在
        $parentDir = Split-Path $dest -Parent
        if (-not (Test-Path $parentDir)) { New-Item -ItemType Directory -Path $parentDir -Force | Out-Null }

        git clone --depth 1 "https://github.com/$($d.repo).git" $dest 2>&1 | Out-Null
        if ($LASTEXITCODE -eq 0) {
            Write-Host " [OK]" -ForegroundColor Green
            $downloaded++
        } else {
            Write-Host " [FAIL]" -ForegroundColor Red
            $failed++
        }
    } catch {
        Write-Host " [FAIL] $_" -ForegroundColor Red
        $failed++
    }
}

# 3b: 生成自建字典
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