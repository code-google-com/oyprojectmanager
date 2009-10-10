import os, re, shutil
from xml.dom import minidom
import oyAuxiliaryFunctions as oyAux
from oyProjectManager.tools import cache, rangeTools
import assetModel, userModel



########################################################################
class Database(object):
    """Database class gives informations about the servers, projects, users etc.
    """
    
    
    
    #----------------------------------------------------------------------
    def __init__(self):
        
        # initialize default variables
        self._databaseSettingsFileName = 'databaseSettings.xml'
        
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
        
        # users
        self._usersFileName = 'users.xml'
        self._usersFileFullPath = ''
        self._users = [] * 0
        
        self._projects = [] * 0
        self._defaultFilesList = [] * 0
        
        self._readSettings()
        self._updatePathVariables()
    
    
    
    #----------------------------------------------------------------------
    def _readSettings(self):
        """reads the settings from the xml file at the project root
        """
        
        # get the module root path
        import oyProjectManager
        settingsFilePath = oyProjectManager.__path__[0]
        
        # then the database settings full path
        settingsFileFullPath = os.path.join( settingsFilePath, self._databaseSettingsFileName )
        
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
    @cache.CachedMethod
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






########################################################################
class Project(object):
    """Project object to help manage project data
    """
    
    
    
    #----------------------------------------------------------------------
    def __init__(self, projectName, databaseObj = None):
        
        if databaseObj == None:
            self._database = Database()
        else:
            self._database = databaseObj
        
        self._name = oyAux.stringConditioner( projectName, False, True, False, True, True, False )
        self._path = ''
        self._fullPath = ''
        
        self._initPathVariables()
        
        self._sequenceList = []
        
        self._exists = self.exists()
    
    
    
    #----------------------------------------------------------------------
    def _initPathVariables(self):
        self._path = self._database._projectsFolderFullPath
        self._fullPath = os.path.join( self._path, self._name)
    
    
    
    #----------------------------------------------------------------------
    def create(self):
        """creates the project
        """
        # check if the folder allready exists
        oyAux.createFolder( self._fullPath )
        self._exists = self.exists()
    
    
    
    #----------------------------------------------------------------------
    def createSequence(self, sequenceName, shots ):
        """creates a sequence and returns the sequence object
        """
        newSequence = Sequence( self, sequenceName )
        newSequence.addShots( shots )
        newSequence.create()
        
        return newSequence
    
    
    
    #----------------------------------------------------------------------
    @cache.CachedMethod
    def getSequenceNames(self):
        """returns the sequence names of that project
        """
        self.updateSequenceList()
        return self._sequenceList
    
    
    
    #----------------------------------------------------------------------
    @cache.CachedMethod
    def getSequences(self):
        """returns the sequences as sequence objects
        
        don't use it offen, because it causes the system to parse all the sequence settings
        for all the sequences under that project
        
        it is now using the caching mechanism use it freely
        """
        
        self.updateSequenceList()
        sequences = [] * 0
        
        for sequenceName in self._sequenceList:
            sequences.append( Sequence( self, sequenceName) )
        
        return sequences
    
    
    
    #----------------------------------------------------------------------
    def updateSequenceList(self):
        """updates the sequenceList variable
        """
        self._sequenceList = os.listdir( self._fullPath )
        self._sequenceList.sort()
    
    
    
    #----------------------------------------------------------------------
    def getFullPath(self):
        return self._fullPath
    
    
    
    #----------------------------------------------------------------------
    def getDatabase(self):
        """returns the current project database object
        """
        return self._database
    
    
    
    #----------------------------------------------------------------------
    def setDatabase(self, database ):
        """sets the project database object
        """
        
        self._database = database
        
        # reset the path variables
        self._initPathVariables
    
    
    
    #----------------------------------------------------------------------
    def getName(self):
        """ returns the name of the project
        """
        return self._name
    
    
    
    #----------------------------------------------------------------------
    def exists(self):
        """returns True if the project folder exists
        """
        
        return os.path.exists( self._fullPath )
    
    
    
    ##----------------------------------------------------------------------
    #def setProject(self, projectName):
        #"""renews the object to a new project
        #"""
        
        #self = Project( projectName )






########################################################################
class Sequence(object):
    """Sequence object to help manage sequence data
    
    the class should be initialized with the projectName a sequenceName
    """
    
    
    
    #----------------------------------------------------------------------
    def __init__(self, project, sequenceName):
        # create the parent project with projectName
        
        assert(isinstance(project, Project) )
        
        self._parentProject = project
        self._database = self._parentProject.getDatabase()
        
        self._name = oyAux.stringConditioner( sequenceName, False, True, False, True, True, False )
        
        self._path = self._parentProject.getFullPath()
        self._fullPath = os.path.join( self._path, self._name )
        
        self._settingsFile = ".settings.xml"
        self._settingsFilePath = self._fullPath
        self._settingsFileFullPath = os.path.join( self._settingsFilePath, self._settingsFile )
        
        self._structure = Structure()
        self._assetTypes = [ assetModel.AssetType() ] * 0
        self._shotList = [] * 0 # should be a string
        
        self._shotPrefix = 'SH'
        self._shotPadding = 3
        self._revPrefix = 'r' # revision number prefix
        self._revPadding = 2
        self._verPrefix = 'v' # version number prefix
        self._verPadding = 3
        
        self._extensionsToIgnore = [] * 0
        self._noSubNameField = False # to support the old types of projects
        
        self._environment = None # the working environment
        
        self._exists = False
        
        self.readSettings()
    
    
    
    #----------------------------------------------------------------------
    def readSettings(self):
        """reads the settingsFile
        """
        
        # check if there is a settings file
        if not os.path.exists( self._settingsFileFullPath ):
            #print "ERROR: no settings file in the sequence..."
            # TODO: assume that it is an old project and try to get
            # the data (just shot list) from the folders
            return
        else:
            self._exists = True
        
        settingsAsXML = minidom.parse( self._settingsFileFullPath )
        
        rootNode = settingsAsXML.childNodes[0]
        
        # -----------------------------------------------------
        # get main nodes
        databaseDataNode = rootNode.getElementsByTagName('databaseData')[0]
        sequenceDataNode = rootNode.getElementsByTagName('sequenceData')[0]
        
        # -----------------------------------------------------
        # get sequence nodes
        structureNode = sequenceDataNode.getElementsByTagName('structure')[0]
        assetTypesNode = sequenceDataNode.getElementsByTagName('assetTypes')[0]
        shotListNode = sequenceDataNode.getElementsByTagName('shotList')[0]
        
        # parse all nodes
        self._parseDatabaseDataNode( databaseDataNode )
        self._parseAssetTypesNode( assetTypesNode )
        self._parseShotListNode( shotListNode )
        self._parseStructureNode( structureNode )
    
    
    
    #----------------------------------------------------------------------
    def _parseDatabaseDataNode(self, databaseDataNode ):
        """parses databaseData node
        """
        
        #assert( isinstance( databaseDataNode, minidom.Element) )
        
        self._shotPrefix = databaseDataNode.getAttribute('shotPrefix')
        self._shotPadding = int( databaseDataNode.getAttribute('shotPadding') )
        self._revPrefix = databaseDataNode.getAttribute('revPrefix')
        self._revPadding = databaseDataNode.getAttribute('revPadding')
        self._verPrefix = databaseDataNode.getAttribute('verPrefix')
        self._verPadding = databaseDataNode.getAttribute('verPadding')
        
        if databaseDataNode.hasAttribute('extensionsToIgnore'):
            self._extensionsToIgnore = databaseDataNode.getAttribute('extensionsToIgnore').split(',')
        
        if databaseDataNode.hasAttribute('noSubNameField'):
            self._noSubNameField = bool( eval( databaseDataNode.getAttribute('noSubNameField') ) )
    
    
    
    #----------------------------------------------------------------------
    def _parseStructureNode(self, structureNode):
        """parses structure node from the XML file
        """
        
        #assert( isinstance( structureNode, minidom.Element ) )
        
        # -----------------------------------------------------
        # get shot dependent/independent folders
        shotDependentFoldersNode = structureNode.getElementsByTagName('shotDependent')[0]
        shotDependentFoldersList = shotDependentFoldersNode.childNodes[0].wholeText.split('\n')
        
        shotIndependentFoldersNode = structureNode.getElementsByTagName('shotIndependent')[0]
        shotIndependentFoldersList = shotIndependentFoldersNode.childNodes[0].wholeText.split('\n')
        
        # strip the elements and remove empty elements
        shotDependentFoldersList = [ folder.strip() for folder in shotDependentFoldersList if folder.strip() != ""  ]
        shotIndependentFoldersList = [ folder.strip() for folder in shotIndependentFoldersList if folder.strip() != ""  ]
        
        # fix path issues for windows
        osName = os.name
        
        if osName=='nt':
            shotDependentFoldersList = [ oyAux.fixWindowsPath(path) for path in shotDependentFoldersList]
            shotIndependentFoldersList = [ oyAux.fixWindowsPath(path) for path in shotIndependentFoldersList]
        
        # set the structure
        self._structure.setShotDependentFolders( shotDependentFoldersList )
        self._structure.setShotIndependentFolders( shotIndependentFoldersList )
        
        # read the output folders node
        outputFoldersNode = structureNode.getElementsByTagName('outputFolders')[0]
        outputNodes = outputFoldersNode.getElementsByTagName('output')
        
        
        for outputNode in outputNodes:
            #assert(isinstance(outpuNode, minidom.Element))
            name = outputNode.getAttribute('name')
            path = outputNode.getAttribute('path')
            
            # fixe path issues for windows
            if osName == 'nt':
                path = oyAux.fixWindowsPath( path )
            
            self._structure.addOutputFolder( name, path )
    
    
    
    #----------------------------------------------------------------------
    def _parseAssetTypesNode(self, assetTypesNode):
        """parses assetTypes node from the XML file
        """
        
        #assert( isinstance( assetTypesNode, minidom.Element) )
        
        # -----------------------------------------------------
        # read asset types
        self._assetTypes = [] * 0
        for node in assetTypesNode.getElementsByTagName('type'):
            #assert( isinstance( node, minidom.Element) )
            
            name = node.getAttribute('name')
            path = node.getAttribute('path')
            shotDependency = bool( int( node.getAttribute('shotDependent') ) )
            playblastFolder = node.getAttribute('playblastFolder')
            environments = node.getAttribute('environments').split(",")
            
            # fix path issues for windows
            if os.name == 'nt':
                path = oyAux.fixWindowsPath( path )
                playblastFolder = oyAux.fixWindowsPath( playblastFolder )
            
            self._assetTypes.append( assetModel.AssetType( name, path, shotDependency, playblastFolder, environments) )
    
    
    
    #----------------------------------------------------------------------
    def _parseShotListNode(self, shotListNode):
        """parses shotList node from the XML file
        """
        
        #assert( isinstance( shotListNode, minidom.Element) )
        
        # -----------------------------------------------------
        # get shot list only if the current shot list is empty
        if len(self._shotList) == 0:
            if len(shotListNode.childNodes):
                self._shotList  = [ shot.strip() for shot in shotListNode.childNodes[0].wholeText.split('\n') if shot.strip() != "" ]
    
    
    
    #----------------------------------------------------------------------
    def saveSettings(self):
        """saves the settings as XML
        """
        
        # create nodes
        rootNode = minidom.Element('root')
        databaseDataNode = minidom.Element('databaseData')
        sequenceDataNode = minidom.Element('sequenceData')
        structureNode = minidom.Element('structure')
        shotDependentNode = minidom.Element('shotDependent')
        shotDependentNodeText = minidom.Text()
        shotIndependentNode = minidom.Element('shotIndependent')
        shotIndependentNodeText = minidom.Text()
        assetTypesNode = minidom.Element('assetTypes')
        typeNode = minidom.Element('type')
        
        shotListNode = minidom.Element('shotList')
        shotListNodeText = minidom.Text()
        
        # set database node attributes
        databaseDataNode.setAttribute('shotPrefix', self._shotPrefix)
        databaseDataNode.setAttribute('shotPadding', unicode( self._shotPadding ) )
        databaseDataNode.setAttribute('revPrefix', self._revPrefix)
        databaseDataNode.setAttribute('revPadding', unicode( self._revPadding ) )
        databaseDataNode.setAttribute('verPrefix', self._verPrefix)
        databaseDataNode.setAttribute('verPadding', unicode( self._verPadding ) )
        databaseDataNode.setAttribute('extensionsToIgnore', unicode( ','.join(self._extensionsToIgnore)) )
        
        if self._noSubNameField:
            databaseDataNode.setAttribute('noSubNameField', unicode( self._noSubNameField ) )
        
        # create shot dependent/independent folders
        shotDependentNodeText.data = '\n'.join( self._structure.getShotDependentFolders() )
        shotIndependentNodeText.data = '\n'.join( self._structure.getShotIndependentFolders() )
        
        # create shot list text data
        shotListNodeText.data = '\n'.join( self._shotList )
        
        # create asset types
        for aType in self._assetTypes:
            #assert( isinstance( aType, assetModel.AssetType ) )
            typeNode = minidom.Element('type')
            typeNode.setAttribute( 'name', aType.getName() )
            typeNode.setAttribute( 'path', aType.getPath() )
            typeNode.setAttribute( 'shotDependent', unicode( int( aType.isShotDependent() ) ) )
            typeNode.setAttribute( 'playblastFolder', aType.getPlayblastFolder() )
            typeNode.setAttribute( 'environments', ",".join( aType.getEnvironments() ) )
            
            assetTypesNode.appendChild( typeNode )
        
        # create output folders node
        
        outputFoldersNode = minidom.Element('outputFolders')
        for fTuple in self._structure.getOutputFolders():
            
            outputNode = minidom.Element('output')
            outputNode.setAttribute( 'name', fTuple[0] )
            outputNode.setAttribute( 'path', fTuple[1] )
            
            outputFoldersNode.appendChild( outputNode )
        
        # append childs
        rootNode.appendChild( databaseDataNode )
        rootNode.appendChild( sequenceDataNode )
        
        sequenceDataNode.appendChild( structureNode )
        sequenceDataNode.appendChild( assetTypesNode )
        sequenceDataNode.appendChild( shotListNode )
        
        structureNode.appendChild( shotDependentNode )
        structureNode.appendChild( shotIndependentNode )
        structureNode.appendChild( outputFoldersNode )
        
        shotDependentNode.appendChild( shotDependentNodeText )
        shotIndependentNode.appendChild( shotIndependentNodeText )
        
        shotListNode.appendChild( shotListNodeText )
        
        # create XML file
        settingsXML = minidom.Document()
        settingsXML.appendChild( rootNode )
        
        try:
            settingsFile = open( self._settingsFileFullPath, 'w' )
        except IOError:
            #print "couldn't open the settings file"
            pass
        finally:
            settingsXML.writexml( settingsFile, "\t", "\t", "\n" )
            settingsFile.close()
    
    
    
    #----------------------------------------------------------------------
    def create(self):
        """creates the sequence
        """
        
        # if the sequence doesn't exist create the folder
        
        if not self._exists:
            # create a folder with sequenceName
            exists = oyAux.createFolder( self._fullPath )
            
            # copy the settings file to the root of the sequence
            shutil.copy( self._database._defaultSettingsFullPath, self._settingsFileFullPath )
        
        # just read the structure from the XML
        self.readSettings()
        
        # tell the sequence to create its own structure
        self.createStructure()
        
        # and create the shots
        self.createShots()
        
        # copy any file to the sequence
        # (like workspace.mel)
        for _fileInfo in self._database.getDefaultFiles():
            sourcePath = os.path.join( _fileInfo[2], _fileInfo[0] )
            targetPath = os.path.join( self._fullPath, _fileInfo[1], _fileInfo[0] )
            
            shutil.copy( sourcePath, targetPath )
    
    
    
    #----------------------------------------------------------------------
    def addShots(self, shots ):
        """adds new shots to the sequence
        
        shots should be a range in on of the following format:
        #
        #,#
        #-#
        #,#-#
        #,#-#,#
        #-#,#
        etc.
        
        you need to invoke self.creatShots and then self.saveSettings to make
        the changes permenant
        """
        
        # for now consider the shots as a string of range
        # do the hard work later
        
        newShotsList = rangeTools.RangeConverter.convertRangeToList( shots )
        
        # convert the list to strings
        newShotsList = map(str, newShotsList)
        
        # add the shotList to the current _shotList
        self._shotList = oyAux.unique( oyAux.concatenateLists( self._shotList, newShotsList ) )
        
        # sort the shotList
        self._shotList = oyAux.sort_strings_with_embedded_numbers( self._shotList )
    
    
    
    ##----------------------------------------------------------------------
    #def addAlternativeShot(self, shotNumber):
        #"""adds an alternative to the given shot
        #"""
        
        #shotNumberAsStr = unicode( shotNumber )
        
        ## check if the shotNumber is in the shotList
        #if shotNumber in self._shotList:
            ## get the alternate letter
    
    
    
    #----------------------------------------------------------------------
    def createShots(self):
        """creates the shot folders in the structure
        """
        if not self._exists:
            return
        
        #for folder in self._shotFolders:
        for folder in self._structure.getShotDependentFolders():
            for shotNumber in self._shotList:
                # get a shotString for that number
                shotString = self.convertToShotString( shotNumber )
                
                # create the folder with that name
                shotFullPath = os.path.join ( self._fullPath, folder, shotString )
                
                #self._database._create_folder( shotFullPath )
                oyAux.createFolder( shotFullPath )
        
        # update settings
        self.saveSettings()
    
    
    
    #----------------------------------------------------------------------
    def getShotFolders(self):
        """returns the shot folder paths
        """
        if not self._exists:
            return
        
        return self._structure.getShotDependentFolders()
    
    
    
    #----------------------------------------------------------------------
    def getShotList(self):
        """returns the shot list object
        """
        return self._shotList
    
    
    
    #----------------------------------------------------------------------
    def getStructure(self):
        """returns the structure object
        """
        return self._structure
    
    
    
    #----------------------------------------------------------------------
    def createStructure(self):
        """creates the folders defined by the structure
        """
        if not self._exists:
            return
        
        createFolder = oyAux.createFolder
        
        # create the structure
        for folder in self._structure.getShotDependentFolders():
            createFolder( os.path.join( self._fullPath, folder ) )
        
        for folder in self._structure.getShotIndependentFolders():
            createFolder( os.path.join( self._fullPath, folder ) )
    
    
    
    #----------------------------------------------------------------------
    def convertToShotString(self, shotNumber ):
        """ converts the input shot number to a padded shot string
        
        for example it converts:
        1   --> SH001
        10  --> SH010
        
        if there is an alternate letter it will add it to the end of the
        shot string, like:
        1a  --> SH001a
        10S --> SH010s
        
        it also properly converts inputs like this
        abc92a --> SH092a
        abc323d432e --> SH323d
        abc001d --> SH001d
        
        if the shotNumber argument is None it will return None
        
        for now it can't convert properly if there is more than one letter at the end like:
        abc23defg --> SH023defg
        """
        
        pieces = oyAux.embedded_numbers( unicode(shotNumber) )
        
        if len(pieces) <= 1:
            return None
        
        number = pieces[1]
        alternateLetter = pieces[2]
        
        return self._shotPrefix + oyAux.padNumber( number, self._shotPadding ) + alternateLetter.lower()
    
    
    
    #----------------------------------------------------------------------
    def convertToRevString(self, revNumber):
        """converts the input revision number to a padded revision string
        
        for example it converts:
        1  --> r01
        10 --> r10
        """
        return self._revPrefix + oyAux.padNumber( revNumber, self._revPadding )
    
    
    
    #----------------------------------------------------------------------
    def convertToVerString(self, verNumber):
        """converts the input version number to a padded version string
        
        for example it converts:
        1  --> v001
        10 --> v010
        """
        return self._verPrefix + oyAux.padNumber( verNumber, self._verPadding )
    
    
    
    #----------------------------------------------------------------------
    def convertToShotNumber(self, shotString):
        """beware that it returns a string, it returns the number plus the alternative
        letter (if exists) as a string
        
        for example it converts:
        
        SH001 --> 1
        SH041a --> 41a
        etc.
        """
        
        # remove the shot prefix
        remainder = shotString[ len(self._shotPrefix) : len(shotString) ]
        
        # get the integer part
        matchObj = re.match('[0-9]+',remainder)
        
        if matchObj:
            numberAsStr = matchObj.group()
        else:
            return None
        
        alternateLetter = ''
        if len(numberAsStr) < len(remainder):
            alternateLetter = remainder[len(numberAsStr):len(remainder)]
        
        # convert the numberAsStr to a number then to a string then add the alternate letter
        return unicode(int(numberAsStr)) + alternateLetter
    
    
    
    #----------------------------------------------------------------------
    def convertToRevNumber(self, revString):
        """converts the input revision string to a revision number
        
        for example it converts:
        r01 --> 1
        r10 --> 10
        """
        return int(revString[len(self._revPrefix):len(revString)])
    
    
    
    #----------------------------------------------------------------------
    def convertToVerNumber(self, verString):
        """converts the input version string to a version number
        
        for example it converts:
        v001 --> 1
        v010 --> 10
        """
        return int(verString[len(self._verPrefix):len(verString)])
    
    
    
    #----------------------------------------------------------------------
    @cache.InputBasedCachedMethod
    def getAssetTypes(self, environment=None):
        """returns a list of AssetType objects that this project has
        
        if the environment is set something other then None only the assetTypes
        for that environment is returned
        """
        
        
        if environment==None:
            return self._assetTypes
        else:
            aTypesList = [] * 0
            
            for aType in self._assetTypes:
                #assert(isinstance(aType, assetModel.AssetType) )
                if environment in aType.getEnvironments():
                    aTypesList.append( aType )
            
            return aTypesList
    
    
    
    #----------------------------------------------------------------------
    @cache.InputBasedCachedMethod
    def getAssetTypeWithName(self, typeName):
        """returns the assetType object that has the name typeName.
        if it can't find any assetType that has the name typeName it returns None
        """
        
        for aType in self._assetTypes:
            if aType.getName() == typeName:
                return aType
        
        return None
    
    
    
    #----------------------------------------------------------------------
    def getName(self):
        """returns the name of the sequence
        """
        return self._name
    
    
    
    #----------------------------------------------------------------------
    def getPath(self):
        """returns the path of the sequence
        """
        return self._path
    
    
    
    #----------------------------------------------------------------------
    def getFullPath(self):
        """returns the full path of the sequence
        """
        return self._fullPath
    
    
    
    #----------------------------------------------------------------------
    def getProject(self):
        """returns the parent project
        """
        return self._parentProject
    
    
    
    #----------------------------------------------------------------------
    def getProjectName(self):
        """returns the parent projects name
        """
        return self._parentProject.getName()
    
    
    
    #----------------------------------------------------------------------
    @cache.CachedMethod
    def getAssetFolders(self):
        """returns all asset folders
        """
        
        # look at the assetType folders
        assetFolders = [] * 0
        
        for aType in self._assetTypes:
            #assert(isinstance(aType, AssetType))
            assetFolders.append( aType.getPath() )
        
        return assetFolders
    
    
    
    #----------------------------------------------------------------------
    @cache.CachedMethod
    def getAllAssets(self):
        """returns Asset objects for all the assets of the sequence
        beware that this method uses a very simple caching algorithm, so it
        tries to reduce file system overhead
        """
        
        # get asset folders
        # look at the child folders
        # and then look at the files under the child folders
        # if a file starts with the folder name
        # mark it as an asset
        
        assets = [] * 0
        
        # get the asset folders
        assetFolders = self.getAssetFolders()
        
        
        # optimization variables
        osPathJoin = os.path.join
        osPathExists = os.path.exists
        osPathIsFile = os.path.isfile
        osPathIsDir = os.path.isdir
        osListDir = os.listdir
        selfFullPath = self._fullPath
        assetModelAsset = assetModel.Asset
        selfProject = self.getProject()
        
        # for each folder search child folders
        for folder in assetFolders:
            fullPath = osPathJoin( selfFullPath, folder)
            
            # 
            # skip if the folder doesn't exists
            # 
            # it is a big problem in terms of management but some old type projects
            # has missing folder, because the folders will be created whenever somebody
            # uses that folder while saving an asset, we don't care about its non existancy
            #
            #if not os.path.exists( fullPath ):
            if not osPathExists( fullPath ):
                continue
            
            childFolders = osListDir( fullPath )
            
            
            for childFolder in childFolders:
                childFolderFullPath = osPathJoin( fullPath, childFolder )
                if childFolder == '' or not osPathIsDir(childFolderFullPath):
                    continue
                
                childFiles = osListDir( childFolderFullPath )
                
                for childFile in childFiles:
                    childFileFullPath = osPathJoin( childFolderFullPath, childFile)
                    if childFile.startswith( childFolder ) and osPathIsFile( childFileFullPath ):
                        
                        asset = assetModelAsset( selfProject, self, childFile )
                        
                        if asset.isValidAsset() and self.isValidExtension(asset.getExtension()):
                            assets.append( asset )
        return assets
    
    
    
    #----------------------------------------------------------------------
    @cache.InputBasedCachedMethod
    def getAllAssetsForType(self, typeName):
        """returns Asset objects for just the given type of the sequence
        """
        
        # get asset folders
        # look at the child folders
        # and then look at the files under the child folders
        # if a file starts with the folder name
        # mark it as an asset
        
        assets = [] * 0
        
        # get the asset folders
        #assetFolders = self.getAssetFolders()
        
        aType = self.getAssetTypeWithName( typeName )
        
        #assert(isinstance(aType,assetModel.AssetType))
        assetFolder = aType.getPath()
        
        # optimization variables
        osPathJoin = os.path.join
        osPathExists = os.path.exists
        osPathIsFile = os.path.isfile
        osPathIsDir = os.path.isdir
        osListDir = os.listdir
        selfFullPath = self._fullPath
        assetModelAsset = assetModel.Asset
        selfProject = self.getProject()
        
        fullPath = osPathJoin( selfFullPath, assetFolder)
        
        # 
        # skip if the folder doesn't exists
        # 
        # it is a big problem in terms of management but some old type projects
        # has missing folder, because the folders will be created whenever somebody
        # uses that folder while saving an asset, we don't care about its non existancy
        #
        #if not os.path.exists( fullPath ):
        if not osPathExists( fullPath ):
            return []
        
        childFolders = osListDir( fullPath )
        
        
        for childFolder in childFolders:
            childFolderFullPath = osPathJoin( fullPath, childFolder )
            
            if childFolder == '' or not osPathIsDir(childFolderFullPath):
                continue
            
            childFiles = osListDir( childFolderFullPath )
            
            for childFile in childFiles:
                childFileFullPath = osPathJoin( childFolderFullPath, childFile)
                if childFile.startswith( childFolder ) and osPathIsFile( childFileFullPath ):
                    
                    asset = assetModelAsset( selfProject, self, childFile )
                    
                    if asset.isValidAsset() and self.isValidExtension(asset.getExtension()):
                        assets.append( asset )
                    #assets.append( asset )
        
        return assets
    
    
    
    #----------------------------------------------------------------------
    @cache.InputBasedCachedMethod
    def getAllAssetFileNamesForType(self, typeName):
        """returns Asset objects for just the given type of the sequence
        """
        
        # get asset folders
        # look at the child folders
        # and then look at the files under the child folders
        # if a file starts with the folder name
        # mark it as an asset
        
        assetFiles = [] * 0
        
        # get the asset folders
        #assetFolders = self.getAssetFolders()
        
        aType = self.getAssetTypeWithName( typeName )
        
        #assert(isinstance(aType,assetModel.AssetType))
        assetFolder = aType.getPath()
        
        # optimization variables
        osPathJoin = os.path.join
        osPathExists = os.path.exists
        osPathIsFile = os.path.isfile
        osPathIsDir = os.path.isdir
        osListDir = os.listdir
        selfFullPath = self._fullPath
        selfIsValidExtension = self.isValidExtension
        
        fullPath = osPathJoin( selfFullPath, assetFolder)
        
        # 
        # skip if the folder doesn't exists
        # 
        # it is a big problem in terms of management but some old type projects
        # has missing folder, because the folders will be created whenever somebody
        # uses that folder while saving an asset, we don't care about its non existancy
        #
        #if not os.path.exists( fullPath ):
        if not osPathExists( fullPath ):
            return []
        
        childFolders = osListDir( fullPath )
        
        for childFolder in childFolders:
            childFolderFullPath = osPathJoin( fullPath, childFolder )
            
            if childFolder == '' or not osPathIsDir(childFolderFullPath):
                continue
            
            childFiles = osListDir( childFolderFullPath )
            
            for childFile in childFiles:
                
                if not selfIsValidExtension( os.path.splitext( childFile )[1][1:] ):
                    continue
                
                childFileFullPath = osPathJoin( childFolderFullPath, childFile)
                if childFile.startswith( childFolder ) and osPathIsFile( childFileFullPath ):
                    
                    assetFiles.append( childFile )
        
        return assetFiles
    
    
    
    #----------------------------------------------------------------------
    @cache.InputBasedCachedMethod
    def getAllAssetsForTypeAndBaseName(self, typeName, baseName):
        """returns Asset objects of the sequence for just the given type and basename
        """
        
        # get asset folders
        # look at the child folders
        # and then look at the files under the child folders
        # if a file starts with the folder name
        # mark it as an asset
        
        assets = [] * 0
        
        # get the asset folder
        aType = self.getAssetTypeWithName( typeName )
        assetFolder = aType.getPath()
        
        # optimization variables
        osPathJoin = os.path.join
        osPathExists = os.path.exists
        osPathIsFile = os.path.isfile
        osPathIsDir = os.path.isdir
        osListDir = os.listdir
        selfFullPath = self._fullPath
        assetModelAsset = assetModel.Asset
        selfProject = self._parentProject
        
        fullPath = osPathJoin( selfFullPath, assetFolder)
        
        # 
        # skip if the folder doesn't exists
        # 
        # it is a big problem in terms of management but some old type projects
        # has missing folder, because the folders will be created whenever somebody
        # uses that folder while saving an asset, we don't care about its non existancy
        #
        if not osPathExists( fullPath ):
            return []
        
        childFolder = baseName
        childFolderFullPath = osPathJoin( fullPath, childFolder )
        
        if childFolder == '' or not osPathIsDir(childFolderFullPath):
            return []
        
        childFiles = osListDir( childFolderFullPath )
        
        for childFile in childFiles:
            childFileFullPath = osPathJoin( childFolderFullPath, childFile)
            if childFile.startswith( childFolder ) and osPathIsFile( childFileFullPath ):
                
                asset = assetModelAsset( selfProject, self, childFile )
                
                if asset.isValidAsset() and self.isValidExtension(asset.getExtension()):
                    assets.append( asset )
                assets.append( asset )
        
        return assets
    
    
    
    ##----------------------------------------------------------------------
    #def getAllBaseNamesForType(self, typeName):
        #"""
        #"""
        
        #aType = self.getAssetTypeWithName( typeName )
        
        ##assert(isinstance(aType,assetModel.AssetType))
        
        #typeFolder = aType.getPath
        
        #os.listdir( typeFolder )
    
    
    
    #----------------------------------------------------------------------
    def filterAssets(self, assetList, **kwargs):
        """filters the given asset list with the key word arguments
        
        the kwargs should have at least on of these keywords:
        
        baseName
        subName
        typeName
        rev
        revString
        ver
        verString
        userInitials
        notes
        fileName
        """
        
        newKwargs = dict()
        
        # remove empty keywords
        for k in kwargs:
            if kwargs[k] != '':
                newKwargs[k] = kwargs[k]
        
        # get all the info variables of the assets
        assetInfos = map( assetModel.Asset.getInfoVariables, assetList )
        
        filteredAssetInfos = self.aFilter( assetInfos, **kwargs)
        
        # recreate assets and return
        # TODO: return without recreating the assets
        return [ assetModel.Asset(self._parentProject, self, x['fileName']) for x in filteredAssetInfos ]
    
    
    
    #----------------------------------------------------------------------
    def filterAssetNames(self, assetFileNames, **kwargs):
        """a fake filter for quick retrieval of infos from asset file names
        
        use filterAsset for filtering with asset objects as input
        
        the kwargs should have at least on of these keywords:
        
        baseName
        subName
        typeName
        """
        
        # generate dictionaries
        assetInfos = map( self.generateFakeInfoVariables, assetFileNames )
        
        filteredAssetFileNames = self.aFilter( assetInfos, **kwargs )
        
        return [ info['fileName'] for info in filteredAssetFileNames ]
    
    
    
    #----------------------------------------------------------------------
    @cache.InputBasedCachedMethod
    def generateFakeInfoVariables(self, assetFileName):
        """generates fake info variables from assetFileNames by splitting the file name
        from '_' characters and trying to get information from those splits
        """
        #assert(isinstance(assetFileName, str))
        splits = assetFileName.split('_') # replace it with data seperator
        
        infoVars = dict()
        
        infoVars['fileName'] = assetFileName
        infoVars['baseName'] = ''
        infoVars['subName'] = ''
        infoVars['typeName'] = ''
        
        if len(splits) > 1:
            if not self._noSubNameField:
                infoVars['baseName'] = splits[0]
                infoVars['subName'] = splits[1]
                infoVars['typeName'] = splits[2]
            else:
                infoVars['baseName'] = splits[0]
                infoVars['subName'] = ''
                infoVars['typeName'] = splits[1]
        
        return infoVars
    
    
    
    #----------------------------------------------------------------------
    def aFilter(self, dicts, **kwargs):
        """filters assets for criteria
        """
        return [ d for d in dicts if all(d.get(k) == kwargs[k] for k in kwargs)]
    
    
    
    #----------------------------------------------------------------------
    def getRevPrefix(self):
        """returns revPrefix
        """
        return self._revPrefix
    
    
    
    #----------------------------------------------------------------------
    def getVerPrefix(self):
        """returns verPrefix
        """
        return self._verPrefix
    
    
    
    #----------------------------------------------------------------------
    def getInvalidExtensions(self):
        """returns invalid extensions for the sequence
        """
        return self._extensionsToIgnore
    
    
    
    #----------------------------------------------------------------------
    @cache.InputBasedCachedMethod
    def isValidExtension(self, extensionString):
        """checks if the given extension is in extensionsToIgnore list
        """
        
        if len(self._extensionsToIgnore) == 0 :
            # no extensions to ignore
            return True
        
        #assert(isinstance(extensionString,str))
        
        if extensionString.lower() in self._extensionsToIgnore:
            return False
        
        return True
    
    
    
    #----------------------------------------------------------------------
    def addExtensionToIgnoreList(self, extension):
        """adds new extension to ignore list
        
        you need to invoke self.saveSettings to make the changes permenant
        """
        self._extensionsToIgnore.append( extension )
    
    
    
    #----------------------------------------------------------------------
    def removeExtensionFromIgnoreList(self, extension):
        """remove the extension from the ignroe list
        
        you need to invoke self.saveSettings to make the changes permenant
        """
        
        if extension in self._extensionsToIgnore:
            self._extensionsToIgnore.remove( extension )
    
    
    
    #----------------------------------------------------------------------
    def addNewAssetType(self, name='', path='', shotDependent=False, playblastFolder='', environments=None):
        """adds a new asset type to the sequence
        
        you need to invoke self.saveSettings to make the changes permenant
        """
        
        # create the assetType object with the input
        newAType = assetModel.AssetType( name, path, shotDependent, playblastFolder, environments )
        
        # add it to the list
        self._assetTypes.append( newAType )
    
    
    
    ##----------------------------------------------------------------------
    #def addNewShotDependentFolder(self, folderPath):
        #"""adds new shot dependent folder
        
        #folderPath should be relative to sequence root
        
        #you need to invoke self.createStructure and then self.saveSettings
        #to make the changes permenant
        #"""
        
        #self._structure.addShotDependentFolder( folderPath )
    
    
    
    ##----------------------------------------------------------------------
    #def addNewShotIndependentFolder(self, folderPath):
        #"""adds new shot independent folder
        
        #folderPath should be relative to sequence root
        
        #you need to invoke self.createStructure and then self.saveSettings
        #to make the changes permenant
        #"""
        
        #self._structure.addShotIndependentFolder( folderPath )
    
    
    
    ##----------------------------------------------------------------------
    #def addNewOutputFolder(self, name, path):
        #"""adds new output folder to the structure
        
        #you need to invoke self.saveSettings to make the changes permenant
        #"""
        
        #self._structure.addOutputFolder( name, path )
    
    
    
    ##----------------------------------------------------------------------
    #def removeOutputFolder(self, name):
        #"""removes the specified output folder
        
        #you need to invoke self.saveSettings to make the changes permenant
        #"""
        
        #self._structure.removeOutputFolder( name )
    
    
    
    #----------------------------------------------------------------------
    def exists(self):
        """returns True if the sequence itself exists, False otherwise
        """
        
        return self._exists
    
    
    
    #----------------------------------------------------------------------
    def noSubNameField(self):
        """returns True if the sequence doesn't support subName fields (old-style)
        """
        
        return self._noSubNameField






########################################################################
class Structure(object):
    """The class that helps to hold data about structures in a sequence
    
    outputFolders should be a list of tuples showing the name and path of the outputFolder
    """
    
    
    
    _shotDependentFolders = [] * 0
    _shotIndependentFolders = [] * 0
    
    
    
    #----------------------------------------------------------------------
    def __init__(self, shotDependentFolders=None, shotIndependentFolders=None, outputFolders=None):
        self._shotDependentFolders = shotDependentFolders # should be a list of str or unicode
        self._shotIndependentFolders = shotIndependentFolders # should be a list of str or unicode
        self._outputFolders = outputFolders # should be a list of tuples
    
    
    
    #----------------------------------------------------------------------
    def setShotDependentFolders(self, folders):
        """sets shot dependent folders
        """
        self._shotDependentFolders = folders
    
    
    
    #----------------------------------------------------------------------
    def setShotIndependentFolders(self, folders):
        """sets shot independent folders
        """
        self._shotIndependentFolders = folders
    
    
    
    #----------------------------------------------------------------------
    def setOutputFolders(self, folders):
        """sets the output folders from a dictionary
        folders should be a list of tuples, the first element of the tuple
        should contain the name and the second should contain the path of that
        output folder
        """
        self._outputFolders = folders
    
    
    
    #----------------------------------------------------------------------
    def addOutputFolder(self, name, path):
        """adds new output folder to the structure
        """
        if self._outputFolders == None:
            self._outputFolders = [] * 0
        
        self._outputFolders.append( (name, path) )
    
    
    #----------------------------------------------------------------------
    def addShotDependentFolder(self, folderPath):
        """adds new shot dependent folder
        
        folderPath should be relative to sequence root
        """
        
        self._shotDependentFolders.append( folderPath )
        self._shotDependentFolders = sorted( self._shotDependentFolders )
    
    
    
    #----------------------------------------------------------------------
    def addShotIndependentFolder(self, folderPath):
        """adds new shot independent folder
        
        folderPath should be relative to sequence root
        """
        
        self._shotIndependentFolders.append( folderPath )
        self._shotIndependentFolders = sorted( self._shotIndependentFolders )
    
    
    
    #----------------------------------------------------------------------
    def getShotDependentFolders(self):
        """returns shot dependent folders as list
        """
        return self._shotDependentFolders
    
    
    
    #----------------------------------------------------------------------
    def getShotIndependentFolders(self):
        """returns shot independent folders as list
        """
        return self._shotIndependentFolders
    
    
    
    #----------------------------------------------------------------------
    def getOutputFolders(self):
        """returns the output folders as a dictionary
        """
        return self._outputFolders
    
    
    #----------------------------------------------------------------------
    def getOutputFolderPathOf(self, name):
        """returns the output folder path with the name
        returns none if name is not in the list
        """
        for oFolderT in self._outputFolders:
            if oFolderT[0] == name:
                return oFolderT[1]
        
        return None
    
    
    
    #----------------------------------------------------------------------
    def removeOutputFolder(self, name):
        """removes the specified output folder
        """
        
        path = self.getOutputFolderPathOf( name )
        oTuple = (name, path)
        self._outputFolders.remove( oTuple )
    
    
    #----------------------------------------------------------------------
    def removeShotDependentFolder(self, folderPath):
        """removes the shot dependent folder from the structure
        
        beware that if the parent sequence uses that folder as a assetType folder
        you introduce an error to the sequence
        """
        
        self._shotDependentFolders.remove( folderPath )
    
    
    
    #----------------------------------------------------------------------
    def removeShotIndependentFolder(self, folderPath):
        """removes the shot independent folder from the structure
        
        beware that if the parent sequence uses that folder as a assetType folder
        you introduce an error to the sequence
        """
        
        self._shotIndependentFolders.remove( folderPath )
    