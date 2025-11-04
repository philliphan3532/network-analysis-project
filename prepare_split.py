import sys
from txgnn import TxData

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python prepare_split.py <data_folder_path>")
        sys.exit(1)

    data_path = sys.argv[1]
    print(f"Preparing split for: {data_path}")

    tx = TxData(data_folder_path=data_path)
    tx.prepare_split(split="full_graph", seed=42)

    print("Done.")
