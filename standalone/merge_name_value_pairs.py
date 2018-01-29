#!/usr/bin/env python2.7
"""
merge_name_value_pairs.py

Merge two or more files containing name-value pairs with identical names.

Example:
merge_name_value_pairs.py \
    --inFile sd01.log2 \
    --inFile sd02.log2 \
    --inFile sd03.log2 \
    --inFile sd04.log2 \
    --inFile sd05.log2 \
    --inFile sd06.log2 \
    --inFile sd07.log2 \
    --inFile sd08.log2 \
    --inFile sd09.log2 \
    --inFile sd10.log2 \
    --outFile expression.tsv

"""

import sys, argparse, csv, traceback

def parse_args(args):
    args = args[1:]
    parser = argparse.ArgumentParser(description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--inFile", action='append', help="input file")
    parser.add_argument("--outFile", type=str, help="output file")
    a = parser.parse_args(args)
    return a

def main(opt):
    matrix = []
    csv.register_dialect('newLineAndTab', delimiter='\t', lineterminator='\n')
    
    # Load the first file.
    inFile = opt.inFile[0]
    print 'processing:', inFile
    with open(inFile, 'rU') as fin:
        fin = csv.reader(fin, dialect='newLineAndTab')
        for row in fin:
            matrix.append(row)

    # Load the rest of the files.
    j = 2
    for inFile in opt.inFile[1:]:
        with open(inFile, 'rU') as fin:
            fin = csv.reader(fin, dialect='newLineAndTab')
            print 'processing:', inFile
            i = 0
            for row in fin:
                matrix[i].append(row[1])
                i += 1
        j += 1
        
    # Write out the merged file.
    with open(opt.outFile, 'w') as fout:
        fout = csv.writer(fout, dialect='newLineAndTab')
        i = 0
        for row in matrix:
            fout.writerow(row)
            i += 1

    return 0

if __name__ == "__main__" :
    try:
        return_code = main(parse_args(sys.argv))
    except:
        traceback.print_exc()
        return_code = 1
    sys.exit(return_code)

