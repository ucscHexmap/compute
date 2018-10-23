
# Initialize the application context.

import os
from util_web import getAppCtx


# Set up the application context.
def init ():
    appCtx = getAppCtx()
    appCtx.adminEmail = os.environ.get('ADMIN_EMAIL')
    appCtx.dataRoot = os.environ.get('DATA_ROOT', 'DATA_ROOT_ENV_VAR_MISSING')
    appCtx.debug = os.environ.get('DEBUG', 0)
    appCtx.dev = int(os.environ.get('DEV', 0))
    appCtx.hubPath = os.environ.get('HEXCALC')
    appCtx.unitTest = int(os.environ.get('UNIT_TEST', 0))
    appCtx.viewServer = os.environ.get('VIEWER_URL', 'https://tumormap.ucsc.edu')
    appCtx.viewServerAddrs = os.environ.get('VIEW_SERVER_ADDRS', '127.0.0.1')

    # Derived context.
    appCtx.databasePath = \
        os.environ.get('DATABASE_PATH', appCtx.hubPath + '/../computeDb')
    appCtx.jobQueuePath = os.path.abspath(
        os.path.join(appCtx.databasePath, 'jobQueue.db'))
    appCtx.jobProcessPath = appCtx.hubPath + '/www/job/jobProcess.py'
    appCtx.viewDir = os.path.join(appCtx.dataRoot, 'view')
    url = os.environ['DATA_HOST_PORT']
    #url = os.environ['WWW_SOCKET']

    if os.environ['USE_HTTPS'] == '1':
        appCtx.dataServer = 'https://' + url
    else:
        appCtx.dataServer = 'http://' + url
    appCtx.jobStatusUrl = appCtx.dataServer + '/jobStatus/jobId/'
    return appCtx

