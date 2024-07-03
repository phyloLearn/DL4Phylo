import argparse
import os
import subprocess

import numpy as np
from dendropy.simulate import treesim
from ete3 import Tree
from tqdm import tqdm
from secrets import token_hex

TOPOLOGIES = ["birth-death", "uniform"]
BRLENS = ["exponential", "uniform"]
SEQGEN_MODELS = [
    "HKY",
    "F84",
    "GTR",
    "REV",
    "JTT",
    "WAG",
    "PAM",
    "BLOSUM",
    "MTREV",
    "CPREV45",
    "MTART",
    "LG",
    "HIVB",
    "GENERAL",
]

def simulate_trees(numtrees, numleaves, outdir, treeType, bl):
    if not os.path.exists(outdir):
        os.mkdir(outdir)

    for i in tqdm(range(numtrees)):
        # Generating the tree topology
        generation_id = token_hex(4)
        outname = os.path.join(outdir, f"{generation_id}.nwk")
        if treeType == "birth-death":  # using dendropy
            t = treesim.birth_death_tree(
                birth_rate=1.0, death_rate=0.5, num_extant_tips=numleaves
            )
            t.write(path=outname, schema="newick", suppress_rooting=True)
        elif treeType == "uniform":  # using ete3
            t = Tree()
            t.populate(numleaves)
            t.write(format=1, outfile=outname)
        else:
            exit("Error, treetype should be birth-death or uniform")
        t = Tree(outname)

        # Assigning the branch lengths
        for node in t.traverse("postorder"):
            if node.is_root():
                pass
            else:
                if bl == "uniform":
                    node.dist = np.random.uniform(low=0.002, high=1.0, size=None)
                elif bl == "exponential":
                    node.dist = np.random.exponential(0.15, size=None)
                else:
                    exit(
                        "Error, branch length distribution should be uniform or exponential"
                    )
        t.write(format=1, outfile=outname)

    with open(os.path.join(outdir, "stdout.txt"), "a") as fout:
        fout.write(
            f"{numtrees} trees with {numleaves} leaves simulated, topology: {treeType}, branch length distribution: {bl}.\n"
        )

def simulate_alignments(in_dir, out_dir, seq_gen_path, model, seq_len):
    if not os.path.exists(out_dir):
        os.mkdir(out_dir)

    trees = [item[:-4] for item in os.listdir(in_dir) if item[-4:] == ".nwk"]

    for tree in tqdm(trees):
        in_path = os.path.join(in_dir, tree + ".nwk")
        out_path = os.path.join(out_dir, tree + ".fasta")
        command = f"{seq_gen_path} -m{model} -q -of -l {seq_len} < {in_path} > {out_path}"
        _ = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

def simulate_dataset(tree_output, ali_output, ntrees, nleaves, topology, branchlength, seq_len, seqgen, model):
    dataset_id = f"{ntrees}-{nleaves}-seqgen-{topology}-{branchlength}-{seq_len}-{model}"

    trees = os.path.join(tree_output, dataset_id)
    if not os.path.exists(trees):
        os.mkdir(trees)

    alignments = os.path.join(ali_output, dataset_id)
    if not os.path.exists(alignments):
        os.mkdir(alignments)

    simulate_trees(ntrees, nleaves, trees, topology, branchlength)
    simulate_alignments(trees, alignments, seqgen, model, seq_len)

def main():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        argument_default=argparse.SUPPRESS
    )
    parser.add_argument(
        "-to", 
        "--tree_output", 
        required=True, 
        type=str, 
        help="path to the output directory were the .nwk tree files will be saved"
    )
    parser.add_argument(
        "-ao",
        "--ali_output",
        type=str,
        required=True,
        help="path to the output directory were the .fasta alignment files will be saved",
    )
    parser.add_argument(
        "-n", 
        "--ntrees", 
        type=int, 
        required=False, 
        default=20, 
        help="number of trees"
    )
    parser.add_argument(
        "-l", 
        "--nleaves", 
        type=int, 
        required=False, 
        default=20, 
        help="number of leaves"
    )
    parser.add_argument(
        "-t",
        "--topology",
        type=str,
        required=False,
        default="uniform",
        help=f"tree topology. Choices: {TOPOLOGIES}",
        choices=TOPOLOGIES,
        metavar="TOPO",
    )
    parser.add_argument(
        "-b",
        "--branchlength",
        type=str,
        required=False,
        default="uniform",
        help=f"branch length distribution. Choices: {BRLENS}",
        choices=BRLENS,
        metavar="BL",
    )
    parser.add_argument(
        "-s",
        "--seqgen",
        required=True,
        type=str,
        help="path to the seq-gen executable",
    )
    parser.add_argument(
        "-sl",
        "--seq_len",
        type=int,
        required=False,
        default=200,
        help="length of the sequences in the alignments",
    )
    parser.add_argument(
        "-m",
        "--model",
        type=str,
        default="PAM",
        choices=SEQGEN_MODELS,
        help=f'model of evolution. Allowed values: [{", ".join(SEQGEN_MODELS)}]',
        metavar="MODEL",
    )
    args = parser.parse_args()

    simulate_dataset(args.tree_output, args.ali_output, args.ntrees, args.nleaves, args.topology, args.branchlength, args.seq_len, args.seqgen, args.model)

if __name__ == "__main__":
    main()
