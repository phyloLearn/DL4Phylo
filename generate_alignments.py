import argparse
import os
import subprocess
from tqdm.auto import tqdm




SEQUENCE_MODELS = [
    'JTT', 'WAG', 'PAM', 'BLOSUM', 'MTREV', 'CPREV45', 'MTART', 'LG', 'HIVB', 'GENERAL',    # amino acids
    'F84', 'HKY', 'REV', 'GTR'                                                              # nucleotides
]




def generate_alignments(input_trees: str, dataset_id: str, sequence_generator: str, sequence_model: str, sequence_length: int):
    """
    Generate a set of alignments from a set of trees.

    Parameters
    ----------
    input_trees : str
        Identifier of the dataset where the generated trees (input) will be read.
    dataset_id : str
        Identifier of the dataset where the generated alignments (output) will be written.
    sequence_generator : str
        Path to the sequence generator.
    sequence_model : str
        Sequence generator model to be used.
    sequence_length : int
        Length of each sequence (number of nucleotides).
    """

    input_trees = os.path.join('./datasets/trees', input_trees)
    assert os.path.exists(input_trees), '> ERROR: Invalid input trees directory.'
    trees = [file for file in os.listdir(input_trees) if file.endswith('.nwk')]
    assert len(trees) > 0, '> ERROR: No tree (.nwk) files found in the input trees directory.'

    assert os.path.exists(sequence_generator), '> ERROR: Invalid sequence generator path.'
    assert sequence_model in SEQUENCE_MODELS, '> ERROR: Invalid sequence model.'
    assert sequence_length > 0, '> ERROR: Invalid sequence length.'

    
    output = os.path.join('./datasets/alignments', dataset_id)
    if not os.path.exists(output):
        os.makedirs(output)

    
    for tree in tqdm(trees, desc='> Generating alignments'):
        in_file = os.path.join(input_trees, tree)
        out_file = os.path.join(output, os.path.splitext(tree)[0] + '.fasta')
        command = f'{sequence_generator} -m{sequence_model} -q -of -l {sequence_length} < {in_file} > {out_file}'
        _ = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)




if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', '--input-trees', type=str, required=True, help='Identifier of the dataset where the generated trees (input) will be read.')
    parser.add_argument('-o', '--dataset-id', type=str, required=True, help='Identifier of the dataset where the generated alignments (output) will be written.')
    parser.add_argument('-g', '--sequence-generator', default='./sequence_generators/seq-gen', type=str, required=False, help='Path to the sequence generator (https://github.com/rambaut/Seq-Gen/releases/tag/1.3.4).')
    parser.add_argument('-m', '--sequence-model', default='F84', choices=SEQUENCE_MODELS, type=str, required=False, help='Sequence generator model to be used.')
    parser.add_argument('-l', '--sequence-length', default=200, type=int, required=False, help='Length of each sequence (number of nucleotides/amino acids).')
    args = parser.parse_args()

    generate_alignments(args.input_trees, args.dataset_id, args.sequence_generator, args.sequence_model, args.sequence_length)
