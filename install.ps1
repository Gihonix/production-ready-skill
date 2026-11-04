# Install the production-ready-skill skills for Claude Code (Windows PowerShell).
#   .\install.ps1              -> $HOME\.claude\skills
#   .\install.ps1 -Project     -> .\.claude\skills
#   .\install.ps1 -Uninstall
param([switch]$Project, [switch]$Uninstall)
$here = Split-Path -Parent $MyInvocation.MyCommand.Path
$dest = if ($Project) { Join-Path (Get-Location) ".claude\skills" } else { Join-Path $HOME ".claude\skills" }
foreach ($d in Get-ChildItem (Join-Path $here "skills") -Directory) {
  $target = Join-Path $dest $d.Name
  if ($Uninstall) {
    if (Test-Path $target) { Remove-Item -Recurse -Force $target; Write-Host "removed $($d.Name)" }
  } else {
    New-Item -ItemType Directory -Force $dest | Out-Null
    if (Test-Path $target) { Remove-Item -Recurse -Force $target }
    Copy-Item -Recurse $d.FullName $target
    Write-Host "installed $($d.Name)"
  }
}
if (-not $Uninstall) { Write-Host "Done. In Claude Code, open your project and run /launch" }
