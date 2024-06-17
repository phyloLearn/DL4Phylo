import argparse
import os

import torch
from tqdm import tqdm

from phyloformer.data import load_alignment, write_dm
from phyloformer.model import AttentionNet, load_model


def is_fasta(path: str) -> bool:
    return path.lower().endswith("fa") or path.lower().endswith("fasta")


def sequence_predicted_trees(input_alignments: str, dataset_id: str, model: str, device: str, save_distance_matrices: bool):
    input_alignments = os.path.join('./datasets/alignments', input_alignments)

    output = os.path.join('./test/predicted_trees', dataset_id)
    if not os.path.exists(output):
        os.makedirs(output)

    model = load_model(model, device=device)
    model.to(device)

    for aln in (pbar := tqdm([file for file in os.listdir(input_alignments) if is_fasta(file)])):
        identifier = aln.split(".")[0]
        pbar.set_description(f"Processing {identifier}")

        tensor, ids = load_alignment(os.path.join(input_alignments, aln))

        # check if model input settings match alignment
        _, seq_len, n_seqs = tensor.shape
        if model.seq_len != seq_len or model.n_seqs != n_seqs:
            model._init_seq2pair(n_seqs=n_seqs, seq_len=seq_len)

        dm = model.infer_dm(tensor, ids)
        if save_distance_matrices:
            write_dm(dm, os.path.join(output, f"{identifier}.pf.dm"))
        tree = model.infer_tree(tensor, dm=dm)
        tree.write(outfile=os.path.join(output, f"{identifier}.pf.nwk"))




if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-a', '--input-alignments', type=str, required=True, help='Identifier of the dataset where the generated alignments (input) will be read.')
    parser.add_argument('-o', '--dataset-id', type=str, required=True, help='Identifier of the dataset where the predicted trees (output) will be written.')
    parser.add_argument('-m', '--model', type=str, required=True, help='<torch model (.pt) filepath>')
    parser.add_argument('-d', '--device', default='cpu', type=str, required=False, help='<torch device>')
    parser.add_argument('-s', '--save-distance-matrices', action='store_true', help='Save distance matrices.')
    args = parser.parse_args()

    sequence_predicted_trees(args.input_alignments, args.dataset_id, args.model, args.device, args.save_distance_matrices)
