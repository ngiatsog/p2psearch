import requests
import gzip
import os
import networkx as nx

METADATA = {
    "gnutella": {
        "url": "http://snap.stanford.edu/data/p2p-Gnutella08.txt.gz",
        "delimiter": "\t",
    },
    "fb": {
        "url": "https://snap.stanford.edu/data/facebook_combined.txt.gz",
        "delimiter": " ",
    },
    "internet": {
        "url": "https://snap.stanford.edu/data/as20000102.txt.gz",
        "delimiter": "\t",
    },
    "toy_erdos": {"n": 50, "p": 0.2},
    "toy_watts_strogatz": {"n": 50, "k": 3, "p": 0.2},
}

COMMON_DELIMITER = ";"
DATA_DIR = os.path.dirname(__file__)


def download(dataset, filepath):
    """
    Downloads the edgelist of a graph dataset to filepath.

    Arguments:
        dataset (str): The name of the dataset. Available names are found in METADATA.
        filepath (str): The path where to download the dataset edgelist. The standard path is given by get_edgelist_path().
    """

    if dataset in ["gnutella", "fb", "internet"]:
        url = METADATA[dataset]["url"]
        print(f"* downloading {dataset} network dataset from {url}")
        res = requests.get(url, allow_redirects=True)
        print(f"** decompressing")
        data = gzip.decompress(res.content)
        print(f"*** transforming to common format")
        with open(filepath, "wb") as f:
            f.write(data)

        f = open(filepath, "r", encoding="utf8")
        lines = f.readlines()
        f.close()

        with open(filepath, "w") as f:
            for line in lines:
                if line.startswith("#"):
                    continue
                f.write(line.replace(METADATA[dataset]["delimiter"], COMMON_DELIMITER))
        print(f"**** done")

    elif dataset == "toy_erdos":
        n, p = METADATA[dataset]["n"], METADATA[dataset]["p"]
        g = nx.gnp_random_graph(n, p)
        while not nx.is_connected(g):
            p = min(1, 1.01 * p)
            g = nx.gnp_random_graph(n, p)

        with open(filepath, "w") as f:
            for e in g.edges:
                f.write(f"{e[0]}{COMMON_DELIMITER}{e[1]}\n")

    elif dataset == "toy_watts_strogatz":
        n, k, p = METADATA[dataset]["n"], METADATA[dataset]["k"], METADATA[dataset]["p"]
        g = nx.connected_watts_strogatz_graph(n, k, p)

        with open(filepath, "w") as f:
            for e in g.edges:
                f.write(f"{e[0]}{COMMON_DELIMITER}{e[1]}\n")

    else:
        raise Exception(
            f"unknown dataset '{dataset}', known datasets: {list(METADATA)}"
        )


def get_edgelist_path(dataset):
    """
    Returns the standard path to store the edgelist for a dataset.

    Arguments:
        dataset (str): The name of the dataset. Available names are found in METADATA.

    Returns:
        str: The standard absolute path for the graph dataset edgelist.
    """

    network_dir = os.path.join(DATA_DIR, "edgelists")
    if not os.path.exists(network_dir):
        os.mkdir(network_dir)
    return os.path.join(network_dir, f"{dataset}_edgelist.csv")


def get_ppr_matrix_path(dataset, alpha, symmetric):
    """
    Returns the standard path for caching the diffusion matrix of the personalized page rank.

    Arguments:
        dataset (str): The name of the dataset. Available names are found in METADATA.
        alpha (float): The teleport probability of the personalized page rank diffusion.
        symmetric (bool): Selects the symmetric or asymmetric form of the matrix.

    """
    network_dir = os.path.join(DATA_DIR, "ppr_mats")
    if not os.path.exists(network_dir):
        os.mkdir(network_dir)
    return os.path.join(
        network_dir, f"{dataset}_alpha{alpha}_{'symm' if symmetric else 'asymm'}.npy"
    )