#!/usr/bin/env python2.7
"""
transform_attr_list_to_binary.py

Example: transform_attr_list_to_binary.py clusterList.tab clusterBinary.tab cluster_Henry

Where the parameters are inputFile, outputFile, attributeName

Converts attributes of this form:
    c1	s1  s2
    c2	s3

To this format:
        cluster_Henry
    s1  c1
    s2  c1
    s3  c2
"""

import sys, argparse, csv, traceback
from array import *

def parse_args(args):
    args = args[1:]
    parser = argparse.ArgumentParser(description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("inputFile", type=str, help="input file")
    parser.add_argument("outputFile", type=str, help="output file")
    parser.add_argument("name", type=str, help="name to give the attribute")
    a = parser.parse_args(args)
    return a

def main(opt):

    print 'processing:', opt.inputFile, '...'

    # Read the data.
    with open(opt.inputFile, 'rU') as fin:
        fin = csv.reader(fin, delimiter='\t')
        cats = ['']
        nodes = ['']
        for row in fin:
            cats.append(row[0])
            nodes.append(row[1:])
    
    # Write the new format of the data.
    with open(opt.outputFile, 'w') as fout:
        fout = csv.writer(fout, delimiter='\t', lineterminator='\n')
        fout.writerow([None, opt.name])
        for i, catNodes in enumerate(nodes[1:]):
            for j, node in enumerate(catNodes):
                fout.writerow([node, cats[i+1]])

    return 0

if __name__ == "__main__" :
    try:
        return_code = main(parse_args(sys.argv))
    except:
        traceback.print_exc()
        return_code = 1
    sys.exit(return_code)

