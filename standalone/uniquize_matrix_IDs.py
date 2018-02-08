#!/usr/bin/env python

# Usage:
# uniquize_matrix_ids.py <input-filename>

# Given a matrix file with IDs in the first row and first column, make those IDs
# unique by adding a number to each nonunique element. Two new files are
# written: one with unique IDs and original values, and one with the duplicates
# IDs, not including the original ID of the duplicates.
# These files are named <input-filename>_noDups and <input-file>_dupIds
#
# Note that the output file will have line terminators of '\n' regardless of
# the line terminators in the original file.

import sys, csv, argparse, traceback
from uniquize_IDs import make_unique

def parse_args(args):
    args = args[1:]
    parser = argparse.ArgumentParser(description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("inputFile", type=str, help="input filename")
    a = parser.parse_args(args)
    return a

def main(opts):
    inFile = opts.inputFile
    uniqFile = inFile + '_noDups'
    dupFile = inFile + '_dupIds'
    colUniqs = colDups = rowUniqs = rowDups = []
    csv.register_dialect('newLineAndTab', delimiter='\t', lineterminator='\n')

    with open(inFile, 'rU') as fin:
        
        # Get the column IDs and make them unique.
        fin = csv.reader(fin, dialect='newLineAndTab')
        colNames = fin.next()
        colUniqs, colDups = make_unique(colNames)
        
        # Get the row IDs and make them unique.
        rowNames = []
        for row in fin:
            rowNames.append(row[0])
        rowUniqs, rowDups = make_unique(rowNames)
        
    # Write out the data with the new IDs.
    with open(inFile, 'rU') as fin:
        fin = csv.reader(fin, dialect='newLineAndTab')
        with open(uniqFile, 'w') as fout:
            fout = csv.writer(fout, dialect='newLineAndTab')
            
            # Write the column IDs.
            fout.writerow(colUniqs)
            
            # Write out all the data rows with the new row IDs.
            i = 0
            fin.next()
            
            for row in fin:
                fout.writerow([rowUniqs[i]] + row[1:])
                i += 1

    # Write out all of the duplicates.
    with open(dupFile, 'w') as fout2:
        for id in (colDups + rowDups):
            fout2.write(id + '\n')

    print 'duplicate column IDs renamed:'
    for id in colDups:
        print id
    print 'duplicate row IDs renamed:'
    for id in rowDups:
        print id
    print 'Number of columns:', len(colNames)


if __name__ == "__main__" :
    try:
        return_code = main(parse_args(sys.argv))
    except:
        traceback.print_exc()
        return_code = 1
    sys.exit(return_code)

