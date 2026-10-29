$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
$out = Join-Path $root 'artifacts/docx-review/word-render'
New-Item -ItemType Directory -Force -Path $out | Out-Null
$word = New-Object -ComObject Word.Application
$word.Visible = $false
$word.DisplayAlerts = 0
$results = @()
try {
    foreach ($set in @('original','edited')) {
        $folder = if ($set -eq 'original') { Join-Path $root 'tài liệu xây dựng và mẫu thầy giáo gửi để tham khảo promt' } else { Join-Path $root 'docs/DOCX_DA_CHINH_SUA' }
        $index = 0
        foreach ($file in Get-ChildItem -LiteralPath $folder -Filter '*.docx' -File | Sort-Object Name) {
            $index++
            $doc = $null
            try {
                $doc = $word.Documents.Open($file.FullName, $false, $true, $false)
                $doc.Repaginate()
                $pages = $doc.ComputeStatistics(2)
                $pdf = Join-Path $out ($set + '-' + $index + '.pdf')
                $doc.ExportAsFixedFormat($pdf, 17)
                $results += [pscustomobject]@{Set=$set;Index=$index;Name=$file.Name;Pages=$pages;PDF=$pdf}
                Write-Output ($set + ' ' + $index + ': ' + $pages + ' pages')
            } finally { if ($null -ne $doc) { $doc.Close(0); [void][Runtime.InteropServices.Marshal]::ReleaseComObject($doc) } }
        }
    }
} finally { $word.Quit(0); [void][Runtime.InteropServices.Marshal]::ReleaseComObject($word) }
$results | ConvertTo-Json | Set-Content -Encoding UTF8 (Join-Path $out 'pages.json')
