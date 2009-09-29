import os
from xml.dom import minidom
import tools.cache
import user



########################################################################
class Database(object):
    """Database class gives informations about the projects.
    """
    
    
    
    #----------------------------------------------------------------------
    def __init__(self):
        # for now use strings for settings
        
        self._settingsFileName = 'oyProjectManager_settings.xml'
        
        self._serverPath = "/home/ozgur/Documents/Works" + os.path.sep
        #self._serverPaths =  [] * 0
        
        self._projectsFolderName = "JOBs2"
        self._projectManagerFolderName = "PROJECT_CREATOR"
        
        self._projectsFolderFullPath = os.path.join( self._serverPath, self._projectsFolderName)
        self._projectManagerFullPath = os.path.join( self._serverPath, self._projectManagerFolderName )
        
        self._defaultSettingsFileName = "defaultProjectSettings.xml"
        self._defaultSettingsFullPath = os.path.join( self._projectManagerFullPath, self._defaultSettingsFileName )
        
        self._lastUserFileName = ".lastUser"
        self._lastUserFilePath = self.getHomePath()
        self._lastUserFileFullPath = os.path.join( self._lastUserFilePath, self._lastUserFileName )
        
        self._nullOptionString = '---'
        self._maxNotesCount = 30
        
        # users
        self._usersFileName = 'users.xml'
        self._usersFileFullPath = os.path.join( self._projectManagerFullPath, self._usersFileName )
        self._users = [] * 0
        self._readUsers()
        
        
        self._projects = [] * 0
        self.updateProjectList()
        
        self._defaultFilesList = [] * 0
        self._defaultFilesList.append('workspace.mel')
    
    
    
    #----------------------------------------------------------------------
    def updatePathVariables(self):
        """updates path variables
        """
        self._projectsFolderFullPath = os.path.join( self._serverPath, self._projectsFolderName)
        self._projectManagerFullPath = os.path.join( self._serverPath, self._projectManagerFolderName )
        self._defaultSettingsFullPath = os.path.join( self._projectManagerFullPath, self._defaultSettingsFileName )
        self._usersFileFullPath = os.path.join( self._projectManagerFullPath, self._usersFileName )
        
        self._users = [] * 0
        self._readUsers()
        
        
        self._projects = [] * 0
        self.updateProjectList()
    
    
    
    #----------------------------------------------------------------------
    @tools.cache.CachedMethod
    def getProjects(self):
        """returns projects names as a list
        """
        self.updateProjectList()
        return self._projects
    
    
    
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
            names.append( user.getName() )
        
        return names
    
    
    
    #----------------------------------------------------------------------
    def getUserInitials(self):
        """returns the user intials
        """
        initials = [] * 0
        for user in self._users:
            #assert(isinstance(user,User))
            initials.append( user.getInitials() )
        
        return initials
    
    
    
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
        
        if os.path.exists( self._projectsFolderFullPath ):
            self._projects = os.listdir( self._projectsFolderFullPath )
    
    
    
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
        
        self.updatePathVariables()
    
    
    
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
    def getHomePath(self):
        """returns the homePath environment variable
        it is :
        /home/userName/ for linux
        C:/Documents and Settings/userName for Windows
        """
        
        homePath = ''
        
        if os.name == 'posix':
            homePath = os.environ.get('HOME')
        elif os.name == 'nt':
            homePath = os.environ.get('HOMEPATH')
        
        return homePath
    
    
    
    #----------------------------------------------------------------------
    @tools.cache.CachedMethod
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
        #assert(isinstance(filePath, str))
        
        if not filePath.startswith( self._projectsFolderFullPath ):
            return None,None
        
        residual = filePath[ len(self._projectsFolderFullPath)+1 : len(filePath) ]
        
        parts = residual.split(os.path.sep)
        
        return parts[0], parts[1]