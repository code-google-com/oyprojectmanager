"""
houdiniEnv.py by Erkan Ozgur Yilmaz (c) 2009


Description:
------------
the houdini environment part of the asset management system...

has commands to save, open and import houdini files

Version History:
----------------
(version history is kept in the main __init__.py file)

TODO:
-----
+ change the environment variables ($JOB etc.) to the current project whenever
  a file is saved or opened

"""



import os
import hou
from oyProjectManager.dataModels import assetModel, projectModel
import oyAuxiliaryFunctions as oyAux



__version__ = "9.11.25"



#----------------------------------------------------------------------
def save( assetObject ):
    """the save action for houdini environment
    """
    
    #assert(isinstance(assetObject, assetModel.Asset ) )
    
    # set the extension to hip
    assetObject.setExtension('hip')
    
    # create the folder if it doesn't exists
    oyAux.createFolder( assetObject.getPath() )
    
    # houdini uses / instead of \ under windows
    # lets fix it
    
    fullPath = assetObject.getFullPath()
    fullPath = fullPath.replace('\\','/')
    
    # houdini accepts only strings as file name, no unicode support as I see
    hou.hipFile.save( file_name = str(fullPath) )
    
    # set the environment variables
    setEnvironmentVariables( assetObject )
    
    return True



#----------------------------------------------------------------------
def open_( assetObject, force=False ):
    """the open action for houdini environment
    """
    
    #assert(isinstance(assetObject, assetModel.Asset ) )
    if hou.hipFile.hasUnsavedChanges() and not force:
        raise RuntimeError
    
    fullPath = assetObject.getFullPath()
    fullPath = fullPath.replace('\\','/')
    
    hou.hipFile.load( file_name = str(fullPath) , suppress_save_prompt=True )
    
    # set the environment variables
    setEnvironmentVariables( assetObject )
    
    return True



#----------------------------------------------------------------------
def import_( assetObject ):
    """the import action for houdini environment
    """
    
    #assert(isinstance(assetObject, assetModel.Asset ) )
    
    fullPath = assetObject.getFullPath()
    fullPath = fullPath.replace('\\','/')
    
    hou.hipFile.merge( str(fullPath) )
    
    return True



#----------------------------------------------------------------------
def getPathVariables():
    """gets the file name from houdini environment
    """
    
    fileName = path = None
    
    fullPath = hou.hipFile.name()
    
    if fullPath != 'untitled.hip':
    
        # unfix windows path
        if os.name == 'nt':
            fullPath = fullPath.replace('/','\\')
        
        path = os.path.dirname( fullPath )
        
        if path != '':
            fileName = os.path.basename( fullPath )
        else:
            path = None
    #else:
        #hou.
    
    return fileName, path



#----------------------------------------------------------------------
def setEnvironmentVariables( assetObject ):
    """sets the environment variables according to the given assetObject
    """
    
    #assert(isinstance(assetObject, assetModel.Asset))
    
    # set the $JOB variable to the sequence root
    os.environ['JOB'] = str(assetObject.getSequenceFullPath()).replace('\\','/')