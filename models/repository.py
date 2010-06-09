import os, shutil
import oyAuxiliaryFunctions as oyAux
from xml.dom import minidom
from oyProjectManager.utils import cache
from oyProjectManager.models import user, abstractClasses



__version__ = "10.6.6"






########################################################################
class Repository( abstractClasses.Singleton ):
    """Repository class gives informations about the servers, projects, users etc.
    """
    
    
    
    #----------------------------------------------------------------------
    def __init__(self):
        
        # initialize default variables
        
        # find where am I installed
        self._packagePath = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
        self._settingsDirPath = os.path.join( self._packagePath, 'settings' )
        
        
        # Repository Settings File ( repositorySettings.xml )
        self._repositorySettingsFileName = 'repositorySettings.xml'
        self._repositorySettingsFilePath = self._settingsDirPath
        self._repositorySettingsFileFullPath = os.path.join( self._repositorySettingsFilePath, self._repositorySettingsFileName )
        
        # Default Settings File ( defaultSettings.xml )
        self._defaultSettingsFileName = 'defaultProjectSettings.xml'
        self._defaultSettingsFilePath = self._settingsDirPath
        self._defaultSettingsFileFullPath = os.path.join( self._defaultSettingsFilePath, self._defaultSettingsFileName )
        
        # Default Files Folder Path ( _defaultFiles_ )
        self._defaultFilesFolderFullPath = os.path.join( self._settingsDirPath, '_defaultFiles_' )
        
        # JOBs folder settings ( M:/, JOBs )
        self._serverPath = ''
        self._projectsFolderName = ''
        self._projectsFolderFullPath = ''
        
        # ---------------------------------------------------
        # Last User File
        # ---------------------------------------------------
        self._lastUserFileName = '.lastUser'
        self._lastUserFilePath = self.homePath
        self._lastUserFileFullPath = os.path.join( self._lastUserFilePath, self._lastUserFileName )
        
        #self._localSettingsFileName = '.localSettings.xml'
        #self._localSettingsPath = self.getHomePath()
        #self._localSettingsFullPath = os.path( self._localSettingsPath, self._localSettingsFileName )
        
        # ---------------------------------------------------
        # Users Settings File
        # ---------------------------------------------------
        self._usersFileName = 'users.xml'
        self._usersFilePath = self._settingsDirPath
        self._usersFileFullPath = os.path.join( self._usersFilePath, self._usersFileName )
        self._users = [] * 0
        
        self._projects = [] * 0
        self._defaultFilesList = [] * 0
        
        # ---------------------------------------------------
        # UNITS
        # ---------------------------------------------------
        # 
        # Only time units are implemented for now,
        # the rest will be added when they are first needed
        # 
        self._timeUnits = {}
        #self._linearUnits = {}
        #self._angularUnits = {}
        
        # ---------------------------------------------------
        
        #self._readLocalSettings()
        self._readSettings()
        self._readUsers()
        #self._updatePathVariables()
    
    
    
    #----------------------------------------------------------------------
    def _readSettings(self):
        """reads the repository settings from the xml file at the project root
        """
        
        # open the repository settings file
        xmlFile = minidom.parse( self._repositorySettingsFileFullPath )
        
        rootNode = xmlFile.childNodes[0]
        
        # -----------------------------------------------------
        # get the nodes
        settingsNode = rootNode.getElementsByTagName('settings')[0]
        serverNodes = settingsNode.getElementsByTagName('server')
        defaultFilesNode = rootNode.getElementsByTagName('defaultFiles')[0]
        
        #assert(isinstance(settingsNode, minidom.Element))
        #assert(isinstance(defaultFilesNode, minidom.Element))
        
        timeNodes = rootNode.getElementsByTagName('time')
        
        for timeNode in timeNodes:
            name = timeNode.getAttribute('name')
            fps = timeNode.getAttribute('fps')
            self._timeUnits[ name ] = fps
        
        # -----------------------------------------------------
        # read the server settings
        # for now just assume one server
        
        self._projectsFolderName = serverNodes[0].getAttribute('projectsFolderName')
        self.serverPath = serverNodes[0].getAttribute('serverPath')
        
        
        # read and create the default files list
        for fileNode in defaultFilesNode.getElementsByTagName('file'):
            #assert(isinstance(fileNode, minidom.Element))
            #                                           fileName                          projectRelativePath                         sourcePath
            self._defaultFilesList.append( (fileNode.getAttribute('name'), fileNode.getAttribute('projectRelativePath') , self._defaultFilesFolderFullPath) )
        
        # -----------------------------------------------------
        # read the environment settings
        
    
    
    
    ##----------------------------------------------------------------------
    #def _updatePathVariables(self):
        #"""updates path variables
        #"""
    
    
    
    #----------------------------------------------------------------------
    #@cache.CachedMethod
    @property
    def projects(self):
        """returns projects names as a list
        """
        self.updateProjectList()
        return self._projects
    
    
    
    #----------------------------------------------------------------------
    @cache.CachedMethod
    @property
    def validProjects(self):
        """returns the projectNames only if they are valid projects.
        A project is only valid if there are some valid sequences under it
        """
        
        # get all projects and filter them
        self.updateProjectList()
        
        from oyProjectManager.models import project
        
        validProjectList = [] * 0
        
        for projName in self._projects:
            
            # get sequences of that project
            projObj = project.Project(projName)
            
            seqList = projObj.sequences()
            
            for seq in seqList:
                
                #assert(isinstance(seq, Sequence))
                if seq.isValid():
                    # it has at least one valid sequence
                    validProjectList.append( projName )
                    break
        
        return validProjectList
    
    
    
    #----------------------------------------------------------------------
    @property
    def users(self):
        """returns users as a list of User objects
        """
        return self._users
    
    
    
    #----------------------------------------------------------------------
    @property
    def userNames(self):
        """returns the user names
        """
        names = [] * 0
        for userObj in self._users:
            names.append( userObj.name )
        
        return names
    
    
    
    #----------------------------------------------------------------------
    @property
    def userInitials(self):
        """returns the user intials
        """
        initials = [] * 0
        for userObj in self._users:
            #assert(isinstance(user,User))
            initials.append( userObj.initials )
        
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
            self._users.append( user.User(name, initials) )
    
    
    
    #----------------------------------------------------------------------
    def updateProjectList(self):
        """updates the project list variable
        """
        
        try:
            self._projects = oyAux.getChildFolders( self._projectsFolderFullPath )
        except IOError:
            print "server path doesn't exists, %s" % self._projectsFolderFullPath
    
    
    
    #----------------------------------------------------------------------
    @property
    def projectsFullPath(self):
        """returns the projects folder full path
        
        ex : M:/JOBs
        """
        
        return self._projectsFolderFullPath
    
    
    #----------------------------------------------------------------------
    def serverPath():
        
        doc = """the server path"""
        
        def fget(self):
            return self._serverPath
        
        def fset(self, serverPath):
            """sets the server path
            """
            # add a trailing separator
            # in any cases os.path.join adds a trailing seperator
            self._serverPath = os.path.join( serverPath, '' )
            
            #self._updatePathVariables()
            self._projectsFolderFullPath = os.path.join( self._serverPath, self._projectsFolderName)
            
            self._projects = [] * 0
            
            self.updateProjectList()
        
        return locals()
    
    serverPath = property( **serverPath() )
    
    
    
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
    @property
    def defaultFiles(self):
        """returns the default files list as list of tuples, the first element contains
        the file name, the second the project relative path, the third the source path
        
        this is the list that contains files those
        need to be copied to every project like workspace.mel for Maya
        """
        
        return self._defaultFilesList
    
    
    
    #----------------------------------------------------------------------
    @property
    def defaultSettingsFileFullPath(self):
        """returns the default settings file full path
        """
        return self._defaultSettingsFileFullPath
    
    
    
    #----------------------------------------------------------------------
    @property
    def homePath(self):
        """returns the homePath environment variable
        it is :
        /home/userName/ for linux
        C:\Documents and Settings\userName\My Documents for Windows
        C:/Users/userName/Documents for Windows 7 (be careful about the slashes)
        """
        
        homePathAsStr = os.environ.get('HOME')
        
        if os.name == 'nt':
            homePathAsStr = homePathAsStr.replace('/','\\')
        
        return homePathAsStr
    
    
    
    #----------------------------------------------------------------------
    def lastUser():
        doc = """returns and saves the last user initials if the lastUserFile file exists otherwise returns None"""
        
        def fget(self):
            lastUserInitials = None
            
            try:
                lastUserFile = open( self._lastUserFileFullPath )
            except IOError:
                pass
            else:
                lastUserInitials = lastUserFile.readline().strip()
                lastUserFile.close()
            
            return lastUserInitials
        
        def fset(self, userInitials):
            try:
                lastUserFile = open( self._lastUserFileFullPath, 'w' )
            except IOError:
                pass
            else:
                lastUserFile.write( userInitials )
                lastUserFile.close()
        
        return locals()
    
    lastUser = property( **lastUser() )
    
    
    
    #----------------------------------------------------------------------
    def getProjectAndSequenceNameFromFilePath(self, filePath):
        """returns the project name and sequence name from the path or fullPath
        """
        
        #assert(isinstance(filePath, (str, unicode)))
        
        if filePath is None:
            return None, None
        
        if not filePath.startswith( self._projectsFolderFullPath ):
            return None, None
        
        residual = filePath[ len(self._projectsFolderFullPath)+1 : ]
        
        print "residual: ", residual
        
        parts = residual.split(os.path.sep)
        
        
        print "parts: ",parts
        
        return parts[0], parts[1]
    
    
    
    #----------------------------------------------------------------------
    @property
    def settingsDirPath(self):
        """returns the settings dir path
        """
        return self._settingsDirPath
    
    
    #----------------------------------------------------------------------
    @property
    def timeUnits(self):
        """returns timeUnits as a dictionary
        """
        return self._timeUnits
    
    
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
        
        