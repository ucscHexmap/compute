#!/usr/bin/env python2.7
"""
remove_attr_lots_categories.py

Example: remove_attr_lots_categories.py attrIn.tab attrOut.tab 60

Removes any attributes with less than so many values.
"""

import sys, argparse, csv, traceback

def parse_args(args):
    args = args[1:]
    parser = argparse.ArgumentParser(description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("inputFile", type=str, help="input file")
    parser.add_argument("outputFile", type=str, help="output file")
    parser.add_argument("threshold", type=int, help="threshold for dropping attribute")
    a = parser.parse_args(args)
    return a

def main(opt):

    print 'processing:', opt.inputFile, '...'
    attrNames = []
    
    # Find the categories for each categorical attribute.
    with open(opt.inputFile, 'rU') as fin:
        fin = csv.reader(fin, delimiter='\t')
        attrNames = fin.next()
        cats = [[] for j in range(0, len(attrNames))]
        for row in fin:
            for j, val in enumerate(row):
                
                # Only consider non-null values
                if val != None:
                
                    # Only consider strings
                    try:
                        float(val)
                    except:
                        if not val in cats[j]:
                            cats[j].append(val)

    # Write out the attributes that are under the threshold
    with open(opt.inputFile, 'rU') as fin:
        fin = csv.reader(fin, delimiter='\t')
        with open(opt.outputFile, 'w') as fout:
            fout = csv.writer(fout, delimiter='\t', lineterminator='\n')
            print 'dropped attributes with more than', opt.threshold, 'categories'
            for i, row in enumerate(fin.__iter__()):
                good = []
                for j, val in enumerate(row):
                
                    # Write out the first column and any good columns.
                    if j == 0 or (len(cats[j]) <= opt.threshold):
                        good.append(val)
            
                fout.writerow(good)

    return 0

if __name__ == "__main__" :
    try:
        return_code = main(parse_args(sys.argv))
    except:
        traceback.print_exc()
        return_code = 1
    sys.exit(return_code)

