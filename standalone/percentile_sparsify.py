"""
This script creates an edge file from a full similarity matrix.
Instead of grabbing the "top" nearest neighbors, the script determines the
amount of edges that would have been included if a particular "top" was
chosen. It includes all of the strongest edges such that there are N-samples X
top edges.

e.g. if 1000 nodes are present (1000X1000 similarity matrix), and top 6 is
chosen, then this script with produce an edge file with the top 6000 edges
excluding the diagonal.
"""

import argparse
import sys
from utils import readPandas
from utils import duplicate_columns_check
from compute_sparse_matrix import percentile_sparsify

def parse_args():

    parser = argparse.ArgumentParser(description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)

    # swat: We should be able to add 'required=True' to some args so the parser
    # will tell the user when they are left out. --directory should be required
    # since scripts get confused with relative paths sometimes.
    fins = []
    parser.add_argument('-i',"--in_file", type=str, help="")

    parser.add_argument('-o',"--out_file", type=str,help="",
                        default="naToMedian.tab")

    parser.add_argument('-t',"--top", type=str,help="",
                        default="naToMedian.tab")

    return parser.parse_args()

def main():
    opts = parse_args()

    in_file = opts.in_file
    out_file = opts.out_file

    df = readPandas(in_file)
    duplicate_columns_check(df)
    sparse_sim = percentile_sparsify(df, opts.top)

    sparse_sim.to_csv(out_file, sep="\t", header=None, index=False)

if __name__ == "__main__":
    sys.exit(main())