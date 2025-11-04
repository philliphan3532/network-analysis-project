# network-analysis-project



Installation Instructions
------------------------------------------------------------
# create venv
python -m venv .venv

# activate (Windows PowerShell)
.\.venv\Scripts\activate

# activate (macOS / Linux)
source .venv/bin/activate

# upgrade pip
pip install --upgrade pip

# install torch (cpu)
pip install "torch>=2.2,<3.0"

# install torch (gpu)
pip install torch --index-url https://download.pytorch.org/whl/cu126

# install TxGNN module (has to be done through git for some reason)
pip install git+https://github.com/mims-harvard/TxGNN.git

# install other requirements
pip install -r requirements.txt




How to import PrimmeKG
(it must be imported in the format TxGNN takes, not just a single csv like on the PrimeKG github repo)
------------------------------------------------------------

# make primekg folder
mkdir -p data/primekg_full

# download data and generate split
python prepare_split.py data/primekg_full




Workflow for creating subgraph data
(example for drug-disease-gene subgraph)
------------------------------------------------------------

# make subgraph folder
mkdir -p data/subgraphs/drug-disease-gene

# copy contents, not whole folder
cp -r data/primekg_full/* data/subgraphs/drug-disease-gene/

# prune to drug-disease-gene
# Put "" around any node type with a '/' in the name
python prune_subgraph.py data/subgraphs/drug-disease-gene drug disease "gene/protein"

# remove old split (if present)
Remove-Item -Recurse -Force data/subgraphs/drug-disease-gene/full_graph_42

# regenerate split
python prepare_split.py data/subgraphs/drug-disease-gene
