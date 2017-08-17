"""
Simple conversion from tab separated matrix to hdf format (faster read-write).
"""

import argparse
import sys
from utils import readPandas

def parse_args():

    parser = argparse.ArgumentParser(description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument('-i',"--in_file", type=str, help="")

    parser.add_argument('-o',"--out_file", type=str,help="",
                        default="didntName.hdf5")

    return parser.parse_args()

def main():
    opts = parse_args()

    in_file = opts.in_file
    out_file = opts.out_file

    df = readPandas(in_file)

    df.to_hdf5(out_file)

if __name__ == "__main__":
    sys.exit(main())