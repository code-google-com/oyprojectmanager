import os
import nuke
import oyAuxiliaryFunctions as oyAux
from oyProjectManager.dataModels import assetModel, projectModel



#----------------------------------------------------------------------
def save( assetObject ):
    """"the save action for maya environment
    
    uses Nukes own python binding
    """
    
    # set the extension to 'nk'
    assetObject.setExtension( 'nk' )
    
    nuke.scriptSaveAs( assetObject.getFullPath() )
    
    if os.name=='nt':
        setRootName()
    
    return True



#----------------------------------------------------------------------
def export( assetObject ):
    """the exprot action for nuke environment
    """
    
    # set the extension to 'nk'
    assetObject.setExtension('nk')
    
    nuke.nodeCopy( assetObject.getFullPath() )
    
    return True



#----------------------------------------------------------------------
def open_( assetObject ):
    """the open action for nuke environment
    """
    
    nuke.scriptOpen( assetObject.getFullPath() )
    
    print "open_ -> assetObject.getFullPath() -> ", assetObject.getFullPath()
    
    # path name bug
    if os.name=='nt':
        rootName = setRootName()
        print "open_ -> rootName -> ", rootName
    
    return True



#----------------------------------------------------------------------
def import_( assetObject ):
    """the import action for nuke environment
    """
    
    nuke.nodePaste( assetObject.getFullPath() )
    
    return True



#----------------------------------------------------------------------
def getPathVariables():
    """gets the file name from nuke
    """
    fullPath = path = fileName = None
    
    
    fullPath = nuke.toNode("root").name()
    
    if fullPath != None and fullPath != '':
        fileName = os.path.basename( fullPath )
        path = os.path.dirname( fullPath )
    else:
        # use the last file from the recent file list
        fullPath = nuke.recentFile(1)
        
        fileName = os.path.basename( fullPath )
        path = os.path.dirname( fullPath )
    
    # if the environment is Windows replace / with \
    if os.name == 'nt':
        myDict = dict()
        myDict[u'/'] = u'\\'
        path = oyAux.multiple_replace( path, myDict)
    
    return fileName, path




#----------------------------------------------------------------------
def setRootName():
    """sets the root name variable
    """
    
    rootNode = nuke.toNode("root")
    
    # get the name and replace \ with / characters
    
    rootName = rootNode.name()
    
    myDict = dict()
    myDict[u'\\'] = u'/'
    
    rootName = oyAux.multiple_replace( rootName, myDict ) 
    
    rootNode.setName( rootName )
    
    return rootName
    