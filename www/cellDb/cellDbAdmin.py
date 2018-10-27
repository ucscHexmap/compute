
# Administrative CLI for the cell databases.

# Before running this be sure to
# source $HEXCALC/ops/config.sh

import argparse, sys
import appContext
import cellDataset as dataset

operations = [
    'addDatasets',
    'getAllDatasets',
]


def parse_args():

    parser = argparse.ArgumentParser(description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument('operation',
        type=str, 
        help='one of: ' + str(operations),
        default=''
    )
    parser.add_argument('-i','--inFile',
        type=str
    )
    parser.add_argument('-o','--outFile',
        type=str
    )
    parser.add_argument('--replace',
        type=bool,
        default=False
    )

    return parser.parse_args()


def yesNo(question):

    # Ask a yes/no question, defaults to 'no'
    print(question + '[yes/NO]')
    choice = raw_input().lower()
    if choice.lower() == 'yes':
        return True
    else:
        return False


def addDatasets(inFile, appCtx, replace=False):
    if replace:

        # When testing we don't ask the 'are you sure' question.
        if appCtx.unitTest or yesNo(
            'Do you want to complete destroy the datasets database content?'):

            dataset.deleteAll(appCtx)
        else:
            print('Datasets database left untouched')
            exit

    dataset.addManyFromFile(inFile, appCtx)


def getAllDatasets(appCtx):
    r = dataset.getAll(appCtx)
    if not appCtx.unitTest:
        print r
    return r


def main():
    print 'If you have any errors, did you "source $HEXCALC/ops/config.sh" ?'

    opts = parse_args()

    op = opts.operation
    inFile = opts.inFile
    replace = opts.replace

    # Get the global application context
    global appCtx
    appCtx = appContext.init()

    if op == 'addDatasets': addDatasets(inFile, appCtx, replace)
    elif op == 'getAllDatasets': getDatasets(appCtx)


if __name__ == '__main__':
    sys.exit(main())