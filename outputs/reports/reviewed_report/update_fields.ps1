$ErrorActionPreference='Stop'
$folder=Join-Path (Get-Location).Path 'outputs\reports\reviewed_report'
$path=Join-Path $folder 'Final Report.docx'
$app=$null;$doc=$null
try {
 $app=New-Object -ComObject Word.Application
 if($app.Documents.Count -ne 0){throw 'The new Word instance already has documents; stop to protect them.'}
 $app.Visible=$false;$app.DisplayAlerts=0;$app.AutomationSecurity=3
 $app.Options.UpdateFieldsAtPrint=$false;$app.Options.UpdateLinksAtPrint=$false
 $doc=$app.Documents.Open($path,$false,$false,$false)
 for($pass=1;$pass -le 2;$pass++){
  $doc.Fields.Update() | Out-Null
  $count=$doc.TablesOfContents.Count
  for($i=1;$i -le $count;$i++){$doc.TablesOfContents.Item($i).Update()}
  $count=$doc.TablesOfFigures.Count
  for($i=1;$i -le $count;$i++){$doc.TablesOfFigures.Item($i).Update()}
  $doc.Repaginate()
 }
 $doc.Save()
 [ordered]@{pages=$doc.ComputeStatistics(2);fields=$doc.Fields.Count;contents=$doc.TablesOfContents.Count;figure_lists=$doc.TablesOfFigures.Count;tables=$doc.Tables.Count;images=$doc.InlineShapes.Count} | ConvertTo-Json | Set-Content -Encoding UTF8 (Join-Path $folder 'field_update_log.json')
 Write-Output 'Updated fields in reviewed copy; no report reconstruction or PDF conversion'
} finally {
 if($null -ne $doc){$doc.Close(0)}
 if($null -ne $app -and $app.Documents.Count -eq 0){$app.Quit()}
}
