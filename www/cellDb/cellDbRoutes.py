
# The cell database HTTP routes.

from flask import request, Blueprint
import cellDatasetDb
from util_web import SuccessResp

cellDbRoutes = Blueprint('cellDbRoutes', __name__)


# Handle the route to get all of the cell dataaset data from the DB.
@uploadRoutes.route('/cell/dataset/getAll', methods=['GET'])
def getAll():
    data = cellDatasetDb.getAll(appCtx)
    raise SuccessResp('upload of ' + filename + ' complete')


# Handle the route to test.
@uploadRoutes.route('/cellDbTest', methods=['POST', 'GET'])
def testRoute():
    raise SuccessResp('just testing cellDb on data server')
