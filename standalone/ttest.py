#!/usr/bin/env python2.7
"""
A script for conducting t-tests on a tab separated matrix.
Input is a single column list of sample identifiers
Output is a two column matrix with t-statistics and corrected
p-values as columns.
"""
import scipy.stats
import statsmodels.sandbox.stats.multicomp as correct
import pandas as pd
import numpy as np
import sys
import argparse

def parse_args():

    parser = argparse.ArgumentParser(description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument('-i', "--input", type=str,
                        help="File path to feature X sample tab separated "
                             "matrix"
    )
    parser.add_argument('-s', "--samples", type=str,
                        help="a single column list of sample identifiers",
                        required=True
    )

    parser.add_argument("-b","--background", type=str,
                        help="An optional single coloumn list of sample identifiers",
                        default=None
    )
    parser.add_argument("-v", "--equal_variance", type=bool,
                        help="A flag for whether or not equal variance of "
                             "samples and background is assumed.",
                        default=False
    )
    parser.add_argument('-o', "--fout", type=str,
        help="output file path, two column tab delimited matrix",
        default="ttestOut.tab"
    )

    return parser.parse_args()


def main():

    args = parse_args()

    #grab relavent args
    samples_file = args.samples
    background_file = args.background
    equal_variance = args.equal_variance

    fin = args.input
    fout = args.fout

    #read in the matrices as pandas dfs
    data_table = pd.read_csv(fin, index_col=0, sep="\t")

    samples = pd.read_csv(samples_file, index_col=0, sep="\t")
    sample_table = data_table[samples.index]

    # If the user provided a background list
    if background_file is not None:
        background = pd.read_csv(background_file, index_col=0, sep="\t")
        background_table = data_table[background.index]
    else:
        background_table = data_table



    # Compute the t-tests of each rows
    ttest = scipy.stats.ttest_ind(sample_table,
                                  background_table,
                                  axis=1, # Row-wise
                                  equal_var=equal_variance
                                  )
    # Grab the t-statistics
    tstats = ttest.statistic

    # Calculate corrected pvalues
    corrected = correct.multipletests(ttest.pvalue,method='bonferroni')[1]
    corrected[corrected == 0] = sys.float_info.min
    corrected = -np.log(corrected)

    # Make a return pandas dataframe
    retDF = pd.DataFrame({"tstats" : tstats,
                          "-log corrected Pvalue" :corrected},
                          index=data_table.index)

    #sort the by the values of tstatistics and then print them to output file.
    retDF.sort_values("tstats").to_csv(fout, sep='\t')

if __name__ == "__main__":
    sys.exit(main())