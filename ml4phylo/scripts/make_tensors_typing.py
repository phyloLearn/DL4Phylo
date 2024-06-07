import argparse
import os

import torch
from tqdm import tqdm

from data import load_tree
from data_typing import load_typing

def make_tensors_typing(tree_dir: str, typing_dir: str, out_dir: str):
    trees = [file for file in os.listdir(tree_dir) if file.endswith(".nwk")]
    for tree_file in (pbar := tqdm(trees)):
        identifier = tree_file.rstrip(".nwk")
        pbar.set_description(f"Processing {identifier}")
        tree_tensor, _ = load_tree(os.path.join(tree_dir, tree_file))
        aln_tensor, _ = load_typing(os.path.join(typing_dir, f"{identifier}.txt"))

        torch.save(
            {"X": aln_tensor, "y": tree_tensor},
            os.path.join(out_dir, f"{identifier}.tensor_pair"),
        )


def main():
    parser = argparse.ArgumentParser(
        description="Generate a tensor training set from trees and typing data"
    )
    parser.add_argument(
        "-t",
        "--treedir",
        required=True,
        type=str,
        help="path to input directory containing the .nwk tree files",
    )
    parser.add_argument(
        "-ty",
        "--typingdir",
        required=True,
        type=str,
        help="path to input directory containing corresponding .txt typing data files",
    )
    parser.add_argument(
        "-o",
        "--output",
        required=False,
        default=".",
        type=str,
        help="path to output directory (default: current directory)",
    )
    args = parser.parse_args()

    if not os.path.exists(args.output):
        os.mkdir(args.output)

    make_tensors_typing(args.treedir, args.typingdir, args.output)


if __name__ == "__main__":
    main()
