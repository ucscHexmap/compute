
import os, json, csv, traceback, requests, logging, pprint, importlib
import tempfile
import smtplib
from email.mime.text import MIMEText


class SuccessResp (Exception):

    # Define a success response class which converts to json.
    def __init__(self, data):
        Exception.__init__(self)
        self.data = data

class SuccessRespNoJson (Exception):

    # Define a success response class which does not convert to json.
    def __init__(self, data):
        Exception.__init__(self)
        self.data = data

class ErrorResp (Exception):

    # Define an error response class
    DEFAULT_STATUS = 400 # default to 'invalid usage'

    def __init__(self,
                 message,
                 status_code=DEFAULT_STATUS):

        Exception.__init__(self)
        self.message = {'error': message}
        self.status_code = status_code

class Context (object):
    def __init__(self, entries):
        self.__dict__.update(entries)
    def __str__(self):
        return str(self.__dict__)

def _getLayerDataTypes (mapId, ctx):
    filename = os.path.join(
        ctx.app.dataRoot, 'view', mapId, 'Layer_Data_Types.tab')
    fd = open(filename, 'rU')
    return csv.reader(fd, delimiter='\t'), fd

def getLayoutIndex (layoutName, mapId, ctx):
    filename = os.path.join(ctx.app.dataRoot, 'view', mapId, 'layouts.tab')
    with open(filename, 'rU') as f:
        f = csv.reader(f, delimiter='\t')
        index = None
        for i, row in enumerate(f.__iter__()):
            if row[0] == layoutName:
                index = i
                break
        return index

def getMapMetaData (mapId, ctx):
    
    # Retrieve the meta data for this map
    dataFd = None
    filename = os.path.join(ctx.app.dataRoot, 'view', mapId, 'mapMeta.json')
    try:
        dataFd = open(filename, 'r')
    except:
        return {}
    try:
        data = json.load(dataFd)
    except:
        raise ErrorResp('Could not convert json to python for ' + filename)

    dataFd.close()
    return data

def createBookmark (state, viewServer, ctx):
    '''
    Create a bookmark.
    @param state: map state to be stored in the bookmark
    @param viewServer: view server on which the bookmark will be stored
    @param ctx: the job context
    @return: a bookmark
    '''
    # Ask the view server to create a bookmark of this client state
    # TODO fix the request to the view server to include cert
    try:
        bResult = requests.post(
            viewServer + '/query/createBookmark',
            #cert=(ctx.app.sslCert, ctx.app.sslKey),
            verify=False,
            headers = { 'Content-type': 'application/json' },
            data = json.dumps(state)
        )
    except:
        traceback.print_exc()
        raise ErrorResp('Unknown error connecting to view server: ' +
            viewServer, 500)

    bData = json.loads(bResult.text)
    if bResult.status_code == 200:
        return bData
    else:
        raise ErrorResp(bData)

def sendMail (fromAddr, toAddrIn, subject, body):
    #import smtplib
    #from email.MIMEMultipart import MIMEMultipart
    #from email.MIMEText import MIMEText
    
    # Force the toAddr to be a list.
    toAddr = toAddrIn
    if isinstance(toAddrIn, str):
        toAddr = [toAddrIn]
    
    #msg = MIMEMultipart()
    msg = MIMEText(body)
    msg['From'] = fromAddr
    msg['To'] = toAddr
    msg['Subject'] = subject
    #msg.attach(MIMEText(body, 'plain'))
    #strMsg = msg.as_string()
    try:
        server = smtplib.SMTP('localhost')
        server.sendmail(fromAddr, toAddr, msg.as_string())
        server.quit()
    except:
        pass

def sendClientEmail (email, subject, msg, appCtx):
    sendMail(appCtx.adminEmail, email, subject, msg)

def sendAdminEmail (subject, msg, appCtx):
    sendMail(appCtx.adminEmail, appCtx.adminEmail, subject, msg)

def reportResult (jobId, operation, status, result, email, doNotEmail, appCtx):

    # Email the success or error result to user email and admin if appropriate.
    subject = 'TumorMap results'
    if appCtx.dev == 1:
        subject = 'DEV: ' + subject
    msg = 'status: ' + status + ' | operation: ' + operation + \
        ' | job ID: ' + str(jobId) + '\n'

    
    if status == 'Error':
        subject = 'TumorMap error'
        if appCtx.dev == 1:
            subject = 'DEV: ' + subject
        if result:
            if 'map' in result:
                msg += '\nmap: ' + result['map']
            if 'error' in result:
                msg += '\nerror: ' + result['error']

        # Send the error to the admin.
        adminMsg = 'email: ' + str(email) + '\n' + msg
        if result and 'stackTrace' in result and result['stackTrace'] != None:
            adminMsg += '\n\n' + result['stackTrace']
        sendAdminEmail(subject, adminMsg, appCtx)

    elif email and not doNotEmail:
    
        # This must be a successful result.
        # If the operation has a success result formatter, use it.
        moduleName = operation + '_web'
        module = importlib.import_module(moduleName, package=None)
        if result and hasattr(module, 'formatEmailResult'):
            formattedResult = module.formatEmailResult(result)
            msg += formattedResult

        else:  # there is no result formatter, so look for a URL.
            if result and 'url' in result:
                msg += '\n' + result['url']

    # Send the success or error to the user if appropriate.
    if email and not doNotEmail:
        sendClientEmail(email, subject, msg, appCtx)

def reportRouteError(statusCode, errorMsg, appCtx, stackTrace=None):
    subject = 'TumorMap error'
    msg = 'http code: ' + str(statusCode) + '\nerror: ' + errorMsg
    if stackTrace:
        msg += '\n' + stackTrace
    if hasattr(appCtx, 'dev'):
        subject = 'DEV: ' + subject
    sendAdminEmail(subject, msg, appCtx)

def getProjMajor (mapId):
    return mapId.split("/")[0]

def getProjMinor (mapId):
    return mapId.split("/")[1]

def mkTempFile ():
    tempDir = tmpDir()
    des, filepath = tempfile.mkstemp(dir=tempDir)
    return filepath

def tmpDir():
    tmpDirName = os.path.join(
        os.environ.get("HUB_PATH"),
        "../computeDb",
        "tmp"
    )
    tmpDirNotThere = (not os.path.isdir(tmpDirName))
    if tmpDirNotThere:
        os.makedirs(tmpDirName)

    return tmpDirName
