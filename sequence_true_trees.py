import argparse
import os

import skbio
import numpy as np
from ete3 import Tree
from tqdm import tqdm
from phyloformer.data import _parse_alignment

def is_fasta(path: str) -> bool:
    return path.lower().endswith("fa") or path.lower().endswith("fasta")

def hamming_distance(seq1, seq2):
    """Calculate the Hamming distance between two sequences."""
    
    assert len(seq1) == len(seq2), "Sequences must be of the same length"
    return sum(char1 != char2 for char1, char2 in zip(seq1, seq2))


def sequence_true_trees(input_alignments: str, dataset_id: str):
    input_alignments = os.path.join('./datasets/alignments', input_alignments)
    
    output = os.path.join('./test/true_trees', dataset_id)
    if not os.path.exists(output):
        os.makedirs(output)
    
    for aln in (pbar := tqdm([file for file in os.listdir(input_alignments) if is_fasta(file)])):
        identifier = aln.split(".")[0]
        pbar.set_description(f"Processing {identifier}")

        alignment = _parse_alignment(os.path.join(input_alignments, aln))

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
        
        tree.write(outfile=os.path.join(output, f"{identifier}.pf.nwk"))

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-a', '--input-alignments', type=str, required=True, help='Identifier of the dataset where the generated alignments (input) will be read.')
    parser.add_argument('-o', '--dataset-id', type=str, required=True, help='Identifier of the dataset where the true trees (output) will be written.')
    args = parser.parse_args()

    sequence_true_trees(args.input_alignments, args.dataset_id)
