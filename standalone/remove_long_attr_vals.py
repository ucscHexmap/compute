#!/usr/bin/env python2.7
"""
remove_long_attr_vals.py

Example: find_long_attr_vals.py attrIn.tab attrOut.tab 200

Removes any attributes with less than so many values.
"""

import sys, argparse, csv, traceback

def parse_args(args):
    args = args[1:]
    parser = argparse.ArgumentParser(description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("inputFile", type=str, help="input file")
    parser.add_argument("outputFile", type=str, help="output file")
    parser.add_argument("threshold", type=int,
        help="threshold for number of chars in a value")
    a = parser.parse_args(args)
    return a

def main(opt):

    print 'processing:', opt.inputFile, '...'
    attrNames = []
    
    # Find the categories for each categorical attribute.
    with open(opt.inputFile, 'rU') as fin:
        fin = csv.reader(fin, delimiter='\t')
        attrNames = fin.next()
        longValAttrs = []
        lengths = []
        for row in fin:
            for j, val in enumerate(row):
                
                # Only consider non-null values
                if val != None:
                
                    # Only consider strings
                    try:
                        float(val)
                    except:
                        if len(val) > opt.threshold:
                            if attrNames[j] not in longValAttrs:
                                longValAttrs.append(attrNames[j])
                                lengths.append(len(val))
                            elif lengths:
                                i = longValAttrs.index(attrNames[j])
                                if len(val) > lengths[i]:
                                    lengths[i] = len(val)

    print 'attrs with values longer than', opt.threshold, ':'
    print longValAttrs
    print 'lengths:', lengths
    
    # Write out the attributes with values that are under the threshold
    with open(opt.inputFile, 'rU') as fin:
        fin = csv.reader(fin, delimiter='\t')
        with open(opt.outputFile, 'w') as fout:
            fout = csv.writer(fout, delimiter='\t', lineterminator='\n')
            for i, row in enumerate(fin.__iter__()):
                good = []
                for j, val in enumerate(row):
                
                    # Write out the first column and any good columns.
                    attrName = attrNames[j]
                    
                    if j == 0 or attrName not in longValAttrs:
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

