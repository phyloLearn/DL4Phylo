import argparse
import os

import skbio
from ete3 import Tree
import skbio.tree
from tqdm import tqdm
from data_typing import _parse_typing
from sklearn.metrics import DistanceMetric

def is_txt(path: str) -> bool:
    return path.lower().endswith("txt")


def predict_true_trees_typing(in_dir: str, out_dir: str):
    for aln in (pbar := tqdm([file for file in os.listdir(in_dir) if is_txt(file)])):
        identifier = aln.split(".")[0]
        pbar.set_description(f"Processing {identifier}")

        dist = DistanceMetric.get_metric("hamming")
        alignment = _parse_typing(os.path.join(in_dir, aln))

        X = [value for value in alignment.values()]
        
        dist_matrix = skbio.DistanceMatrix(dist.pairwise(X, X), ids=list(alignment.keys()))
        
        newick_tree = skbio.tree.nj(dist_matrix, result_constructor=str)
        tree = Tree(newick_tree)
        
        tree.write(outfile=os.path.join(out_dir, f"{identifier}.pf.nwk"))


def main():
    parser = argparse.ArgumentParser(
        description=(
            "Predict phylogenetic trees from MSAs "
            "using the ML4Phylo neural network"
        )
    )
    parser.add_argument(
        "-i",
        "--indir",
        type=str,
        required= True,
        help="path to input directory containing the\
    .txt typing data",
    )
    parser.add_argument(
        "-o",
        "--outdir",
        type=str,
        required=True,
        help="path to the output directory were the\
    .nwk tree files will be saved",
    )
    args = parser.parse_args()

    predict_true_trees_typing(args.indir, args.outdir)

    print("\nDone!")


if __name__ == "__main__":
    main()
