#!/usr/bin/env python2.7
"""
nor_neg_xy.py

Example:
    norm_neg_xy.py --filename xyfile.tab --outFilename xyNormFile.tab \
    --xmin -0.9 --ymin -0.4 --skipFirstLine
Returns: the normalized file as <filename>.normalized.tab

From an XY positions file with some negative coordinates, normalize to
positive coordinates.

"""

import sys, argparse, csv, traceback

CODES = True

def parse_args(args):
    args = args[1:]
    
    parser = argparse.ArgumentParser(description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument("--filename", type=str, help="file to be normalized")
    parser.add_argument("--outFilename", type=str, help="normalized filename")
    parser.add_argument("--xmin", type=float,
        help="minium X to add to each X value")
    parser.add_argument("--ymin", type=float,
        help="minium Y to add to each Y value")
    parser.add_argument("--skipFirstLine", action="store_true", default=False,
        help="minium Y to add to each Y value")
    
    a = parser.parse_args(args)
    return a

def get_xlate(row):
    i = 1
    code = 0
    xlate = []
    while True:
        try:
            j = int(row[i])
            str = row[i+1]
            xlate.insert(j, str)
            i += 3
        except:
            break;

    return xlate

def main(opt):

    filename = opt.filename
    outFilename = opt.outFilename
    xmin = opt.xmin
    ymin = opt.ymin
    outFilename = opt.outFilename
    skipFirstLine = opt.skipFirstLine
    
    print 'normalizing:', filename
    
    
    with open(filename, 'rU') as fin:
        with open(outFilename, 'w') as fout:
        
            fin = csv.reader(fin, delimiter='\t')
            fout = csv.writer(fout, delimiter='\t')

            firstLine = True
            for row in fin:
            
                if skipFirstLine and firstLine:
                    firstLine = False
                    continue
                
                fout.writerow([row[0], float(row[1]) - xmin,
                    float(row[2]) - ymin])

    print 'done and written to:', outFilename

    return 0

if __name__ == "__main__" :
    try:
        return_code = main(parse_args(sys.argv))
    except:
        traceback.print_exc()
        return_code = 1
    sys.exit(return_code)

