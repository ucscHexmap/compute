
import os, json, csv, traceback, requests, logging
import tempfile

class SuccessResp(Exception):

    # Define a success response class which converts to json.

    def __init__(self, data):
        Exception.__init__(self)
        self.data = data

    def to_dict(self):
        return self.data


class SuccessRespNoJson(Exception):

    # Define a success response class which does not convert to json.

    def __init__(self, data):
        Exception.__init__(self)
        self.data = data

    def to_dict(self):
        return self.data


class ErrorResp(Exception):

    # Define an error response class

    DEFAULT_STATUS = 400 # default to 'invalid usage'

    def __init__(self,
                 message,
                 status_code=DEFAULT_STATUS,
                 payload=None):

        Exception.__init__(self)
        self.message = message
        self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['error'] = self.message
        return rv

class Context(object):
    def __init__(self, entries):
        self.__dict__.update(entries)
    def __str__(self):
        return str(self.__dict__)

def _getLayerDataTypes(mapId, ctx):
    filename = os.path.join(
        ctx.app.dataRoot, 'view', mapId, 'Layer_Data_Types.tab')
    fd = open(filename, 'rU')
    return csv.reader(fd, delimiter='\t'), fd


def getLayoutIndex(layoutName, mapId, ctx):
    filename = os.path.join(ctx.app.dataRoot, 'view', mapId, 'layouts.tab')
    with open(filename, 'rU') as f:
        f = csv.reader(f, delimiter='\t')
        index = None
        for i, row in enumerate(f.__iter__()):
            if row[0] == layoutName:
                index = i
                break
        return index


def getMapMetaData(mapId, ctx):
    
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


def createBookmark(state, viewServer, ctx):
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


def sendMail(fromaddr, toaddr, subject, body):
    import smtplib
    from email.MIMEMultipart import MIMEMultipart
    from email.MIMEText import MIMEText
    
    msg = MIMEMultipart()
    msg['From'] = fromaddr
    msg['To'] = toaddr
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))
    strMsg = msg.as_string()
    try:
        server = smtplib.SMTP('localhost')
        server.sendmail(fromaddr, toaddr, strMsg)
        server.quit()
    except:
        logging.warning('sendMail not implemented. Message: ' + strMsg);

def sendResultsEmail (emails, msg, ctx):
    sendMail(ctx.app.adminEmail, emails, 'Tumor Map results', msg)

def getProjMajor(mapId):
    return mapId.split("/")[0]


def getProjMinor(mapId):
    return mapId.split("/")[1]


def mkTempFile():
    tempDir = tmpDir()
    des, filepath = tempfile.mkstemp(dir=tempDir)
    return filepath


def tmpDir():
    return os.path.join(os.environ.get("HUB_PATH", "/home/duncan/hex/compute"), "tmp")
