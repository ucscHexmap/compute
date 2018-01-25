#!/usr/bin/env python2.7
"""
replace_NA_attribute_values_with_none.py

Example: replace_NA_attribute_values_with_none.py meta.cleaned.tab meta_no_NA.tab

In an attribute file, replace all NA with None.
"""

import sys, argparse, csv, traceback

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
    
    # Drop any nulls or values used to indicate no value.
    NAs = ['', '#N/A', 'N/A', '#NA', 'NA', 'NAN', '-NAN']
    
    with open(opt.input_file, 'rU') as fin:
        with open(opt.output_file, 'w') as fout:
            fin = csv.reader(fin, delimiter='\t')
            fout = csv.writer(fout, delimiter='\t')
            
            first = True
            
            for row in fin:
            
                if first:
                
                    # write the header as is
                    fout.writerow(row)
                    first = False
                    continue
                
                outRow = []
                for value in row:
                    val = str(value).strip()
                    val = val.upper()
                    if val in NAs:
                        value = None
                    outRow.append(value)
                    
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

