<img src="./resources/ML4Phylo_logo.png" alt="ML4Phylo" width="500"/>

# ML4Phylo
Machine Learning techniques applied to Phylogenetic Analysis

# Dependencies
Python 3.9 minimum.

The dependencies to be installed are as follows:
- scipy 
- numpy 
- ete3 
- biopython 
- dendropy 
- scikit-bio
- scikit-learn
- tqdm

For training the neural model it is also required:
- wandb - for loggin

To install any of these packages you only need to run the command:

```txt
    pip install <package name>
```

## Torch Dependency
You should also install the torch package. 
If you intend to train the model using torch with CUDA, instead of just installing torch you should run one of these commands:

### CUDA 11.8
```txt
   pip install torch==2.2.2 torchvision==0.17.2 torchaudio==2.2.2 --index-url https://download.pytorch.org/whl/cu118 
```

### CUDA 12.1
```txt
    pip install torch==2.2.2 torchvision==0.17.2 torchaudio==2.2.2 --index-url https://download.pytorch.org/whl/cu121
```

# Seq-Gen (Random genetic sequence generator)
To install Seq-Gen:
https://github.com/rambaut/Seq-Gen/releases/tag/1.3.4

The Seq-Gen executable for Windows is already available in the repository. If a Linux executable is needed, a new one should be compiled for Linux.

# SimBac (Random dataset generator)
To install SimBac: https://github.com/tbrown91/SimBac

The SimBac executable for Windows is already available in the repository.
If a Linux executable is needed, a new one should be compiled for Linux.

**Attention:** SimBac uses GNU Scientific Library (GLS), meaning this library must be  installed if you need too compile a new Simbac executable. While easily set-up in Linux, in Windows it can be harder if you choose not to go with the existent Cygwin add-on, so we recommend using MSYS2 with mingw64 and installing the following package: https://packages.msys2.org/package/mingw-w64-x86_64-gsl?repo=mingw64; avoiding the need of compiling the library yourself.

# Instructions to train the neural model 
After having the dependencies ready, you can run the ML4Phylo scripts:

In config.json file, you should checked first what device you're planning on using: "cpu" or "cuda". (default is "cuda")
You should open the command line through the console.bat present in the repo to set the necessary environment variable.

## Simulate the dataset for train

### Seq-Gen
```txt
simulate_dataset_SeqGen
    --tree_output <path to the output directory were the .nwk tree files will be saved>
    --ali_output <path to the output directory were the .fasta alignment files will be saved>
    --ntrees <number of trees> (default 20)
    --nleaves <number of leaves> (default 20)
    --topology <tree topology> (default uniform)
    --branchlength <branch length distribution> (default uniform)
    --seqgen <path to the seq-gen executable>
    --seq_len <length of the sequences in the alignments>
    --model <seq-gen model of evolution> (default PAM)
```
Example: python .\ml4phylo\scripts\simulate_dataset_SeqGen.py ....args......

### SimBac
```txt
simulate_dataset_SimBac
    --tree_output <path to the output directory were the .nwk tree files will be saved>
    --ali_output <path to the output directory were the .fasta alignments files will be saved>
    --simbac <path to the seq-gen executable>
    --ntrees <number of trees> (default 20)
    -nleaves <number of leaves> (default 20)
    --seq_len <length of the sequences in the alignments> (default 200)
    --rate_recombination <site-specific rate of internal recombination> (default 0.001)
    --mutation_rate <site-specific mutation rate> (default 0.001)
```
Example: python .\ml4phylo\scripts\simulate_dataset_SimBac.py ....args......

## Transforming genetic sequences into typing data
```txt
simulate_typing_data
    --input <input directory with the .fasta files>
    --output <output directory>
    --blocks <number of blocks for typing data>
    --block_size <size of each block>
    --interval <size of the interval between blocks>
```
Example: python .\ml4phylo\scripts\simulate_typing_data.py ....args......

## Creating tensors for the neural model training
```txt
make_tensors
    --treedir <input directory with the .nwk tree files>
    --datadir <input directory containing corresponding data files: [.fasta for alignments or .txt for typing data]>
    --output <output directory>
    --data_type <type of input data. Possible values: [AMINO_ACIDS, NUCLEOTIDES, TYPING]> (default: AMINO_ACIDS)
```
Example: python .\ml4phylo\scripts\make_tensors.py ....args......

## Train the neural model
```txt
train
    --input <input directory containing the tensor pairs on which the model will be trained>
    --validation <input directory containing the tensor pairs on which the model will be evaluated.>
                    (If left empty 10% of the training set will be used as validation data.)
    --config <configuration json file for the hyperparameters.>
    --output <output directory where the model parameters and the metrics will be saved.>
    --data_type <type of input data. Possible values: [AMINO_ACIDS, NUCLEOTIDES, TYPING].> (default: AMINO_ACIDS)
    --n_data <Number of sequences in input alignments.> (default: 20)
    --data_len <Length of sequences in the alignments or the number of genomes in typing.> (default: 200)
```
Example: python .\ml4phylo\scripts\train.py ....args......

```txt
train_wandb
    --config {<yaml sweep config filepath>, <wandb sweep author/project/id>} <number of runs>
    --device <torch device>
    --wandb <WandB logging mode. Choices: online, offline, disabled>
    --input </path/ to input directory containing the
    the tensor pairs on which the model will be trained>
    --output </path/ to output directory where the model parameters and the metrics will be saved>
```
Example: python .\ml4phylo\scripts\train_wandb.py ....args......

## Alignments with Intervals
Instead of converting the sequences to typing data, it is also possible, for training purposes, to split these sequences into blocks without converting them to genome identifiers.
```txt
alignments_intervals
    --input <path to input directory containing the .fasta files>
    --output <path to output directory>
    --blocks <number of blocks of sequences required>
    --block_size <size of the blocks of sequences required>
    --interval <size of the interval between blocks of sequences>
```
Example: python .\ml4phylo\scripts\alignments_intervals.py ....args......


## Prediction of pair wise distances
Its objective is to predict the pairwise distances of the provided data, whether they are sequences or typing data.

### With sequences
```txt
predict
    --datadir <path to input directory containing corresponding data files: [.fasta for alignments or .txt for typing data]>
    --output <path to the output directory were the .tree tree files will be saved>
    --model <NN model state dictionary, path/to/model.pt>
    --data_type <type of input data. Possible values: [AMINO_ACIDS, NUCLEOTIDES, TYPING].> (default: AMINO_ACIDS)
```
Example: python .\ml4phylo\scripts\predict.py ....args......

## Prediction of true trees
It is responsible for predicting the trees whose distance matrices are obtained through Hamming Distance. 
These will be used to compare with the trees obtained by ML4Phylo.

### With sequences
```txt
predict_true_trees
    --indir <path to input directory containing corresponding data files: [.fasta for alignments or .txt for typing data]>
    --outdir <output directory were the .nwk tree files will be saved>
    --data_type <type of input data. Possible values: [AMINO_ACIDS, NUCLEOTIDES, TYPING].> (default: AMINO_ACIDS)
```
Example: python .\ml4phylo\scripts\predict_true_trees.py ....args......

## Evaluation of the obtained phylogenetic trees
```txt
evaluate
    --true <directory containing true trees in .nwk format>
    --predictions <directory containing predicted trees in .nwk format>
```
Example: python .\ml4phylo\scripts\evaluate.py ....args......

# Important Note

## Training folders
In \testdata\training there are some folders you can use to store any values gotten from any operations necessary to train the model:

- \testdata\training\ &rarr; seqgen || simbac
    - trees &rarr; Store any .nwk files of generated trees;
    - alignments &rarr; Store any .fasta files of generated sequence alignments;
    - typing_data &rarr; Store any .txt files of typing data;
    - tensors
        - sequences &rarr; Store any tensor pairs of your sequence alignments;
        - typing_data &rarr; Store any tensor pairs of your typing data;
    - models 
        - sequences &rarr; Store any models gotten from training the model with sequences.
        - typing_data &rarr; Store any models gotten from training the model with typing data.

This folder structure is used for the data generated by both Seq-Gen and SimBac. The training folder is divided into two parts: one for each dataset generator.

## Prediction folders
In \testdata\predictions there are some folders you can use to store any values gotten from any operations necessary to predict the phylogenetic trees:

- \testdata\predictions
    - alignments &rarr; Store any .fasta files of sequence alignments;
    - typing_data &rarr; Store any .txt files of typing data;
    - trees:
      - predicted:
        - sequences &rarr; Store any .nwk files of predicted trees from sequence alignments;
        - typing_data &rarr; Store any .nwk files of predicted trees from typing data;
      - true:
        - sequences &rarr; Store any .nwk files of true trees from sequence alignments;
        - typing_data &rarr; Store any .nwk files of true trees from typing data;

Feel free to use these existing folders, but you can always have your own!
