import argparse
from phyloformer.data import write_dm
from phyloformer.data_typing import load_typing
from phyloformer.model import load_model
import os
import torch
from tqdm.auto import tqdm


def is_txt(path: str) -> bool:
    return path.lower().endswith("txt")


def typing_predicted_trees(input_typings: str, dataset_id: str, model: str, device: str, save_distance_matrices: bool):
    input_typings = os.path.join('./datasets/typings', input_typings)

    output = os.path.join('./test/typing_predicted_trees', dataset_id)
    if not os.path.exists(output):
        os.makedirs(output)

    model = load_model(model, device=device)
    model.to(device)
    
    for aln in (pbar := tqdm([file for file in os.listdir(input_typings) if file.lower().endswith("txt")])):
        base = aln.split(".")[0]
        pbar.set_description(f"Processing {base}")

        tensor, ids = load_typing(os.path.join(input_typings, aln))

        # check if model input settings match alignment
        _, seq_len, n_seqs = tensor.shape
        if model.seq_len != seq_len or model.n_seqs != n_seqs:
            model._init_seq2pair(n_seqs=n_seqs, seq_len=seq_len)

        dm = model.infer_dm(tensor, ids)
        if save_distance_matrices:
            write_dm(dm, os.path.join(output, f"{base}.pf.dm"))
        tree = model.infer_tree(tensor, dm=dm)
        tree.write(outfile=os.path.join(output, f"{base}.pf.nwk"))




if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-y', '--input-typings', type=str, required=True, help='Identifier of the dataset where the generated typings (input) will be read.')
    parser.add_argument('-o', '--dataset-id', type=str, required=True, help='Identifier of the dataset where the predicted trees (output) will be written.')
    parser.add_argument('-m', '--model', type=str, required=True, help='<torch model (.pt) filepath>')
    parser.add_argument('-d', '--device', default='cpu', type=str, required=False, help='<torch device>')
    parser.add_argument('-s', '--save-distance-matrices', action='store_true', help='Save distance matrices.')
    args = parser.parse_args()

    typing_predicted_trees(args.input_typings, args.dataset_id, args.model, args.device, args.save_distance_matrices)
