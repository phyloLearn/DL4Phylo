<img src="./resources/ML4Phylo_logo.png" alt="ML4Phylo" width="500"/>

# ML4Phylo
Machine Learning techniques applied to Phylogenetic Analysis

# Dependências
As dependências a serem instaladas são as seguintes:
scipy, numpy, ete3, biopython, dendropy, scikit-bio, tqdm

## Dependência torch
Também deve-se instalar o package torch, aaso se pretenda treinar o modelo através do torch com o CUDA em vez de somente instalar o torch 
deve-se correr um destes comandos:

### CUDA 11.8
pip install torch==2.2.2 torchvision==0.17.2 torchaudio==2.2.2 --index-url https://download.pytorch.org/whl/cu118
### CUDA 12.1
pip install torch==2.2.2 torchvision==0.17.2 torchaudio==2.2.2 --index-url https://download.pytorch.org/whl/cu121

# Seq-Gen (Gerador aleatório de sequências)
Para instalar o Seq-Gen:
https://github.com/rambaut/Seq-Gen/releases/tag/1.3.4

O executável do Seq-Gen para Windows já está disponivél no repositório, caso seja necessário o executável para Linux deve-se compilar um novo para Linux.

# Instruções para treinar o modelo (valores padrão)
Após ter as dependências e o Seq-Gen prontos pode-se correr os scripts do ML4Phylo:

Deve-se abrir a linha de comandos através do console.bat presente no repo para se colocar a variavél de ambiente necessária.

## Simular as árvores
simulate_trees \
    --nleaves <number of leaves in each tree> (default 20) \
    --ntrees <number of trees> \
    --type <tree topology> (default uniform) \
    --output <output directory> \
    --branchlength <branch lenght distribution> (default uniform)

Exemplo: python .\ml4phylo\scripts\simulate_trees.py ....args......

## Simular os alinhamentos (sequências)
simulate_alignments \
    --input <input directory with the .nwk tree files>  \
    --output <output directory> \
    --length <length of the simulated sequences> (default 200) \
    --seqgen <path to Seq-Gen executable> \
    --model <model of evolution> (default PAM)

Exemplo: python .\ml4phylo\scripts\simulate_alignments.py ....args......

## Passar de sequências de DNA a typing data
simulate_typing_data \
    --input <input directory with the .fasta files>  \
    --output <output directory> \
    --blocks <number of blocks for typing data> \
    --block_size <size of eah block> \
    --interval <size of the interval between blocks> (default PAM)

Exemplo: python .\ml4phylo\scripts\simulate_typing_data.py ....args......

## Criar os tensores para o treino do modelo
make_tensors_typing \
    --treedir <input directory with the .nwk tree files> \
    --typingdir <input directory with the corresponding .txt typing data files>  \
    --output <output directory>

Exemplo: python .\ml4phylo\scripts\make_tensors_typing.py ....args......

# Notas finais 

Em .\testdata\dataset\training podem-se encontrar alguns ficheiros de árvores, sequências, typing data e tensor_pairs antes criados.
Podem-se usar estas diretorias para armanezar novos ficheiros que sejam criados. (Faz overwrite nos ficheiros já lá presentes)




    
