"""
Input a tab separated matrix and outputs the same matrix but removing
columns (or rows) having a standard deviation of 0.
"""

import argparse
import sys
from utils import readPandas

def parse_args():

    parser = argparse.ArgumentParser(description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument('-i',"--in_file", type=str, help="")

    parser.add_argument('-o',"--out_file", type=str,help="",
                        default="stdRemoved.tab")

    parser.add_argument("--rows", action="store_true",
        help="will take row wise similarity instead of columns")

    return parser.parse_args()

def main():
    opts = parse_args()

    in_file = opts.in_file
    out_file = opts.out_file

    df = readPandas(in_file)

    if not opts.rows: # Col-wise fill requested.
        df = df.transpose()

    # Keep rows that have a std that isn't 0
    df = df.loc[(df.std(axis=1) != 0)]

    if not opts.rows: # Return to same orientation
        df = df.transpose()

    df.to_csv(out_file, sep="\t")

if __name__ == "__main__":
    sys.exit(main())