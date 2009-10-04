import os
import pymel as pm
from oyProjectManager.dataModels import assetModel, projectModel



#----------------------------------------------------------------------
def save( assetObject ):
    """the save action for maya environment
    
    uses PyMel to save the file (not necessary but comfortable )
    """
    
    # set the extension to ma by default
    #assert(isinstance(assetObject, assetModel.Asset))
    assetObject.setExtension( 'ma' )
    
    # set the project to the current environment
    pm.workspace.open( assetObject.getSequenceFullPath() )
    
    # set the render file name and version
    setRenderFileName( assetObject )
    
    # set the playblast file name
    setPlayblastFileName( assetObject )
    
    # save the file
    pm.saveAs( assetObject.getFullPath(), type='mayaAscii' )
    
    return True



#----------------------------------------------------------------------
def open_():
    """the open action for maya environment
    """
    pass



#----------------------------------------------------------------------
def import_():
    """the import action for maya environment
    """
    pass



#----------------------------------------------------------------------
def reference():
    """the reference action for maya environment
    """
    pass



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
        path = pm.workspace.name
    
    return fileName, path



#----------------------------------------------------------------------
def setRenderFileName( assetObject ):
    """sets the render file name
    """
    assert(isinstance(assetObject,assetModel.Asset))
    parentSeq = assetObject.getParentSequence()
    
    renderOutputFolder = parentSeq.getStructure().getOutputFolderPathOf( 'RENDER' ) # _RENDERED_IMAGES_/SHOTS
    
    # image folder from the workspace.mel
    imageFolderFromWS = pm.workspace.fileRules['image'] # _RENDERED_IMAGES_/
    
    shotFolder = renderOutputFolder[ len(imageFolderFromWS):] # SHOTS
    
    assetBaseName = assetObject.getBaseName()
    renderFileName = shotFolder + "/" + assetBaseName + "/<Layer>/" + assetBaseName + "_<Layer>_<RenderPass>_<Version>"
    
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
