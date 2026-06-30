param(
    [switch]$CheckOnly,
    [switch]$AllowDirtyPull
)

$ErrorActionPreference = "Continue"
$ScriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path

function Resolve-GitRepo {
    param([string]$Path)

    $resolved = Resolve-Path -LiteralPath $Path -ErrorAction SilentlyContinue
    if ($null -eq $resolved) {
        return $null
    }

    $repoPath = $resolved.ProviderPath
    if (Test-Path -LiteralPath (Join-Path $repoPath ".git")) {
        return $repoPath
    }

    return $null
}

function Invoke-GitText {
    param(
        [string]$Repo,
        [string[]]$GitArgs
    )

    Push-Location -LiteralPath $Repo
    try {
        $output = & git -c "safe.directory=$Repo" -c "core.excludesfile=" @GitArgs 2>&1
        return @{
            Output = $output
            ExitCode = $LASTEXITCODE
        }
    }
    finally {
        Pop-Location
    }
}

function Show-And-SyncRepo {
    param(
        [string]$Name,
        [string]$Repo
    )

    Write-Host ""
    Write-Host "== $Name =="
    Write-Host $Repo

    $branch = Invoke-GitText -Repo $Repo -GitArgs @("rev-parse", "--abbrev-ref", "HEAD")
    $commit = Invoke-GitText -Repo $Repo -GitArgs @("rev-parse", "--short", "HEAD")
    $status = Invoke-GitText -Repo $Repo -GitArgs @("status", "--porcelain")

    if ($branch.ExitCode -ne 0 -or $commit.ExitCode -ne 0) {
        Write-Host "Could not inspect this repository."
        if ($branch.Output) { $branch.Output | ForEach-Object { Write-Host $_ } }
        if ($commit.Output) { $commit.Output | ForEach-Object { Write-Host $_ } }
        return
    }

    Write-Host ("Branch: " + (($branch.Output | Select-Object -First 1) -as [string]))
    Write-Host ("Commit before sync: " + (($commit.Output | Select-Object -First 1) -as [string]))

    $hasChanges = ($status.Output | Measure-Object).Count -gt 0
    if ($hasChanges) {
        Write-Host "Local changes detected:"
        $status.Output | ForEach-Object { Write-Host ("  " + $_) }
    }
    else {
        Write-Host "Working tree clean."
    }

    if ($CheckOnly) {
        Write-Host "CheckOnly enabled; skipping pull."
    }
    elseif ($hasChanges -and -not $AllowDirtyPull) {
        Write-Host "Skipping pull because local changes exist. Commit, stash, or rerun with -AllowDirtyPull."
    }
    else {
        Write-Host "Running: git pull --ff-only"
        $pull = Invoke-GitText -Repo $Repo -GitArgs @("pull", "--ff-only")
        $pull.Output | ForEach-Object { Write-Host $_ }
        if ($pull.ExitCode -ne 0) {
            Write-Host "Pull failed. Keep using the pre-sync commit until this is resolved."
        }
    }

    $after = Invoke-GitText -Repo $Repo -GitArgs @("rev-parse", "--short", "HEAD")
    if ($after.ExitCode -eq 0) {
        Write-Host ("Commit after sync: " + (($after.Output | Select-Object -First 1) -as [string]))
    }
}

$candidates = @(
    @{ Name = "SEIP-27 paper"; Path = $ScriptRoot },
    @{ Name = "ML implementation (external)"; Path = Join-Path $ScriptRoot "external\ML" },
    @{ Name = "ML implementation (sibling)"; Path = Join-Path $ScriptRoot "..\ML" }
)

$seen = @{}
$repos = @()

foreach ($candidate in $candidates) {
    $repo = Resolve-GitRepo -Path $candidate.Path
    if ($null -ne $repo -and -not $seen.ContainsKey($repo)) {
        $seen[$repo] = $true
        $repos += @{
            Name = $candidate.Name
            Repo = $repo
        }
    }
}

if ($repos.Count -eq 0) {
    Write-Host "No Git repositories found to sync."
    exit 1
}

foreach ($entry in $repos) {
    Show-And-SyncRepo -Name $entry.Name -Repo $entry.Repo
}
