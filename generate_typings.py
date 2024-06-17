import argparse
import os
from phyloformer.data import _parse_alignment
from tqdm.auto import tqdm




def sequence_to_typing(seq, gene_dic, total_blocks,  block_size, interval_block_size):
    n_blocks = 0
    typing_seq = []
    
    for char in range(0, len(seq), block_size + interval_block_size):
        if char + block_size > len(seq) or n_blocks >= total_blocks:
            break
        
        current_block = seq[char:char + block_size]
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




def generate_typings(input_alignments, dataset_id, blocks, block_size, interval_size):
    input_alignments = os.path.join('./datasets/alignments', input_alignments)
    assert os.path.exists(input_alignments), '> ERROR: Invalid input alignments directory.'
    alignments = [file for file in os.listdir(input_alignments) if file.endswith('.fasta')]
    assert len(alignments) > 0, '> ERROR: No alignment (.fasta) files found in the input alignments directory.'

    
    output = os.path.join('./datasets/typings', dataset_id)
    if not os.path.exists(output):
        os.makedirs(output)
    
    
    gene_dict = {}
    for alignment in (pbar := tqdm(alignments)):
        identifier = alignment.split(".")[0]
        pbar.set_description(f"Processing {identifier}")
        
        alignment_dict = _parse_alignment(os.path.join(input_alignments, alignment))

        typing_data_dict, genes = fasta_to_typing(blocks, block_size, interval_size, alignment_dict, gene_dict)
        
        row = "ST\t" + "\t".join(genes) + "\n"
        
        ST_id = 1
        for typing_seq in typing_data_dict.values():
            typing_seq_string = f"{ST_id}\t" + "\t".join([str(gene_id) for gene_id in typing_seq])
            row += typing_seq_string + '\n'
            ST_id += 1

        with open(os.path.join(output, f"{identifier}.txt"), "w") as fout:
            fout.write(row)

        


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-a', '--input-alignments', type=str, required=True, help='Identifier of the dataset where the generated alignments (input) will be read.')
    parser.add_argument('-o', '--dataset-id', type=str, required=True, help='Identifier of the dataset where the generated typings (output) will be written.')
    parser.add_argument('-b', '--nblocks', default=7, type=int, required=False, help='Number of blocks (contiguous segments) per sequence per alignment.')
    parser.add_argument('-e', '--nextracted', default=900, type=int, required=False, help='Number of nucleotides extracted per block.')
    parser.add_argument('-i', '--nignored', default=100, type=int, required=False, help='Number of nucleotides ignored per block).')
    args = parser.parse_args()

    generate_typings(args.input_alignments, args.dataset_id, args.nblocks, args.nextracted, args.nignored)
