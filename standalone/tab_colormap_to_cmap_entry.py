"""
Takes in a two column (tab sep) file and produces the format expected
when reading colormaps.tab files.

e.g. a file (color.file) like this may be inputed:
AttrId  hexCode
a   #382894
b   #425454

producing a file (single_colormap.tab) with a single line:

Attrid 0 a #382894 1 b #425454

by calling this script like this

python2.7 tab_colormap_cmap_entry.py -i color.file -o single_colormap.tab

You can then cat that onto an existing colormap
e.g.
cat colormaps.tab single_colormap.tab > colormaps.tab
"""

import argparse
import sys

def parse_args():

    parser = argparse.ArgumentParser(description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument('-i',"--in_file", type=str, help=""
                        )

    parser.add_argument('-o',"--out_file", type=str, help="",
                        default="single_colormap.tab"
                        )

    return parser.parse_args()


def main():

    opts = parse_args()

    in_file = opts.in_file
    out_file = opts.out_file
    out = []

    with open(out_file, "w") as fout:
        with open(in_file, "r") as fin:
            for i, line in enumerate(fin):
                line_arr = line.strip().split("\t")
                if i == 0:
                    out.append(line_arr[0])
                else:
                    out.append(str(i-1))
                    out.append(line_arr[0])
                    out.append(line_arr[1])


        fout.write("\t".join(out) + "\n")

if __name__ == "__main__":
    sys.exit(main())