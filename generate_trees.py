import argparse
from dendropy.simulate import treesim
from ete3 import Tree
import numpy as np
import os
from secrets import token_hex
from tqdm.auto import tqdm




TOPOLOGIES = ['uniform', 'birth-death']
BRANCH_LENGTHS = ['uniform', 'exponential']




def generate_trees(dataset_id: str, ntrees: int, nleaves: int, topology: str, branch_lengths: str):
    """
    Generate a set of phylogenetic trees with the specified parameters.

    Parameters
    ----------
    dataset_id : str
        Identifier of the dataset where the generated trees (output) will be written.
    ntrees : int
        Number of trees to be generated.
    nleaves : int
        Number of leaves per tree.
    topology : str
        Topology of the tree (shape).
    branch_lengths : str
        Statistical distribution of branch lengths.
    """

    assert ntrees > 0, '> ERROR: Invalid number of trees.'

    assert nleaves > 0, '> ERROR: Invalid number of leaves.'
    
    assert topology in TOPOLOGIES, '> ERROR: Invalid topology.'
    
    assert branch_lengths in BRANCH_LENGTHS, '> ERROR: Invalid branch lengths.'

    
    output = os.path.join('./datasets/trees', dataset_id)
    if not os.path.exists(output):
        os.makedirs(output)
    
    
    generation_id = token_hex(4)
    for i in tqdm(range(ntrees), desc='> Generating trees'):
        file = os.path.join(output, f'{generation_id}-{i+1}_{ntrees}.nwk')

        if topology == 'uniform':
            tree = Tree()
            tree.populate(size=nleaves)
            tree.write(outfile=file, format=1)
        elif topology == 'birth-death':
            tree = treesim.birth_death_tree(birth_rate=1.0, death_rate=0.5, num_extant_tips=nleaves)
            tree.write(path=file, schema='newick', suppress_rooting=True)
    
        tree = Tree(file)

        for node in tree.traverse('postorder'):
            if not node.is_root():
                if branch_lengths == 'uniform':
                    node.dist = np.random.uniform(low=0.002, high=1.0, size=None)
                elif branch_lengths == 'exponential':
                    node.dist = np.random.exponential(0.15, size=None)
        tree.write(outfile=file, format=1)




if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-o', '--dataset-id', type=str, required=True, help='Identifier of the dataset where the generated trees (output) will be written.')
    parser.add_argument('-t', '--ntrees', default=20, type=int, required=False, help='Number of trees to be generated.')
    parser.add_argument('-l', '--nleaves', default=20, type=int, required=False, help='Number of leaves per tree.')
    parser.add_argument('-s', '--topology', default='uniform', choices=TOPOLOGIES, type=str, required=False, help='Topology of the tree (shape).')
    parser.add_argument('-d', '--branch-lengths', default='uniform', choices=BRANCH_LENGTHS, type=str, required=False, help='Statistical distribution of branch lengths.')
    args = parser.parse_args()

    generate_trees(args.dataset_id, args.ntrees, args.nleaves, args.topology, args.branch_lengths)
