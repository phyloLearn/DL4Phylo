import argparse
import os
from phyloformer.data import load_tree
from phyloformer.data_typing import load_typing
import torch
from tqdm.auto import tqdm




def generate_typing_data(input_trees: str, input_typings: str, dataset_id: str):
    """
    Generate a set of typing data from a set of trees and typings.

    Parameters
    ----------
    input_trees : str
        Path to the directory where the generated trees will be read.
    input_typings : str
        Path to the directory where the generated typings will be read.
    output : str
        Path to the directory where the generated typing data will be written.
    """

    input_trees = os.path.join('./datasets/trees', input_trees)
    assert os.path.exists(input_trees), '> ERROR: Invalid input trees directory.'
    trees = [file for file in os.listdir(input_trees) if file.endswith('.nwk')]
    assert len(trees) > 0, '> ERROR: No tree (.nwk) files found in the input trees directory.'

    input_typings = os.path.join('./datasets/typings', input_typings)
    assert os.path.exists(input_typings), '> ERROR: Invalid input typings directory.'
    typings = [file for file in os.listdir(input_typings) if file.endswith('.txt')]
    assert len(typings) > 0, '> ERROR: No typing (.txt) files found in the input typings directory.'


    output = os.path.join('./datasets/typing_data', dataset_id)
    if not os.path.exists(output):
        os.makedirs(output)


    for tree in (progress := tqdm(trees)):
        tree_id = os.path.splitext(tree)[0]
        progress.set_description(f'> Processing {tree_id}')
        tree_file = os.path.join(input_trees, tree)
        typing_file = os.path.join(input_typings, tree_id + '.txt')
        tree_tensor, _ = load_tree(tree_file)
        typing_tensor, _ = load_typing(typing_file)
        torch.save({'X': typing_tensor, 'y': tree_tensor}, os.path.join(output, tree_id + '.tensor_pair'))




if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', '--input-trees', type=str, required=True, help='Identifier of the dataset where the generated trees (input) will be read.')
    parser.add_argument('-y', '--input-typings', type=str, required=True, help='Identifier of the dataset where the generated typings (input) will be read.')
    parser.add_argument('-o', '--dataset-id', type=str, required=True, help='Identifier of the dataset where the generated typing data (output) will be written.')
    args = parser.parse_args()

    generate_typing_data(args.input_trees, args.input_typings, args.dataset_id)
