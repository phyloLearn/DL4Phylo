import argparse
from ete3 import Tree
import os
from phyloformer.data_typing import _parse_typing
import skbio
import skbio.tree
from sklearn.metrics import DistanceMetric
from tqdm.auto import tqdm




def typing_true_trees(input_typings: str, dataset_id: str):
    input_typings = os.path.join('./datasets/typings', input_typings)
    
    output = os.path.join('./test/typing_true_trees', dataset_id)
    if not os.path.exists(output):
        os.makedirs(output)
    
    for aln in (pbar := tqdm([file for file in os.listdir(input_typings) if file.lower().endswith("txt")])):
        identifier = aln.split(".")[0]
        pbar.set_description(f"Processing {identifier}")

        dist = DistanceMetric.get_metric("hamming")
        alignment = _parse_typing(os.path.join(input_typings, aln))

        X = [value for value in alignment.values()]
        
        dist_matrix = skbio.DistanceMatrix(dist.pairwise(X, X), ids=list(alignment.keys()))
        
        newick_tree = skbio.tree.nj(dist_matrix, result_constructor=str)
        tree = Tree(newick_tree)
        
        tree.write(outfile=os.path.join(output, f"{identifier}.pf.nwk"))




if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-y', '--input-typings', type=str, required=True, help='Identifier of the dataset where the generated typings (input) will be read.')
    parser.add_argument('-o', '--dataset-id', type=str, required=True, help='Identifier of the dataset where the true trees (output) will be written.')
    args = parser.parse_args()

    typing_true_trees(args.input_typings, args.dataset_id)
