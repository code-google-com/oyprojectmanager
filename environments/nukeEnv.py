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
    #if os.name == 'nt':
        #myDict = dict()
        #myDict[u'/'] = u'\\'
        #path = oyAux.multiple_replace( path, myDict)
    
    return fileName, path
