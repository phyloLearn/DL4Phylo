import os
from setuptools import setup, find_packages

setup(
    name="ML4Phylo",
    version="0.0.1a4",
    description="Machine Learning techniques applied to Phylogenetic Analysis",
    long_description=open("./README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/phyloLearn/ML4Phylo",
    author="Miguel Raposo, Gonçalo Silva",
    license="CeCIL",
    packages=find_packages(),
    install_requires=[
        "torch>=1.13.1",
        "scipy>=1.7.3",
        "numpy>=1.21.2",
        "ete3>=3.1.2",
        "biopython>=1.79",
        "dendropy>=4.5.2",
        "scikit-bio>=0.5.6",
        "scikit-learn>=1.4.2",
        "tqdm>=4.65.0",
        "wandb>=0.17.3",
    ],
    package_data={
        'phyloformer': [
            os.path.join("pretrained_models", "*"),
            "LICENSE",
        ]
    },
    include_package_data=True,
    python_requires=">=3.7, <3.10",
    entry_points = {
        'console_scripts': [
            "train_wandb = ml4phylo.scripts.train_wandb:main",
            "train = ml4phylo.scripts.train:main",
            "evaluate = ml4phylo.scripts.evaluate:main",
            "make_tensors = ml4phylo.scripts.make_tensors:main",
            "predict_true_trees = ml4phylo.scripts.predict_true_trees:main",
            "predict = ml4phylo.scripts.predict:main",
            "simulate_dataset_SeqGen = ml4phylo.scripts.simulate_dataset_SeqGen:main",
            "simulate_dataset_SimBac = ml4phylo.scripts.simulate_dataset_SimBac:main",
            "simulate_typing_data = ml4phylo.scripts.simulate_typing_data:main",
        ]
    }
)
