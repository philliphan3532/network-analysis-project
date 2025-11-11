import sys
import csv
from pathlib import Path
import pandas as pd

def summarize_graph(graph_dir: Path):
    """Summarize a TxGNN-formatted graph (PrimeKG or subgraph)."""

    print(f"\n=== Summary for {graph_dir} ===")

    # --- File paths ---
    node_path = graph_dir / 'node.csv'
    edge_path = graph_dir / 'edges.csv'
    split_dir = graph_dir / 'full_graph_42'

    if not node_path.exists() or not edge_path.exists():
        raise FileNotFoundError("node.csv or edges.csv not found in given directory.")

    # --- Load data ---
    nodes = pd.read_csv(node_path, sep='\t', quotechar='"', engine='python')
    edges = pd.read_csv(edge_path, engine='python')

    # --- Print basic info ---
    print(f"Total nodes: {len(nodes):,}")
    print(f"Total edges: {len(edges):,}")

    # --- Node-type counts ---
    if 'node_type' in nodes.columns:
        node_counts = nodes['node_type'].value_counts()
        print("\nNodes per type:")
        for ntype, count in node_counts.items():
            print(f"  {ntype:<25} {count:,}")

    # --- Edge-type counts ---
    if 'relation' in edges.columns:
        rel_counts = edges['relation'].value_counts()
        print("\nEdges per relation type:")
        for rel, count in rel_counts.items():
            print(f"  {rel:<40} {count:,}")

    # --- Split stats ---
    if split_dir.exists():
        for split_name in ['train.csv', 'valid.csv', 'test.csv']:
            split_path = split_dir / split_name
            if split_path.exists():
                df = pd.read_csv(split_path, engine='python')
                print(f"{split_name.replace('.csv',''):<6}: {len(df):,} edges")

    # --- Directed KG info (optional) ---
    kg_path = graph_dir / 'kg.csv'
    kg_dir_path = graph_dir / 'kg_directed.csv'
    for p in [kg_path, kg_dir_path]:
        if p.exists():
            df = pd.read_csv(p, engine='python')
            print(f"{p.name:<20}: {len(df):,} entries")

    print("\nSummary complete.\n")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python summarize_primekg_graph.py <path_to_graph_folder>")
        sys.exit(1)

    graph_folder = Path(sys.argv[1]).resolve()
    summarize_graph(graph_folder)
