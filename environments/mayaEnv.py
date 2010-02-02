import os
import pymel as pm
import oyAuxiliaryFunctions as oyAux
from oyProjectManager.dataModels import assetModel, projectModel, repositoryModel, abstractClasses



__version__ = "10.1.28"






########################################################################
class MayaEnvironment(abstractClasses.Environment):
    """the maya environment class
    """
    
    
    
    #----------------------------------------------------------------------
    def save(self):
        """the save action for maya environment
        
        uses PyMel to save the file (not necessary but comfortable )
        """
        
        # set the extension to ma by default
        self._asset.extension = 'ma'
        
        # set the project to the current environment
        pm.workspace.open( self._asset.sequenceFullPath )
        
        # set the render file name and version
        self.setRenderFileName()
        
        # set the playblast file name
        self.setPlayblastFileName()
        
        # create the folder if it doesn't exists
        oyAux.createFolder( self._asset.path )
        
        # save the file
        pm.saveAs( self._asset.fullPath, type='mayaAscii' )
        
        # append it to the recent file list
        self.appendToRecentFiles( self._asset.fullPath )
        
        return True
    
    
    
    #----------------------------------------------------------------------
    def export(self):
        """the export action for maya environment
        """
        
        # check if there is something selected
        if len(pm.ls(sl=True)) < 1:
            print "selection error"
            return False
        
        # set the extension to ma by default
        self._asset.extension = 'ma'
        
        # create the folder if it doesn't exists
        oyAux.createFolder( self._asset.path )
        
        # export the file
        pm.exportSelected( self._asset.fullPath, type='mayaAscii' )
        
        return True
    
    
    
    #----------------------------------------------------------------------
    def open_(self, force=False):
        """the open action for maya environment
        
        returns assets those needs to be updated as a list of asset objects
        """
        
        # check for unsaved changes
        assetFullPath = self._asset.fullPath
        
        pm.openFile( assetFullPath, f=force )
        
        # set the project
        pm.workspace.open( self._asset.sequenceFullPath )
        
        # set the playblast folder
        self.setPlayblastFileName()
        
        self.appendToRecentFiles( assetFullPath )
        
        # check the referenced assets for newer version
        toUpdateList = self.checkReferenceVersions()
        
        return True, toUpdateList
    
    
    
    #----------------------------------------------------------------------
    def import_(self):
        """the import action for maya environment
        """
        pm.importFile( self._asset.fullPath )
        
        return True
    
    
    
    #----------------------------------------------------------------------
    def reference(self):
        """the reference action for maya environment
        """
        
        # use the file name without extension as the namespace
        nameSpace = self._asset.fileNameWithoutExtension
        
        pm.createReference( self._asset.fullPath, gl=True, loadReferenceDepth='all', namespace=nameSpace, options='v=0')
        
        return True
    
    
    
    #----------------------------------------------------------------------
    def getPathVariables(self):
        """gets the file name from maya environment
        """
        
        foundValidAsset = False
        readRecentFile = True
        fileName = path = None
        
        repo = repositoryModel.Repository()
        
        fullPath = pm.env.sceneName()
        if os.name == 'nt':
            fullPath = fullPath.replace('/','\\')
        
        #print "the fullPath in maya is ", fullPath
        
        if fullPath != '':
            fileName = os.path.basename( fullPath )
            
            # try to create an asset with that info
            projName, seqName = repo.getProjectAndSequenceNameFromFilePath( fullPath )
            
            proj = projectModel.Project( projName )
            seq = projectModel.Sequence( proj, seqName )
            
            testAsset = assetModel.Asset( proj, seq, fileName )
            
            if testAsset.isValidAsset:
                fileName = testAsset.fileName
                path = testAsset.path
                readRecentFile = False
        
        if readRecentFile:
            # read the fileName from recent files list
            # try to get the a valid asset file from starting the last recent file
            
            recentFiles = pm.optionVar['RecentFilesList']
            for i in range(len(recentFiles)-1, -1,-1):
                
                fileName = os.path.basename( recentFiles[i] )
                projName, seqName = repo.getProjectAndSequenceNameFromFilePath( recentFiles[i] )
                
                if projName != None and seqName != None:
                
                    proj = projectModel.Project( projName )
                    seq = projectModel.Sequence( proj, seqName )
                    
                    testAsset = assetModel.Asset( proj, seq, fileName )
                    if testAsset.isValidAsset:
                        path = testAsset.path
                        foundValidAsset = True
                        break
            
            # get the workscape path
            workspacePath = self.getWorkspacePath()
            returnWorkspace = False
            
            if foundValidAsset:
                #print "found a valid asset with path", path
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
    def setRenderFileName(self):
        """sets the render file name
        """
        
        # check/load Mentalray
        #if pm.pluginInfo(
        
        parentSeq = self._asset.parentSequence
        
        renderOutputFolder = parentSeq.structure.getOutputFolderPathOf( 'RENDER' ) # _RENDERED_IMAGES_/SHOTS
        
        # image folder from the workspace.mel
        imageFolderFromWS = pm.workspace.fileRules['image'] # _RENDERED_IMAGES_/
        
        shotFolder = renderOutputFolder[ len(imageFolderFromWS):] # SHOTS
        
        assetBaseName = self._asset.baseName
        
        renderFileName = ''
        if parentSeq.noSubNameField():
            renderFileName = shotFolder + "/" + assetBaseName + "/<Layer>/" + assetBaseName + "_<Layer>_<RenderPass>_<Version>"
        else: # remove later when the support for old project is over
            assetSubName = self._asset.subName
            renderFileName = shotFolder + "/" + assetBaseName + "/<Layer>/" + assetBaseName + "_" + assetSubName + "_<Layer>_<RenderPass>_<Version>"
        
        # defaultRenderGlobals
        dRG = pm.PyNode('defaultRenderGlobals')
        dRG.setAttr('imageFilePrefix', renderFileName)
        dRG.setAttr('renderVersion', self._asset.versionString )
        dRG.setAttr('animation', 1)
        dRG.setAttr('outFormatControl', 0 )
        dRG.setAttr('extensionPadding', 3 )
        dRG.setAttr('pff', 1)
    
    
    
    #----------------------------------------------------------------------
    def setPlayblastFileName(self):
        """sets the playblast file name
        """
        
        playblastFolderPath = self._asset.type.playblastFolder
        
        if os.name == 'nt':
            playblastFolderPath = playblastFolderPath.replace('/','\\')
        
        assert(isinstance(self._asset, assetModel.Asset))
        
        seqFullPath = self._asset.parentSequence.fullPath
        
        baseName = self._asset.baseName
        
        playblastFullPath = os.path.join( seqFullPath, playblastFolderPath, baseName, self._asset.fileNameWithoutExtension ) + '.avi'
        
        pm.optionVar['playblastFile'] = playblastFullPath
    
    
    
    #----------------------------------------------------------------------
    def setProject(self, projectName, sequenceName ):
        """sets the project
        """
        repo = repositoryModel.Repository()
        
        mayaProjectPath = os.path.join( repo.getProjectsFullPath(), projectName, sequenceName )
        
        pm.workspace.open(mayaProjectPath)
    
    
    
    #----------------------------------------------------------------------
    def getWorkspacePath(self):
        """returns the workspace path
        tries to fix the path separator for windows
        """
        
        path = pm.workspace.name
        
        if os.name == 'nt':
            path = path.replace('/','\\')
        
        return path
    
    
    
    #----------------------------------------------------------------------
    def appendToRecentFiles(self, path):
        """appends the given path to the recent files list
        """
        
        # add the file to the recent file list
        recentFiles = pm.optionVar['RecentFilesList']
        
        #assert(isinstance(recentFiles,pm.OptionVarList))
        
        recentFiles.appendVar( path )
        #pm.optionVar['RecentFilesList'] = recentFiles
    
    
    
    #----------------------------------------------------------------------
    def checkReferenceVersions(self):
        """checks the referenced assets versions
        
        returns a list of asset and maya reference objects in a tupple
        """
        
        # get all the valid asset references
        assetTupleList = self.getValidReferencedAssets()
        
        updateList = []
        
        for assetTuple in assetTupleList:
            #assert(isinstance(asset, assetModel.Asset))
            
            asset = assetTuple[0]
            
            if not asset.isLatestVersion():
                # add asset to the update list
                updateList.append( assetTuple )
        
        return updateList
    
    
    
    #----------------------------------------------------------------------
    def getValidReferencedAssets(self):
        """returns the valid assets those been referenced to the current scene
        
        returns asset objects and the corresponding reference object as a
        tupple in a list
        """
        
        validAssets = []
        
        # get all the references
        allReferences = pm.listReferences()
        
        # create a repository object
        repo = repositoryModel.Repository()
        
        # iterate over them to find valid assets
        for ref in allReferences:
            # it is a dictionary
            
            #assert(isinstance(ref, pm.FileReference))
            tempAssetFullPath = ref.path
            if os.name == 'nt':
                tempAssetFullPath = tempAssetFullPath.replace('/','\\')
            
            tempAssetPath = os.path.basename( tempAssetFullPath )
            
            #print "tempAssetFullPath".ljust(25), ":", tempAssetFullPath
            #print "tempAssetPath".ljust(25), ":", tempAssetPath
            
            projName, seqName = repo.getProjectAndSequenceNameFromFilePath( tempAssetFullPath )
            proj = projectModel.Project( projName )
            seq = projectModel.Sequence( proj, seqName )
            
            tempAsset = assetModel.Asset( proj, seq, tempAssetPath )
            
            if tempAsset.isValidAsset:
                validAssets.append( (tempAsset, ref) )
        
        return validAssets
    
    
    
    #----------------------------------------------------------------------
    def updateAssets(self, assetTupleList):
        """update assets to the lates version
        """
        
        for assetTuple in assetTupleList:
            
            asset = assetTuple[0]
            ref = assetTuple[1]
            
            #assert(isinstance(asset, assetModel.Asset))
            #assert(isinstance(ref, pm.FileReference))
            
            latestAsset = asset.latestVersion2[0]
            
            ref.replaceWith( latestAsset.fullPath )
    
    
    
    #----------------------------------------------------------------------
    def getFrameRange(self):
        """returns the current playback frame range
        """
        startFrame = int( pm.playbackOptions(q=True, ast=True) )
        endFrame = int( pm.playbackOptions(q=True, aet=True) )
        return startFrame, endFrame
    
    
    
    #----------------------------------------------------------------------
    def setFrameRange(self, startFrame=1, endFrame=100):
        """sets the start and end frame range
        """
        
        # set it in the playback
        pm.playbackOptions(ast=startFrame, aet=endFrame)
        
        # set in the render range
        dRG = pm.PyNode('defaultRenderGlobals')
        dRG.setAttr('startFrame', startFrame )
        dRG.setAttr('endFrame', endFrame )
        