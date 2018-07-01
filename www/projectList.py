
# Handle the project list and authorization.

import os, traceback, json, logging
from util_web import ErrorResp
from validate_web import cleanFileName

def _getSubDirs (rootDir):

    # Get immediate sub directories.
    allSubDirs = next(os.walk(rootDir))[1]

    # Remove any hidden directories.
    subDirs = filter(lambda x: x[0] != '.', allSubDirs)
    
    return sorted(list(subDirs))

def _addMinors (majors, viewDir):
    projects = []
    '''
    [
        ['Gliomas'],
        ['Pancan12', ['GeneMap', 'SampleMap']],
        ...
    ]
    '''
    for major in majors:
    
        # Add the first-level sub directories to this major directory's list.
        minors = _getSubDirs(os.path.join(viewDir, major))
        if len(minors) > 0:
            projects.append([major, minors])
        else:
            projects.append([major])

    return projects

def _isUserInRole (userRoles, projRoles):

    # If any of the user roles are in the project roles, return True.
    for projRole in projRoles:
        if projRole in userRoles:
            return True

    return False

def _userAuthorization (userEmail, userRole, major, projRole):

    # Is this user authorized to view or edit this project?
    #
    # @param userEmail: email of the user used in locating her projects or None
    # @param userRole: the roles of this user as a list
    # @param major: the first portion of the two-level map names
    # @param projRole: the roles of this project as a list
    # @returns: 'view' when the user is authorized to see this map group;
    #           'edit' when the user is authorized to edit this map group;
    #           'not'' otherwise

    VIEW_ACCESS = ['dev', 'viewAll'];
    
    # When not logged in, only public projects may be viewed.
    if userEmail == None:
        if 'public' in projRole:
            return 'view'
        else:
            return 'not'
    
    # A user can view and edit her personal maps.
    if cleanFileName(userEmail) == major:
        return 'edit'

    # No role at this point means only public projects may be viewed.
    if userRole == []:
        if 'public' in projRole:
            return 'view'
        else:
            return 'not'
    
    # Authorize edit if the user has the edit role for a role of this project.
    for role in userRole:
        #print 'projRole:', projRole
        #print 'role:', role
        roleI = role.find('Edit')
        #print 'roleI:', roleI
        if roleI > -1:
            viewRole = role[0:roleI]
            #print 'viewRole:', viewRole
            if viewRole in projRole:
                #print 'viewRole in projRole'
                return 'edit'

    # Public projects with are viewable by anyone.
    if 'public' in projRole:
        return 'view'

    # Authorize viewing if the user has all view access.
    if _isUserInRole(userRole, VIEW_ACCESS):
        return 'view'

    # Authorize viewing if the user is in the given role
    if _isUserInRole(userRole, projRole):
        return 'view'

    # Not authorized
    return 'not'

def _rolesToList(roles):

    # Convert the roles to a list for easy operations later.
    if roles == None:
        roles = []
    elif not type(roles) == list:
        roles = [roles]

    return roles

def _getProjectRoles (project, viewDir):
    roles = None
    jsonStr = ''
    try:
        # Look for a meta file containing roles with access to this project.
        with open(os.path.join(viewDir, project, 'meta.json'), 'rU') as f:
            jsonStr = f.read()
    except:
        # There is no meta data for this project, so no roles.
        return []
    try:
        meta = json.loads(jsonStr)
        roles = meta['role']
    except:
        # Bad json in the meta data.
        raise ErrorResp('bad json in meta data for map: ' + project)
        return []
    
    return _rolesToList(roles)

def _removeNonAuthdDirs (majors, userEmail, userRoles, viewDir):

    # Remove any directories not authorized by the given roles.
    goodDirs = []
    for major in majors:
        projRoles = _getProjectRoles(major, viewDir)
        auth = _userAuthorization(userEmail, userRoles, major, projRoles)
        if auth != 'not':
            goodDirs.append(major)

    return goodDirs

def authorize (project, email, userRole, viewDir):

    # Authorize a project based on userRoles.
    # @param project: the project to authorize.
    # @param email: user's email or None
    # @param userRole: a list of roles or None
    # @param viewDir: the data view directory root
    # @returns: True or False in the form:
    #   {
    #       'authorized': True
    #   }
    major = project.split('/')[0]
    return {
        'authorized':
            _userAuthorization (
                email,
                userRole,
                major,
                projRole=_getProjectRoles(major, viewDir)
            )
    }

def get (userEmail, userRoles, viewDir):

    # Retrieve projects names.
    # @param userEmail: the username/email or None
    # @param userRoles: a list of roles or None
    # @param viewDir: the data view directory root
    # @returns: two-tiered list of projects in the form:
    #   {
    #       'major1': ['minor1a', 'minor1b', ...],
    #       'major2': ['minor2a', 'minor2b', ...],
    #       'major3: [],
    #       ...
    #   }
    #   OR
    #   None? TODO

    # Convert the user roles to a list if need be.
    userRoles = _rolesToList(userRoles)

    # Get the major directory names.
    allMajors = _getSubDirs(viewDir)
    
    # Get the major directories authorized by the roles.
    majors = _removeNonAuthdDirs(allMajors, userEmail, userRoles, viewDir)

    # Build the project list from their major and minor components.
    projects = _addMinors(majors, viewDir)
    
    return projects

