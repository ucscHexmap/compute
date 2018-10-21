
# The upload HTTP routes.

import os
from flask import request, Blueprint
import uploadFile
from util_web import SuccessResp

uploadRoutes = Blueprint('uploadRoutes', __name__)

"""
# Handle route to upload files by an individual with an email.
basic =
    '/upload' + \
    '/email/<string:userEmail>' + \
    '/token/<string:token>' + \
    '/authGroup/<string:authGroup>'+ \
    '/major/<string:major>'
@uploadRoutes.route(basic, methods=['POST'])
@uploadRoutes.route(basic + '/minor/<string:minor>', methods=['POST'])
def upload(userEmail, token, authGroup, major, minor=None):
    uploadedFileName = uploadFile.add(
        userEmail, token, authGroup, major, minor, request)
    print '### upload/email/...()'
    raise SuccessResp('upload of ' + uploadedFileName + ' complete')
"""

# Handle deprecated route to upload files.
@uploadRoutes.route('/upload/<path:dataId>', methods=['POST'])
def upload(dataId):
    filename = uploadFile.oldApi(dataId, request)
    raise SuccessResp('upload of ' + filename + ' complete')


# Handle the route to test.
@uploadRoutes.route('/uploadTest', methods=['POST', 'GET'])
def testRoute():
    raise SuccessResp('just testing upload on data server')
