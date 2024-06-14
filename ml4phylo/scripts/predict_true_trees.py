import argparse
import os

import skbio
import numpy as np
from ete3 import Tree
from tqdm import tqdm
from data import _parse_alignment

def is_fasta(path: str) -> bool:
    return path.lower().endswith("fa") or path.lower().endswith("fasta")

def hamming_distance(seq1, seq2):
    """Calculate the Hamming distance between two sequences."""
    
    assert len(seq1) == len(seq2), "Sequences must be of the same length"
    return sum(char1 != char2 for char1, char2 in zip(seq1, seq2))


def predict_true_trees(in_dir: str, out_dir: str):
    for aln in (pbar := tqdm([file for file in os.listdir(in_dir) if is_fasta(file)])):
        identifier = aln.split(".")[0]
        pbar.set_description(f"Processing {identifier}")

        alignment = _parse_alignment(os.path.join(in_dir, aln))

        sequences = [value for value in alignment.values()]

        n = len(sequences)
        matrix = np.zeros((n, n), dtype=int)
        for i in range(n):
            for j in range(i, n):
                dist = hamming_distance(sequences[i], sequences[j])
                matrix[i][j] = dist
                matrix[j][i] = dist
        
        dist_matrix = skbio.DistanceMatrix(matrix, ids=list(alignment.keys()))
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
        help="path to input directory containing the\
    .fasta alignments",
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

    predict_true_trees(args.indir, args.outdir)

    print("\nDone!")


if __name__ == "__main__":
    main()
