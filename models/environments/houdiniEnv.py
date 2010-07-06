"""
houdiniEnv.py by Erkan Ozgur Yilmaz (c) 2009-2010

Description:
------------
the houdini environment part of the asset management system...

has commands to save, open and import houdini files

"""



import os
import hou
import re
from oyProjectManager.models import asset, project, repository, abstractClasses
import oyAuxiliaryFunctions as oyAux



__version__ = "10.7.6"






########################################################################
class HoudiniEnvironment(abstractClasses.Environment):
    """the houdini environment class
    """
    
    #----------------------------------------------------------------------
    def save(self):
        """the save action for houdini environment
        """
        
        # set the extension to hip
        self._asset.extension = 'hip'
        
        # create the folder if it doesn't exists
        oyAux.createFolder( self._asset.path )
        
        # houdini uses / instead of \ under windows
        # lets fix it
        
        fullPath = self._asset.fullPath
        fullPath = fullPath.replace('\\','/')
        
        # houdini accepts only strings as file name, no unicode support as I see
        hou.hipFile.save( file_name = str(fullPath) )
        
        # set the environment variables
        self.setEnvironmentVariables()
        
        return True
    
    
    
    #----------------------------------------------------------------------
    def open_(self, force=False ):
        """the open action for houdini environment
        """
        
        if hou.hipFile.hasUnsavedChanges() and not force:
            raise RuntimeError
        
        fullPath = self._asset.fullPath
        fullPath = fullPath.replace('\\','/')
        
        hou.hipFile.load( file_name = str(fullPath) , suppress_save_prompt=True )
        
        # set the environment variables
        self.setEnvironmentVariables()
        
        return True
    
    
    
    #----------------------------------------------------------------------
    def import_(self):
        """the import action for houdini environment
        """
        
        fullPath = self._asset.fullPath
        fullPath = fullPath.replace('\\','/')
        
        hou.hipFile.merge( str(fullPath) )
        
        return True
    
    
    
    #----------------------------------------------------------------------
    def getPathVariables(self):
        """gets the file name from houdini environment
        """
        
        foundValidAsset = False
        readRecentFile = True
        fileName = path = None
        
        #db = project.Database()
        repo = repository.Repository()
        
        fullPath = hou.hipFile.name()
        
        # unfix windows path
        if os.name == 'nt':
            fullPath = fullPath.replace('/','\\')
        
        
        if fullPath != 'untitled.hip':
            fileName = os.path.basename( fullPath )
            path = os.path.dirname( fullPath )
            
            # try to create an asset with that info
            projName, seqName = repo.getProjectAndSequenceNameFromFilePath( fullPath )
            
            proj = project.Project( projName )
            seq = project.Sequence( proj, seqName )
            
            testAsset = asset.Asset( proj, seq, fileName )
            
            #if path != '':
                #fileName = os.path.basename( fullPath )
            #else:
                #path = None
            if testAsset.isValidAsset:
                fileName = testAsset.fileName
                path = testAsset.path
                readRecentFile = False
        
        if readRecentFile:
            # there is no file oppend yet use the first valid file
            # from the recent files list
            
            recentFiles = self.getRecentFileList()
            
            # unfix the windows paths from / to \\
            if os.name == 'nt':
                recentFiles = [ recentFile.replace('/','\\') for recentFile in recentFiles ]
            
            for i in range(len(recentFiles)-1,0,-1):
                
                fileName = os.path.basename( recentFiles[i] )
                projName, seqName = repo.getProjectAndSequenceNameFromFilePath( recentFiles[i] )
                
                if projName != None and seqName != None:
                    
                    proj = project.Project( projName )
                    seq = project.Sequence( proj, seqName )
                    
                    testAsset = asset.Asset( proj, seq, fileName )
                    
                    if testAsset.isValidAsset:
                        path = testAsset.path
                        foundValidAsset = True
                        break
            
    ##        # get the workspace path
    ##        workspacePath = os.getenv('JOB')
    ##        returnWorkspace = False
    ##        
    ##        workspaceIsValid = False
    ##        
    ##        if workspacePath != '' and workspacePath != None:
    ##            workspaceIsValid = True
    ##        
    ##        if foundValidAsset:
    ##            #print "found a valid asset with path", path
    ##            
    ##            # check if teh recent files path matches the current workspace
    ##            if not path.startswith( workspacePath ) and workspaceIsValid:
    ##                # use the workspacePath
    ##                returnWorkspace = True
    ##        else:
    ##            # just get the path from workspace and return an empty fileName
    ##            returnWorkspace = True
    ##        
    ##        if returnWorkspace and workspaceIsValid:
    ##            fileName = None
    ##            path = workspacePath
        
        return fileName, path
    
    
    
    #----------------------------------------------------------------------
    def setEnvironmentVariables(self):
        """sets the environment variables according to the given assetObject
        """
        # set the $JOB variable to the sequence root
        os.environ['JOB'] = str( self._asset.sequenceFullPath ).replace('\\','/')
    
    
    
    #----------------------------------------------------------------------
    def getRecentFileList(self):
        """returns the recent HIP files list from the houdini
        """
        
        # use a FileHistory object
        fHist = FileHistory()
        
        # get the hip files list
        recentHipFiles = fHist.getRecentFiles('HIP')
        
        return recentHipFiles
    
    
    
    #----------------------------------------------------------------------
    def getFrameRange(self):
        """returns the frame range of the
        """
        # use the hscript commands to get the frame range
        timeInfo = hou.hscript('tset')[0].split('\n')
        
        pattern = r'[0-9\.]+'
        
        startFrame = int( hou.timeToFrame( float( re.search( pattern, timeInfo[2] ).group(0) ) ) )
        duration = int( re.search( pattern, timeInfo[0] ).group(0) )
        endFrame = startFrame + duration - 1
        
        return startFrame, endFrame
    
    
    
    #----------------------------------------------------------------------
    def setFrameRange(self, startFrame=1, endFrame=100):
        """sets the frame range
        """
        
        # --------------------------------------------
        # set the timeline
        currFrame = hou.frame()
        if currFrame < startFrame:
            hou.setFrame( startFrame )
        elif currFrame > endFrame:
            hou.setFrame( endFrame )
        
        # for now use hscript, the python version is not implemented yet
        hou.hscript('tset `('+ str(startFrame) +'-1)/$FPS` `'+ str(endFrame)+'/$FPS`')
        
        # --------------------------------------------
        # Set the render nodes frame ranges if any
        # get the out nodes
        ropContext = hou.node('/out')
        
        # get the children
        outNodes = ropContext.children()
        
        if len(outNodes):
            for outNode in outNodes:
                outNode.setParms( {'trange':1,'f1':startFrame,'f2':endFrame,'f3':1})
    
    
    
    #----------------------------------------------------------------------
    def getTimeUnit(self):
        """returns the current time unit
        """
        
        repo = repository.Repository()
        timeUnits = repo.timeUnits
        
        currentFps = str(hou.fps())
        
        timeUnit = 'pal'
        
        for timeUnitName, timeUnitFps in timeUnits.iteritems():
            if currentFps == timeUnitFps:
                timeUnit = timeUnitName
                break
        
        return timeUnit
    
    
    
    #----------------------------------------------------------------------
    def setTimeUnit(self, timeUnit='pal'):
        """sets the time unit of the environment
        """
        
        repo = repository.Repository()
        
        try:
            timeUnitFps = float(repo.timeUnits[timeUnit])
        except KeyError:
            # set it to pal by default
            timeUnit='pal'
            timeUnitFps = float(repo.timeUnits[timeUnit])
        
        # keep the current start and end time of the time range
        startFrame, endFrame = self.getFrameRange()
        hou.setFps( timeUnitFps )
        
        self.setFrameRange( startFrame, endFrame)






########################################################################
class FileHistory( abstractClasses.Singleton ):
    """a houdini recent file history parser
    
    holds the data in a dictionary, where the keys are the file types and the
    values are string list of recent file paths of that type
    """
    
    #----------------------------------------------------------------------
    def __init__(self):
        self._historyFileName = 'file.history'
        
        self._historyFilePath = ''
        
        if os.name == 'nt':
            # under windows the HIH is useless
            # interpret the HIH from POSE environment variable
            
            self._historyFilePath = os.path.dirname( os.getenv('POSE') )
        else:
            self._historyFilePath = os.getenv('HIH')
        
        self._historyFileFullPath = os.path.join( self._historyFilePath, self._historyFileName )
        
        self._buffer =  []
        
        self._history = dict()
        
        self._read()
        self._parse()
    
    
    
    #----------------------------------------------------------------------
    def _read(self):
        """reads the history file to a buffer
        """
        try:
            historyFile = open( self._historyFileFullPath )
        except IOError:
            self._buffer = []
            return
        
        self._buffer = historyFile.readlines()
        
        # strip all the lines
        self._buffer = [ line.strip() for line in self._buffer ]
        
        historyFile.close()
    
    
    
    #----------------------------------------------------------------------
    def _parse(self):
        """parses the data in self._buffer
        """
        
        self._history = dict()
        
        bufferList = self._buffer
        
        keyName = ''
        pathList = []
        
        lenBuffer = len(bufferList)
        
        for i in range(lenBuffer):
            
            # try to find a '{'
            if bufferList[i] == '{':
                # create a key with the previous line
                keyName = bufferList[i-1]
                pathList = []
                
                # starting from the next line
                for j in range(i+1, lenBuffer ):
                    
                    # add all the lines to the pathList until you find a '}'
                    currentElement = bufferList[j]
                    if  currentElement != '}':
                        pathList.append( currentElement )
                    else:
                        # set i to j+1 and let it continue
                        i = j + 1
                        break
                
                # append the key and data to the dictionary
                self._history[ keyName ] = pathList
    
    
    
    #----------------------------------------------------------------------
    def getRecentFiles(self, typeName=''):
        """returns the file list of the given file type
        """
        
        if typeName == '' or typeName == None:
            return []
        else:
            if self._history.has_key( typeName ):
                return self._history[ typeName ]
            else:
                return []