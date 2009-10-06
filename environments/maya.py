import os
import pymel as pm
import oyAuxiliaryFunctions as oyAux
from oyProjectManager.dataModels import assetModel, projectModel



#----------------------------------------------------------------------
def save( assetObject ):
    """the save action for maya environment
    
    uses PyMel to save the file (not necessary but comfortable )
    """
    
    #assert(isinstance(assetObject, assetModel.Asset ) )
    
    # set the extension to ma by default
    #assert(isinstance(assetObject, assetModel.Asset))
    assetObject.setExtension( 'ma' )
    
    # set the project to the current environment
    pm.workspace.open( assetObject.getSequenceFullPath() )
    
    # set the render file name and version
    setRenderFileName( assetObject )
    
    # set the playblast file name
    setPlayblastFileName( assetObject )
    
    # create the folder if it doesn't exists
    oyAux.createFolder( assetObject.getPath() )
    
    # save the file
    pm.saveAs( assetObject.getFullPath(), type='mayaAscii' )
    
    return True



#----------------------------------------------------------------------
def open_( assetObject, force=False):
    """the open action for maya environment
    """
    #assert(isinstance(assetObject, assetModel.Asset ) )
    
    # check for unsaved changes
    pm.openFile( assetObject.getFullPath(), f=force )
    
    # set the project
    pm.workspace.open( assetObject.getSequenceFullPath() )
    
    # set the playblast folder
    setPlayblastFileName( assetObject )
    
    return True



#----------------------------------------------------------------------
def import_( assetObject ):
    """the import action for maya environment
    """
    #assert( isinstance(assetObject, assetModel.Asset ) )
    
    pm.importFile( assetObject.getFullPath() )
    
    return True



#----------------------------------------------------------------------
def reference( assetObject ):
    """the reference action for maya environment
    """
    
    #assert( isinstance(assetObject, assetModel.Asset ) )
    
    pm.createReference( assetObject.getFullPath() )
    
    return True



#----------------------------------------------------------------------
def getPathVariables():
    """gets the file name from maya environment
    """
    
    fileName = path = None
    
    fullPath = pm.env.sceneName()
    
    if fullPath != '':
        fileName = os.path.basename( fullPath )
        path = os.path.dirname( fullPath )
    else: # no file is open
        #try to get at least the project and sequence names
        path = getWorkspacePath()
    
    return fileName, path



#----------------------------------------------------------------------
def setRenderFileName( assetObject ):
    """sets the render file name
    """
    #assert(isinstance(assetObject,assetModel.Asset))
    parentSeq = assetObject.getParentSequence()
    
    renderOutputFolder = parentSeq.getStructure().getOutputFolderPathOf( 'RENDER' ) # _RENDERED_IMAGES_/SHOTS
    
    # image folder from the workspace.mel
    imageFolderFromWS = pm.workspace.fileRules['image'] # _RENDERED_IMAGES_/
    
    shotFolder = renderOutputFolder[ len(imageFolderFromWS):] # SHOTS
    
    assetBaseName = assetObject.getBaseName()
    
    renderFileName = ''
    if parentSeq.noSubNameField():
        renderFileName = shotFolder + "/" + assetBaseName + "/<Layer>/" + assetBaseName + "_<Layer>_<RenderPass>_<Version>"
    else: # remove later when the support for old project is over
        assetSubName = assetObject.getSubName()
        renderFileName = shotFolder + "/" + assetBaseName + "/<Layer>/" + assetBaseName + "_" + assetSubName + "_<Layer>_<RenderPass>_<Version>"
    
    # defaultRenderGlobals
    dRG = pm.PyNode('defaultRenderGlobals')
    dRG.setAttr('imageFilePrefix', renderFileName)
    dRG.setAttr('renderVersion', assetObject.getVersionString() )
    dRG.setAttr('animation', 1)
    dRG.setAttr('outFormatControl', 0 )
    dRG.setAttr('extensionPadding', 3 )
    dRG.setAttr('pff', 1)



#----------------------------------------------------------------------
def setPlayblastFileName( assetObject ):
    """sets the playblast file name
    """
    pm.optionVar['playblastFile'] =  assetObject.getType().getPlayblastFolder()



#----------------------------------------------------------------------
def setProject( projectName, sequenceName ):
    """sets the project
    """
    db = projectModel.Database()
    
    mayaProjectPath = os.path.join( db.getProjectsFullPath(), projectName, sequenceName )
    
    pm.workspace.open(mayaProjectPath)



#----------------------------------------------------------------------
def getWorkspacePath():
    """returns the workspace path
    tries to fix the path separator for windows
    """
    
    path = pm.workspace.name
    
    if os.name == 'nt':
        myDict = dict()
        myDict['/'] = '\\'
        path = oyAux.multiple_replace( path, myDict)
    
    return path
