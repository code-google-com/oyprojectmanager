import os
import pymel as pm
import oyAuxiliaryFunctions as oyAux
from oyProjectManager.dataModels import assetModel, projectModel



__version__ = "9.11.22"



#----------------------------------------------------------------------
def save( assetObject ):
    """the save action for maya environment
    
    uses PyMel to save the file (not necessary but comfortable )
    """
    
    # set the extension to ma by default
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
    
    # append it to the recent file list
    appendToRecentFiles( assetObject.getFullPath() )
    
    return True




#----------------------------------------------------------------------
def export( assetObject ):
    """the export action for maya environment
    """
    
    # check if there is something selected
    if len(pm.ls(sl=True)) < 1:
        print "selection error"
        return False
    
    # set the extension to ma by default
    assetObject.setExtension( 'ma' )
    
    # create the folder if it doesn't exists
    oyAux.createFolder( assetObject.getPath() )
    
    # export the file
    pm.exportSelected( assetObject.getFullPath(), type='mayaAscii' )
    
    return True



#----------------------------------------------------------------------
def open_( assetObject, force=False):
    """the open action for maya environment
    """
    assert(isinstance(assetObject, assetModel.Asset ) )
    
    # check for unsaved changes
    assetFullPath = assetObject.getFullPath()
    
    pm.openFile( assetFullPath, f=force )
    
    # set the project
    pm.workspace.open( assetObject.getSequenceFullPath() )
    
    # set the playblast folder
    setPlayblastFileName( assetObject )
    
    appendToRecentFiles( assetFullPath )
    
    # check the referenced assets for newer version
    toUpdateList = checkReferenceVersions()
    
    #print toUpdateList
    
    return True, toUpdateList



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
    
    assert( isinstance(assetObject, assetModel.Asset ) )
    
    # use the file name without extension as the namespace
    nameSpace = assetObject.getFileNameWithoutExtension()
    
    pm.createReference( assetObject.getFullPath(), gl=True, loadReferenceDepth='all', namespace=nameSpace, options='v=0')
    
    return True



#----------------------------------------------------------------------
def getPathVariables():
    """gets the file name from maya environment
    """
    
    foundValidAsset = False
    readRecentFile = True
    fileName = path = None
    
    db = projectModel.Database()
    
    fullPath = pm.env.sceneName()
    if os.name == 'nt':
        fullPath = oyAux.fixWindowsPath(fullPath)
    
    print "the fullPath in maya is ", fullPath
    
    if fullPath != '':
        fileName = os.path.basename( fullPath )
        
        # try to create an asset with that info
        projName, seqName = db.getProjectAndSequenceNameFromFilePath( fullPath )
        
        proj = projectModel.Project( projName )
        seq = projectModel.Sequence( proj, seqName )
        
        testAsset = assetModel.Asset( proj, seq, fileName )
        
        if testAsset.isValidAsset():
            fileName = testAsset.getFileName()
            path = testAsset.getPath()
            readRecentFile = False
    
    if readRecentFile:
        # read the fileName from recent files list
        # try to get the a valid asset file from starting the last recent file
        
        recentFiles = pm.optionVar['RecentFilesList']
        for i in range(len(recentFiles)-1, -1,-1):
            
            fileName = os.path.basename( recentFiles[i] )
            projName, seqName = db.getProjectAndSequenceNameFromFilePath( recentFiles[i] )
            
            if projName != None and seqName != None:
            
                proj = projectModel.Project( projName )
                seq = projectModel.Sequence( proj, seqName )
                
                testAsset = assetModel.Asset( proj, seq, fileName )
                if testAsset.isValidAsset():
                    path = testAsset.getPath()
                    foundValidAsset = True
                    break
        
        # get the workscape path
        workspacePath = getWorkspacePath()
        returnWorkspace = False
        
        if foundValidAsset:
            print "found a valid asset with path", path
            # check if the recent files path matches the current workspace
            if not path.startswith( workspacePath ):
                # use the workspacePath
                returnWorkspace = True
        else:
            # just get the path from workspace and return an empty fileName
            returnWorkspace = True
        
        if returnWorkspace:
            fileName = None
            path = workspacePath

    
    return fileName, path



#----------------------------------------------------------------------
def setRenderFileName( assetObject ):
    """sets the render file name
    """
    
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
        #myDict = dict()
        #myDict[u'/'] = u'\\'
        #path = oyAux.multiple_replace( path, myDict)
        path = oyAux.fixWindowsPath( path )
    
    return path



#----------------------------------------------------------------------
def appendToRecentFiles(path):
    """appends the given path to the recent files list
    """
    
    # add the file to the recent file list
    recentFiles = pm.optionVar['RecentFilesList']
    
    #assert(isinstance(recentFiles,pm.OptionVarList))
    
    recentFiles.appendVar( path )
    #pm.optionVar['RecentFilesList'] = recentFiles




#----------------------------------------------------------------------
def checkReferenceVersions():
    """checks the referenced assets versions
    """
    
    # get all the valid asset references
    assets = getValidReferencedAssets()
    
    updateList = []
    
    for asset in assets:
        #assert(isinstance(asset, assetModel.Asset))
        
        if not asset.isLatestVersion():
            # add asset to the update list
            
            updateList.append( asset.getFileName() )
    
    # for now just return the list that contains the asset file names those
    # need to be updated
    
    return updateList




#----------------------------------------------------------------------
def getValidReferencedAssets():
    """returns the valid assets those been referenced to the current scene
    """
    
    validAssets = []
    
    # get all the references
    allReferences = pm.listReferences()
    
    # create a database object
    db = projectModel.Database()
    
    # iterate over them to find valid assets
    for ref in allReferences:
        # it is a dictionary
        
        #assert(isinstance(ref, pm.FileReference))
        tempAssetFullPath = ref.path
        tempAssetPath = os.path.basename( tempAssetFullPath )
        
        projName, seqName = db.getProjectAndSequenceNameFromFilePath( tempAssetFullPath )
        proj = projectModel.Project( projName )
        seq = projectModel.Sequence( proj, seqName )
        
        tempAsset = assetModel.Asset( proj, seq, tempAssetPath )
        
        if tempAsset.isValidAsset():
            validAssets.append( tempAsset )
    
    return validAssets