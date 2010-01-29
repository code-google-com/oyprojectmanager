import os, shutil
from xml.dom import minidom
from oyProjectManager.tools import cache
from oyProjectManager.dataModels import userModel, abstractClasses



__version__ = "10.1.28"






########################################################################
class Repository( abstractClasses.Singleton ):
    """Repository class gives informations about the servers, projects, users etc.
    """
    
    
    
    #----------------------------------------------------------------------
    def __init__(self):
        
        # initialize default variables
        self._repositorySettingsFileName = 'repositorySettings.xml'
        
        self._serverPath = ''
        self._projectsFolderName = ''
        
        self._projectManagerFolderName = ''
        self._projectManagerFolderPath = ''
        self._projectManagerFolderFullPath = ''

        self._projectsFolderFullPath = ''
        self._defaultSettingsFileName = 'defaultProjectSettings.xml'
        self._defaultSettingsFullPath = ''
        
        self._lastUserFileName = '.lastUser'
        self._lastUserFilePath = self.getHomePath()
        self._lastUserFileFullPath = os.path.join( self._lastUserFilePath, self._lastUserFileName )
        
        #self._localSettingsFileName = '.localSettings.xml'
        #self._localSettingsPath = self.getHomePath()
        #self._localSettingsFullPath = os.path( self._localSettingsPath, self._localSettingsFileName )
        
        # users
        self._usersFileName = 'users.xml'
        self._usersFileFullPath = ''
        self._users = [] * 0
        
        self._projects = [] * 0
        self._defaultFilesList = [] * 0
        
        #self._readLocalSettings()
        self._readSettings()
        self._updatePathVariables()
    
    
    
    #----------------------------------------------------------------------
    def _readSettings(self):
        """reads the settings from the xml file at the project root
        """
        
        # get the module root path
        import oyProjectManager
        settingsFilePath = oyProjectManager.__path__[0]
        
        # then the repository settings full path
        settingsFileFullPath = os.path.join( settingsFilePath, self._repositorySettingsFileName )
        
        # open the file
        xmlFile = minidom.parse( settingsFileFullPath )
        
        rootNode = xmlFile.childNodes[0]
        
        # -----------------------------------------------------
        # get the nodes
        settingsNode = rootNode.getElementsByTagName('settings')[0]
        serverNodes = settingsNode.getElementsByTagName('server')
        defaultFilesNode = rootNode.getElementsByTagName('defaultFiles')[0]
        
        #assert(isinstance(settingsNode, minidom.Element))
        #assert(isinstance(defaultFilesNode, minidom.Element))
        
        
        # -----------------------------------------------------
        # read the server settings
        # for now just assume one server
        self._serverPath = serverNodes[0].getAttribute('serverPath')
        self._projectsFolderName = serverNodes[0].getAttribute('projectsFolderName')
        
        
        # read the project manager folder path
        self._projectManagerFolderPath = settingsNode.getAttribute('projectManagerFolderPath')
        self._projectManagerFolderName = settingsNode.getAttribute('projectManagerFolderName')
        self._projectManagerFolderFullPath = os.path.join( self._projectManagerFolderPath, self._projectManagerFolderName )
        
        defaultFilesFolderFullPath = os.path.join( self._projectManagerFolderFullPath, "_defaultFiles_" )
        # read and create the default files list
        for fileNode in defaultFilesNode.getElementsByTagName('file'):
            #assert(isinstance(fileNode, minidom.Element))
            #                                    fileName                          projectRelativePath                       sourcePath
            self._defaultFilesList.append( (fileNode.getAttribute('name'), fileNode.getAttribute('projectRelativePath') , defaultFilesFolderFullPath) )
    
    
    
    #----------------------------------------------------------------------
    def _updatePathVariables(self):
        """updates path variables
        """
        self._projectsFolderFullPath = os.path.join( self._serverPath, self._projectsFolderName)
        self._projectManagerFolderFullPath = os.path.join( self._projectManagerFolderPath, self._projectManagerFolderName )
        self._defaultSettingsFullPath = os.path.join( self._projectManagerFolderFullPath, self._defaultSettingsFileName )
        self._usersFileFullPath = os.path.join( self._projectManagerFolderFullPath, self._usersFileName )
        
        self._users = [] * 0
        self._readUsers()
        
        self._projects = [] * 0
        self.updateProjectList()
        
        # udpate the default files lists third element : the source path
        defaultFilesFolderFullPath = os.path.join( self._projectManagerFolderFullPath, "_defaultFiles_" )
        for fileNode in self._defaultFilesList:
            fileNode = ( fileNode[0], fileNode[1], defaultFilesFolderFullPath )
    
    
    
    #----------------------------------------------------------------------
    #@cache.CachedMethod
    def getProjects(self):
        """returns projects names as a list
        """
        self.updateProjectList()
        return self._projects
    
    
    
    #----------------------------------------------------------------------
    @cache.CachedMethod
    def getValidProjects(self):
        """returns the projectNames only if they are valid projects.
        A project is only valid if there are some valid sequences under it
        """
        
        # get all projects and filter them
        self.updateProjectList()
        
        from oyProjectManager.dataModels import projectModel
        
        validProjectList = [] * 0
        
        for projName in self._projects:
            
            # get sequences of that project
            projObj = projectModel.Project(projName)
            
            seqList = projObj.sequences()
            
            for seq in seqList:
                
                #assert(isinstance(seq, Sequence))
                if seq.isValid():
                    # it has at least one valid sequence
                    validProjectList.append( projName )
                    break
        
        return validProjectList
    
    
    
    #----------------------------------------------------------------------
    def getUsers(self):
        """returns users as a list of User objects
        """
        return self._users
    
    
    
    #----------------------------------------------------------------------
    def getUserNames(self):
        """returns the user names
        """
        names = [] * 0
        for user in self._users:
            names.append( user.name )
        
        return names
    
    
    
    #----------------------------------------------------------------------
    def getUserInitials(self):
        """returns the user intials
        """
        initials = [] * 0
        for user in self._users:
            #assert(isinstance(user,User))
            initials.append( user.initials )
        
        return sorted(initials)
    
    
    
    #----------------------------------------------------------------------
    def _readUsers(self):
        """parses the usersFile
        """
        
        # check if the usersFile exists
        if not os.path.exists( self._usersFileFullPath ):
            return
        
        usersXML = minidom.parse( self._usersFileFullPath )
        
        rootNode = usersXML.childNodes[0]
        
        # -----------------------------------------------------
        # get the users node
        userNodes = rootNode.getElementsByTagName('user')
        
        self._users = [] * 0
        
        for node in userNodes:
            name = node.getAttribute('name')
            initials = node.getAttribute('initials')
            self._users.append( userModel.User(name, initials) )
    
    
    
    #----------------------------------------------------------------------
    def updateProjectList(self):
        """updates the project list variable
        """
        
        if os.path.exists( self._projectsFolderFullPath ):
            self._projects = os.listdir( self._projectsFolderFullPath )
    
    
    
    #----------------------------------------------------------------------
    def getProjectsFullPath(self):
        """returns the projects folder full path
        
        ex : M:/JOBs
        """
        
        return self._projectsFolderFullPath
    
    
    
    #----------------------------------------------------------------------
    def getServerPath(self):
        """gets the server path
        """
        return self._serverPath
    
    
    
    #----------------------------------------------------------------------
    def setServerPath(self, serverPath):
        """sets the server path
        """
        self._serverPath = serverPath + os.path.sep
        
        self._updatePathVariables()
    
    
    
    #----------------------------------------------------------------------
    #def createStructureDataFromPath(self, structurePath ):
        #"""creates structure data of a given path
        #can be used to create new structure definitions for new projects
        #"""
        #structureData = [] * 0
        
        #for dirPath, dirNames, fileNames in os.walk(defaultProjectPath):
            #structureData.append( dirPath[len(defaultProjectPath)+1:len(dirPath)] )
        
        #structureData.sort()
        
        #return structureData
    
    
    
    #----------------------------------------------------------------------
    def getDefaultFiles(self):
        """returns the default files list as list of tuples, the first element contains
        the file name, the second the project relative path, the third the source path
        
        this is the list that contains files those
        need to be copied to every project like workspace.mel for Maya
        """
        
        return self._defaultFilesList
    
    
    
    #----------------------------------------------------------------------
    def getHomePath(self):
        """returns the homePath environment variable
        it is :
        /home/userName/ for linux
        C:\Documents and Settings\userName\My Documents for Windows
        """
        
        homePath = os.environ.get('HOME')
        
        return homePath
    
    
    
    #----------------------------------------------------------------------
    @cache.CachedMethod
    def getLastUser(self):
        """returns the last user initials if the lastUserFile file exists
        otherwise returns None
        """
        
        lastUserInitials = None
        
        try:
            lastUserFile = open( self._lastUserFileFullPath )
        except IOError:
            pass
        else:
            lastUserInitials = lastUserFile.readline().strip()
            lastUserFile.close()
        
        return lastUserInitials
    
    
    
    #----------------------------------------------------------------------
    def setLastUser(self, userInitials):
        """saves the last user initials to the lastUserFile
        """
        
        try:
            lastUserFile = open( self._lastUserFileFullPath, 'w' )
        except IOError:
            pass
        else:
            lastUserFile.write( userInitials )
            lastUserFile.close()
    
    
    
    #----------------------------------------------------------------------
    def getProjectAndSequenceNameFromFilePath(self, filePath):
        """returns the project name and sequence name from the path or fullPath
        """
        
        #assert(isinstance(filePath, (str, unicode)))
        
        if not filePath.startswith( self._projectsFolderFullPath ):
            return None,None
        
        residual = filePath[ len(self._projectsFolderFullPath)+1 : ]
        
        parts = residual.split(os.path.sep)
        
        return parts[0], parts[1]
    
    
    
    ##----------------------------------------------------------------------
    #def _readLocalSettings(self):
        #"""reads the local settings file or creates it
        #"""
        
        ##check if there is a local settings file
        #if os.path.exists( self._localSettingsFullPath ):
            ## parse it
            #self._parseLocalSettings()
        #else:
            ## create it
            #self._saveLocalSettings()
            ## then parse it
            #self._parseLocalSettings()
    
    
    
    ##----------------------------------------------------------------------
    #def _parseLocalSettings(self):
        #"""parses the local settings xml file
        #"""
        
        #settingsFile = minidom.parse( self._localSettingsFullPath )
        
        #rootNode = settingsFile.childNodes[0]
        #programsNode = rootNode.childNodes[0]
        
        #allProgramNodes = programsNode.childNodes
        
        #for program in allProgramNodes:
            #programName = program.getAttr('name')
            
            #recentFilesNode = program.childNodes[0]
            #recentFiles = recentFilesNode.childNodes[0].wholeText.splitlines()
        
        
        
        # read the last user
        
        
        
        # read the program settings
        
    
    
    
    ##----------------------------------------------------------------------
    #def _saveLocalSettings(self):
        #"""saves the 
        #"""
    
    
    
    ##----------------------------------------------------------------------
    #def getRecentFile(self, environmentName):
        #"""returns the recent file from the given environment
        #"""
        
        