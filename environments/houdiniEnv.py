"""
houdiniEnv.py by Erkan Ozgur Yilmaz (c) 2009

Description:
------------
the houdini environment part of the asset management system...

has commands to save, open and import houdini files

"""



import os
import hou
from oyProjectManager.dataModels import assetModel, projectModel, abstractClasses
import oyAuxiliaryFunctions as oyAux



__version__ = "9.12.26"






########################################################################
class HoudiniEnvironment(abstractClasses.Environment):
    """the houdini environment class
    """
    
    #----------------------------------------------------------------------
    def save(self):
        """the save action for houdini environment
        """
        
        # set the extension to hip
        self._asset.setExtension('hip')
        
        # create the folder if it doesn't exists
        oyAux.createFolder( self._asset.getPath() )
        
        # houdini uses / instead of \ under windows
        # lets fix it
        
        fullPath = self._asset.getFullPath()
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
        
        fullPath = self._asset.getFullPath()
        fullPath = fullPath.replace('\\','/')
        
        hou.hipFile.load( file_name = str(fullPath) , suppress_save_prompt=True )
        
        # set the environment variables
        self.setEnvironmentVariables()
        
        return True
    
    
    
    #----------------------------------------------------------------------
    def import_(self):
        """the import action for houdini environment
        """
        
        fullPath = self._asset.getFullPath()
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
        
        db = projectModel.Database()
        
        fullPath = hou.hipFile.name()
        
        # unfix windows path
        if os.name == 'nt':
            fullPath = fullPath.replace('/','\\')
        
        
        if fullPath != 'untitled.hip':
            fileName = os.path.basename( fullPath )
            path = os.path.dirname( fullPath )
            
            # try to create an asset with that info
            projName, seqName = db.getProjectAndSequenceNameFromFilePath( fullPath )
            
            proj = projectModel.Project( projName )
            seq = projectModel.Sequence( proj, seqName )
            
            testAsset = assetModel.Asset( proj, seq, fileName )
            
            #if path != '':
                #fileName = os.path.basename( fullPath )
            #else:
                #path = None
            if testAsset.isValidAsset():
                fileName = testAsset.getFileName()
                path = testAsset.getPath()
                readRecentFile = False
        
        if readRecentFile:
            # there is no file oppend yet use the first valid file
            # from the recent files list
            
            recentFiles = self.getRecentFileList()
            
            # unfix the windows paths from / to \\
            if os.name == 'nt':
                recentFiles = [ recentFile.replace('/','\\') for recentFile in recentFiles ]
            
            for i in range(len(recentFiles)):
                
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
        os.environ['JOB'] = str( self._asset.getSequenceFullPath()).replace('\\','/')
    
    
    
    #----------------------------------------------------------------------
    def getRecentFileList(self):
        """returns the recent HIP files list from the houdini
        """
        
        # use a FileHistory object
        fHist = FileHistory()
        
        # get the hip files list
        recentHipFiles = fHist.getRecentFiles('HIP')
        
        return recentHipFiles






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
        
        historyFile = open( self._historyFileFullPath )
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