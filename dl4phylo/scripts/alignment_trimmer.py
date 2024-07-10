import os
import argparse
from tqdm import tqdm
from data import _parse_alignment
from utils import is_fasta

def alignment_trimmer(in_dir, out_dir, blocks, block_size, interval_size, separator):

    ali_intervals_dir = os.path.join(out_dir, in_dir.split("\\")[-1] + f"-{blocks}-{block_size}-{interval_size}" + ("-sep" if separator else ""))
    if not os.path.exists(ali_intervals_dir):
        os.mkdir(ali_intervals_dir)

    for alignment in (pbar := tqdm([file for file in os.listdir(in_dir) if is_fasta(file)])):
        identifier = alignment.split(".")[0]
        pbar.set_description(f"Processing {identifier}")
        
        alignment_dict = _parse_alignment(os.path.join(in_dir, alignment))
        output = ""

        for seq_name, sequence in alignment_dict.items():
            seq = break_into_blocks(sequence, blocks, block_size, interval_size, separator)
            output += f">{seq_name}\n{seq}\n"
        
        with open(os.path.join(ali_intervals_dir, f"{identifier}.fasta"), "w") as fout:
            fout.write(output)

def break_into_blocks(sequence, blocks, block_size, interval_size, separator):
    n_blocks = 0
    seq = ""
    for i in range(0, len(sequence), block_size + interval_size):
        if i + block_size > len(sequence) or n_blocks >= blocks:
            break
        
        current_block = sequence[i:i + block_size]
        n_blocks += 1
        
        seq += current_block + ("-" if separator else "")

    return seq

def main():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        argument_default=argparse.SUPPRESS,
        description="Trim the sequences in the input .fasta files into blocks of sequences.",
    )
    parser.add_argument(
        "-in",
        "--input",
        required=True,
        type=str,
        help="path to input directory containing the\
    .fasta files",
    )
    parser.add_argument(
        "-out", 
        "--output", 
        required=False,
        default=".",
        type=str,
        help="path to output directory"
    )
    parser.add_argument(
        "-b",
        "--blocks",
        required=True,
        type=int,
        help="number of blocks of sequences required",
    )
    parser.add_argument(
        "-s",
        "--block_size",
        required=True,
        type=int,
        help="size of the blocks of sequences required",
    )
    parser.add_argument(
        "-i",
        "--interval",
        required=True,
        type=int,
        help="size of the interval between blocks of sequences",
    )
    parser.add_argument(
        "-se",
        "--separator",
        action="store_true",
        default=False,
        help="boolean to identify if it is necessary to separate the blocks with '-'",
    )

    args = parser.parse_args()

    alignment_trimmer(args.input, args.output, args.blocks, args.block_size, args.interval, args.separator)

if __name__ == "__main__":
    main()