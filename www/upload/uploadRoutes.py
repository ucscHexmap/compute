
# The upload HTTP routes.

from flask import Blueprint
from util_web import SuccessResp, SuccessRespNoJson, ErrorResp, Context, \
    reportRouteError

uploadRoutes = Blueprint('uploadRoutes', __name__)

# TODO: how do we use the error and success handlers in www.py?

# Handle the route to test.
@uploadRoutes.route('/uploadTest', methods=['POST', 'GET'])
def testRoute():
    raise SuccessResp('just testing upload on data server')


# Handle route to upload files
@uploadRoutes.route('/upload/<path:dataId>', methods=['POST'])
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
