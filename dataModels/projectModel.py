import os
from xml.dom import minidom
import oyAuxiliaryFunctions as oyAux
from oyProjectManager.tools import cache
import assetModel, userModel



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
        #assert(isinstance(filePath, str))
        
        if not filePath.startswith( self._projectsFolderFullPath ):
            return None,None
        
        residual = filePath[ len(self._projectsFolderFullPath)+1 : len(filePath) ]
        
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
        
        self._name = oyAux.file_name_conditioner( projectName )
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
        
        self._parentProject = project
        self._database = self._parentProject.getDatabase()
        
        self._name = oyAux.file_name_conditioner( sequenceName )
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
        
        self._exists = False
        
        self._readSettings()
    
    
    
    #----------------------------------------------------------------------
    def _readSettings(self):
        """reads the settingsFile
        """
        
        # check if there is a settings file
        if not os.path.exists( self._settingsFileFullPath ):
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
        
        assert( isinstance( databaseDataNode, minidom.Element) )
        
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
        
        assert( isinstance( structureNode, minidom.Element ) )
        
        # -----------------------------------------------------
        # get shot dependent/independent folders
        shotDependentFoldersNode = structureNode.getElementsByTagName('shotDependent')[0]
        shotDependentFoldersList = shotDependentFoldersNode.childNodes[0].wholeText.split('\n')
        
        shotIndependentFoldersNode = structureNode.getElementsByTagName('shotIndependent')[0]
        shotIndependentFoldersList = shotIndependentFoldersNode.childNodes[0].wholeText.split('\n')
        
        # strip the elements and remove empty elements
        shotDependentFoldersList = [ folder.strip() for i, folder in enumerate(shotDependentFoldersList) if folder.strip() != ""  ]
        shotIndependentFoldersList = [ folder.strip() for i, folder in enumerate(shotIndependentFoldersList) if folder.strip() != ""  ]
        
        # set the structure
        self._structure.setShotDependentFolders( shotDependentFoldersList )
        self._structure.setShotIndependentFolders( shotIndependentFoldersList )
    
    
    
    #----------------------------------------------------------------------
    def _parseAssetTypesNode(self, assetTypesNode):
        """parses assetTypes node from the XML file
        """
        
        assert( isinstance( assetTypesNode, minidom.Element) )
        
        # -----------------------------------------------------
        # read asset types
        self._assetTypes = [] * 0
        for node in assetTypesNode.getElementsByTagName('type'):
            
            name = node.getAttribute('name')
            path = node.getAttribute('path')
            shotDependency = bool( int( node.getAttribute('shotDependent') ) )
            playblastFolder = node.getAttribute('playblastFolder')
            
            self._assetTypes.append( assetModel.AssetType( name, path, shotDependency, playblastFolder) )
    
    
    
    #----------------------------------------------------------------------
    def _parseShotListNode(self, shotListNode):
        """parses shotList node from the XML file
        """
        
        assert( isinstance( shotListNode, minidom.Element) )
        
        # -----------------------------------------------------
        # get shot list only if the current shot list is empty
        if len(self._shotList) == 0:
            if len(shotListNode.childNodes):
                self._shotList  = [ shot.strip() for i, shot in enumerate( shotListNode.childNodes[0].wholeText.split('\n') ) if shot.strip() != "" ]
    
    
    
    #----------------------------------------------------------------------
    def _saveSettings(self):
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
        databaseDataNode.setAttribute('shotPadding', str( self._shotPadding ) )
        databaseDataNode.setAttribute('revPrefix', self._revPrefix)
        databaseDataNode.setAttribute('revPadding', str( self._revPadding ) )
        databaseDataNode.setAttribute('verPrefix', self._verPrefix)
        databaseDataNode.setAttribute('verPadding', str( self._verPadding ) )
        databaseDataNode.setAttribute('extensionsToIgnore', str( ','.join(self._extensionsToIgnore)) )
        
        if self._noSubNameField:
            databaseDataNode.setAttribute('noSubNameField', str( self._noSubNameField ) )
        
        # create shot dependent/independent folders
        shotDependentNodeText.data = '\n'.join( self._structure.getShotDependentFolders() )
        shotIndependentNodeText.data = '\n'.join( self._structure.getShotIndependentFolders() )
        
        # create shot list text data
        shotListNodeText.data = '\n'.join( self._shotList )
        
        # create asset types
        for aType in self._assetTypes:
            assert( isinstance( aType, assetModel.AssetType ) )
            typeNode = minidom.Element('type')
            typeNode.setAttribute( 'name', aType.getName() )
            typeNode.setAttribute( 'path', aType.getPath() )
            typeNode.setAttribute( 'shotDependent', str( int( aType.isShotDependent() ) ) )
            typeNode.setAttribute( 'playblastFolder', aType.getPlayblastFolder() )
            
            assetTypesNode.appendChild( typeNode )
        
        # append childs
        rootNode.appendChild( databaseDataNode )
        rootNode.appendChild( sequenceDataNode )
        
        sequenceDataNode.appendChild( structureNode )
        sequenceDataNode.appendChild( assetTypesNode )
        sequenceDataNode.appendChild( shotListNode )
        
        structureNode.appendChild( shotDependentNode )
        structureNode.appendChild( shotIndependentNode )
        
        shotDependentNode.appendChild( shotDependentNodeText )
        shotIndependentNode.appendChild( shotIndependentNodeText )
        
        shotListNode.appendChild( shotListNodeText )
        
        # create XML file
        settingsXML = minidom.Document()
        settingsXML.appendChild( rootNode )
        
        try:
            settingsFile = open( self._settingsFileFullPath, 'w' )
        except IOError:
            print "couldn't open the settings file"
        finally:
            settingsXML.writexml( settingsFile )
            settingsFile.close()
    
    
    
    #----------------------------------------------------------------------
    def create(self):
        """creates the sequence
        """
        # create a folder with sequenceName
        exists = oyAux.createFolder( self._fullPath )
        
        if not exists:
            # copy the settings file to the root of the sequence
            shutil.copy( self._database._defaultSettingsFullPath, self._settingsFileFullPath )
        
        # just read the structure from the XML
        self._readSettings()
        
        # tell the sequence to create its own structure
        self.createStructure()
        
        # and create the shots
        self.createShots()
        
        # copy any file to the sequence
        # (like workspace.mel, find a reasonable way)
        for _file in self._database._defaultFilesList:
            shutil.copy( os.path.join( self._database._projectManagerFullPath, _file), self._fullPath )
    
    
    
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
        """
        
        # for now consider the shots as a string of range
        # do the hard work later
        
        #rConv = RangeConverter()
        newShotsList = RangeConverter.convertRangeToList( shots )
        
        # convert the list to strings
        newShotsList = map(str, newShotsList)
        
        # add the shotList to the current _shotList
        self._shotList = oyAux.unique( oyAux.concatenateLists( self._shotList, newShotsList ) )
        
        # sort the shotList
        self._shotList = oyAux.sort_strings_with_embedded_numbers( self._shotList )
    
    
    
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
        self._saveSettings()
    
    
    
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
        
        pieces = oyAux.embedded_numbers( str(shotNumber) )
        
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
        return str(int(numberAsStr)) + alternateLetter
    
    
    
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
    def getAssetTypes(self):
        """returns a list of AssetType objects that this project has
        """
        return self._assetTypes
    
    
    
    #----------------------------------------------------------------------
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
        
        # for each folder search child folders
        for folder in assetFolders:
            fullPath = os.path.join( self._fullPath, folder)
            childFolders = os.listdir( fullPath )
            
            # -- experience --
            #childFolders = [ folder for folder in os.listdir( fullPath ) if os.path.isdir(os.path.join(fullPath,folder)) and folder != '']
            
            for childFolder in childFolders:
                
                childFolderFullPath = os.path.join( fullPath, childFolder )
                if childFolder == '' or not os.path.isdir(childFolderFullPath):
                    continue
                
                childFiles = os.listdir( childFolderFullPath )
                
                for childFile in childFiles:
                    childFileFullPath = os.path.join( childFolderFullPath, childFile)
                    if childFile.startswith( childFolder ) and os.path.isfile( childFileFullPath ):
                        asset = assetModel.Asset( self.getProject(), self, childFile ) 
                        
                        if asset.isValidAsset() and self.isValidExtension(asset.getExtension()):
                            assets.append( asset )
        
        return assets
    
    
    
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
        assetInfos = [ asset.getInfoVariables() for asset in assetList ]
        
        filteredAssetInfos = self.assetFilter( assetInfos, **kwargs)
        
        # recreate assets and return
        # TODO: return without recreating the assets
        #return [ assetModel.Asset(self._parentProject._name, self._name, x['fileName']) for x in filteredAssetInfos ]
        return [ assetModel.Asset(self._parentProject, self, x['fileName']) for x in filteredAssetInfos ]
    
    
    
    #----------------------------------------------------------------------
    def assetFilter(self, dicts, **kwargs):
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
        """
        self._extensionsToIgnore.append( extension )






########################################################################
class Structure(object):
    _shotDependentFolders = [] * 0
    _shotIndependentFolders = [] * 0
    
    
    
    
    #----------------------------------------------------------------------
    def __init__(self, shotDependentFolders=None, shotIndependentFolders=None):
        self._shotDependentFolders = shotDependentFolders
        self._shotIndependentFolders = shotIndependentFolders
    
    
    
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
    def getShotDependentFolders(self):
        """returns shot dependent folders as list
        """
        return self._shotDependentFolders
    
    
    
    #----------------------------------------------------------------------
    def getShotIndependentFolders(self):
        """returns shot independent folders as list
        """
        return self._shotIndependentFolders