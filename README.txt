# Network Analysis Project


Installation Instructions
------------------------------------------------------------
1. create venv
python -m venv venv

2. activate venv

(Windows PowerShell)
venv\Scripts\activate

(macOS / Linux)
source venv/bin/activate

3. upgrade pip (if necessary)
pip install --upgrade pip

4. configure requirements.txt to install torch for GPU if possible.
To do so, uncomment the GPU installation and comment out the default installation.

5. install requirements
pip install -r requirements.txt




How to import PrimmeKG
(it must be imported in the format TxGNN takes, not just a single csv like on the PrimeKG github repo)
------------------------------------------------------------
1. make primekg folder
mkdir -p data/primekg_full

2. download data and generate split
python prepare_split.py data/primekg_full




Workflow for creating subgraph data
(example for drug-disease-gene subgraph)
------------------------------------------------------------
1. make subgraph folder
mkdir -p data/subgraphs/drug-disease-gene

2. copy contents, not whole folder
cp -r data/primekg_full/* data/subgraphs/drug-disease-gene/

3. prune to drug-disease-gene
(Put "" around any node type with a '/' in the name)
python src/prune_subgraph.py data/subgraphs/drug-disease-gene drug disease "gene/protein"

4. remove old train/test/val split from full dataset (if present)
Remove-Item -Recurse -Force data/subgraphs/drug-disease-gene/full_graph_42

5. regenerate train/test/val split for subgraph
python src/prepare_split.py data/subgraphs/drug-disease-gene
