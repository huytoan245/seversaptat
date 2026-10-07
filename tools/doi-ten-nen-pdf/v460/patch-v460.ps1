$ErrorActionPreference = 'Stop'

$project = Split-Path $PSScriptRoot -Parent
Set-Location $project
$nl = [Environment]::NewLine

if(-not (Test-Path 'main.go')) { throw 'main.go missing; run v450 patch first' }
$src = Get-Content -Raw 'main.go'

$src = $src.Replace('v4.5.0 OFFLINE', 'v4.6.0 OFFLINE')
$src = $src.Replace('DoiTenNenPDFMainWindow_v410', 'DoiTenNenPDFMainWindow_v460')

if(-not $src.Contains('WS_GROUP')) {
    $needle = 'WS_TABSTOP          = 0x00010000'
    if(-not $src.Contains($needle)){ throw 'WS_TABSTOP anchor missing' }
    $src = $src.Replace($needle, $needle + $nl + [char]9 + 'WS_GROUP            = 0x00020000')
}

$idNeedle = 'ID_COMP_STOP   = 1029'
if(-not $src.Contains($idNeedle)){ throw 'ID_COMP_STOP anchor missing' }
$idExtra = $idNeedle + $nl + [char]9 + 'ID_AUTO_MODE1  = 1030' + $nl + [char]9 + 'ID_AUTO_MODE2  = 1031' + $nl + [char]9 + 'ID_AUTO_MODE3  = 1032'
$src = $src.Replace($idNeedle, $idExtra)

$handleNeedle = 'compAuto, compManual, dpi300, dpi250, dpi220, dpi200                  uintptr'
if(-not $src.Contains($handleNeedle)){ throw 'ui handle anchor missing' }
$handleNew = 'compAuto, compManual, autoMode1, autoMode2, autoMode3, dpi300, dpi250, dpi220, dpi200 uintptr'
$src = $src.Replace($handleNeedle, $handleNew)

$uiStart = $src.IndexOf('// Compress view')
$uiEnd = $src.IndexOf('switchMode(1)', $uiStart)
if($uiStart -lt 0 -or $uiEnd -le $uiStart){ throw 'compress UI block not found' }
$uiFragment = (Get-Content -Raw (Join-Path $PSScriptRoot 'ui-compress.go.txt')).TrimEnd()
$src = $src.Substring(0,$uiStart) + $uiFragment + $nl + $nl + [char]9 + $src.Substring($uiEnd)

$switchStart = $src.IndexOf('func switchMode(')
$switchEnd = $src.IndexOf('func wndProc(', $switchStart)
if($switchStart -lt 0 -or $switchEnd -le $switchStart){ throw 'switchMode/setBusy block not found' }
$switchFragment = (Get-Content -Raw (Join-Path $PSScriptRoot 'switch-busy.go.txt')).TrimEnd()
$src = $src.Substring(0,$switchStart) + $switchFragment + $nl + $nl + $src.Substring($switchEnd)

$wndStart = $src.IndexOf('func wndProc(')
$cmdStart = $src.IndexOf('case ID_COMP_AUTO:', $wndStart)
$cmdEnd = $src.IndexOf('case ID_DPI_300, ID_DPI_250, ID_DPI_220, ID_DPI_200:', $cmdStart)
if($cmdStart -lt 0 -or $cmdEnd -le $cmdStart){ throw 'AUTO command block not found' }
$cmdFragment = (Get-Content -Raw (Join-Path $PSScriptRoot 'command-auto-modes.go.txt')).TrimEnd()
$src = $src.Substring(0,$cmdStart) + $cmdFragment + $nl + [char]9 + [char]9 + [char]9 + $src.Substring($cmdEnd)

$startComp = $src.IndexOf('func startCompress()')
$startDPI = $src.IndexOf('func selectedDPI()', $startComp)
if($startComp -lt 0 -or $startDPI -le $startComp){ throw 'startCompress block not found' }
$startFragment = (Get-Content -Raw (Join-Path $PSScriptRoot 'startcompress.go.txt')).TrimEnd()
$src = $src.Substring(0,$startComp) + $startFragment + $nl + $nl + $src.Substring($startDPI)

$runStart = $src.IndexOf('func runCompress(')
$runEnd = $src.IndexOf('func mb(', $runStart)
if($runStart -lt 0 -or $runEnd -le $runStart){ throw 'runCompress block not found' }
$runFragment = (Get-Content -Raw (Join-Path $PSScriptRoot 'runcompress.go.txt')).TrimEnd()
$src = $src.Substring(0,$runStart) + $runFragment + $nl + $nl + $src.Substring($runEnd)

$compStart = $src.IndexOf('type compressionResult struct')
$compEnd = $src.IndexOf('func compressAtDPI', $compStart)
if($compStart -lt 0 -or $compEnd -le $compStart){ throw 'AUTO compression block not found' }
$compFragment = (Get-Content -Raw (Join-Path $PSScriptRoot 'compression.go.txt')).TrimEnd()
$src = $src.Substring(0,$compStart) + $compFragment + $nl + $nl + $src.Substring($compEnd)

Set-Content 'main.go' $src -Encoding utf8

gofmt -w main.go
if($LASTEXITCODE -ne 0){ throw 'gofmt failed' }
go vet ./...
if($LASTEXITCODE -ne 0){ throw 'go vet failed' }

$check = Get-Content -Raw 'main.go'
foreach($token in @(
    'appVersion = "v4.6.0 OFFLINE"',
    'ID_AUTO_MODE1',
    'ID_AUTO_MODE2',
    'ID_AUTO_MODE3',
    'selectedAutoMode460',
    'autoPolicyForMode460',
    'FileLimit: 30_000_000',
    'PageLimit: 500_000',
    'workerCount = 2',
    'NEVER used as input to another Ghostscript pass'
)){
    if(-not $check.Contains($token)){ throw "v4.6 invariant missing: $token" }
}

Write-Host 'v4.6.0 source patch OK'
