
# Handle any project edits.

import os, traceback, json, logging, shutil
import os.path as path
from util_web import ErrorResp
from validate_web import cleanFileName
from projectList import authorize


def delete(project, userEmail, userRole, appCtx):

    # Delete one map from the database.
    
    # Check for authorization to edit this map.
    auth = authorize(project, userEmail, userRole, appCtx.viewDir)
    if auth['authorized'] != 'edit':
        raise ErrorResp('', 404)

    # Break the map ID into major and minor parts.
    projParts = project.split('/')
    major = projParts[0]
    minor = None
    if (len(projParts)) > 1:
        minor = projParts[1]
    
    # Remove the map view and featureSpace data.
    viewDir = path.join(appCtx.viewDir, major)
    featureSpaceDir = path.join(appCtx.dataRoot, 'featureSpace', major)
    for dir in [viewDir, featureSpaceDir]:
        try:
            # If there is a minor part and more than one map in this group,
            # we only want to remove that one map and not the group dir.
            # Account for the meta.json file that must be present to obtain
            # edit authorization.
            if minor and len(os.listdir(dir)) > 2:
                dir = path.join(dir, minor)
            shutil.rmtree(dir)
        except:
            pass

    return 'success'
