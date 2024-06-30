import argparse
from ete3 import Tree
import numpy as np
import os




def evaluate(true, predicted):
    true = os.path.join('./test/true_trees', true)
    predicted = os.path.join('./test/predicted_trees', predicted)
    true_trees=[item for item in os.listdir(true) if item[-3:]=='nwk']
    RFs=[]
    for tree in true_trees:
        t1=Tree(os.path.join(true, tree))
        # --------------------------------
        tree=tree.split('.')[0]+'.pf.nwk'
        # --------------------------------
        t2=Tree(os.path.join(predicted, tree))
        # RFs.append(t1.compare(t2,unrooted=True)['norm_rf'])
        rf_value = t1.compare(t2, unrooted=True)['norm_rf']
        RFs.append(float(rf_value))
    print(f'Mean normalized Robinson-Foulds distance between true and predicted trees: {np.mean(RFs):.3f}')




if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', '--true', type=str, required=True, help='Identifier of the dataset where the true trees will be read.')
    parser.add_argument('-p', '--predicted', type=str, required=True, help='Identifier of the dataset where the predicted trees will be read.')
    args = parser.parse_args()

    evaluate(true=args.true, predicted=args.predicted)
