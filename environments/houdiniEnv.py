import os
import hou
from oyProjectManager.dataModels import assetModel, projectModel



__version__ = "9.11.3"



#----------------------------------------------------------------------
def save( assetObject ):
    """the save action for houdini environment
    """
    
    #assert(isinstance(assetObject, assetModel.Asset ) )
    
    # set the extension to hip
    assetObject.setExtension('hip')
    
    # houdini accepts only strings as file name, no unicode support as I see
    hou.hipFile.save( file_name = str(assetObject.getFullPath()) )
    
    return True



#----------------------------------------------------------------------
def open_( assetObject, force=False ):
    """the open action for houdini environment
    """
    
    #assert(isinstance(assetObject, assetModel.Asset ) )
    if hou.hipFile.hasUnsavedChanges() and not force:
        raise RuntimeError
    
    hou.hipFile.load( file_name = str(assetObject.getFullPath()) , suppress_save_prompt=(not force) )
    
    return True



#----------------------------------------------------------------------
def import_( assetObject ):
    """the import action for houdini environment
    """
    
    #assert(isinstance(assetObject, assetModel.Asset ) )
    
    hou.hipFile.merge( str(assetObject.getFullPath()) )
    
    return True



#----------------------------------------------------------------------
def getPathVariables():
    """gets the file name from houdini environment
    """
    
    fileName = path = None
    
    fullPath = hou.hipFile.name()
    
    path = os.path.dirname( fullPath )
    
    if path != '':
        fileName = os.path.basename( fullPath )
    else:
        path = None
    
    return fileName, path