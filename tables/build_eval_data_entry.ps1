# Regenerate tables/tab_eval_data_entry.tex from docs/evaluation-table.xlsx.
#
# Workflow: fill the measured values in the workbook's "Data Entry" sheet,
# save it, then run this script from the repository root:
#
#     powershell -File tables\build_eval_data_entry.ps1
#
# It reads the "Data Entry" sheet (no Excel install required -- the .xlsx is
# parsed directly) and rewrites tables/tab_eval_data_entry.tex in place.
#
# Structure is fixed by this script: two tables (12MP, 24MP), overheat levels
# Lv0..Lv6, shot counts 5/10/30, Normal and Memory-pressure side by side, and
# the daggers on 24MP Lv5/Lv6. Only the numeric values come from the sheet.

param(
    [string]$Xlsx = (Join-Path $PSScriptRoot '..\docs\evaluation-table.xlsx'),
    [string]$Out  = (Join-Path $PSScriptRoot 'tab_eval_data_entry.tex')
)
$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.IO.Compression.FileSystem

function Get-ColLetter([string]$ref) { return ($ref -replace '[0-9]', '') }

function Get-CellValue($c, $shared) {
    $v = $c.v
    if ($c.t -eq 's' -and $null -ne $v) { return $shared[[int]$v] }
    if ($c.t -eq 'inlineStr' -and $c.is) { return $c.is.t }
    if ($null -eq $v -and $c.is) { return $c.is.t }
    return $v
}

function Read-DataEntry([string]$path) {
    if (-not (Test-Path $path)) { throw "Workbook not found: $path" }
    # Copy first so a workbook left open in Excel can still be read.
    $tmp = [System.IO.Path]::GetTempFileName()
    $src = [System.IO.File]::Open($path, 'Open', 'Read', 'ReadWrite')
    $dst = [System.IO.File]::Create($tmp)
    $src.CopyTo($dst); $dst.Close(); $src.Close()

    $zip = [System.IO.Compression.ZipFile]::OpenRead($tmp)
    try {
        function ReadEntry([string]$name) {
            $e = $zip.GetEntry($name); if ($null -eq $e) { return $null }
            $sr = New-Object System.IO.StreamReader($e.Open())
            $t = $sr.ReadToEnd(); $sr.Close(); return $t
        }
        $shared = @()
        $ssXml = ReadEntry 'xl/sharedStrings.xml'
        if ($ssXml) {
            $x = [xml]$ssXml
            foreach ($si in $x.sst.si) {
                $txt = ''
                if ($si.t) { $inner = $si.t.'#text'; if ($null -eq $inner) { $inner = $si.t }; $txt = $inner }
                elseif ($si.r) { foreach ($r in $si.r) { $txt += $r.t } }
                $shared += , [string]$txt
            }
        }
        $wsEntries = $zip.Entries | Where-Object { $_.FullName -match '^xl/worksheets/sheet\d+\.xml$' }
        foreach ($we in $wsEntries) {
            $sr = New-Object System.IO.StreamReader($we.Open())
            $doc = [xml]($sr.ReadToEnd()); $sr.Close()
            $rows = @($doc.worksheet.sheetData.row)
            if ($rows.Count -eq 0) { continue }

            $hdr = @{}
            foreach ($c in $rows[0].c) {
                $v = Get-CellValue $c $shared
                if ($v) { $hdr[[string]$v] = (Get-ColLetter $c.r) }
            }
            if (-not ($hdr.ContainsKey('Tier') -and $hdr.ContainsKey('Bokeh admits'))) { continue }

            $result = @()
            foreach ($row in $rows) {
                if ($row.r -eq '1') { continue }
                $byCol = @{}
                foreach ($c in $row.c) { $byCol[(Get-ColLetter $c.r)] = (Get-CellValue $c $shared) }
                $val = { param($name) $col = $hdr[$name]; if ($col) { $byCol[$col] } else { $null } }
                $tier = & $val 'Tier'
                if ([string]::IsNullOrWhiteSpace([string]$tier)) { continue }
                $result += [pscustomobject]@{
                    Tier         = [string](& $val 'Tier')
                    Level        = [string](& $val 'Level')
                    Memory       = [string](& $val 'Memory')
                    Shots        = [int][double](& $val 'Shots')
                    BokehAdmits  = [int][double](& $val 'Bokeh admits')
                    FilterAdmits = [int][double](& $val 'Filter admits')
                    MarginMs     = [int][math]::Round([double](& $val 'UB margin (ms)'))
                    CoverPct     = [double](& $val 'UB cover (%)')
                    AvgMs        = [int][math]::Round([double](& $val 'Pacing Avg (ms)'))
                    MaxMs        = [int][math]::Round([double](& $val 'Pacing Max (ms)'))
                }
            }
            return $result
        }
        throw "No 'Data Entry' worksheet with the expected headers (Tier, Bokeh admits, ...) was found."
    }
    finally {
        $zip.Dispose()
        Remove-Item $tmp -Force -ErrorAction SilentlyContinue
    }
}

# ---- read + index -----------------------------------------------------------
$data = Read-DataEntry $Xlsx
$map = @{}
foreach ($r in $data) { $map["$($r.Tier)|$($r.Level)|$($r.Memory)|$($r.Shots)"] = $r }

function Get-Row($tier, $lv, $mem, $shots) {
    $key = "$tier|Lv$lv|$mem|$shots"
    if (-not $map.ContainsKey($key)) { throw "Missing Data Entry row: $key" }
    return $map[$key]
}

# ---- emit -------------------------------------------------------------------
$sb = New-Object System.Text.StringBuilder
function AL([string]$s) { [void]$script:sb.AppendLine($s) }

$preamble = @'
% Combined per-burst measurement tables (Data Entry mirror). One table per
% image-size tier, placing Normal and Memory-pressure capture side by side.
%
% GENERATED FILE -- do not edit values by hand. Fill measured numbers in
% docs/evaluation-table.xlsx (sheet "Data Entry") and regenerate with
% tables/build_eval_data_entry.ps1.
%
% Column meanings:
%   Run rate    : cumulative admits/shots for the stage over the shot sequence.
%   Upper bound : margin = median headroom of the predicted upper bound
%                 over the actual sequence duration (ms; smaller = tighter);
%                 cover = %% of executions whose actual stayed within the
%                 upper bound (bound coverage; misses recovered by watchdog).
%   Pacing      : added delay of the captureAvailable callback (Avg / Max).
'@
AL $preamble
AL ''

$cap12 = 'Per-burst draft-sequence measurements under our admission controller (12MP tier), with normal and memory-pressure capture side by side. All optional stages are admitted with zero Capture Timeouts (stability 100\%). Run rate is the cumulative number of captures in which the stage was admitted over the shot sequence. Under \emph{Upper bound}, margin is the median headroom of the predicted upper bound over the observed sequence duration (predicted minus actual, in milliseconds; smaller is tighter) and cover is the percentage of stage executions whose observed duration stayed within the predicted upper bound (bound coverage; the rare misses are recovered by the watchdog so no capture times out). Pacing is the added delay of the \texttt{captureAvailable} callback.'
$cap24 = 'Per-burst draft-sequence measurements under our admission controller (24MP tier), with normal and memory-pressure capture side by side. All optional stages are admitted with zero Capture Timeouts (stability 100\%). Run rate is the cumulative number of captures in which the stage was admitted over the shot sequence. Under \emph{Upper bound}, margin is the median headroom of the predicted upper bound over the observed sequence duration (predicted minus actual, in milliseconds; smaller is tighter) and cover is the percentage of stage executions whose observed duration stayed within the predicted upper bound (bound coverage; the rare misses are recovered by the watchdog so no capture times out). Pacing is the added delay of the \texttt{captureAvailable} callback. Rows marked $^{\dagger}$ report 12MP-mode measurements because 24MP capture falls back to 12MP mode at Lv5 and above.'

$tiers = @(
    @{ tier = '12MP'; label = 'tab:eval_data_12mp'; caption = $cap12; is24 = $false },
    @{ tier = '24MP'; label = 'tab:eval_data_24mp'; caption = $cap24; is24 = $true }
)
$shotsList = @(5, 10, 30)

foreach ($t in $tiers) {
    AL '\begin{table*}[t]'
    AL '  \centering'
    AL ('  \caption{' + $t.caption + '}')
    AL ('  \label{' + $t.label + '}')
    AL '  \resizebox{\textwidth}{!}{%'
    AL '  \begin{tabular}{c|c||cc|cc|rr||cc|cc|rr}'
    AL '  \toprule \midrule'
    AL '  \multirow{3}{*}[-12pt]{\makecell{\textbf{Overheat}\\\textbf{Level}}} &'
    AL '  \multirow{3}{*}[-12pt]{\makecell{\textbf{Shots}}} &'
    AL '  \multicolumn{6}{c||}{\textbf{Normal capture}} &'
    AL '  \multicolumn{6}{c}{\textbf{Memory-pressure capture}} \\'
    AL '  \cmidrule(lr){3-8}\cmidrule(l){9-14}'
    AL '  & & \multicolumn{2}{c|}{\textbf{Run rate}} & \multicolumn{2}{c|}{\textbf{Upper bound}} & \multicolumn{2}{c||}{\textbf{Pacing (ms)}}'
    AL '    & \multicolumn{2}{c|}{\textbf{Run rate}} & \multicolumn{2}{c|}{\textbf{Upper bound}} & \multicolumn{2}{c}{\textbf{Pacing (ms)}} \\'
    AL '  \cmidrule(lr){3-4}\cmidrule(lr){5-6}\cmidrule(lr){7-8}\cmidrule(lr){9-10}\cmidrule(lr){11-12}\cmidrule(l){13-14}'
    AL '  & & \textbf{Bokeh} & \textbf{Filter} & \makecell{\textbf{margin}\\{\scriptsize ms}} & \makecell{\textbf{cover}\\{\scriptsize \%}} & \textbf{Avg} & \textbf{Max}'
    AL '    & \textbf{Bokeh} & \textbf{Filter} & \makecell{\textbf{margin}\\{\scriptsize ms}} & \makecell{\textbf{cover}\\{\scriptsize \%}} & \textbf{Avg} & \textbf{Max} \\'
    AL '  \midrule \midrule'

    for ($lv = 0; $lv -le 6; $lv++) {
        $dag = ''
        if ($t.is24 -and $lv -ge 5) { $dag = '$^{\dagger}$' }
        $bi = 0
        foreach ($s in $shotsList) {
            $n = Get-Row $t.tier $lv 'Normal' $s
            $p = Get-Row $t.tier $lv 'Memory-pressure' $s
            $cn = '{0:0.0}' -f $n.CoverPct
            $cp = '{0:0.0}' -f $p.CoverPct
            if ($bi -eq 0) { $lead = "  \multirow{3}{*}{Lv$lv$dag} " } else { $lead = '  ' }
            AL ("$lead& $s & $($n.BokehAdmits)/$s & $($n.FilterAdmits)/$s & $($n.MarginMs) & $cn & $($n.AvgMs) & $($n.MaxMs) & $($p.BokehAdmits)/$s & $($p.FilterAdmits)/$s & $($p.MarginMs) & $cp & $($p.AvgMs) & $($p.MaxMs) \\")
            $bi++
        }
        if ($lv -lt 6) { AL '  \midrule' }
    }

    AL '  \midrule \bottomrule'
    AL '  \end{tabular}%'
    AL '  }'
    AL '\end{table*}'
    AL ''
}

[System.IO.File]::WriteAllText($Out, $sb.ToString(), (New-Object System.Text.UTF8Encoding($false)))
Write-Output "Wrote $Out from $Xlsx ($($data.Count) data rows)."
