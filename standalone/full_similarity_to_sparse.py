"""
This script creates an edge file ("sparse similarity matrix") from a
full similarity matrix.

usage examples:

    # Note: requires calc/utils.py and calc/compute_sparse_matrix.py to
    #be in your $PYTHONPATH

    # Defaults to top 6 neighbors.
    full_similarity_to_sparse.py -i full_sim.tab -o sparse6_sim.tab

    # Top 10 neighbors.
    full_similarity_to_sparse.py -i full_sim.tab -o sparse10.tab -t 10

    # Percentile cutoff (varying number of edges per node).
    full_similarity_to_sparse.py -i full_sim.tab -o sparse6-percentile.tab -p

Without the --percentile flag, the script will create the edge file
format for the --top nearest neighbors.

The --percentile flag allows for varying numbers of neighbors per
node, by including edges  > than a percentile threshold 
calculated from the given --top parameter. Calculating the percentile
through top lets the user intuitively control the amount of edges 
included in the sparse format. The upper bound for
number of edges using the --percentile flag == --top * n_nodes.


For example if --top 10 --percentile was chosen on 200 nodes, then
2000 edges would be included but those edges would be in the >95%
(1 -(10*200 / 200*200)) of edge values. Note with --percentile it is 
possible to have a node excluded from the sparse format if there
are no similarities passing the determined cutoff.

Author: Duncan McColl dmccoll@ucsc.edu
"""
import argparse
import sys
from utils import readPandas
from utils import duplicate_columns_check
from compute_sparse_matrix import percentile_sparsify
from compute_sparse_matrix import extract_similarities


def parse_args():

    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        '-i', "--in_file", type=str,
        help="""Path to full similarity tab delimited file."""
    )

    parser.add_argument(
        '-o',"--out_file", type=str,
        help="""Path/Name of the output file. Defaults to
        './sparseSimilarity.tab'""",
        default="sparseSimilarity.tab"
    )

    parser.add_argument(
        '-t',"--top", type=int,
        help="""Number of nearest neighbors. Defaults to 6.""",
        default=6
    )

    parser.add_argument(
        '-p',"--percentile", action="store_true",
        help="""Flag for whether to use percentile cut off.
        This allows for a varying number of edges per node,
        which may be 0 depending on the similarity values. See
        doc string for more details.""",
        default=False
    )

    return parser.parse_args()


def main():
    # Gather the args.
    opts = parse_args()
    in_file = opts.in_file
    out_file = opts.out_file
    n_neighbors = opts.top
    doing_percentile = opts.percentile

    # Read in data and guard against cause of funky error.
    full_similarity = readPandas(in_file)
    duplicate_columns_check(full_similarity)

    # Make the sparse similarity representation.
    if doing_percentile:
        sparse_sim = percentile_sparsify(full_similarity, n_neighbors)
    else:  # Using top X nearest neighbors.
        sparse_sim = extract_similarities(
            full_similarity.values,
            full_similarity.columns.tolist(),
            n_neighbors
        )

    # Write out the sparse similarity representation.
    sparse_sim.to_csv(out_file, sep="\t", header=None, index=False)

if __name__ == "__main__":
    sys.exit(main())
