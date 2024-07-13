import argparse
import os

import torch
from tqdm import tqdm
from dl4phylo.data import load_data, write_dm, DataType
from dl4phylo.model import AttentionNet, load_model
from dl4phylo.utils import is_fasta, is_txt

def make_predictions(model: AttentionNet, aln_dir: str, out_dir: str, save_dm: bool, data_type: DataType):
    predict_dir = os.path.join(out_dir, aln_dir.split("\\")[-1])
    if not os.path.exists(predict_dir):
        os.mkdir(predict_dir)
    
    for aln in (pbar := tqdm([file for file in os.listdir(aln_dir) if is_fasta(file) or is_txt(file)])):
        identifier = aln.split(".")[0]
        pbar.set_description(f"Processing {identifier}")

        tensor, ids = load_data(os.path.join(aln_dir, aln), data_type)

        # check if model input settings match alignment
        _, data_len, n_data = tensor.shape
        if model.data_len != data_len or model.n_data != n_data:
            model._init_seq2pair(n_data=n_data, data_len=data_len)

        dm = model.infer_dm(tensor, ids)
        if save_dm:
            write_dm(dm, os.path.join(predict_dir, f"{identifier}.pf.dm"))
        tree = model.infer_tree(tensor, dm=dm)
        tree.write(outfile=os.path.join(predict_dir, f"{identifier}.pf.nwk"))

DATA_TYPES = DataType.toList()

def main():
    parser = argparse.ArgumentParser(
        description=(
            "Predict phylogenetic trees from MSAs "
            "using the DL4Phylo neural network"
        )
    )
    parser.add_argument(
        "-dd",
        "--datadir",
        type=str,
        help="path to input directory containing corresponding\
            data files: [.fasta for alignments or .txt for typing data]",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=str,
        required=False,
        default=".",
        help="path to the output directory where the\
    .tree tree files will be saved.",
    )
    parser.add_argument(
        "-m",
        "--model",
        type=str,
        required=True,
        help=(
            "path to the NN model state dictionary, path/to/model.pt"
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
    parser.add_argument(
        "-dt",
        "--data_type",
        required=False,
        type=str,
        default=DataType.AMINO_ACIDS.name,
        choices=DATA_TYPES,
        help=f"type of input data. Choices: {DATA_TYPES}",
    )
    args = parser.parse_args()

    out_dir = args.output if args.output is not None else args.datadir
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

    print("DL4Phylo predict:\n")
    print(f"Predicting trees for alignments in {args.datadir}")
    print(f"Using the {args.model} model on {device}")
    print(f"Saving predicted trees in {out_dir}")
    if args.dm:
        print(f"Saving Distance matrices in {out_dir}")
    print()

    make_predictions(model, args.datadir, out_dir, args.dm, DataType[args.data_type])

    print("\nDone!")


if __name__ == "__main__":
    main()
