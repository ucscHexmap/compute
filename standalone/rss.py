"""
Reciprocal significance of similarity (RSS) method as described in supplemental
section of tumormap paper.

Input is tab separated similarity matrix, symmetry is assumed.
Output is tab separated similarity matrix, symmetry is enforced.

Notes:
    Excludes the inputs diagonal so self similarities do not influence the
    z-scores going into RSS.

Example usage:
    rss.py -i path/to/full_similarity/matrix -o path/to/output/filename
"""

import argparse
import sys
import pandas as pd
import numpy as np
from itertools import combinations as combo

def parse_args():

    parser = argparse.ArgumentParser(description= __doc__,
                 formatter_class=argparse.RawDescriptionHelpFormatter,
                                    )

    parser.add_argument(
                        '-i','--fin',
                        help='''path of tab delimited similarity matrix''',
                        type=str,
                       )

    parser.add_argument(
                        '-o','--fout',
                        help='''name of tab output file''',
                        type=str,
                        default='youDidntNameRSS.tab'
                       )

    args = parser.parse_args()

    return args


def rss(simdf):
    """
    Produces an RSS matrix from a similarity matrix.
    :param simdf (pandas dataframe): A symmetric similarity matrix.
    :return (pandas dataframe): A symmetric RSS matrix.
    """
    # Fill diagonal with Na so that self similarity is not included in
    # distribution.
    np.fill_diagonal(simdf.values, np.NAN)

    # Gather mean and standard deviations of each objects similarities.
    mus = simdf.mean()
    stds = simdf.std()

    # Initialize matrix and fill diagonals with NAN.
    rssmat = np.zeros((simdf.shape[0],simdf.shape[1]),np.float)
    np.fill_diagonal(rssmat,np.NAN)

    # Loop over combos of object i, j in similarity matrix
    # and calculate individual RSS values. Assume symmetry.
    for i, j in combo(range(len(simdf.columns)), 2):
        sim_value = simdf.iloc[i, j]
        # Averages the zscore from perspective of i and j.
        rss_value = .5*(( (sim_value - mus.iloc[i]) / stds.iloc[i])\
                    + ( (sim_value - mus.iloc[j]) / stds.iloc[j]))
        # Enforces symmetry.
        rssmat[i,j] = rss_value
        rssmat[j,i] = rss_value

    rssdf = pd.DataFrame(rssmat, columns=simdf.columns, index=simdf.index)
    return rssdf

def main():

    args = parse_args()
    fin = args.fin
    fout = args.fout

    # Read input.
    simdf = pd.read_table(fin, index_col=0)

    # Calculate rss.
    rssdf = rss(simdf)

    # Dump output.
    rssdf.to_csv(fout, sep='\t')

if __name__ == "__main__":
    sys.exit(main())
