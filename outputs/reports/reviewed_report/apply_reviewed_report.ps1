$ErrorActionPreference='Stop'
$folder=Join-Path (Get-Location).Path 'outputs\reports\reviewed_report'
$source=Join-Path $folder 'Final Report.docx'
$destination='C:\Users\LENOVO\OneDrive\Desktop\Final Report.docx'
$original=Get-Content -Raw -LiteralPath (Join-Path $folder 'original_source.json') | ConvertFrom-Json
$validation=Get-Content -Raw -LiteralPath (Join-Path $folder 'report_validation.json') | ConvertFrom-Json
if ((Get-FileHash -LiteralPath $destination -Algorithm SHA256).Hash.ToLowerInvariant() -ne $(if($original.expected_target_sha256){$original.expected_target_sha256}else{$original.sha256})) { throw 'The original manual report changed after review. Do not overwrite it.' }
if ((Get-FileHash -LiteralPath $source -Algorithm SHA256).Hash.ToLowerInvariant() -ne $validation.reviewed_sha256) { throw 'The reviewed copy changed after validation.' }
$backup=Join-Path $env:TEMP 'STAT3013_manual_report_before_review.docx'
if(-not (Test-Path -LiteralPath $backup)) { Copy-Item -LiteralPath $destination -Destination $backup }
Copy-Item -LiteralPath $source -Destination $destination -Force
if ((Get-FileHash -LiteralPath $destination -Algorithm SHA256).Hash.ToLowerInvariant() -ne $validation.reviewed_sha256) { throw 'Copy verification failed.' }
Write-Output 'Saved and hash-verified the reviewed report at the exact user-specified Desktop path.'
