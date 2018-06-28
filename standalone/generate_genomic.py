#!/usr/bin/env python2.7
"""
generate_genomic.py

Generate genomic data from existing data by replicating the existing data and
giving new node IDs. reps must be < 10.

Example:
generate_genomic.py
    --reps 5
    --inFile pca50.tab
    --outFile pca50test.tab
"""

import sys, argparse, csv, traceback

def parse_args(args):
    args = args[1:]
    parser = argparse.ArgumentParser(description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--reps", type=int, help="input file")
    parser.add_argument("--inFile", type=str, help="input file")
    parser.add_argument("--outFile", type=str, help="output file")
    a = parser.parse_args(args)
    return a

def main(opt):
    matrix = []
    csv.register_dialect('newLineAndTab', delimiter='\t', lineterminator='\n')

    # Load the file and write out repeats of each node ID.
    inFile = opt.inFile
    print 'processing:', inFile
    with open(inFile, 'rU') as fin:
        fin = csv.reader(fin, dialect='newLineAndTab')
        with open(opt.outFile, 'w') as fout:
            fout = csv.writer(fout, dialect='newLineAndTab')
            head = fin.next()
            fout.writerow(head)
            for row in fin:
                x = row[0] + str(0)
                row[0] = x
                for i in range(opt.reps):
                    fout.writerow(row)
                    x = row[0][:-1] + str(i+1)
                    row[0] = x
    return 0

if __name__ == "__main__" :
    try:
        return_code = main(parse_args(sys.argv))
    except:
        traceback.print_exc()
        return_code = 1
    sys.exit(return_code)

