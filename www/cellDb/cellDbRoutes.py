
# The cell database HTTP routes.

from flask import request, Blueprint
import cellDataset
from util_web import SuccessResp, getAppCtx

cellDbRoutes = Blueprint('cellDbRoutes', __name__)
appCtx = getAppCtx()

# Handle the route to get all of the cell dataset data from the DB.
@cellDbRoutes.route('/cell/dataset/getAll', methods=['GET'])
def getAll():
    data = cellDataset.getAll(appCtx)
    raise SuccessResp(data)


# Handle the route to test.
@cellDbRoutes.route('/cellDbTest', methods=['POST', 'GET'])
def testRoute():
    raise SuccessResp('just testing cellDb on data server')
