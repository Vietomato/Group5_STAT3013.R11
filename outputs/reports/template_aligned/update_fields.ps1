$ErrorActionPreference='Stop'
$folder=Join-Path (Get-Location).Path 'outputs\reports\template_aligned'
$path=Join-Path $folder 'final_report_en.docx'
$log=Join-Path $folder 'update_progress.log'
function Progress($message){$message | Add-Content -LiteralPath $log -Encoding UTF8; Write-Output $message}
Set-Content -LiteralPath $log -Value 'Starting Word field update' -Encoding UTF8
$app=$null;$doc=$null
try {
 $app=New-Object -ComObject Word.Application
 $app.Visible=$false;$app.DisplayAlerts=0;$app.AutomationSecurity=3
 $app.Options.UpdateFieldsAtPrint=$false;$app.Options.UpdateLinksAtPrint=$false
 Progress 'Word created'
 $doc=$app.Documents.Open($path,$false,$false,$false)
 Progress ('Opened: fields='+$doc.Fields.Count+'; TOCs='+$doc.TablesOfContents.Count+'; TOFs='+$doc.TablesOfFigures.Count)
 for($pass=1;$pass -le 2;$pass++){
  Progress ('Updating fields, pass '+$pass)
  $doc.Fields.Update() | Out-Null
  Progress 'Fields updated'
  $count=$doc.TablesOfContents.Count
  for($i=1;$i -le $count;$i++){$doc.TablesOfContents.Item($i).Update();Progress ('TOC '+$i+' updated')}
  $count=$doc.TablesOfFigures.Count
  for($i=1;$i -le $count;$i++){$doc.TablesOfFigures.Item($i).Update();Progress ('TOF '+$i+' updated')}
  $doc.Repaginate();Progress 'Repaginated'
 }
 $doc.Save();Progress 'Saved Word'
 $app.Options.UpdateFieldsAtPrint=$true
 $result=[ordered]@{pages=$doc.ComputeStatistics(2);fields=$doc.Fields.Count;contents=$doc.TablesOfContents.Count;figure_lists=$doc.TablesOfFigures.Count;tables=$doc.Tables.Count;images=$doc.InlineShapes.Count}
 $result | ConvertTo-Json | Set-Content (Join-Path $folder 'word_update_log.json') -Encoding UTF8
} finally {
 if($null -ne $doc){$doc.Close(0)}
 if($null -ne $app -and $app.Documents.Count -eq 0){$app.Quit()}
}
