#!/usr/bin/env python2.7
"""
transform_to_log2(x+1).py

Example:
transform_to_log2(x+1).py expression.tab expressionLog2(x+1).tab

In a matrix file, replace all numeric values with log2(x+1). This assumes the
first row and first column contain labels.
"""

import sys, argparse, csv, traceback, math

def parse_args(args):
    args = args[1:]
    parser = argparse.ArgumentParser(description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("input_file", type=str, help="input file")
    parser.add_argument("output_file", type=str, help="output file")
    a = parser.parse_args(args)
    return a

def main(opt):

    print 'processing:', opt.input_file
    
    with open(opt.input_file, 'rU') as fin:
        with open(opt.output_file, 'w') as fout:
            fin = csv.reader(fin, delimiter='\t')
            fout = csv.writer(fout, delimiter='\t')
            
            # Write out the header row
            fout.writerow(fin.next())
            
            for row in fin:
                outRow = [row[0]]
                for val in row[1:]:
                    logVal = math.log(float(val) + 1, 2)
                    outRow.append(logVal)
                    
                fout.writerow(outRow)

    print 'done'

    return 0

if __name__ == "__main__" :
    try:
        return_code = main(parse_args(sys.argv))
    except:
        traceback.print_exc()
        return_code = 1
    sys.exit(return_code)

