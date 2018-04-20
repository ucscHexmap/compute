
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
    # Include the email addrs in the bookmark.
    if hasattr(ctx, 'email'):
        state['email'] = ctx.email
    
    # Ask the view server to create a bookmark of this client state
    try:
        bResult = requests.post(
            viewServer + '/query/createBookmark',
            verify=True,
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
    
    msg = MIMEText(body)
    msg['From'] = fromAddr
    msg['To'] = toAddr
    msg['Subject'] = subject
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


def findStackTrace(traceStr=None):
    try:
        return '\n\nData server ' + traceStr + '\n'
    except Exception as e:
        try:
            return '\n\nError finding stack trace: + str(e)\n'
        except:
            return '\n\nUnknown error finding stack trace.\n'


def findEmailForSubject(email):
    try:
        return ' for user: ' + email
    except:
        return ' for user: None'


def findUserMessage(msg):
    return 'User message:\n------------\n' + msg


def reportResult (jobId, operation, status, result, email, doNotEmail, ctx):
    
    # Email the success or error result to user email and admin if appropriate.

    # Capture any errors here so the admin gets notified via email because
    # uncaught errors won't show up in the log.
    subject = 'Tumormap '
    msg = ''
    adminMsg = ''
    mapId = ''
    url = ''
    
    try:
        if ctx.app.dev == 1:
            subject = 'DEV: ' + subject

        # Build the admin summary.
        adminMsg += '     job ID:  ' + str(jobId)
        adminMsg += '\n  operation:  ' + operation
        adminMsg += '\n     status:  ' + status
        adminMsg += '\n      email:  ' + email
        
        # Map is required but may have not made it to here.
        try:
            mapId = ctx.map
        except Exception as e:
            mapId = 'None'
        adminMsg += '\n        map:  ' + mapId
        
        # URL is optional.
        try:
            url = result['url']
        except Exception as e:
            url = 'None'
        adminMsg += '\n        url:  ' + url

        # Find the operation module related to this message.
        module = importlib.import_module(operation + '_web', package=None)

        # Handle the successful result and mail it to user unless told not to.
        if status == 'Success' and not doNotEmail:
            
            subject += 'results'

            # If the operation has a success result formatter, use it.
            if hasattr(module, 'formatEmailResult'):
                formattedResult = module.formatEmailResult(result, ctx)
                msg += formattedResult

            else:  # there is no result formatter, so use the default message.
                msg = 'See the results of your request to ' + operation + \
                    ' for map: ' + mapId + \
                    ' at:\n\n' + url
                    
            sendClientEmail(email, subject, msg, ctx.app)

        elif status == 'Error':

            # Prepare the standard user error message.
            subject += 'error'
            
            # If the operation has an error formatter, use it.
            if hasattr(module, 'formatEmailError'):
                formattedResult = module.formatEmailError(result, ctx)
                msg += formattedResult

            else:  # there is no error formatter, so use the default message.
                msg = 'There was an error while calculating results for '
                msg += operation
                msg += ' for map: ' + mapId
                msg += '\n\nerror: ' + result['error']

            # Send the message to the user if appropriate.
            if not doNotEmail:
                sendClientEmail(email, subject, msg, ctx.app)
            
            # Send the admin message.
            if 'stackTrace' in result:
                adminMsg += findStackTrace(result['stackTrace'])
            adminMsg += findUserMessage(msg)
            subject += findEmailForSubject(email)
            sendAdminEmail(subject, adminMsg, ctx.app)
            
    except:
    
        # Send admin error email due to an exception in error reporting.
        subject += 'exception when reporting job results'
        subject += findEmailForSubject(email)
        adminMsg += findStackTrace(traceback.format_exc(100))
        adminMsg += findUserMessage(msg)
        sendAdminEmail(subject, adminMsg, ctx.app)


def reportRouteError(statusCode, errorMsg, appCtx, stackTrace=None):
    subject = 'TumorMap error'
    msg = 'http code: ' + str(statusCode) + '\nerror: ' + errorMsg
    if stackTrace:
        msg += '\n' + stackTrace
    if hasattr(appCtx, 'dev'):
        subject = 'DEV: ' + subject
    sendAdminEmail(subject, msg, appCtx)


def getProjMajor(mapId):
    try:
        majorId = mapId.split("/")[0]
    except IndexError:
        majorId = None
    return majorId


def getProjMinor(mapId):
    try:
        minorId = mapId.split("/")[1]
    except IndexError:
        minorId = None
    return minorId


def mkTempFile():
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


# Convert a string to integer or float.
def stringToFloatOrInt(s, dataType):
    val = float(s)
    if dataType == 'Categorical':
        val = int(round(val))
    return val

