#!/usr/bin/env python2.7
"""
find_dup_attr_nodes.py

Example: find_dup_attr_nodes.py attr.tab dupNodes.tab dupRows.tab

Find any entries with the node ID in more than one entry,
and find any entries that are totally duplicated.

"""

import sys, argparse, csv, traceback
from collections import Counter

def parse_args(args):
    args = args[1:]
    parser = argparse.ArgumentParser(description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("inputFile", type=str, help="input filename")
    parser.add_argument("dupNodesFile", type=str, help="duplicate nodes filename")
    parser.add_argument("dupRowsFile", type=str, help="duplicate rows filename")
    a = parser.parse_args(args)
    return a

def main(opt):

    print 'processing:', opt.inputFile, '...'

    dups = []
    with open(opt.inputFile, 'rU') as fin:
        fin = csv.reader(fin, delimiter='\t')
        with open(opt.dupNodesFile, 'w') as fout:
            fout = csv.writer(fout, delimiter='\t')
            with open(opt.dupRowsFile, 'w') as fout2:
                fout2 = csv.writer(fout2, delimiter='\t')
                rows = list(fin)
                rows.sort()
                prevNode = rows[0][0]
                prevRow = rows[0]
                secondRow = True
                for row in rows[1:]:
                    if row[0] == prevNode:
                        fout.writerow(prevRow)
                        fout.writerow(row)
                        if row == prevRow:
                            fout2.writerow(prevRow)
                            fout2.writerow(row)
                    else:
                        prevNode = row[0]
                        prevRow = row
                    secondRow = False

    return 0

if __name__ == "__main__" :
    try:
        return_code = main(parse_args(sys.argv))
    except:
        traceback.print_exc()
        return_code = 1
    sys.exit(return_code)

