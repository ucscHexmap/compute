#!/usr/bin/env python2.7
"""
Script to order the category ids of pre-existing colormaps files alphabetically.
"""

from process_categoricals import *
import argparse


def parse_args(args):

    parser = argparse.ArgumentParser(description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument('-c',"--colormaps", type=str,
                        help="path to a previously generated colormapping file",
                        )

    parser.add_argument('-o',"--out_file", type=str,
                        help="ordered colormap",
                        default="colormaps_ordered.tab"
                        )

    return parser.parse_args(args)


def main(args):
    opts = parse_args(args)
    cmapfile = opts.colormaps
    fout = opts.out_file
    colormaps = read_colormaps(cmapfile)
    colormaps = order_catids_alphabetically(colormaps)
    write_colormaps(fout, colormaps)

if __name__ == "__main__" :
    main(sys.argv[1:])