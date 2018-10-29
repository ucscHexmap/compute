
# Administrative CLI for the cell databases.

# Before running this be sure to
# source $HEXCALC/ops/config.sh

import os, argparse, sys
import appContext

operations = [
    'addClusters',
    'getAllClusters',
    'addClusterAttrs',
    'getAllClusterAttrs',
    'addDatasets',
    'getAllDatasets',
    'addSampleAttrs',
    'getAllSampleAttrs',
    'addTrajectories',
    'getAllTrajectories',
]

dbFileName = 'cell.db'


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


def add(inFile, table, appCtx, replace=False):
    if replace:

        # When testing we don't ask the 'are you sure' question.
        if appCtx.unitTest or yesNo(
            'Do you want to complete destroy the table content?'):

            table.deleteAll()
        else:
            print('Table left untouched')
            exit

    table.addManyFromFile(inFile)


def getAll(table, appCtx):
    r = table.getAll()
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
    cellDbInit.init(appCtx)

    # Get the handles to all of the tables.
    cluster = cellDbInit.Cluster()
    clusterAttr = cellDbInit.ClusterAttr()
    dataset = cellDbInit.Dataset()
    sampleAttr = cellDbInit.SampleAttr()
    trajectory = cellDbInit.Trajectory()

    if op == 'addClusters': add(inFile, cluster, appCtx, replace)
    elif op == 'getAllClusters': getAll(appCtx, cluster)

    elif op == 'addClusterAttrs': add(inFile, clusterAttr, appCtx, replace)
    elif op == 'getAllClusterAttrs': getAll(appCtx, clusterAttr)

    elif op == 'addDatasets': add(inFile, dataset, appCtx, replace)
    elif op == 'getAllDatasets': getAll(appCtx, dataset)

    elif op == 'addSampleAttrs': add(inFile, sampleAttr, appCtx, replace)
    elif op == 'getAllSampleAttrs': getAll(appCtx, sampleAttr)

    elif op == 'addTrajectories': add(inFile, trajectory, appCtx, replace)
    elif op == 'getAllTrajectories': getAll(appCtx, trajectory)


if __name__ == '__main__':
    sys.exit(main())