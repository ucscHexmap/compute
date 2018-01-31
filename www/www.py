
# Main module for the http server, including all routes.

import os, traceback, logging, json
from flask import Flask, request, jsonify, Response
from flask_cors import CORS
from werkzeug.utils import secure_filename

import createMap_web
import job
import jobTestHelper_web
import placeNode_web
import reflect_web
import statsNoLayout_web
import statsLayout_web

from util_web import SuccessResp, SuccessRespNoJson, ErrorResp, Context, \
    reportRouteError
import validate_web as validate

# Set up the flask application.
app = Flask(__name__)

# Set up the application context used by all threads.
def contextInit ():
    global appCtx
    appCtx = Context({})
    appCtx.adminEmail = os.environ.get('ADMIN_EMAIL')
    appCtx.dataRoot = os.environ.get('DATA_ROOT', 'DATA_ROOT_ENV_VAR_MISSING')
    appCtx.debug = os.environ.get('DEBUG', 0)
    appCtx.dev = int(os.environ.get('DEV', 0))
    appCtx.hubPath = os.environ.get('HUB_PATH')
    appCtx.unitTest = int(os.environ.get('UNIT_TEST', 0))
    appCtx.viewServer = os.environ.get('VIEWER_URL', 'http://hexdev.sdsc.edu')

    # Derived context.
    appCtx.databasePath = os.environ.get('DATABASE_PATH', appCtx.hubPath + '/../computeDb')
    appCtx.jobQueuePath = os.path.abspath(
        os.path.join(appCtx.databasePath, 'jobQueue.db'))
    appCtx.jobProcessPath = appCtx.hubPath + '/www/jobProcess.py'
    appCtx.viewDir = os.path.join(appCtx.dataRoot, 'view')
    jobStatusUrl = os.environ['WWW_SOCKET'] + '/jobStatus/jobId/'
    if os.environ['USE_HTTPS'] == '1':
        appCtx.jobStatusUrl = 'https://' + jobStatusUrl
    else:
        appCtx.jobStatusUrl = 'http://' + jobStatusUrl
    return appCtx

# Set up logging
def loggingInit ():
    logFormat = '%(asctime)s %(levelname)s: %(message)s'
    logLevel = None
    if appCtx.unitTest:

        # Use critical level to disable all messages so unit tests only output
        # unit test errors.
        logging.basicConfig(level=logging.CRITICAL, format=logFormat)
        logLevel = 'CRITICAL'
    elif appCtx.debug:
        logging.basicConfig(level=logging.DEBUG, format=logFormat)
        logLevel = 'DEBUG'
    else:
        logging.basicConfig(level=logging.INFO, format=logFormat)
        logLevel = 'INFO'

    logging.info('WWW server started with log level: ' + logLevel)
    logging.info('Allowable viewers: ' + str(allowableViewers))

# Initialize the app.
def initialize():

    # Other local vars.
    global allowableViewers
    allowableViewers = os.environ.get('ALLOWABLE_VIEWERS').split(',')

    # Make cross-origin AJAX possible
    CORS(app)

    contextInit()
    loggingInit()

    # Create the database path if it does not exist.
    try:
        os.makedirs(appCtx.databasePath)
    except:
        pass

# Validate a post
def validatePost():
    if request.headers['Content-Type'] != 'application/json':
        raise ErrorResp('Content-Type must be application/json')
    try:
        dataIn = request.get_json()
    except:
        raise ErrorResp('Post content is invalid JSON')

    # Validate an optional email address so we know who a job belongs to.
    validate.email(dataIn)

    return dataIn

# Register the success handler to convert to json
@app.errorhandler(SuccessResp)
def successResponse(success):
    response = jsonify(success.data)
    response.status_code = 200
    #logging.info('success json response: ' + str(response))
    return response

# Register the success handler that doesn't convert to json
@app.errorhandler(SuccessRespNoJson)
def successResponseNoJson(success):
    response = success.data
    response.status_code = 200
    #logging.info('success no json response: ' + str(response))
    return response

# Register the error handler
@app.errorhandler(ErrorResp)
def errorResponse(error):
    response = jsonify(error.message)
    response.status_code = error.status_code
    statusCode, responseStr = str(response.status_code), str(response)
    return response

# Register the unhandled Exception handler
@app.errorhandler(Exception)
def unhandledException(e):
    trace = traceback.format_exc()
    # Build response.
    rdict = {
            "stackTrace" : trace,
            "error" : 'Server uncaught exception: ' + str(e),
            }
    response = jsonify(rdict)
    response.status_code = 500
    reportRouteError(response.status_code, rdict['error'], appCtx,
        rdict['stackTrace'])
    return response

# Handle route to upload files
@app.route('/upload/<path:dataId>', methods=['POST'])
def upload(dataId):
        
    # If the client does not include a file property in the post
    # there is nothing to upload. So bail.
    if 'file' not in request.files:
        raise ErrorResp('No file property provided for upload', 400)
    
    file = request.files['file']

    # If a browser user does not select a file, the browser submits an
    # empty file property. So bail.
    if file.filename == '':
        raise ErrorResp('No file provided for upload', 400)
        
    filename = secure_filename(file.filename)
    path = os.path.join(appCtx.dataRoot, dataId)
    
    # Make the directories if they are not there.
    try:
        os.makedirs(path[:path.rfind('/')], 0770)
    except Exception:
        pass
    
    # Save the file
    try:
        file.save(path)
    except Exception:
        raise ErrorResp('Unable to save file.', 500)
    
    raise SuccessResp('upload of ' + filename + ' complete')

def dataRouteInner(dataId, ok404=False):
    """
    # For now, let anyone read.
    # Only allow authorized view servers to pull data.
    try:
        origin = request.environ['HTTP_ORIGIN']
    except Exception:
        raise ErrorResp('http-origin not defined', 400)
    if not origin in app.config['ALLOWABLE_VIEWERS']:
        raise ErrorResp('Unauthorized http-origin: ' + origin, 400)
    """

    # Not using flask's send_file() as it mangles files larger than 32k.
    # Not using flask's GET because we need to capture 404-file-not-found
    # errors in the case that is ok with the client and return success.
    try:
        with open(os.path.join(appCtx.dataRoot, dataId)) as f:
            data = f.read()
            result = Response(
                data,
                mimetype='text/csv',
                headers={'Content-disposition': 'attachment'})
    except IOError:
        if ok404:
            result = Response(
                '404',
                mimetype='text/csv',
                headers={'Content-disposition': 'attachment'})
            raise SuccessRespNoJson(result)
        else:
            raise ErrorResp('File not found or other IOError', 404)

    raise SuccessRespNoJson(result)

# Handle data/<dataId> routes which are data requests by data ID.
@app.route('/data/<path:dataId>', methods=['GET'])
def dataRoute(dataId):
    dataRouteInner(dataId)

# Handle data404ok/<dataId> routes which are data requests by data ID.
# A 404 is ok to return here, so we do it as 'success' so that errors
# will not be thrown on the client console.
@app.route('/dataOk404/<path:dataId>', methods=['GET'])
def dataRouteOk404(dataId):
    dataRouteInner(dataId, True)

# Handle get all jobs route
@app.route('/getAllJobs', methods=['GET'])
def getAllJobsRoute():
    result = job.getAll(appCtx.jobQueuePath)
    raise SuccessResp(result)

# Handle jobStatus route
@app.route('/jobStatus/jobId/<int:jobId>', methods=['GET'])
def jobStatusRoute(jobId):
    logging.info('job status req')
    result = job.getStatus(jobId, appCtx.jobQueuePath)
    raise SuccessResp(result)

# Handle query/jobTestHelper routes
@app.route('/query/jobTestHelper', methods=['POST'])
def queryJobTestHelperRoute():
    result = jobTestHelper_web.preCalc(validatePost(), Context({'app': appCtx}))
    raise SuccessResp(result)

# Handle query/createMap route.
@app.route('/query/createMap', methods=['POST'])
def queryCreateMapRoute():
    result = createMap_web.preCalc(validatePost(), Context({'app': appCtx }))
    raise SuccessResp(result)

# Handle query/overlayNode route, older version of placeNode
@app.route('/query/overlayNodes', methods=['POST'])
def queryOverlayNodesRoute():
    result = placeNode_web.preCalc(validatePost(),
        Context({'app': appCtx, 'overlayNodes': True}))
    raise SuccessResp(result)

# Handle query/placeNode routes
@app.route('/query/placeNode', methods=['POST'])
def queryPlaceNodeRoute():
    result = placeNode_web.preCalc(validatePost(), Context({'app': appCtx}))
    raise SuccessResp(result)

@app.route('/oneByAll/statCalculation', methods=['POST'])
def onByAllStatRequest():
    """
    Post example:
    {
        mapName : "PancanAtlas/SampleMap",
        focusAttr: opts.dynamicData,
        focusAttrDatatype : dType,
        mail : Meteor.user().username,
    };
    focusAttr is in this form:
        {"attrName" : { "sampleId" : value}, ... }
    focus attribute datatype is one of:
        ["bin", "cat", "cont"]

    JSON response on Success from job queue:
        {result:
            [
                [ attributeId, single-test pvalue, BHFDR, bonefonni],
                ...,
                ...
            ]
        }
        For all attributes on the requested map.
    """
    logging.info('One By All Stat requested')

    parms = validatePost()
    ctx = Context({'app': appCtx})

    responseDict = statsNoLayout_web.preCalc(parms, ctx)
    logging.info(responseDict)

    raise SuccessResp(responseDict)

@app.route('/oneByAll/leesLCalculation', methods=['POST'])
def onByAllLeesLRequest():
    """
    Post example:
    {
        mapName : "PancanAtlas/SampleMap",
        focusAttr: opts.dynamicData,
        layoutIndex : 1,
        mail : Meteor.user().username,
    };
    focusAttr is in this form:
        {"attrName" : { "sampleId" : value}, ... }

    JSON response on Success from job queue:
        {result:
            [
                [ attributeId, leesL, Rank, Pearson],
                ...,
                ...
            ]
        }
        For all attributes on the requested map.
    """
    logging.info('One By All LeesL requested')

    parms = validatePost()
    ctx = Context({'app': appCtx})

    responseDict = statsLayout_web.preCalc(parms, ctx)
    logging.info(responseDict)

    raise SuccessResp(responseDict)

# Handle reflect/metadata routes
@app.route(
'/reflect/metaData/majorId/<string:majorId>/minorId/<string:minorId>',
    methods=['GET']
)
def getReflectMetadata(majorId, minorId):
    """

    :param majorId:
    :param minorId:
    :return:
     {
        toMapIds : []
        dataType : []
    }
    """
    responseDict = reflect_web.getReflectionMetadata(majorId, minorId)
    raise SuccessResp(responseDict)

@app.route('/reflect', methods=['POST'])
def reflectionRequest():
    """
    JSON post example
    {
        dataType : "dataTypePointsToAFileInReflectionConfig"
        toMapId : "Pancan12/GeneMap",
        mapId : "Pancan12/SampleMap",
        nodeIds : [id, id, ...],
        rankCategories: True/False,
        dynamicAttrName : "Kindey Isle"
        email: dmccoll@ucsc.edu
    };
    JSON response on Success from job queue:
        {
            url : /reflect/attrId/<string:fileId>,
            nNodes : 123
        }
        url is an enpoint to download the calculated file.
    """
    logging.info('Reflection requested')

    parms = validatePost()
    ctx = Context({'app': appCtx})

    responseDict = reflect_web.preCalc(parms, ctx)
    logging.info(responseDict)

    raise SuccessResp(responseDict)

@app.route('/reflect/attrId/<string:attrId>', methods=['GET'])
def getRefAttr(attrId):
    """Returns reflection request JSON.
    define return schema
    """
    logging.info('Reflection get request, attrid: ' + attrId)
    responseDict = reflect_web.getReflectionAttr(attrId)
    raise SuccessResp(responseDict)

@app.route('/allpointclouds', methods=['GET'])
def getAllPointCloud():
    """
    """
    import pandas as pd

    xypath = "/home/duncan/data/view/PancanAtlas/SampleMap/xyPreSquiggle_0.tab"
    dpath = "./patlas.dbscan.all.tab"
    xys = pd.read_table(xypath, index_col=0)
    df = pd.read_table(dpath, index_col=0)
    pointSamples=[]
    urls=[]
    nSamples=[]
    cs = 0

    for col in df.columns:
        cs+=1

        if not(cs == 0 or cs == 0):
            logging.info("#################" + str(len(urls)))

        layer = df[df[col] != "Outlier"][col]
        for uniqueVal in layer.unique():
            valueCountsDF = layer.value_counts()
            subset = layer[layer == uniqueVal]
            nSamples.append(len(subset))
            if valueCountsDF[uniqueVal] > 2000:
                sampleList = subset.sample(2000).index
            else:
                sampleList = subset.index

            pointSamples.append(
                xys.loc[sampleList.tolist()].as_matrix().tolist()
            )
            urls.append('http://localhost:5000/nextpointclouds/' + col)

    means = xys.mean().tolist()

    responseDict = {
        "pointClouds": pointSamples,
        "urlIds": urls,
        "means": means,
        'nSamples': nSamples
    }

    logging.info("#################" + str(len(urls)))

    raise SuccessResp(responseDict)


@app.route('/pointclouds', methods=['GET'])
def getPointCloud():
    """
    """
    import pandas as pd
    from sklearn.cluster import DBSCAN
    import numpy as np

    xypath = "/home/duncan/data/view/PancanAtlas/SampleMap/xyPreSquiggle_0.tab"
    dpath = "/home/duncan/data/view/PancanAtlas/SampleMap/hdbscanPAtalasHomeMin5"
    xys = pd.read_table(xypath, index_col=0)

    clusterer = DBSCAN(min_samples=4, eps=5)
    cluster_labels = clusterer.fit_predict(xys)
    name = "hdbscan"
    output = pd.DataFrame(map(lambda x: name + '_' + str(x) ,
                              cluster_labels), index=xys.index,
                          columns=[name])
    output.iloc[np.array(output[name] == name+ '_-1')] = 'Outlier'
    output.index.rename('nodes',inplace=True)
    df = output
    logging.info('pointcloud request: ' + str((df.hdbscan ==
                                               "Outlier").sum()))
    df = df[df.hdbscan != "Outlier"]

    pointSamples=[]
    valueCountsDF = df.hdbscan.value_counts()
    uniqueVals = df.hdbscan.unique()
    for uniqueVal in df.hdbscan.unique():
        subset = df[df.hdbscan == uniqueVal]
        if valueCountsDF[uniqueVal] > 2000:
           sampleList = subset.sample(2000).index
        else:
            sampleList = subset.index

        pointSamples.append(
            xys.loc[sampleList.tolist()].as_matrix().tolist()
        )
    means = xys.mean().tolist()

    responseDict = {
        "pointClouds" : pointSamples,
        "means" : means
    }
    raise SuccessResp(responseDict)

@app.route('/nextpointclouds/<string:nextId>', methods=['GET'])
def nextPointCloud(nextId):
    import pandas as pd
    from sklearn.cluster import DBSCAN
    import numpy as np
    xypath = "/home/duncan/data/view/PancanAtlas/SampleMap/xyPreSquiggle_0.tab"
    dpath = "/home/duncan/data/view/PancanAtlas/SampleMap/hdbscanPAtalasHomeMin5"

    df = pd.read_pickle(dpath)
    df = df[df.hdbscan != "Outlier"]

    xys = pd.read_table(xypath, index_col=0)

    sampInCluster = df[df.hdbscan == nextId].index
    clusterer = DBSCAN(min_samples=4, eps=3)
    logging.info('pointcloud request with: ' + nextId + str(len(
        sampInCluster)))
    xys = xys.loc[sampInCluster]
    cluster_labels = clusterer.fit_predict(xys)

    name = nextId
    output = pd.DataFrame(map(lambda x: name + '_' + str(x) , cluster_labels),index=xys.index,columns=[name])
    output.iloc[np.array(output[name] == name+ '_-1')] = 'Outlier'
    output.index.rename('nodes',inplace=True)
    df = output

    logging.info('pointcloud request: ' + str((df[name] ==
                                               "Outlier").sum()))
    df = df[df[name] != "Outlier"]

    pointSamples=[]
    valueCountsDF = df[name].value_counts()
    for uniqueVal in df[name].unique():
        subset = df[df[name] == uniqueVal]
        if valueCountsDF[uniqueVal] > 2000:
           sampleList = subset.sample(2000).index
        else:
            sampleList = subset.index

        pointSamples.append(
            xys.loc[sampleList.tolist()].as_matrix().tolist()
        )
    means = xys.mean().tolist()
    #urls = map( lambda x: 'http://localhost:5000/nextpointclouds/' +
    #
    #                       x, uniqueVals)

    responseDict = {
        "pointClouds" : pointSamples,
        "urlIds" : means
    }

    raise SuccessResp(responseDict)


# Handle the route to test
@app.route('/test', methods=['POST', 'GET'])
def testRoute():
    raise SuccessResp('just testing data server')

@app.route('/allpointclouds', methods=['GET'])
def getAllPointCloud():
    """
    """
    import pandas as pd

    xypath = "/home/duncan/data/view/PancanAtlas/SampleMap/xyPreSquiggle_0.tab"
    dpath = "./patlas.dbscan.all.tab"
    xys = pd.read_table(xypath, index_col=0)
    df = pd.read_table(dpath, index_col=0)
    pointSamples=[]
    urls=[]
    nSamples=[]
    cs = 0

    for col in df.columns:
        cs+=1

        if not(cs == 0 or cs == 0):
            logging.info("#################" + str(len(urls)))

        layer = df[df[col] != "Outlier"][col]
        for uniqueVal in layer.unique():
            valueCountsDF = layer.value_counts()
            subset = layer[layer == uniqueVal]
            nSamples.append(len(subset))
            if valueCountsDF[uniqueVal] > 2000:
                sampleList = subset.sample(2000).index
            else:
                sampleList = subset.index

            pointSamples.append(
                xys.loc[sampleList.tolist()].as_matrix().tolist()
            )
            urls.append('http://localhost:5000/nextpointclouds/' + col)

    means = xys.mean().tolist()

    responseDict = {
        "pointClouds": pointSamples,
        "urlIds": urls,
        "means": means,
        'nSamples': nSamples
    }

    logging.info("#################" + str(len(urls)))

    raise SuccessResp(responseDict)


@app.route('/pointclouds', methods=['GET'])
def getPointCloud():
    """
    """
    import pandas as pd
    from sklearn.cluster import DBSCAN
    import numpy as np

    xypath = "/home/duncan/data/view/PancanAtlas/SampleMap/xyPreSquiggle_0.tab"
    dpath = "/home/duncan/data/view/PancanAtlas/SampleMap/hdbscanPAtalasHomeMin5"
    xys = pd.read_table(xypath, index_col=0)

    clusterer = DBSCAN(min_samples=4, eps=5)
    cluster_labels = clusterer.fit_predict(xys)
    name = "hdbscan"
    output = pd.DataFrame(map(lambda x: name + '_' + str(x) ,
                              cluster_labels), index=xys.index,
                          columns=[name])
    output.iloc[np.array(output[name] == name+ '_-1')] = 'Outlier'
    output.index.rename('nodes',inplace=True)
    df = output
    logging.info('pointcloud request: ' + str((df.hdbscan ==
                                               "Outlier").sum()))
    df = df[df.hdbscan != "Outlier"]

    pointSamples=[]
    valueCountsDF = df.hdbscan.value_counts()
    uniqueVals = df.hdbscan.unique()
    for uniqueVal in df.hdbscan.unique():
        subset = df[df.hdbscan == uniqueVal]
        if valueCountsDF[uniqueVal] > 2000:
           sampleList = subset.sample(2000).index
        else:
            sampleList = subset.index

        pointSamples.append(
            xys.loc[sampleList.tolist()].as_matrix().tolist()
        )
    means = xys.mean().tolist()

    responseDict = {
        "pointClouds" : pointSamples,
        "means" : means
    }
    raise SuccessResp(responseDict)

@app.route('/nextpointclouds/<string:nextId>', methods=['GET'])
def nextPointCloud(nextId):
    import pandas as pd
    from sklearn.cluster import DBSCAN
    import numpy as np
    xypath = "/home/duncan/data/view/PancanAtlas/SampleMap/xyPreSquiggle_0.tab"
    dpath = "/home/duncan/data/view/PancanAtlas/SampleMap/hdbscanPAtalasHomeMin5"

    df = pd.read_pickle(dpath)
    df = df[df.hdbscan != "Outlier"]

    xys = pd.read_table(xypath, index_col=0)

    sampInCluster = df[df.hdbscan == nextId].index
    clusterer = DBSCAN(min_samples=4, eps=3)
    logging.info('pointcloud request with: ' + nextId + str(len(
        sampInCluster)))
    xys = xys.loc[sampInCluster]
    cluster_labels = clusterer.fit_predict(xys)

    name = nextId
    output = pd.DataFrame(map(lambda x: name + '_' + str(x) , cluster_labels),index=xys.index,columns=[name])
    output.iloc[np.array(output[name] == name+ '_-1')] = 'Outlier'
    output.index.rename('nodes',inplace=True)
    df = output

    logging.info('pointcloud request: ' + str((df[name] ==
                                               "Outlier").sum()))
    df = df[df[name] != "Outlier"]

    pointSamples=[]
    valueCountsDF = df[name].value_counts()
    for uniqueVal in df[name].unique():
        subset = df[df[name] == uniqueVal]
        if valueCountsDF[uniqueVal] > 2000:
           sampleList = subset.sample(2000).index
        else:
            sampleList = subset.index

        pointSamples.append(
            xys.loc[sampleList.tolist()].as_matrix().tolist()
        )
    means = xys.mean().tolist()
    #urls = map( lambda x: 'http://localhost:5000/nextpointclouds/' +
    #
    #                       x, uniqueVals)

    responseDict = {
        "pointClouds" : pointSamples,
        "urlIds" : means
    }

    raise SuccessResp(responseDict)


initialize()
