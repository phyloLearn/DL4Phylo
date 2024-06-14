import argparse
import os

import torch
from tqdm import tqdm

from data_typing import load_typing
from data import write_dm
from model import AttentionNet, load_model


def is_txt(path: str) -> bool:
    return path.lower().endswith("txt")


def make_predictions(model: AttentionNet, aln_dir: str, out_dir: str, save_dm: bool):
    for aln in (pbar := tqdm([file for file in os.listdir(aln_dir) if is_txt(file)])):
        base = aln.split(".")[0]
        pbar.set_description(f"Processing {base}")

        tensor, ids = load_typing(os.path.join(aln_dir, aln))

        # check if model input settings match alignment
        _, seq_len, n_seqs = tensor.shape
        if model.seq_len != seq_len or model.n_seqs != n_seqs:
            model._init_seq2pair(n_seqs=n_seqs, seq_len=seq_len)

        dm = model.infer_dm(tensor, ids)
        if save_dm:
            write_dm(dm, os.path.join(out_dir, f"{base}.pf.dm"))
        tree = model.infer_tree(tensor, dm=dm)
        tree.write(outfile=os.path.join(out_dir, f"{base}.pf.nwk"))


def main():
    parser = argparse.ArgumentParser(
        description=(
            "Predict phylogenetic trees from Typing Data "
            "using the ML4Phylo neural network"
        )
    )
    parser.add_argument(
        "typingdir",
        type=str,
        help="path to input directory containing the\
    .txt files with typing data",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=str,
        required=False,
        help="path to the output directory where the\
    .tree tree files will be saved (default: typingdir)",
    )
    parser.add_argument(
        "-m",
        "--model",
        type=str,
        required=True,
        help=(
            "path to the NN model's state dictionary [path/to/model.pt file]"
        ),
    )
    parser.add_argument(
        "-g",
        "--gpu",
        required=False,
        action="store_true",
        help="use the GPU for inference (default: false)",
    )
    parser.add_argument(
        "-d",
        "--dm",
        required=False,
        action="store_true",
        help="save predicted distance matrix (default: false)",
    )
    args = parser.parse_args()

    out_dir = args.output if args.output is not None else args.typingdir
    if out_dir != "." and not os.path.exists(out_dir):
        os.mkdir(out_dir)

    device = "cpu"
    if args.gpu and torch.cuda.is_available():
        device = "cuda"
    elif args.gpu and torch.backends.mps.is_available():
        device = "mps"


    model = None
    if args.model is not None:
        if not os.path.isfile(args.model):
            raise ValueError(f"The specified model file: {args.model} does not exist")
        model = load_model(args.model, device=device)
    else:
        raise ValueError("You must specify the model to use")

    model.to(device)

    print("ML4Phylo predict:\n")
    print(f"Predicting trees for typing data in {args.typingdir}")
    print(f"Using the {args.model} model on {device}")
    print(f"Saving predicted trees in {out_dir}")
    if args.dm:
        print(f"Saving Distance matrices in {out_dir}")
    print()

    make_predictions(model, args.typingdir, out_dir, args.dm)

    print("\nDone!")


if __name__ == "__main__":
    main()
