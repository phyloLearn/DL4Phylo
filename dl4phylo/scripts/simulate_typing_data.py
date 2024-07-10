import os
import argparse
from tqdm import tqdm
from data import _parse_alignment
from utils import is_fasta

def sequence_to_typing(seq, gene_dic, total_blocks,  block_size, interval_block_size):
    n_blocks = 0
    typing_seq = []
    
    for i in range(0, len(seq), block_size + interval_block_size):
        if i + block_size > len(seq) or n_blocks >= total_blocks:
            break
        
        current_block = seq[i:i + block_size]
        n_blocks += 1
        
        current_gene = "gene_" + str(n_blocks)
        
        if current_gene not in gene_dic:
            gene_dic[current_gene] = {current_block: 1}
        elif current_block not in gene_dic[current_gene]:
            gene_dic[current_gene][current_block] = len(gene_dic[current_gene]) + 1
            
            
        typing_seq.append(gene_dic[current_gene][current_block])

    return typing_seq
    
def fasta_to_typing(total_blocks, block_size, interval_block_size, alignment, gene_dict):
    typing_seqs = {}
    
    for seq_name, seq in alignment.items():
        typing_data = sequence_to_typing(seq, gene_dict, total_blocks, block_size, interval_block_size)
        typing_seqs[seq_name] = typing_data
        
    return typing_seqs, gene_dict.keys()


def simulate_typing_data(in_dir, out_dir, blocks, block_size, interval_size):
    typing_dir = os.path.join(out_dir, in_dir.split("\\")[-1] + f"-{blocks}-{block_size}-{interval_size}")
    if not os.path.exists(typing_dir):
        os.mkdir(typing_dir)
    
    gene_dict = {}

    for alignment in (pbar := tqdm([file for file in os.listdir(in_dir) if is_fasta(file)])):
        identifier = alignment.split(".")[0]
        pbar.set_description(f"Processing {identifier}")
        
        alignment_dict = _parse_alignment(os.path.join(in_dir, alignment))

        typing_data_dict, genes = fasta_to_typing(blocks, block_size, interval_size, alignment_dict, gene_dict)
        
        output = "ST\t" + "\t".join(genes) + "\n"
        
        ST_id = 1
        for typing_seq in typing_data_dict.values():
            typing_seq_string = f"{ST_id}\t" + "\t".join([str(gene_id) for gene_id in typing_seq])
            output += typing_seq_string + '\n'
            ST_id += 1

        with open(os.path.join(typing_dir, f"{identifier}.txt"), "w") as fout:
            fout.write(output)
        
        
    
def main():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        argument_default=argparse.SUPPRESS,
        description="Convert the .fasta files to typing data files.",
    )
    parser.add_argument(
        "-in",
        "--input",
        required=True,
        type=str,
        help="path to input directory containing the .fasta files",
    )
    parser.add_argument(
        "-out", 
        "--output", 
        required=False,
        default=".", 
        type=str,
        help="path to output directory where the typing data files will be saved"
    )
    parser.add_argument(
        "-b",
        "--blocks",
        required=True,
        type=int,
        help="number of blocks in the typing data",
    )
    parser.add_argument(
        "-s",
        "--block_size",
        required=True,
        type=int,
        help="size of the blocks in the typing data",
    )
    parser.add_argument(
        "-i",
        "--interval",
        required=True,
        type=int,
        help="size of the interval between blocks in the typing data",
    )
    args = parser.parse_args()

    simulate_typing_data(args.input, args.output, args.blocks, args.block_size, args.interval)

if __name__ == "__main__":
    main()
