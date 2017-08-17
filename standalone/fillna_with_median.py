"""
Fills a tab separated matrix missing values with the median of the columns
(or rows as specified in CLI args).
"""

import argparse
import sys
from utils import readPandas

def parse_args():

    parser = argparse.ArgumentParser(description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument('-i',"--in_file", type=str, help="")

    parser.add_argument('-o',"--out_file", type=str,help="",
                        default="naToMedian.tab")

    parser.add_argument("--rows", action="store_true",
        help="will take row wise similarity instead of columns")

    return parser.parse_args()

def main():
    opts = parse_args()

    in_file = opts.in_file
    out_file = opts.out_file

    df = readPandas(in_file)

    if opts.rows: # Row-wise fill requested.
        df = df.transpose()

    # Fill the Na's with the Median (column wise)
    df= df.apply(lambda x: x.fillna(x.median()),axis=0)

    if opts.rows: # Return to same orientation
        df = df.transpose()

    df.to_csv(out_file, sep="\t")

if __name__ == "__main__":
    sys.exit(main())