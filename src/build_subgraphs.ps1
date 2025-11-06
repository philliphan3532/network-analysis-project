# Requires PowerShell 7+
# Equivalent to: set -euo pipefail
$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

# ---- Config (paths are relative to repo root / current working dir) ----
$FULL_DATA_DIR  = 'data/primekg_full'
$SUBGRAPHS_ROOT = 'data/subgraphs'
$PRUNE_SCRIPT   = 'src/prune_subgraph.py'
$SPLIT_SCRIPT   = 'src/prepare_split.py'

# ---- Sanity checks ----
if (-not (Test-Path -Path $FULL_DATA_DIR  -PathType Container)) { throw "ERROR: $FULL_DATA_DIR not found" }
if (-not (Test-Path -Path $PRUNE_SCRIPT   -PathType Leaf))      { throw "ERROR: $PRUNE_SCRIPT not found" }
if (-not (Test-Path -Path $SPLIT_SCRIPT   -PathType Leaf))      { throw "ERROR: $SPLIT_SCRIPT not found" }

# ---- Combinations (space-separated node types per line) ----
$COMBOS_HERE = @'
drug disease
drug disease gene/protein
drug disease pathway
drug disease gene/protein pathway
drug disease gene/protein pathway molecular_function
'@

function Process-Combo {
    param(
        [Parameter(Mandatory)]
        [string]$Combo
    )

    $comboTrim = $Combo.Trim()
    if ([string]::IsNullOrWhiteSpace($comboTrim)) { return }

    # Build array of node types
    $types = $comboTrim -split '\s+'

    # Safe subdir name: join with '-' and replace '/' -> '_'
    $safeNames  = foreach ($t in $types) { $t -replace '/', '_' }
    $subdirName = [string]::Join('-', $safeNames)
    $SUBDIR     = Join-Path $SUBGRAPHS_ROOT $subdirName

    Write-Host ('=' * 60)
    Write-Host ">> Building subgraph for: $comboTrim"
    Write-Host ">> Subgraph directory: $SUBDIR"

    # 1) make subgraph folder
    New-Item -ItemType Directory -Path $SUBDIR -Force | Out-Null

    # 2) copy contents (not the folder itself), include dotfiles/hidden files
    Write-Host ">> Copying contents from $FULL_DATA_DIR -> $SUBDIR"
    Copy-Item -Path (Join-Path $FULL_DATA_DIR '*') -Destination $SUBDIR -Recurse -Force

    # 3) prune to the requested node types
    $shownTypes = foreach ($t in $types) { if ($t -match '/') { '"' + $t + '"' } else { $t } }
    Write-Host ">> Pruning: python $PRUNE_SCRIPT $SUBDIR $($shownTypes -join ' ')"
    & python $PRUNE_SCRIPT $SUBDIR @types

    # 4) remove old train/test/val split (if present)
    $oldSplit = Join-Path $SUBDIR 'full_graph_42'
    if (Test-Path -Path $oldSplit -PathType Container) {
        Write-Host ">> Removing old split directory: $oldSplit"
        Remove-Item -Recurse -Force -Path $oldSplit
    }

    # 5) regenerate train/test/val split for this subgraph
    Write-Host ">> Preparing fresh train/test/val split..."
    & python $SPLIT_SCRIPT $SUBDIR

    Write-Host ">> Done: $comboTrim"
    Write-Host
}

# ---- Main loop over combinations ----
foreach ($line in ($COMBOS_HERE -split "`n")) {
    Process-Combo -Combo $line
}

Write-Host "All subgraphs complete."
