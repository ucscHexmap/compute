#!/usr/bin/env python2.7
"""
remove_attr_data_not_in_node_list.py

Example: remove_attr_data_not_in_node_list.py attr.tab nodeList cleanAttr.tab

Removes rows of attribute data that do not have nodes in the node list.
"""

import sys, argparse, csv, traceback

def parse_args(args):
    args = args[1:]
    parser = argparse.ArgumentParser(description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("inputFile", type=str, help="input filename")
    parser.add_argument("nodeFile", type=str, help="node list filename")
    parser.add_argument("outputFile", type=str, help="output filename")
    a = parser.parse_args(args)
    return a

def main(opt):

    print 'processing:', opt.inputFile, 'with', opt.nodeFile, '...'

    # Read in the node list.
    nodes = []
    with open(opt.nodeFile, 'rU') as fin:
        for row in fin:
            if not row == '\n':
                nodes.append(row[:-1])

    print '1len(nodes):', len(nodes)
    print 'nodes[0]:', nodes[0]

    # Remove any duplicate nodes.
    nodes = set(nodes)

    print '2len(nodes):', len(nodes)

    # For each line in the attr file, write it out to the new file if its
    # node is in the node list.
    with open(opt.inputFile, 'rU') as fin:
        fin = csv.reader(fin, delimiter='\t')
        with open(opt.outputFile, 'w') as fout:
            fout = csv.writer(fout, delimiter='\t')
            for row in fin:
                if row[0] in nodes:
                    fout.writerow(row)

    return 0

if __name__ == "__main__" :
    try:
        return_code = main(parse_args(sys.argv))
    except:
        traceback.print_exc()
        return_code = 1
    sys.exit(return_code)

