import argparse
import os   

from data import load_data, DataType

def is_fasta(path: str) -> bool:
    return path.lower().endswith("fa") or path.lower().endswith("fasta")

def is_txt(path: str) -> bool:
    return path.lower().endswith("txt")

def encoding(datadir: str, block_size: int, data_type: str):
    align_encoded = 0
    
    for aln in [file for file in os.listdir(datadir) if is_txt(file) or is_fasta(file)]:

        # This function is applied to every file present the input directory
        load_data(os.path.join(datadir, aln), data_type, block_size)
        
        align_encoded += 1
        
    
    print(f"Encoded {align_encoded} alignments")

DATA_TYPES = DataType.toList()

def main():
    parser = argparse.ArgumentParser(description=("Encodes typing data files into tensors"))
    parser.add_argument(
        "datadir",
        type=str,
        help="path to input directory containing the typing data",
    )
    parser.add_argument(
        "-dt",
        "--data_type",
        required=False,
        choices=DATA_TYPES,
        default="AMINO_ACIDS",
        type=str,
        help=f"type of data to encode (typing or sequences). Allowed Values: {DATA_TYPES}",
    )
    parser.add_argument(
        "-b",
        "--block_size",
        required=False,
        default=None,
        type=int,
        help="size of the block to encode",
    )
    args = parser.parse_args()

    encoding(args.datadir, args.block_size, DataType[args.data_type])

    print("\nDone!")


if __name__ == "__main__":
    main()
