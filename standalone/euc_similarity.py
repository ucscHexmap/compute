"""
Takes in a tab separated (row X col) matrix and outputs a full similarity matrix
(col X col) using the inverse euclidean similarity.

This script assumes you have taken care of missing values.

example: python2.7 euc_similarity.py -i tab_mat.tab -o euc_full_sim.tab
"""

import argparse
import sys
from utils import readPandas
from utils import duplicate_columns_check
import spatial
import pandas as pd


def parse_args():

    parser = argparse.ArgumentParser(description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument('-i',"--in_file", type=str, help=""
                        )

    parser.add_argument('-o',"--out_file", type=str, help="",
                        default="full_sim.euc.tab"
                        )

    parser.add_argument('-r',"--rows", action="store_true",
                        help="Flag for whether to make a row X row sim matrix"
                        )

    return parser.parse_args()


def main():

    opts = parse_args()

    in_file = opts.in_file
    out_file = opts.out_file
    doing_rows = opts.rows

    df = readPandas(in_file)
    duplicate_columns_check(df)
    if not doing_rows:
        df = df.transpose()

    row_names = df.index
    full_sim = spatial.inverseEucDistance(df)
    full_sim = pd.DataFrame(full_sim, index=row_names, columns=row_names)

    full_sim.to_csv(out_file, sep="\t")

if __name__ == "__main__":
    sys.exit(main())