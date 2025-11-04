# prune_subgraph.py  (robust TSV+CSV + index-based filtering)
import sys
import csv
from pathlib import Path

def read_nodes_tsv(path: Path):
    with open(path, 'r', encoding='utf-8', errors='replace', newline='') as f:
        r = csv.reader(f, delimiter='\t', quotechar='"', doublequote=True)
        header = next(r)
        rows = []
        for row in r:
            # repair malformed row lengths
            if len(row) < len(header):
                row += [''] * (len(header) - len(row))
            elif len(row) > len(header):
                row = row[:len(header)]
            rows.append(row)
    return header, rows

def write_nodes_tsv(path: Path, header, rows):
    with open(path, 'w', encoding='utf-8', newline='') as f:
        w = csv.writer(f, delimiter='\t', quotechar='"', quoting=csv.QUOTE_MINIMAL, lineterminator='\n')
        w.writerow(header)
        w.writerows(rows)

def read_edges_csv(path: Path):
    with open(path, 'r', encoding='utf-8', errors='replace', newline='') as f:
        r = csv.reader(f, delimiter=',', quotechar='"', doublequote=True)
        header = next(r)
        rows = []
        for row in r:
            if len(row) < len(header):
                row += [''] * (len(header) - len(row))
            elif len(row) > len(header):
                row = row[:len(header)]
            rows.append(row)
    return header, rows

def write_edges_csv(path: Path, header, rows):
    with open(path, 'w', encoding='utf-8', newline='') as f:
        w = csv.writer(f, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL, lineterminator='\n')
        w.writerow(header)
        w.writerows(rows)

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print('Usage: python prune_subgraph.py <data_folder> <node_type1> <node_type2> ...')
        sys.exit(1)

    data_dir = Path(sys.argv[1])
    keep_types = set(sys.argv[2:])

    node_path = data_dir / 'node.csv'
    edge_path = data_dir / 'edges.csv'

    # --- load nodes (TSV) ---
    n_header, n_rows = read_nodes_tsv(node_path)
    # Required columns: node_index, node_id, node_type
    try:
        idx_i = n_header.index('node_index')
        type_i = n_header.index('node_type')
    except ValueError:
        raise SystemExit(f'node.csv must contain columns node_index and node_type; found: {n_header}')

    # filter nodes by type (string compare)
    pruned_n_rows = [row for row in n_rows if row[type_i] in keep_types]
    kept_indices = {row[idx_i] for row in pruned_n_rows}  # as strings

    # --- load edges (CSV) ---
    e_header, e_rows = read_edges_csv(edge_path)
    # Required columns: x_index, y_index
    try:
        x_i = e_header.index('x_index')
        y_i = e_header.index('y_index')
    except ValueError:
        raise SystemExit(f'edges.csv must contain x_index and y_index; found: {e_header}')

    # filter edges where both endpoints remain
    pruned_e_rows = [row for row in e_rows if row[x_i] in kept_indices and row[y_i] in kept_indices]

    # --- write back ---
    write_nodes_tsv(node_path, n_header, pruned_n_rows)
    write_edges_csv(edge_path, e_header, pruned_e_rows)

    print(f'✅ Done. Kept {len(pruned_n_rows)} nodes and {len(pruned_e_rows)} edges.')
