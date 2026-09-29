$ErrorActionPreference = 'Stop'

$project = Split-Path $PSScriptRoot -Parent
Set-Location $project

$b64 = (Get-Content -Raw 'main.go.gz.b64').Trim()
$bytes = [Convert]::FromBase64String($b64)
$ms = [IO.MemoryStream]::new($bytes)
$gz = [IO.Compression.GZipStream]::new($ms, [IO.Compression.CompressionMode]::Decompress)
$out = [IO.File]::Create((Join-Path $project 'main.go'))
$gz.CopyTo($out)
$out.Dispose(); $gz.Dispose(); $ms.Dispose()

$src = Get-Content -Raw 'main.go'
$src = $src.Replace('ĐỔI TÊN - NÉN FILE PDF', 'ĐUỔI ĐUÔI PDF VÀ NÉN FILE PDF')
$src = $src.Replace('Đổi tên - Nén file PDF', 'Đuổi đuôi PDF và Nén file PDF')
$src = $src.Replace('v4.1.0 OFFLINE', 'v4.4.0 OFFLINE')
$src = $src.Replace('v4.1.0', 'v4.4.0')
$src = $src.Replace('AUTO là mặc định: chọn thư mục → BẮT ĐẦU NÉN. Chỉ AUTO mới bỏ qua file dưới 20 MB.', 'AUTO: kiểm tra từng trang >500 KB + file <20 MB • chỉ nén 1 thế hệ từ bản gốc • ưu tiên độ nét.')
$src = $src.Replace('Bộ nén PDF: tích hợp sẵn • OFFLINE 100%', 'Bộ phân tích trang + nén PDF: tích hợp sẵn • OFFLINE 100%')

# Replace runCompress + its old progress helper in one operation. This avoids
# concatenation/syntax bugs and keeps the rest of the application untouched.
$runStart = $src.IndexOf('func runCompress(')
$runEnd = $src.IndexOf('func mb(', $runStart)
if ($runStart -lt 0 -or $runEnd -le $runStart) {
    throw 'Cannot locate runCompress/updateCompressProgress block'
}
$runFragment = (Get-Content -Raw (Join-Path $PSScriptRoot 'runcompress.go.txt')).TrimEnd()
$src = $src.Substring(0, $runStart) + $runFragment + "`r`n`r`n" + $src.Substring($runEnd)

# Replace only compressionResult + AUTO implementation. Manual compression and
# lower-level Ghostscript helpers remain the proven existing implementation.
$compStart = $src.IndexOf('type compressionResult struct')
$compEnd = $src.IndexOf('func compressAtDPI', $compStart)
if ($compStart -lt 0 -or $compEnd -le $compStart) {
    throw 'Cannot locate compressionResult/compressAuto block'
}
$compFragment = (Get-Content -Raw (Join-Path $PSScriptRoot 'compression.go.txt')).TrimEnd()
$src = $src.Substring(0, $compStart) + $compFragment + "`r`n`r`n" + $src.Substring($compEnd)

Set-Content 'main.go' $src -Encoding utf8
"module duoi-duoi-pdf-nen-file-pdf`n`ngo 1.23`n" | Set-Content 'go.mod' -Encoding ascii

gofmt -w main.go
if ($LASTEXITCODE -ne 0) { throw 'gofmt failed' }
go vet ./...
if ($LASTEXITCODE -ne 0) { throw 'go vet failed' }

Write-Host 'v4.4.0 source patch OK'
