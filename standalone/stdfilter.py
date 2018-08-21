#!/usr/bin/env python2.7
'''
Reduce features of a matrix with a standard deviation filter.
Input is a samples x feature tab delimited matrix.

Example:
stdfilter.py -i input.tab -o filtered.tab

where 'input.tab' is a samples x feature tab delimited matrix.
where 'filtered.tab' is a samples x feature tab delimited matrix
with only genes higher than the 75th percentile.
'''


import pandas as pd
import numpy as np
import argparse
import sys

def parse_args():

    parser = argparse.ArgumentParser(description= __doc__,
                 formatter_class=argparse.RawDescriptionHelpFormatter,
                                    )
    parser.add_argument(
                        '-i','--fin',
                        help='''input matrix file''',
                        type=str
                       )
    parser.add_argument(
                        '-o','--fout',
                        help='''name of output file''',
                        type=str,
                        default='out.tab'
                       )
    parser.add_argument(
                        '-p','--percentile',
                        help='''rows with std greater than this percentile will be kept.
                        float range [0, 100]''',
                        type=float,
                        default=75
                       )
    parser.add_argument(
                        '-d','--sep',
                        help='''separator or delimiter for file''',
                        type=str,
                        default='\t'
                       )

    args = parser.parse_args()

    return args.fin, args.fout, args.percentile, args.sep


def main():

    fin, fout, percentile, sep = parse_args()
    df = pd.read_csv(file=fin, index_col=0, sep=sep)
    stds = df.std()
    df = df[stds > np.percentile(df.std(), q=percentile)]
    df.to_csv(fout, sep=sep)


if __name__ == "__main__":
    sys.exit(main())
