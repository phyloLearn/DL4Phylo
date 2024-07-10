import os
import argparse
from secrets import token_hex
import subprocess

def simulate_dataset_SimBac(tree_output, ali_output, ntrees, nleaves, seq_len, rate_recombination, mutation_rate, simbac):
    dataset_id = f'{ntrees}-{nleaves}-simbac-{seq_len}-{rate_recombination}-{mutation_rate}'

    trees = os.path.join(tree_output, dataset_id)
    if not os.path.exists(trees):
        os.mkdir(trees)

    alignments = os.path.join(ali_output, dataset_id)
    if not os.path.exists(alignments):
        os.mkdir(alignments)


    for i in range(ntrees):
        generation_id = token_hex(4)
        print(f'{i+1}/{ntrees}:{generation_id}', end='\r')
        command = f'{simbac} -N {nleaves} -B {seq_len} -R {rate_recombination} -T {mutation_rate} -o {alignments}/{generation_id}.fasta -c {trees}/{generation_id}.nwk'
        _ = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)



def main():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        argument_default=argparse.SUPPRESS,
        description="Simulate a dataset using the SimBac simulator.",
    )
    parser.add_argument(
        "-to",
        "--tree_output",
        required=False,
        default=".",
        type=str,
        help="path to the output directory where the .nwk tree files will be saved"
    )
    parser.add_argument(
        "-ao", 
        "--ali_output", 
        required=False,
        default=".", 
        type=str, 
        help="path to the output directory where the .fasta alignments files will be saved"
    )
    parser.add_argument(
        "-s",
        "--simbac",
        required=True,
        type=str,
        help="path to the seq-gen executable",
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
        "-sl",
        "--seq_len",
        type=int,
        required=False,
        default=200,
        help="length of the sequences in the alignments",
    )
    parser.add_argument(
        "-r",
        "--rate_recombination",
        type=float,
        required=False,
        default=0.001,
        help="site-specific rate of internal recombination",
    )
    parser.add_argument(
        "-t",
        "--mutation_rate",
        type=float,
        required=False,
        default=0.001,
        help="site-specific mutation rate",
    )
    args = parser.parse_args()

    simulate_dataset_SimBac(args.tree_output, args.ali_output, args.ntrees, args.nleaves, args.seq_len, args.rate_recombination, args.mutation_rate, args.simbac)


if __name__ == "__main__":
    main()