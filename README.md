<img src="./resources/DL4Phylo_logo.png" alt="DL4Phylo" width="500"/>

<!-- ![](https://raw.githubusercontent.com/phyloLearn/ML4phylo/main/resources/DL4Phylo_logo.png) -->

# DL4Phylo: Deep Learning techniques applied to Phylogenetic Analysis

## Authors
- Gon�alo Silva
- Miguel Raposo
- C�tia Vaz (Supervisor)

## Main Objective
There are numerous databases with Typing Data and various approaches for performing the phylogenetic inference of this kind of data instead of DNA sequences. Therefore, it would be ideal to have a tool that supports this type of data. With this problem in mind, we propose DL4Phylo.

DL4Phylo is a tool designed to support data typing by enhancing the accuracy and efficiency of the inference process through deep learning techniques.

**For a more detailed look at our work we recommend having a look at our report, which is available in this repository.**

# How to install DL4Phylo
The simplest way of installing **DL4Phylo** would be to simply install the existing PyPi package by typing the following command in the command-line:
```
pip install dl4phylo
```

If you wish to install it locally through the setup.py present in the repository than we suggest cloning the git repository then navigate to its respective directory and simply run:
```
pip install .
```

You can always create a new **Conda** environment to isolate this installation from the rest of your system:
```
conda create -n dl4phylo python=3.9
conda activate dl4phylo
```
Then if you wish to delete the created environment:
```
conda remove -n dl4phylo --all
```

Ok, all set! You're ready to begin using **DL4Phylo**!

# Tool dependencies

## Python

Version 3.9 minimum required.

## Packages utilized by the tool

**torch | scipy | numpy | ete3 | biopython | dendropy | scikit-bio | scikit-learn | tqdm | wandb**

If you intend to train the model using **torch** with **CUDA**, instead of just installing torch you should run one of these commands:

### CUDA 11.8
```
pip install torch==2.2.2 torchvision==0.17.2 torchaudio==2.2.2 --index-url https://download.pytorch.org/whl/cu118 
```

### CUDA 12.1
```
pip install torch==2.2.2 torchvision==0.17.2 torchaudio==2.2.2 --index-url https://download.pytorch.org/whl/cu121
```

## Seq-Gen (Random genetic sequence generator) & SimBac (Random dataset generator)
To install Seq-Gen: https://github.com/rambaut/Seq-Gen/releases/tag/1.3.4
To install SimBac: https://github.com/tbrown91/SimBac


The Seq-Gen and SimBac executables for Windows are already available in the repository. If any of the executables is needed for any other OS (Linux, MacOS), a new one should be compiled for the respective one.

**Attention:** SimBac uses GNU Scientific Library (GLS), meaning this library must be  installed if you need too compile a new Simbac executable. While easily set-up in Linux or MacOS, in Windows it can be challenging if you choose not to go with the existent Cygwin add-on, so we recommend using MSYS2 with mingw64 and installing the following package:
https://packages.msys2.org/package/mingw-w64-x86_64-gsl?repo=mingw64

Avoiding the need of compiling the library yourself.

# Instructions to train the neural model 

## Simulate the dataset

### Simulating datasets with Seq-Gen
```
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

### Simulating datasets with SimBac
```
simulate_dataset_SimBac
    --tree_output <path to the output directory were the .nwk tree files will be saved>
    --ali_output <path to the output directory were the .fasta alignments files will be saved>
    --simbac <path to the seq-gen executable>
    --ntrees <number of trees> (default 20)
    --nleaves <number of leaves> (default 20)
    --seq_len <length of the sequences in the alignments> (default 200)
    --rate_recombination <site-specific rate of internal recombination> (default 0.001)
    --mutation_rate <site-specific mutation rate> (default 0.001)
```

## Transforming genetic sequences into typing data
```
simulate_typing_data
    --input <input directory with the .fasta files>
    --output <output directory>
    --blocks <number of blocks for typing data>
    --block_size <size of each block>
    --interval <size of the interval between blocks>
```

## Trimming alignments
Instead of converting the sequences to typing data, it is also possible, to split these sequences into blocks without converting them to genome identifiers.

```
alignment_trimmer
    --input <path to input directory containing the .fasta files>
    --output <path to output directory>
    --blocks <number of blocks of sequences required>
    --block_size <size of the blocks of sequences required>
    --interval <size of the interval between blocks of sequences>
    --separator <boolean to identify if it is necessary to separate the blocks with '-'>
```

## Creating tensors for the neural model training
```
make_tensors
    --treedir <input directory with the .nwk tree files>
    --datadir <input directory containing corresponding data files: [.fasta for alignments or .txt for typing data]>
    --output <output directory>
    --data_type <type of input data. Possible values: [AMINO_ACIDS, AMINO_ACIDS_BLOCKS, NUCLEOTIDES, NUCLEOTIDES_BLOCKS, TYPING]> (default: AMINO_ACIDS)
```

## Train the neural model

### Training with TensorBoard
```
train_tersorboard
    --input <input directory containing the tensor pairs on which the model will be trained>
    --validation <input directory containing the tensor pairs on which the model will be evaluated.>
                    (If left empty 10% of the training set will be used as validation data.)
    --config <configuration json file for the hyperparameters.>
    --output <output directory where the model parameters and the metrics will be saved.>
    --log <how to log training process. Possible values: [tensorboard, file, both]> (default: file)
```
We recommend running this script with the default logging option (file) if you wish to perform the training with your local machine without requiring logging-in to any external accounts (**TensorBoard** or **WandB**). 

### Training with WandB
```
train_wandb
    --config {<yaml sweep config filepath>, <wandb sweep author/project/id>} <number of runs>
    --device <torch device>
    --wandb <WandB logging mode. Choices: online, offline, disabled>
    --input </path/ to input directory containing the tensor pairs on which the model will be trained>
    --output </path/ to output directory where the model parameters and the metrics will be saved>
```

To understand better the two ways **alignment_trimmer** can be used, mainly due to the presence of the **separator** option, we recommend reading the chapter **DL4Phylo vs Phyloformer** in our report.

## Predicting the pair wise distances
Its objective is to predict the pairwise distances of the provided data, whether they are sequences or typing data.

```
predict
    --datadir <path to input directory containing corresponding data files: [.fasta for alignments or .txt for typing data]>
    --output <path to the output directory were the .tree tree files will be saved>
    --model <NN model state dictionary, path/to/model.pt>
    --data_type <type of input data. Possible values: [AMINO_ACIDS, AMINO_ACIDS_BLOCKS, NUCLEOTIDES, NUCLEOTIDES_BLOCKS, TYPING].> (default: AMINO_ACIDS)
    
```
**Attention**: If you choose to predict the pairwise distances for alignments in blocks (AMINO_ACID_BLOCKS or NUCLEOTIDE_BLOCKS), your alignments should have the same block size as the alignments used to train the model. This is a limitation of this type of data.

## Prediction of true trees
It is responsible for predicting the trees whose distance matrices are obtained through Hamming Distance. 
These will be used to compare with the trees obtained by DL4Phylo.

```
predict_true_trees
    --indir <path to input directory containing corresponding data files: [.fasta for alignments or .txt for typing data]>
    --outdir <output directory were the .nwk tree files will be saved>
    --data_type <type of input data. Possible values: [AMINO_ACIDS, AMINO_ACIDS_BLOCKS, NUCLEOTIDES, NUCLEOTIDES_BLOCKS, TYPING].> (default: AMINO_ACIDS)
```

## Evaluation of the obtained phylogenetic trees
```
evaluate
    --true <directory containing true trees in .nwk format>
    --predictions <directory containing predicted trees in .nwk format>
```

# Training folders
In \testdata\training there are some folders you can use to store the values gotten from any operation available in the tool:

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

This folder structure is used for the data generated by both Seq-Gen and SimBac.

# Prediction folders
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

Feel free to use the existing folders, but you can always have your own!

# Example of use
The following example shows how to use the tool to train a model with typing data and predict the phylogenetic trees. 
All scripts were executed from the root of the project.

## Simulate the dataset

### Simulating datasets with Seq-Gen
```
python dl4phylo\scripts\simulate_dataset_SeqGen.py
    --tree_output .\testdata\training\seqgen\trees 
    --ali_output .\testdata\training\seqgen\alignments 
    --ntrees 12 
    --nleaves 5 
    --seqgen .\simulators\seq-gen.exe 
    --seq_len 20
```
Simulating datasets for 12 trees with 5 leaves each and 20 characters in length each leaf. 
Generates ".nwk" (trees) and ".fasta" (alignments) files for each tree.

## Transforming genetic sequences into typing data
```
python dl4phylo\scripts\simulate_typing_data.py 
    --input testdata\training\seqgen\alignments\12-5-seqgen-uniform-uniform-20-PAM 
    --output testdata\training\seqgen\typing_data 
    --blocks 7 
    --block_size 2 
    --interval 1
```
[Input alignments](./testdata/training/seqgen/alignments/12-5-seqgen-uniform-uniform-20-PAM/)

The folder "12-5-seqgen-uniform-uniform-20-PAM" is generated by our tool and it represents alignments that have 12 trees with 5 leaves and that was generated by seqgen with both `uniform` branch length and topology. The sequences have a length of 20 and the model of evolution is PAM.

## Trimming alignments
For our example this alignment trimmer is not going to be used however the following script is an example of how to use it.
```
python dl4phylo\scripts\alignment_trimmer.py 
    --input testdata\training\seqgen\alignments\12-5-seqgen-uniform-uniform-20-PAM 
    --output testdata\training\seqgen\alignments_blocks 
    --blocks 7 
    --block_size 2 
    --interval 1 
    --separator
```
[Input alignments](./testdata/training/seqgen/alignments/12-5-seqgen-uniform-uniform-20-PAM/)

## Creating tensors for the neural model training
```
python dl4phylo\scripts\make_tensors.py 
    --treedir testdata\training\seqgen\trees\12-5-seqgen-uniform-uniform-20-PAM 
    --datadir testdata\training\seqgen\typing_data\12-5-seqgen-uniform-uniform-20-PAM-7-2-1 
    --output testdata\training\seqgen\tensors\typing_data 
    --data_type TYPING
```
[Input trees](./testdata/training/seqgen/trees/12-5-seqgen-uniform-uniform-20-PAM/)
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
[Input data](./testdata/training/seqgen/typing_data/12-5-seqgen-uniform-uniform-20-PAM-7-2-1/)
## Train the neural model

### Training with TensorBoard
```
python dl4phylo\scripts\train_tensorboard.py 
    --input testdata\training\seqgen\tensors\typing_data\12-5-seqgen-uniform-uniform-20-PAM-7-2-1 
    --config train_config\tensorboard\config.json 
    --output testdata\training\seqgen\models\typing_data
```
[Input tensors](./testdata/training/seqgen/tensors/typing_data/12-5-seqgen-uniform-uniform-20-PAM-7-2-1/)

## Predicting the pair wise distances
```
python dl4phylo\scripts\predict.py 
    --datadir testdata\prediction\typing_data 
    --output testdata\prediction\trees\predicted\typing_data 
    --model testdata\training\seqgen\models\typing_data\12-5-seqgen-uniform-uniform-20-PAM-7-2-1\LR_0.00039_O_Adam_L_L2_E_185_BS_4NB_6_NH_4_HD_64_A_D_0.0.best_model.pt
    --data_type TYPING
```
[Input data](./testdata/prediction/typing_data/)

The model used in this example should be the best model obtained from the training process.

## Prediction of true trees
```
python dl4phylo\scripts\predict_true_trees.py 
    --indir testdata\prediction\typing_data 
    --outdir testdata\prediction\trees\true\typing_data 
    --data_type TYPING
```
[Input data](./testdata/prediction/typing_data/)

## Evaluation of the obtained phylogenetic trees
```
python dl4phylo\scripts\evaluate.py 
    --true testdata\prediction\trees\true\typing_data\typing_data
    --predictions testdata\prediction\trees\predicted\typing_data\typing_data
```
[True trees](./testdata/prediction/trees/true/typing_data/typing_data/)
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
[Predicted trees](./testdata/prediction/trees/predicted/typing_data/typing_data/)

The second "typing_data" folder is named after the input folder used in the prediction script. For example, if the input folder is called "haemophilus_influenzae", the corresponding output folder inside the first "typing_data" will also be named "haemophilus_influenzae". In this case, we used a folder named "typing_data" as input, so the output will contain two folders with the same name.

# Results
The results obtained through our tool can be seen in the chapter **Experimental Evaluation** of our report, these were obtained by training using WanbD on a machine with the following specifications:
```
Intel(R) Xeon(R) Gold 6330 CPU @ 2.00GHz
00:06.0 3D controller: NVIDIA Corporation GA100 [A100 PCIe 80GB] (rev a1)
00:07.0 3D controller: NVIDIA Corporation GA100 [A100 PCIe 80GB] (rev a1)
00:08.0 3D controller: NVIDIA Corporation GA100 [A100 PCIe 80GB] (rev a1)
00:09.0 3D controller: NVIDIA Corporation GA100 [A100 PCIe 80GB] (rev a1)
``` 

# Final Notes
The insertion of the Typing Data extensions (**Trimming alignments**) presented some challenges. Hardware limitations made it impossible to test realistic sets of values like we did for regular Typing Data, and only very small dimensions could be tested. Due to time constraints and these extensions not being our main priority, further work has not been done on them. However, their use remains possible within our tool, but additional testing should be conducted, either by us in the future or by someone with high-end hardware and storage capability. Taking into account our results, we plan also to incorporate a tree comparison metric in the objective loss function to be optimized in the model training.