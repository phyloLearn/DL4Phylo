import argparse
import os
from phyloformer.data import load_alignment, load_tree
import torch
from tqdm.auto import tqdm




SEQUENCE_VOCABULARY = ['nucleotides', 'amino_acids']




def generate_sequence_data(input_trees: str, input_alignments: str, dataset_id: str, sequence_vocabulary: str):
    """
    Generate a set of sequence data from a set of trees and alignments.

    Parameters
    ----------
    input_trees : str
        Identifier of the dataset where the generated trees (input) will be read.
    input_alignments : str
        Identifier of the dataset where the generated alignments (input) will be read.
    dataset_id : str
        Identifier of the dataset where the generated sequence data (output) will be written.
    sequence_vocabulary : str
        Type of sequence vocabulary to use. Options are "nucleotides" or "amino_acids".
    """

    input_trees = os.path.join('./datasets/trees', input_trees)
    assert os.path.exists(input_trees), '> ERROR: Invalid input trees directory.'
    trees = [file for file in os.listdir(input_trees) if file.endswith('.nwk')]
    assert len(trees) > 0, '> ERROR: No tree (.nwk) files found in the input trees directory.'

    input_alignments = os.path.join('./datasets/alignments', input_alignments)
    assert os.path.exists(input_alignments), '> ERROR: Invalid input alignments directory.'
    alignments = [file for file in os.listdir(input_alignments) if file.endswith('.fasta')]
    assert len(alignments) > 0, '> ERROR: No alignment (.fasta) files found in the input alignments directory.'
    
    assert sequence_vocabulary in SEQUENCE_VOCABULARY, '> ERROR: Invalid sequence vocabulary.'
    

    output = os.path.join('./datasets/sequence_data', dataset_id)
    if not os.path.exists(output):
        os.makedirs(output)


    for tree in (progress := tqdm(trees)):
        tree_id = os.path.splitext(tree)[0]
        progress.set_description(f'> Processing {tree_id}')
        tree_file = os.path.join(input_trees, tree)
        alignment_file = os.path.join(input_alignments, tree_id + '.fasta')
        tree_tensor, _ = load_tree(tree_file)
        alignment_tensor, _ = load_alignment(alignment_file, sequence_vocabulary == 'nucleotides')
        torch.save({'X': alignment_tensor, 'y': tree_tensor}, os.path.join(output, tree_id + '.tensor_pair'))




if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', '--input-trees', type=str, required=True, help='Identifier of the dataset where the generated trees (input) will be read.')
    parser.add_argument('-a', '--input-alignments', type=str, required=True, help='Identifier of the dataset where the generated alignments (input) will be read.')
    parser.add_argument('-o', '--dataset-id', type=str, required=True, help='Identifier of the dataset where the generated sequence data (output) will be written.')
    parser.add_argument('-v', '--sequence-vocabulary', default='nucleotides', choices=SEQUENCE_VOCABULARY, type=str, required=False, help='Type of sequence vocabulary to use. Options are "nucleotides" or "amino_acids". Default is "nucleotide".')
    args = parser.parse_args()

    generate_sequence_data(args.input_trees, args.input_alignments, args.dataset_id, args.sequence_vocabulary)
