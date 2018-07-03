
# Handle any project edits.

import os, traceback, json, logging, shutil, csv
import os.path as path
from util_web import ErrorResp, getProjMajor, getProjMinor
from validate_web import cleanFileName
import projectList


def authorize (project, userEmail, userRole, viewDir):

    # Check for authorization to edit this map.
    auth = projectList.authorize(project, userEmail, userRole, viewDir)
    if auth['authorized'] != 'edit':
        raise ErrorResp('', 404)


def updateColor (data, appCtx):

    # Change some colors in the colormap.
    project = data['mapId']
    colors = data['colors']
    attrs = colors.keys()
    authorize(project, data['userEmail'], data['userRole'], appCtx.viewDir)

    # Write to the database.
    filename = path.join(appCtx.viewDir, project, 'colormaps.tab')
    filenameNew = filename + '.tmp'
    with open(filename, 'rU') as fin:
        fin = csv.reader(fin, delimiter='\t')
        with open(filenameNew, 'w') as fout:
            fout = csv.writer(fout, delimiter='\t')
            for i, row in enumerate(fin.__iter__()):
                orow = row
                if row[0] in attrs:
                
                    # This row is to be edited.
                    attr = row[0]
                    cats = colors[attr]
                    orow = [attr]  # the attr name
                    i = 0
                    while i < len(cats) / 2:
                        orow.extend([i, cats[i*2], cats[i*2+1]])
                        i += 1

                fout.writerow(orow)

    # Overwrite the original file with this new one.
    os.rename(filenameNew, filename)
    return 'success'

def delete (project, userEmail, userRole, appCtx):

    # Delete one map from the database.
    authorize(project, userEmail, userRole, appCtx.viewDir)

    # Break the map ID into major and minor parts.
    major = getProjMajor(project)
    minor = getProjMinor(project)

    # Remove the map view and featureSpace data.
    majorViewDir = path.join(appCtx.viewDir, major)

    # Remove the map view and featureSpace data.
    featureSpaceDir = path.join(appCtx.dataRoot, 'featureSpace', major)
    for dir in [majorViewDir, featureSpaceDir]:
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
