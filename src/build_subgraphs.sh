#!/usr/bin/env bash
set -euo pipefail

# ---- Config (paths are relative to repo root) ----
FULL_DATA_DIR="data/primekg_full"
SUBGRAPHS_ROOT="data/subgraphs"
PRUNE_SCRIPT="src/prune_subgraph.py"
SPLIT_SCRIPT="src/prepare_split.py"

# ---- Sanity checks ----
[[ -d "$FULL_DATA_DIR" ]] || { echo "ERROR: $FULL_DATA_DIR not found"; exit 1; }
[[ -f "$PRUNE_SCRIPT" ]]   || { echo "ERROR: $PRUNE_SCRIPT not found"; exit 1; }
[[ -f "$SPLIT_SCRIPT" ]]   || { echo "ERROR: $SPLIT_SCRIPT not found"; exit 1; }

# ---- Combinations (space-separated node types per item) ----
# Note: we will pass raw types to prune (e.g., "gene/protein"),
# and use a safe directory name by replacing '/' with '_'.
COMBOS="$(cat <<'EOF'
drug disease
drug disease gene/protein
drug disease pathway
drug disease gene/protein pathway
drug disease gene/protein pathway molecular_function
EOF
)"

process_combo() {
  local combo="$1"

  # Build array of node types
  read -r -a TYPES <<< "$combo"

  # Make a safe subdir name: join with '-' and replace '/' -> '_'
  local subdir_name=""
  for t in "${TYPES[@]}"; do
    local safe="${t//\//_}"
    subdir_name="${subdir_name:+$subdir_name-}$safe"
  done

  local SUBDIR="${SUBGRAPHS_ROOT}/${subdir_name}"

  echo "============================================================"
  echo ">> Building subgraph for: $combo"
  echo ">> Subgraph directory: $SUBDIR"

  # 1) make subgraph folder
  mkdir -p "$SUBDIR"

  # 2) copy contents (not the folder itself), include dotfiles
  #    cp -a FULL_DATA_DIR/. SUBDIR/ ensures we copy the contents only.
  echo ">> Copying contents from $FULL_DATA_DIR -> $SUBDIR"
  cp -a "${FULL_DATA_DIR}/." "$SUBDIR/"

  # 3) prune to the requested node types
  #    Show the command with quotes around any type containing '/'
  printf ">> Pruning: python %s %s " "$PRUNE_SCRIPT" "$SUBDIR"
  for t in "${TYPES[@]}"; do
    if [[ "$t" == */* ]]; then printf '"%s" ' "$t"; else printf '%s ' "$t"; fi
  done
  echo
  python "$PRUNE_SCRIPT" "$SUBDIR" "${TYPES[@]}"

  # 4) remove old train/test/val split (if present)
  #    Your note referenced 'full_graph_42'; remove it defensively if it exists.
  if [[ -d "$SUBDIR/full_graph_42" ]]; then
    echo ">> Removing old split directory: $SUBDIR/full_graph_42"
    rm -rf "$SUBDIR/full_graph_42"
  fi

  # 5) regenerate train/test/val split for this subgraph
  echo ">> Preparing fresh train/test/val split..."
  python "$SPLIT_SCRIPT" "$SUBDIR"

  echo ">> Done: $combo"
  echo
}

# ---- Main loop over combinations ----
while IFS= read -r line; do
  [[ -z "$line" ]] && continue
  process_combo "$line"
done <<< "$COMBOS"

echo "All subgraphs complete."