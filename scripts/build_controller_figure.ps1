<#
.SYNOPSIS
  Regenerates figures/fig_controller_interaction.pptx and its PDF.

.DESCRIPTION
  Two steps:
    1. node scripts/build_controller_figure_pptx.js  -- draws the slide.
    2. PowerPoint COM SaveCopyAs                     -- exports the PDF at the
       slide's exact size (12 x 5.16 in), so \includegraphics gets no margin.

  pptxgenjs must be resolvable; if it is not installed in this repository set
  NODE_PATH to a node_modules directory that has it.

  The icon PNGs are consumed as-is.  If they are ever replaced, run
  scripts/trim_icons.ps1 first -- an opaque margin around an icon hides the
  arrowheads that terminate on it.

.EXAMPLE
  powershell -ExecutionPolicy Bypass -File scripts/build_controller_figure.ps1
#>

[CmdletBinding()]
param(
  [string]$RepoRoot = (Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path))
)

$ErrorActionPreference = "Stop"

$script = Join-Path $RepoRoot "scripts\build_controller_figure_pptx.js"
$pptx   = Join-Path $RepoRoot "figures\fig_controller_interaction.pptx"
$pdf    = Join-Path $RepoRoot "figures\fig_controller_interaction.pdf"

& node $script
if ($LASTEXITCODE -ne 0) { throw "build_controller_figure_pptx.js failed ($LASTEXITCODE)" }

if (Test-Path $pdf) { Remove-Item $pdf -Force }
$pp = New-Object -ComObject PowerPoint.Application
try {
  $pres = $pp.Presentations.Open($pptx, $true, $false, $false)
  $pres.SaveCopyAs($pdf, 32)   # 32 = ppSaveAsPDF
  $pres.Close()
} finally { $pp.Quit() }

Get-Item $pptx, $pdf | Select-Object Name, Length, LastWriteTime
