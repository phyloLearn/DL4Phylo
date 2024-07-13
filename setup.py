from setuptools import setup, find_packages

setup(
    name="DL4Phylo",
    version="0.0.3",
    description="Deep Learning techniques applied to Phylogenetic Analysis",
    long_description=open("./README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/phyloLearn/DL4Phylo",
    author="Miguel Raposo, Gonçalo Silva",
    license="CeCILL",
    packages=find_packages(),
    install_requires=[
        "torch>=1.13.1",
        "scipy>=1.7.3",
        "numpy>=1.21.2, <2.0.0",
        "ete3>=3.1.2",
        "biopython>=1.79",
        "dendropy>=4.5.2",
        "scikit-bio>=0.5.6",
        "scikit-learn>=1.4.2",
        "tqdm>=4.65.0",
        "wandb>=0.17.3",
    ],
    extras_require={
        "dev": ["twine>=4.0.2, !=5.1.0"]
    },
    python_requires=">=3.9, <3.13",
    entry_points = {
        'console_scripts': [
            "train_wandb = dl4phylo.scripts.train_wandb:main",
            "train_tensorboard = dl4phylo.scripts.train_tensorboard:main",
            "evaluate = dl4phylo.scripts.evaluate:main",
            "make_tensors = dl4phylo.scripts.make_tensors:main",
            "predict_true_trees = dl4phylo.scripts.predict_true_trees:main",
            "predict = dl4phylo.scripts.predict:main",
            "simulate_dataset_SeqGen = dl4phylo.scripts.simulate_dataset_SeqGen:main",
            "simulate_dataset_SimBac = dl4phylo.scripts.simulate_dataset_SimBac:main",
            "simulate_typing_data = dl4phylo.scripts.simulate_typing_data:main",
            "alignment_trimmer = dl4phylo.scripts.alignment_trimmer:main",
        ]
    }
)
