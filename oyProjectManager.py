"""
oyProjectManager.py by Erkan Ozgur Yilmaz (c) 2009

v0.1.3

Description :
-------------
The oyProjectManager is created to manage our animation studios own projects,
within a predefined project structure. It is also a simple asset management
system. The main purpose of this system is to create projects, sequences and
to prevent users to save their files in correct folders with correct names. So
anyone can find their files by using this system. But again it is not a
complete Project Asset Management System.

This system uses the file system as a database, and extracts the information
from the folder and file names. And because it uses a consistent structure
while creating both the projects, sequences and assets, it works very fine.

Another aim of this code is to prevent the user to use the OSes own file
manager (ie. Windows Explorer on Windows ) to define the name and placement of
the asset file.

While working for a project, everytime we create an asset the files can
generally be grouped with the aim of that file. For example we create files for
models, animations, renders etc.. So it is easy to define a file name that can
spesify the type of that asset, and we can place the same types of the files
in to same folders, in a predifined folder structure. So this project manager
creates the folder structure and the file name whenever a user uses this code
while saving its asset.



Definitions :
-------------
Project  : A project is a folder under the default projects folder that
           contains sequence folders

Sequence : A sequence is a structure of child folders. All of these child
           folders created for a spesific task. Like a folder for Models, a
           folder for Animations etc. But the structure can be freely edited
           by changing the .settings.xml file under the sequences root.
           
           The default structure is hold in the project managers own folder
           (this folder can be queried by using a database object), and every
           project has a modified copy of this XML file.
           
           So, while one project can have an animation folder for animations,
           another can choose not to have one. So while working for a project
           the creator of the project can freely decide the structure of the
           new project. This was one of the missing properties in the previous
           systems.
           
           Most of the child folders are for assets. So some specific types
           of assets are placed under the folders for those asset types.

Asset    : Assets are any files those the users have created. They have
           several information those needs to be carried with the asset file.
           Generally these information called the Metadata.
           
           In our current system, the metadata is saved in the file name. So
           the file system is used as a database.
           
           When the users wants to save their files, the system automatically
           decides the file name and the placement of the file, by trying to
           get the minimum amount of information from the user.
           
           Assets have their own folders under the type folder. So every
           version of that asset are saved under the same folder, with the
           increasing version number in the file name.



The asset management done by injecting the Metadata to the name of the asset
file. This way it is very simple to get information about that asset, both for
a human and for a parser.

Asset names consists from these parts:

{BaseName}_{SubName}_{TypeName}_{RevString}_{VerString}_{UserInitials}_{Notes}

BaseName     : The base name that specifies the asset, for shot dependent asset
               types it is the ShotString ( e.g. SH010 ), for shot independent
               assets it is user dependent

SubName      : For assets that doesn't have an subName it is MAIN, for other
               assets it is user dependent

TypeName     : The asset types are defined in the sequence settings, and the
               typeName takes its string representation from that settings
               file. There is no default value, it can completely be changed
               from project to project, examples to asset type names are MODEL,
               ANIMATION, RENDER, PREVIS etc. for more information about asset
               types look to the documentation of Sequence class

RevString    : The revision string represents a number that is usually
               increased when the director or the client has commented the
               asset and when the asset needs revisions, it can be hold at 0
               all the time. A typical revision string is something like that
               r00, r02 etc. Again the revision prefix ('r') is defined in the
               Sequence settings file

VerString    : The version string represents the current version of the asset.
               It is increased for every incarnation of that asset. So version
               tracking is done by increasing that number for every version of
               that asset. A typical version string is something like that
               v001, v010, v548 etc. Again the version prefix ('v') is defined
               in the Sequence settings file

UserInitials : Represents the user that created that version of the asset file.
               It comes from the users.xml file at the server

Notes        : The notes about the asset can be hold here. Although it
               increases the file name a lot, it is helpful to add a note for
               specific asset versions. Generally it is limited to 30
               characters, but that limitation can be changed from the
               Sequence .settings.xml



Assets are placed under:

{projectsPath}/{projectName}/{sequenceName}/{typeFolder}/{baseName}/{assetFileName}



Command Line Options :
----------------------

-e, --environment    specifies the working environment, currently it accepts
                     values like:
                     
                     MAYA, NUKE, PHOTOSHOP, HOUDINI and None
                     
                     the default value is None

-f, --fileName       the file name of the current asset, it helps getting some
                     of the information

-h, --help           displays the doc string (this)

-p, --path           the path of the current asset, it helps getting some of
                     the information

-u, --userInterface  displays the user interface ( needs PyQt4 installed )

-v, --version        displays version information



Version History :
-----------------
v0.1.3
- added external settings file for the database

v0.1.2
- switched to QMainWindow from QDialog
- added the version information to the window title

v0.1.1
- the MainDialog object now stores a local Project and a Sequence object to
  help its methods to use the cache system while querying the data
- increased the maxTimeDelta in CachedMethod attribute to 60 seconds

v0.1.0
- Added support for old style of Asset naming, which has no subName field, this
  support made the code a little bit unreadable and dirty so it needs to be
  removed as soon as this support is obsolute

v0.0.9
- in previous versions, even there was a parser for the database node in the
  sequence settings, it was not used, so the sequence was running with its
  default values for some variables, it is fixed now
- added functionalities to open tab in the UI, this update introduced a lot of
  code duplication, this will be fixed in next versions
- now the interface tries to keep the assetType fixed from one sequence to
  another sequence
- replaced the saveCancel_buttonBox with individual Save and Cancel buttons
- convertToShotString in Sequence object now accepts both integers and strings
  as shotNumber argument, and converts them properly to shotStrings
- Asset objects getAllVersions method was trying to dive in to the file system
  to get the other versions, now it uses the parentSequence to get all the
  versions, it has a little bit more overhead but later on if we switch to a
  real database it will be easy to implement this way
- added extensionsToIgnore settings to Sequence objects, to prevent listinings
  of files which are not actually an Asset but has valid file name structure
  (for example the .smr files have correct naming convention but they are not
  actual assets)
- the asset info variables are now initialized with None instead of ''
- in Asset object, it is now possible to query the versions of an Asset object
  without supplying all of the information (_fullInfo), the baseName, subName
  and typeName (_baseInfo) is now enough to get a list of Asset objects
- Asset objects extension is now queryable

v0.0.8
- Asset objects now accepts one of the rev/revString and ver/verString info
  variables when setting the infoVariables
- Asset objects now has exists and baseExists attributes. exists is True when
  the file exists, baseExists is True when there are files starting with same
  critiqueName
- Asset objects now has getPathVariables() method that returns the
  pathVariables
- Asset objects now has getCritiqueName() method that returns the critique part
  of the asset fileName, which is the string baseName_subName_typeName
- Asset objects now has several get methods for getting the whole info about
  that particular asset
- Database object now has a method that converts a path in to a project and
  sequence name if possible
- Sequence objects now can convert a shotString to shotNumber, which is also a
  string
- Fixed the alignment problems in the MainDialog interface elements
- changed the baseName and subName lineEdit fields to comboBox, to let the user
  choose from a list of available choises for the current asset. For example,
  if the user choose MODEL for assetType then all the model assets baseNames
  are listed in baseName comboBox, and if the user selects one of the MODELs
  then the subName comboBox is filled with subNames of that MODEL...
- added a main function for the script to be used from the command line
- the MainDialog now initializes with the environment, fileName and path
  variable, so it is now possible to fill the fields with the info that comes
  from those variables
- "get latest revision" and "get latest version" buttons are now working
- the MainDialog now can return an Asset object build with the data from the
  fields

v0.0.7
- added a main function
- added an environment option to setup the program for that environment
  like( MAYA, NUKE, HOUDINI, PHOTOSHOP etc. )
- changed the commented region at the start (this section) to a doc string

v0.0.6
- fixed CachedMethod, it was storing the data in class instead of the
  instance object, so two objects in the same type were sharing the same
  cache, resulting false information, it is fixed now by completely re-writing
  the CachedMethod class
- the assetTypes comboBox was complaining about the assetTypes variable
  to be None, this is fixed now by checking the assetTypes variable against
  None

v0.0.5
- added an PyQt4 interface
- added CachedMethod function decorator to cache functions return values
  over a period of time

v0.0.4
- added asset filtering routines to help getting data more quickly

v0.0.3
- Sequence can now query all assets, all asset in specific type and all asset
  of a specific user
- Sequence uses a simple cache for querying assets
- for all the classes added 'get/set' prefixes for the functions that gets or
  sets something

v0.0.2
- database, project and sequence classes are now working properly, but they
  definitely need more attention

v0.0.1
- intial development version



TODO List :
-----------
- use the user class to define if the user can change the project
- keep track of the project timings, progress of the project
+ add an Asset class
- create appropriate Error classes for errors
- use a SQLDatabase running in the server to gather quick information about
  the projects, sequences and assets
+ add an interface with PyQt4
- add program names attribute to the assetType objects, so they can be
  listed for specific programs only (e.g. MAYA, NUKE, PHOTOSHOP etc.)
+ use external settings file in XML format for the database, instead of
  burrying the data to the class
- to get benefit from the caching system in the MainDialog class, add a project
  and sequence attribute and fill them whenever the project and sequence is
  changed to something else
- try to add another type of caching system, which is input dependent, so for
  same input it should return the same value without evaluating anything
- the objects needs a more robust caching method
- reduce the code duplication in MainDialog

-------------------------------------------------------------------------------
"""


__version__ = "0.1.2"



import os, sys, re, shutil, time, unittest, getopt
import oyAuxiliaryFunctions as oyAux
from xml.dom import minidom
from PyQt4 import QtGui, QtCore
from oyProjectManagerUI import Ui_MainWindow



mainWindow = None



# the decorators
#######################################################################
class CachedMethod(object):
    """caches the result of a class method inside the instance
    """
    
    
    
    def __init__(self, method):
        # record the unbound-method and the name
        self._method = method
        self._name = method.__name__
        self._obj = None
    
    
    
    def __get__(self, inst, cls):
        """use __get__ just to get the instance object
        """
        #print "running __get__ in CachcedMethod"
        
        self._obj = inst
        try:
            getattr ( self._obj, self._name + "._data" )
        except AttributeError:
            #print "AttributeError, filling the data"
            setattr ( self._obj, self._name + "._data", None )
            setattr ( self._obj, self._name + "._lastQueryTime", 0 )
            setattr ( self._obj, self._name + "._maxTimeDelta", 60 )
            #print "finished filling"
        
        return self
    
    
    
    def __call__(self, *args, **kwargs):
        """
        """
        #print "running __call__ in CachedMethod"
        
        delta = time.time() - getattr( self._obj, self._name + "._lastQueryTime" )
        
        if delta > getattr(self._obj, self._name + "._maxTimeDelta") or getattr(self._obj, self._name + "._data" ) == None:
            # call the function and store the result as a cache
            #print "caching the data"
            data = self._method(self._obj, *args, **kwargs )
            setattr( self._obj, self._name + "._data", data )
            
            # zero the time
            lastQueryTime = time.time()
            setattr( self._obj, self._name + "._lastQueryTime", time.time() )
        #else:
            #print "returning the cached data"
        
        return getattr( self._obj, self._name + "._data" )
    
    
    
    def __repr__(self):
        """Return the function's docstring
        """
        return self._method.__doc__






# the classes
########################################################################
class Database(object):
    """Database class gives informations about the projects.
    """
    
    
    
    #----------------------------------------------------------------------
    def __init__(self):
        # for now use strings for settings
        
        self._settingsFileName = 'oyProjectManager_settings.xml'
        
        #self._serverPath = "/home/ozgur/Documents/Works" + os.path.sep
        #self._serverPaths =  [] * 0
        
        #self._projectsFolderName = "JOBs2"
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
    @CachedMethod
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
            self._users.append( User(name, initials) )
    
    
    
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
    @CachedMethod
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
    def __init__(self, projectName, database = None):
        
        if database == None:
            self._database = Database()
        else:
            self._database = database
        
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
        newSequence = Sequence( self._name, sequenceName )
        newSequence.addShots( shots )
        newSequence.create()
        
        return newSequence
    
    
    
    #----------------------------------------------------------------------
    @CachedMethod
    def getSequenceNames(self):
        """returns the sequence names of that project
        """
        self.updateSequenceList()
        return self._sequenceList
    
    
    
    #----------------------------------------------------------------------
    @CachedMethod
    def getSequences(self):
        """returns the sequences as sequence objects
        
        don't use it offen, because it causes the system to parse all the sequence settings
        for all the sequences under that project
        
        it is now using the caching mechanism use it freely
        """
        
        self.updateSequenceList()
        sequences = [] * 0
        
        for sequenceName in self._sequenceList:
            sequences.append( Sequence( self._name, sequenceName) )
        
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
        
        assert(isinstance(database, Database))
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
    def __init__(self, projectName, sequenceName):
        # create the parent project with projectName
        self._parentProject = Project( projectName )
        self._database = self._parentProject.getDatabase()
        
        self._name = oyAux.file_name_conditioner( sequenceName )
        self._path = self._parentProject.getFullPath()
        self._fullPath = os.path.join( self._path, self._name )
        
        self._settingsFile = ".settings.xml"
        self._settingsFilePath = self._fullPath
        self._settingsFileFullPath = os.path.join( self._settingsFilePath, self._settingsFile )
        
        self._structure = Structure()
        self._assetTypes = [ AssetType() ] * 0
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
            
            self._assetTypes.append( AssetType( name, path, shotDependency, playblastFolder) )
    
    
    
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
        for assetType in self._assetTypes:
            assert( isinstance( assetType, AssetType ) )
            typeNode = minidom.Element('type')
            typeNode.setAttribute( 'name', assetType.getName() )
            typeNode.setAttribute( 'path', assetType.getPath() )
            typeNode.setAttribute( 'shotDependent', str( int( assetType.isShotDependent() ) ) )
            typeNode.setAttribute( 'playblastFolder', assetType.getPlayblastFolder() )
            
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
    @CachedMethod
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
    @CachedMethod
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
                        asset = Asset( self.getProjectName(), self.getName(), childFile ) 
                        
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
        return [ Asset(self._parentProject._name, self._name, x['fileName']) for x in filteredAssetInfos ]
    
    
    
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






########################################################################
class Asset(object):
    """yet another asset class
    to work properly it needs a valid project and sequence name
    
    an Assets folder is something like that:
    
    ProjectsFolder / ProjectName / SequenceName / TypePath / BaseName / assetFileName
    """
    
    
    
    #----------------------------------------------------------------------
    def __init__(self, projectName, sequenceName, fileName=None):
        
        self._parentProject = Project( projectName )
        self._parentSequence = Sequence( projectName, sequenceName )
        
        # asset metadata
        # info variables
        
        # baseName could represent a shot string
        self._baseName = None
        self._subName = None
        self._type = None
        self._typeName = None
        self._rev = None
        self._revString = None
        self._ver = None
        self._verString = None
        self._userInitials = None
        self._notes = None
        self._extension = ''
        
        # path variables
        self._fileName = None #os.path.splitext(fileName)[0] # remove the extension
        self._path = None
        self._fullPath = None
        
        self._hasFullInfo = False
        self._hasBaseInfo = False
        
        self._dataSeparator = '_'
        
        if fileName != None:
            self._fileName = str( os.path.splitext(fileName)[0] ) # remove the extension
            self._extension = str( os.path.splitext(fileName)[1] ).split( os.path.extsep )[-1] # remove the . in extension
            self.guessInfoVariablesFromFileName()
        
        self._exists = False
        self._baseExists = False
        
        self.updateExistancy()
    
    
    
    #----------------------------------------------------------------------
    def setInfoVariables(self, **keys):
        """ sets the info variables with a dictionary
        
        the minimum valid info variables are:
        
        baseName
        subName
        typeName
        
        and the rest are:
        rev or revString
        ver or verString
        userInitials
        notes (optional)
        extension (optional for most of the methods)
        """
        assert(isinstance(keys,dict))
        
        if keys.has_key('baseName'):
            self._baseName = keys['baseName']
        
        if keys.has_key('subName'):
            self._subName = keys['subName']
        
        if keys.has_key('typeName'):
            self._typeName = keys['typeName']
            self._type = self._parentSequence.getAssetTypeWithName( self._typeName )
        
        # convert revision and version strings to number
        if keys.has_key('revString'):
            self._revString = keys['revString']
            self._rev = self._parentSequence.convertToRevNumber( self._revString )
        elif keys.has_key('rev'):
            self._rev = int( keys['rev'] )
            self._revString = self._parentSequence.convertToRevString( self._rev )
        
        if keys.has_key('verString'):
            self._verString = keys['verString']
            self._ver = self._parentSequence.convertToVerNumber( self._verString )
        elif keys.has_key('ver'):
            self._ver = int( keys['ver'])
            self._verString = self._parentSequence.convertToVerString( self._ver )
        
        if keys.has_key('userInitials'):
            self._userInitials = keys['userInitials']
        
        if keys.has_key('notes'):
            self._notes = keys['notes']
        
        if keys.has_key('extension'):
            self._extension = keys['extension']
        
        if not self._parentSequence._noSubNameField:
            if self._baseName != None and self._subName != None and self._type != None:
                self._hasBaseInfo = True
                if self._rev != None and self._ver != None and self._userInitials != None:
                    self._hasFullInfo = True
        else:  # remove this block when the support for old version becomes obsolute
            if self._baseName != None and self._type != None:
                self._hasBaseInfo = True
                if self._rev != None and self._ver != None and self._userInitials != None:
                    self._hasFullInfo = True
        
        # get path variables
        self.setPathVariables()
        self.updateExistancy()
    
    
    
    #----------------------------------------------------------------------
    def getInfoVariables(self):
        """returns the info variables as a dictionary
        """
        
        infoVars = dict()
        infoVars['baseName'] = self._baseName
        infoVars['subName'] = self._subName
        infoVars['typeName'] = self._type.getName()
        infoVars['rev'] = self._rev
        infoVars['revString'] = self._revString
        infoVars['ver'] = self._ver
        infoVars['verString'] = self._verString
        infoVars['userInitials'] = self._userInitials
        infoVars['notes'] = self._notes
        infoVars['fileName'] = self._fileName
        
        return infoVars
    
    
    
    #----------------------------------------------------------------------
    def guessInfoVariablesFromFileName(self):
        """tries to get all the info variables from the file name
        """
        
        parts = self._fileName.split( self._dataSeparator )
        
        if not self._parentSequence._noSubNameField:
            if len(parts) < 5:
                return
            
            self._baseName     = parts[0]
            self._subName      = parts[1]
            self._typeName     = parts[2]
            self._revString    = parts[3]
            self._verString    = parts[4]
            self._userInitials = parts[5]
            
            if len(parts) > 6: # there should be a notes part
                self._notes = self._dataSeparator.join( parts[6:len(parts)] )
            else:
                self._notes = ""
        
        else: # remove this block when the support for old version becomes obsolute
            if len(parts) < 4:
                return
            
            self._baseName     = parts[0]
            self._typeName     = parts[1]
            self._revString    = parts[2]
            self._verString    = parts[3]
            self._userInitials = parts[4]
        
            if len(parts) > 5: # there should be a notes part
                self._notes = self._dataSeparator.join( parts[6:len(parts)] )
            else:
                self._notes = ""
        
        # get the type object
        self._type = self._parentSequence.getAssetTypeWithName( self._typeName )
        self._rev = self._parentSequence.convertToRevNumber( self._revString )
        self._ver = self._parentSequence.convertToVerNumber( self._verString )
        
        self._hasFullInfo = self._hasBaseInfo = True
        
        self.setPathVariables()
    
    
    
    #----------------------------------------------------------------------
    def setPathVariables(self):
        """sets path variables
        needs the info variables to be set before
        """
        
        # if it has just the base info update some of the variables
        if self._hasBaseInfo:
            seqFullPath = self._parentSequence.getFullPath()
            typeFolder = self._type.getPath()
            
            self._path = os.path.join( seqFullPath, typeFolder, self._baseName )
            
            # if it has full info update the rest of the variables
            if self._hasFullInfo:
                
                self._fileName = self.getFileName()
                self._fullPath = os.path.join( self._path, self._fileName )
                
                self.updateExistancy()
    
    
    
    #----------------------------------------------------------------------
    def getFullPath(self):
        """returns the fullPath of the asset
        """
        return self._fullPath
    
    
    
    #----------------------------------------------------------------------
    def getPath(self):
        """retrurns the path of the asset
        """
        return self._path
    
    
    
    #----------------------------------------------------------------------
    def getExtension(self):
        """returns the extension
        """
        return self._extension
    
    
    
    #----------------------------------------------------------------------
    def getFileName(self):
        """gathers the info variables to a fileName
        """
        
        if not self.isValidAsset():
            return None
        
        parts = [] * 0
        parts.append( self._baseName )
        
        if not self._parentSequence._noSubNameField:
            parts.append( self._subName )
        
        parts.append( self._type.getName() )
        parts.append( self._revString )
        parts.append( self._verString )
        parts.append( self._userInitials )
        
        # if there is no note don't add any self._dataSeparator
        if self._notes != None and self._notes != '':
            parts.append( self._notes )
        
        fileName = self._dataSeparator.join(parts)
        
        if self._extension != None and self._extension != '':
            fileName = fileName + os.path.extsep + self._extension
        
        return fileName
    
    
    
    #----------------------------------------------------------------------
    def getPathVariables(self):
        """returns the path variables which are
        fullPath
        path
        fileName
        """
        return self.getFullPath(), self.getPath(), self.getFileName()
    
    
    
    #----------------------------------------------------------------------
    def getAllVersions(self):
        """returns all version names for that asset as a list of strings
        """
        # return if we can't even get some little information
        if not self._baseExists and not self._hasBaseInfo:
            return []
        
        # use the Sequence object instead of letting the Asset object to dive in to the
        # file system to get other versions
        
        if not self._parentSequence._noSubNameField:
            return self._parentSequence.filterAssets( self._parentSequence.getAllAssets(), baseName = self._baseName, subName = self._subName, typeName = self._typeName )
        else:
            return self._parentSequence.filterAssets( self._parentSequence.getAllAssets(), baseName = self._baseName, typeName = self._typeName )
    
    
    
    #----------------------------------------------------------------------
    def _getCritiqueName(self):
        """ returns the critique part of the asset name, which is:
        BaseName_SubName_TypeName
        """
        
        if not self._parentSequence._noSubNameField:
            if self._baseName == None or self._subName == None or self._typeName == None:
                return None
            
            return self._dataSeparator.join( [self._baseName, self._subName, self._typeName ] )
        
        else: # remove this block when the support for old version becomes obsolute
            if self._baseName == None or self._typeName == None:
                return None
            
            return self._dataSeparator.join( [self._baseName, self._typeName ] )
    
    
    
    #----------------------------------------------------------------------
    def getLatestVersion(self):
        """returns the lastest version of an asset as an asset object and the number as an integer
        if the asset file doesn't exists yet it returns None, None
        """
        
        if not self._baseExists:
            return None, None
        
        allVersions = self.getAllVersions()
        
        if len(allVersions) == 0:
            return None, None
        
        maxVerNumber = -1
        currentVerNumber = -1
        maxVerAsset = self
        
        for asset in allVersions:
            currentVerNumber = asset.getVersionNumber()
            
            if currentVerNumber > maxVerNumber:
                maxVerNumber = currentVerNumber
                maxVerAsset = asset
        
        return maxVerAsset, maxVerNumber
    
    
    
    #----------------------------------------------------------------------
    def getLatestRevision(self):
        """returns the latest revision of an asset as an asset object and the number as an integer
        if the asset doesn't exists yet it returns None, None
        """
        
        if not self._baseExists:
            return None, None
        
        allVersions = self.getAllVersions()
        
        if len(allVersions) == 0:
            return None, None
        
        maxRevNumber = -1
        currentRevNumber = -1
        maxRevAsset = self
        
        for asset in allVersions:
            currentRevNumber = asset.getRevisionNumber()
            
            if currentRevNumber > maxRevNumber:
                maxRevNumber = currentRevNumber
                maxRevAsset = asset
        
        return maxRevAsset, maxRevNumber
    
    
    
    #----------------------------------------------------------------------
    def increaseVersion(self):
        """increases the version by 1
        """
        self._ver += 1
        self._verString = self._parentSequence.convertToVerString( self._ver )
    
    
    
    #----------------------------------------------------------------------
    def increaseRevision(self):
        """increases the revision by 1
        """
        self._rev += 1
        self._revString = self._parentSequence.convertToRevString( self._rev )
    
    
    
    #----------------------------------------------------------------------
    def isShotDependent(self):
        """returns True if the asset is shot dependent
        """
        return self._type.isShotDependent()
    
    
    
    #----------------------------------------------------------------------
    def isValidAsset(self):
        """returns True if this file is an Asset False otherwise
        """
        # if it has a baseName, subName, typeName, revString, verString and a userInitial string
        # and the parent folder for the asset starts with assets baseName
        # then it is considered as a valid asset
        
        if not self._parentSequence._noSubNameField:
            # check the fileName
            validFileName = bool(self._baseName != '' and self._subName != '' and self._typeName != '' and self._revString != '' and \
               self._verString != '' and self._userInitials != '' and self._validateRevString() and \
               self._validateVerString())
            
        else: # remove this block when the support for old version becomes obsolute
            # check the fileName
            validFileName = bool(self._baseName != '' and self._typeName != '' and self._revString != '' and \
               self._verString != '' and self._userInitials != '' and self._validateRevString() and \
               self._validateVerString())
        
        return validFileName
    
    
    
    #----------------------------------------------------------------------
    def _validateRevString(self):
        """validates if the revision string follows the format
        """
        revPrefix = self._parentSequence._revPrefix
        
        return re.match( revPrefix+'[0-9]+', self._revString )
    
    
    
    #----------------------------------------------------------------------
    def _validateVerString(self):
        """validates if the version string follows the format
        """
        verPrefix = self._parentSequence._verPrefix
        
        return re.match( verPrefix+'[0-9]+', self._verString )
    
    
    
    ##----------------------------------------------------------------------
    #def _validateExtension(self):
        #"""check if the extension is in the ignore list in the parent
        #sequence
        #"""
    
    
    
    #----------------------------------------------------------------------
    def getVersionNumber(self):
        """returns the version number of the asset
        """
        return self._ver
    
    
    
    #----------------------------------------------------------------------
    def getRevisionNumber(self):
        """returns the revsion number of the asset
        """
        return self._rev
    
    
    #----------------------------------------------------------------------
    def getShotNumber(self):
        """returns the shot number of the asset if the asset is shot dependent
        """
        
        if self.isShotDependent():
            return self._parentSequence.convertToShotNumber( self._baseName )
    
    
    
    #----------------------------------------------------------------------
    def getVersionString(self):
        """returns the version string of the asset
        """
        return self._verString
    
    
    
    #----------------------------------------------------------------------
    def getRevisionString(self):
        """returns the revision string of the asset
        """
        return self._revString
    
    
    
    #----------------------------------------------------------------------
    def getTypeName(self):
        """returns asset type
        """
        return self._type.getName()
    
    
    
    #----------------------------------------------------------------------
    def getUserInitials(self):
        """returns user initials
        """
        return self._userInitials
    
    
    
    #----------------------------------------------------------------------
    def getBaseName(self):
        """returns the base name of the asset
        """
        return self._baseName
    
    
    #----------------------------------------------------------------------
    def getSubName(self):
        """returns the sub name of the asset
        """
        return self._subName
    
    
    
    #----------------------------------------------------------------------
    def getNotes(self):
        """returns 
        """
        return self._notes
    
    
    
    #----------------------------------------------------------------------
    def exists(self):
        """returns True if the asset file exists
        """
        return self._exists
    
    
    
    #----------------------------------------------------------------------
    def updateExistancy(self):
        """updates the self._exists variable
        """
        if self._hasBaseInfo:
            if os.path.exists( self._path ):
                files = os.listdir( self._path )
                critiquePart = self._getCritiqueName()
                
                # update baseExistancy
                for _file in files:
                    if _file.startswith( critiquePart ):
                        self._baseExists = True
                        return
            
            if self._hasFullInfo:
                self._exists = os.path.exists( self._fullPath )
            
        else:
            self._exists = False
            self._baseExists = False







########################################################################
class AssetType(object):
    """Holds data like:\n
    - the asset type name
    - relative path of that type
    - the shot dependency of that AssetType
    """
    
    
    
    #----------------------------------------------------------------------
    def __init__(self, name='', path='', shotDependent=False, playblastFolder=''):
        self._name = name
        self._path = path
        self._shotDependency = shotDependent
        self._playblastFolder = playblastFolder
    
    
    
    #----------------------------------------------------------------------
    def getName(self):
        """return AssetType name
        """
        return self._name
    
    
    
    #----------------------------------------------------------------------
    def getPath(self):
        """returns AssetType path
        """
        return self._path
    
    
    
    #----------------------------------------------------------------------
    def isShotDependent(self):
        """returns True or False depending on to the shot dependency
        """
        return self._shotDependency
    
    
    
    #----------------------------------------------------------------------
    def getPlayblastFolder(self):
        """returns playblast folder of that asset type
        """
        return self._playblastFolder
    
    
    
    #----------------------------------------------------------------------
    def setName(self, name):
        """sets asset type name
        """
        self._name = name
    
    
    
    #----------------------------------------------------------------------
    def setPath(self, path):
        """sets asset type path
        """
        self._path = path
    
    
    
    #----------------------------------------------------------------------
    def setShotDependency(self, shotDependency):
        """sets shot dependency of that asset type
        """
        self._shotDependency = shotDependency






########################################################################
class RangeConverter(object):
    """a class for manipulating shot lists
    """
    
    
    
    #----------------------------------------------------------------------
    @staticmethod
    def convertRangeToList(_range):
        """a shotRange is a string that contains numeric data with "," and "-"
        characters
        
        1-4 expands to 1,2,3,4
        10-5 expands to 5,6,7,8,9,10
        1,4-7 expands to 1,4,5,6,7
        1,4-7,11-4 expands to 1,4,5,6,7,8,9,10,11
        """
        
        shotList = [] * 0
        number = 0
        
        assert(isinstance(_range, str))
        
        # first split for ","
        groups = _range.split(",")
        
        for group in groups:
            # try to split for "-"
            ranges = group.split("-")
            
            if len(ranges) > 1:
                if ranges[0] != '' and ranges[1] != '':
                    minRange = min( int(ranges[0]), int(ranges[1]))
                    maxRange = max( int(ranges[0]), int(ranges[1]))
                    
                    for number in range(minRange, maxRange+1):
                        if number not in shotList:
                            shotList.append( number )
            else:
                number = int(ranges[0])
                if number not in shotList:
                    shotList.append( int(ranges[0]) )
        
        shotList.sort()
        shotList = oyAux.concatenateLists( shotList )
        
        return shotList






########################################################################
class User(object):
    """a class for managing users
    """
    
    
    
    #----------------------------------------------------------------------
    def __init__(self, name='', initials=''):
        self._name = name
        self._initials = initials
        #self._type = ''
        pass
    
    
    
    #----------------------------------------------------------------------
    def getName(self):
        """returns the user name
        """
        return self._name
    
    
    
    #----------------------------------------------------------------------
    def getInitials(self):
        """returns the user initials
        """
        return self._initials
    
    
    
    #----------------------------------------------------------------------
    def setName(self, name):
        """sets the user name
        """
        self._name = name
    
    
    
    #----------------------------------------------------------------------
    def setInitials(self, initials):
        """sets the user initials
        """
        self._initials = initials






########################################################################
class MainWindow(QtGui.QMainWindow, Ui_MainWindow):
    """the main dialog of the system
    """
    
    
    
    #----------------------------------------------------------------------
    def __init__(self, environment, fileName, path):
        QtGui.QDialog.__init__(self)
        self.setupUi(self)
        
        # change the window title
        self.setWindowTitle( self.windowTitle() + ' v' + __version__ )
        
        # connect SIGNALs
        # close button
        QtCore.QObject.connect(self.save_button, QtCore.SIGNAL("clicked()"), self.saveButton_action )
        QtCore.QObject.connect(self.cancel_button1, QtCore.SIGNAL("clicked()"), self.close )
        QtCore.QObject.connect(self.cancel_button2, QtCore.SIGNAL("clicked()"), self.close )
        
        # project change ---> update sequence
        QtCore.QObject.connect(self.project_comboBox, QtCore.SIGNAL("currentIndexChanged(int)"), self._updateProjectObject )
        QtCore.QObject.connect(self.project_comboBox, QtCore.SIGNAL("currentIndexChanged(int)"), self.updateSequenceList)
        
        # sequence change ---> update _noSubNameField
        QtCore.QObject.connect(self.sequence_comboBox, QtCore.SIGNAL("currentIndexChanged(int)"), self._updateSequenceObject )
        QtCore.QObject.connect(self.sequence_comboBox, QtCore.SIGNAL("currentIndexChanged(int)"), self.updateForNoSubName)
        
        # sequence change ---> update asset type
        QtCore.QObject.connect(self.sequence_comboBox, QtCore.SIGNAL("currentIndexChanged(int)"), self.updateAssetTypeList)
        
        # sequence change ---> update shot lists
        QtCore.QObject.connect(self.sequence_comboBox, QtCore.SIGNAL("currentIndexChanged(int)"), self.updateShotList )
        
        # type change ---> base and shot enable disable
        QtCore.QObject.connect(self.assetType_comboBox1, QtCore.SIGNAL("currentIndexChanged(int)"), self.updateShotDependentFieldsInSave )
        QtCore.QObject.connect(self.assetType_comboBox2, QtCore.SIGNAL("currentIndexChanged(int)"), self.updateShotDependentFieldsInOpen )
        
        # type change ---> fill baseName comboBox
        QtCore.QObject.connect(self.assetType_comboBox1, QtCore.SIGNAL("currentIndexChanged(int)"), self.updateBaseNameFieldInSave )
        QtCore.QObject.connect(self.assetType_comboBox2, QtCore.SIGNAL("currentIndexChanged(int)"), self.updateBaseNameFieldInOpen )
        
        # shotName or baseName change ---> fill subName comboBox
        QtCore.QObject.connect(self.shot_comboBox1, QtCore.SIGNAL("currentIndexChanged(int)"), self.updateSubNameFieldInSave )
        QtCore.QObject.connect(self.shot_comboBox2, QtCore.SIGNAL("currentIndexChanged(int)"), self.updateSubNameFieldInOpen )
        QtCore.QObject.connect(self.baseName_comboBox1, QtCore.SIGNAL("currentIndexChanged(int)"), self.updateSubNameFieldInSave )
        QtCore.QObject.connect(self.baseName_comboBox2, QtCore.SIGNAL("currentIndexChanged(int)"), self.updateSubNameFieldInOpen )
        
        # subName change ---> fille assets_listWidget2 update ( OPEN TAB only )
        QtCore.QObject.connect(self.subName_comboBox2, QtCore.SIGNAL("currentIndexChanged(int)"), self.updateAssetsListWidget )
        QtCore.QObject.connect(self.baseName_comboBox2, QtCore.SIGNAL("currentIndexChanged(int)"), self.updateAssetsListWidget )
        QtCore.QObject.connect(self.shot_comboBox2, QtCore.SIGNAL("currentIndexChanged(int)"), self.updateAssetsListWidget )
        QtCore.QObject.connect(self.assetType_comboBox2, QtCore.SIGNAL("currentIndexChanged(int)"), self.updateAssetsListWidget )
        
        # get latest revision --> revision
        QtCore.QObject.connect(self.revision_pushButton, QtCore.SIGNAL("clicked()"), self.updateRevisionToLatest )
        
        # get latest version --> version
        QtCore.QObject.connect(self.version_pushButton, QtCore.SIGNAL("clicked()"), self.updateVersionToLatest )
        
        QtCore.QMetaObject.connectSlotsByName(self)
        
        # create a database
        self._db = Database()
        
        # fill them later
        self._project = None
        self._sequence = None
        
        self.environment = environment
        self.fileName = fileName
        self.path = path
        
        self.setDefaults()
        self.updateProjectList()
        
        self.fillFieldsFromFileInfo()
    
    
    
    #----------------------------------------------------------------------
    def setDefaults(self):
        """sets the default values
        """
        
        # set sub name to MAIN by default
        self.subName_comboBox1.clear()
        self.subName_comboBox1.addItem( "MAIN" )
        
        # append the users to the users list
        userInits = self._db.getUserInitials()
        
        self.user_comboBox1.clear()
        self.user_comboBox1.addItems( userInits )
        
        # update the user with the last selected user
        lastUser = self._db.getLastUser()
        
        userIndex = 0
        
        # get the user index
        for i in range(0, len(userInits)):
            if userInits[i] == lastUser:
                userIndex = i 
        
        self.user_comboBox1.setCurrentIndex( userIndex )
    
    
    
    #----------------------------------------------------------------------
    def fillFieldsFromFileInfo(self):
        """fills the ui fields from the data that comes from the fileName and path
        """
        
        # no use without the path
        if self.path == None:
            return
        
        # get the project and sequence names
        projectName, sequenceName = self._db.getProjectAndSequenceNameFromFilePath( self.path )
        
        # set the project and sequence
        self.setProjectName(projectName)
        self.setSequenceName(sequenceName)
        
        # no file name no use of the rest
        if self.fileName == None:
            return
        
        # fill the fields with those info
        # create an asset with the file name and get the information from that asset object
        
        asset = Asset( projectName, sequenceName, self.fileName )
        
        assetType = asset.getTypeName()
        shotNumber = asset.getShotNumber()
        baseName = asset.getBaseName()
        subName = asset.getSubName()
        revNumber = asset.getRevisionNumber()
        verNumber = asset.getVersionNumber()
        userInitials = asset.getUserInitials()
        notes = asset.getNotes()
        
        # fill the fields
        # assetType
        element = self.assetType_comboBox1
        element.setCurrentIndex( element.findText( assetType ) )
        
        # shotNumber and baseName
        if asset.isShotDependent():
            element = self.shot_comboBox1
            element.setCurrentIndex( element.findText( shotNumber) )
        else:
            self.baseName_comboBox1.setCurrentIndex( self.baseName_comboBox1.findText(baseName) )
        
        sequenceObject = Sequence( projectName, sequenceName )
        
        if not sequenceObject._noSubNameField: # remove this block when the support for old version becomes obsolute
            # sub Name
            self.subName_comboBox1.setCurrentIndex( self.subName_comboBox1.findText(subName) )
        
        # revision
        self.revision_spinBox.setValue( revNumber )
        
        # version : set the version and increase it by one
        self.version_spinBox.setValue( verNumber + 1 )
        
        # user
        element = self.user_comboBox1
        element.setCurrentIndex( element.findText( userInitials ) )
        
        # notes
        self.note_lineEdit1.setText( notes )
    
    
    
    #----------------------------------------------------------------------
    def updateProjectList(self):
        """updates projects list
        """
        
        serverPath = self._db.getServerPath()
        
        projectsList = self._db.getProjects()
        projectsList.sort()
        
        self.server_comboBox.clear()
        self.project_comboBox.clear()
        self.server_comboBox.addItem( serverPath )
        self.project_comboBox.addItems( projectsList )
    
    
    
    #----------------------------------------------------------------------
    def updateSequenceList(self, *arg):
        """updates the sequence according to selected project
        """
        
        self._updateProjectObject()
        currentProjet = self._project
        
        # create a project and ask the child sequences
        self.sequence_comboBox.clear()
        sequences = currentProjet.getSequenceNames()
        
        self.sequence_comboBox.addItems( sequences )
        
        self._updateSequenceObject() # it is not needed but do it for now
    
    
    
    #----------------------------------------------------------------------
    def updateAssetTypeList(self):
        """updates asset types
        """
        
        # get the asset types of that sequence
        self._updateSequenceObject()
        currentSequence = self._sequence
        
        # get asset types
        assetTypes = currentSequence.getAssetTypes()
        
        assetTypeNames = [ assetType.getName() for assetType in assetTypes ]
        
        # SAVE ASSET TAB
        # clear and update the comboBoxes
        # try to keep the same item in the list
        lastSelectedItem = self.assetType_comboBox1.currentText()
        self.assetType_comboBox1.clear()
        self.assetType_comboBox1.addItems( assetTypeNames )
        # reselect the last selected item
        
        if lastSelectedItem != "":
            self.assetType_comboBox1.setCurrentIndex( self.assetType_comboBox1.findText( lastSelectedItem ) )
        
        # OPEN ASSET TAB
        lastSelectedItem = self.assetType_comboBox2.currentText()
        self.assetType_comboBox2.clear()
        self.assetType_comboBox2.addItems( assetTypeNames )
        #reselect the last seelected item
        if lastSelectedItem != "":
            self.assetType_comboBox2.setCurrentIndex( self.assetType_comboBox2.findText( lastSelectedItem ) )
    
    
    
    #----------------------------------------------------------------------
    def updateShotList(self):
        """
        """
        
        self._updateSequenceObject()
        currentSequence = self._sequence
        
        # get shot list
        shotList = currentSequence.getShotList()
        
        # clear and update the list
        self.shot_comboBox1.clear()
        self.shot_comboBox1.addItems( shotList )
        
        self.shot_comboBox2.clear()
        self.shot_comboBox2.addItems( shotList )
    
    
    
    #----------------------------------------------------------------------
    def updateBaseNameFieldInSave(self):
        """updates the baseName fields with current asset baseNames for selected
        type, if the type is not shot dependent
        """
        
        # if the current selected type is not shot dependent
        # get all the assets of that type and get their baseNames
        
        self._updateSequenceObject()
        currentSequence = self._sequence
        
        currentTypeName = self.getCurrentAssetTypeInSave()
        
        if currentTypeName == None:
            return
        
        comboBox = self.baseName_comboBox1
        
        currentType = currentSequence.getAssetTypeWithName( currentTypeName )
        
        if currentType == None or currentType.isShotDependent():
            # do nothing
            return
        
        # get the assets of that type
        allAssets = currentSequence.filterAssets( currentSequence.getAllAssets(), typeName = currentTypeName )
        
        # get the base names
        baseNamesList = [] * 0
        for asset in allAssets:
            baseNamesList.append( asset.getBaseName() )
        
        # remove duplicates
        baseNamesList = oyAux.unique( baseNamesList )
        
        # add them to the baseName combobox
        comboBox.clear()
        
        # add an item for new items
        comboBox.addItem("")
        
        # add the list
        comboBox.addItems( baseNamesList )    
    
    
    
    #----------------------------------------------------------------------
    def updateBaseNameFieldInOpen(self):
        """updates the baseName fields with current asset baseNames for selected
        type, if the type is not shot dependent
        """
        
        # if the current selected type is not shot dependent
        # get all the assets of that type and get their baseNames
        self._updateSequenceObject()
        currentSequence = self._sequence
        
        currentTypeName = self.getCurrentAssetTypeInOpen()
        
        if currentTypeName == None:
            return
        
        comboBox = self.baseName_comboBox2
        
        currentType = currentSequence.getAssetTypeWithName( currentTypeName )
        
        if currentType == None or currentType.isShotDependent():
            return
        
        # get the assets of that type
        allAssets = currentSequence.filterAssets( currentSequence.getAllAssets(), typeName = currentTypeName )
        
        # get the base names
        baseNamesList = [] * 0
        for asset in allAssets:
            baseNamesList.append( asset.getBaseName() )
        
        # remove duplicates
        baseNamesList = oyAux.unique( baseNamesList )
        
        # add them to the baseName combobox
        comboBox.clear()
        
        # add the list
        comboBox.addItems( baseNamesList )
    
    
    
    #----------------------------------------------------------------------
    def updateSubNameFieldInSave(self):
        """updates the subName fields with current asset subNames for selected
        baseName, if the type is not shot dependent
        """
        
        # if the current selected type is not shot dependent
        # get all the assets of that type and get their baseNames
        self._updateSequenceObject()
        currentSequence = self._sequence
        
        # if the current sequence doesn't support subName field just return
        if currentSequence._noSubNameField:
            return
        
        currentAssetTypeName = self.getCurrentAssetTypeInSave()
        
        assetTypeObj = currentSequence.getAssetTypeWithName( currentAssetTypeName )
        
        if assetTypeObj == None:
            return
        
        if assetTypeObj.isShotDependent():
            currentBaseName = currentSequence.convertToShotString( self.getCurrentShotStringInSave() )
        else:
            currentBaseName = self.getCurrentBaseNameInSave()
        
        self._updateSubNameField( currentSequence, currentAssetTypeName, currentBaseName, self.subName_comboBox1 )
    
    
    
    #----------------------------------------------------------------------
    def updateSubNameFieldInOpen(self):
        """updates the subName fields with current asset subNames for selected
        baseName, if the type is not shot dependent
        """
        
        # if the current selected type is not shot dependent
        # get all the assets of that type and get their baseNames
        self._updateSequenceObject()
        currentSequence = self._sequence
        
        # if the current sequence doesn't support subName field just return
        if currentSequence._noSubNameField:
            return
        
        currentAssetTypeName = self.getCurrentAssetTypeInOpen()
        
        assetTypeObj = currentSequence.getAssetTypeWithName( currentAssetTypeName )
        
        if assetTypeObj == None:
            return
        
        if assetTypeObj.isShotDependent():
            currentBaseName = currentSequence.convertToShotString( self.getCurrentShotStringInOpen() )
        else:
            currentBaseName = self.getCurrentBaseNameInOpen()
        
        self._updateSubNameField( currentSequence, currentAssetTypeName, currentBaseName, self.subName_comboBox2 )
    
    
    
    #----------------------------------------------------------------------
    def _updateSubNameField(self, currentSequence, currentTypeName, currentBaseName, comboBox):
        """
        """
        
        if currentTypeName == None or currentBaseName == None:
            return
        
        currentType = currentSequence.getAssetTypeWithName( currentTypeName )
        
        if currentType == None:
            # do nothing
            return
        
        # get the assets of that type
        allAssets = currentSequence.filterAssets( currentSequence.getAllAssets(), typeName=currentTypeName, baseName=currentBaseName )
        
        # get the subNames
        subNamesList = [] * 0
        for asset in allAssets:
            subNamesList.append( asset.getSubName() )
        
        # add MAIN as default
        subNamesList.append('MAIN')
        
        # remove duplicates
        subNamesList = oyAux.unique( subNamesList )
        
        # add them to the baseName combobox
        comboBox.clear()
        
        # do not add an item for new items, the default should be MAIN
        # add the list
        comboBox.addItems( subNamesList )
    
    
    
    #----------------------------------------------------------------------
    def updateShotDependentFields(self):
        """updates shot dependent fields like the shotList and basName
        """
        
        self._updateSequenceObject()
        currentSequence = self._sequence
        
        # get selected asset type name
        assetTypeName1 = self.getCurrentAssetTypeInSave()
        assetTypeName2 = self.getCurrentAssetTypeInOpen()
        
        assetType1 = currentSequence.getAssetTypeWithName( assetTypeName1 )
        assetType2 = currentSequence.getAssetTypeWithName( assetTypeName2 )
        
        if assetType1 != None:
            # enable the shot if the asset type is shot dependent
            isShotDependent = assetType1.isShotDependent() 
            self.shot_comboBox1.setEnabled( isShotDependent )
            self.baseName_comboBox1.setEnabled( not isShotDependent )
        
        # ----- update OPEN ASSET FIELDS -------
        if assetType2 != None:
            isShotDependent = assetType2.isShotDependent()
            self.shot_comboBox2.setEnabled( isShotDependent )
            self.baseName_comboBox2.setEnabled( not isShotDependent )
    
    
    
    #----------------------------------------------------------------------
    def updateShotDependentFieldsInSave(self):
        """updates shot dependent fields like the shotList and baseName
        """
        
        self._updateSequenceObject()
        currentSequence = self._sequence
        
        # get selected asset type name
        assetTypeName = self.getCurrentAssetTypeInSave()
        
        assetType = currentSequence.getAssetTypeWithName( assetTypeName )
        
        if assetType == None:
            return
        
        # enable the shot if the asset type is shot dependent
        isShotDependent = assetType.isShotDependent() 
        self.shot_comboBox1.setEnabled( isShotDependent )
        self.baseName_comboBox1.setEnabled( not isShotDependent )
    
    
    
    #----------------------------------------------------------------------
    def updateShotDependentFieldsInOpen(self):
        """updates shot dependent fields like the shotList and baseName
        """
        
        self._updateSequenceObject()
        currentSequence = self._sequence
        
        # get selected asset type name
        assetTypeName = self.getCurrentAssetTypeInOpen()
        
        assetType = currentSequence.getAssetTypeWithName( assetTypeName )
        
        if assetType == None:
            return
        
        # enable the shot if the asset type is shot dependent
        isShotDependent = assetType.isShotDependent() 
        self.shot_comboBox2.setEnabled( isShotDependent )
        self.baseName_comboBox2.setEnabled( not isShotDependent )
    
    
    
    #----------------------------------------------------------------------
    def updateAssetsListWidget(self):
        """fills the assets listWidget with assets
        """
        
        self._updateProjectObject()
        self._updateSequenceObject()
        
        currentProject = self._project
        currentSequence = self._sequence
        
        typeName = self.getCurrentAssetTypeInOpen()
        
        if typeName == '' or typeName == None:
            return
        
        # if the type is shot dependent get the shot number
        # if it is not use the baseName
        if currentSequence.getAssetTypeWithName( typeName ).isShotDependent():
            baseName = currentSequence.convertToShotString( self.getCurrentShotStringInOpen() )
        else:
            baseName = self.getCurrentBaseNameInOpen()
        
        subName = self.getCurrentSubNameInOpen()
        
        # construct the dictionary
        assetInfo = dict()
        assetInfo['baseName'] = baseName
        assetInfo['subName' ] = subName
        assetInfo['typeName'] = typeName
        
        # construct the asset with base info
        asset = Asset( currentProject.getName(), currentSequence.getName())
        asset.setInfoVariables( **assetInfo )
        
        # get all versions list
        allVersionsList = asset.getAllVersions()
        
        # append them to the asset list view
        self.assets_listWidget2.clear()
        
        if len(allVersionsList) > 0:
            self.assets_listWidget2.addItems( sorted([asset.getFileName() for asset in allVersionsList]) )
    
    
    
    #----------------------------------------------------------------------
    def getCurrentProjectName(self):
        """returns the current project name
        """
        return str( self.project_comboBox.currentText() )
    
    
    
    def getCurrentSequenceName(self):
        """returns the current sequence name
        """
        return str( self.sequence_comboBox.currentText() )
    
    
    
    ##----------------------------------------------------------------------
    #def getCurrentAssetType(self):
        #"""returns the current assetType from the UI
        #"""
        
        #return str( self.assetType_comboBox1.currentText() ), str( self.assetType_comboBox2.currentText() )
    
    
    
    #----------------------------------------------------------------------
    def getCurrentAssetTypeInSave(self):
        """returns the current assetType from the UI
        """
        return str( self.assetType_comboBox1.currentText() )
    
    
    
    #----------------------------------------------------------------------
    def getCurrentAssetTypeInOpen(self):
        """returns the current assetType from the UI
        """
        return str( self.assetType_comboBox2.currentText() )
    
    
    
    #----------------------------------------------------------------------
    def getCurrentShotStringInSave(self):
        """returns the current shot string from the UI
        """
        
        return str( self.shot_comboBox1.currentText() )
    
    
    
    #----------------------------------------------------------------------
    def getCurrentShotStringInOpen(self):
        """returns the current shot string from the UI
        """
        
        return str( self.shot_comboBox2.currentText() )
    
    
    
    #----------------------------------------------------------------------
    def getCurrentBaseNameInSave(self):
        """returns the current baseName from the UI
        """
        
        return str( self.baseName_comboBox1.currentText() )
    
    
    
    #----------------------------------------------------------------------
    def getCurrentBaseNameInOpen(self):
        """returns the current baseName from the UI
        """
        
        return str( self.baseName_comboBox2.currentText() )
    
    
    
    #----------------------------------------------------------------------
    def getCurrentSubNameInSave(self):
        """returns the current subName from the UI
        """
        
        return str( self.subName_comboBox1.currentText() )
    
    
    
    #----------------------------------------------------------------------
    def getCurrentSubNameInOpen(self):
        """returns the current subName from the UI
        """
        
        return str( self.subName_comboBox2.currentText() )
    
    
    
    #----------------------------------------------------------------------
    def getCurrentRevNumber(self):
        """returns the current revision number from the UI
        """
        
        return str( self.revision_spinBox.value() )
    
    
    
    #----------------------------------------------------------------------
    def getCurrentVerNumber(self):
        """returns the current version number from the UI
        """
        
        return str( self.version_spinBox.value() )
    
    
    
    #----------------------------------------------------------------------
    def getCurrentUserInitials(self):
        """returns the current user initials from the UI
        """
        
        return str( self.user_comboBox1.currentText() )
    
    
    
    #----------------------------------------------------------------------
    def getCurrentNote(self):
        """returns the current note from the UI
        """
        
        return str( self.note_lineEdit1.text() )
    
    
    
    #----------------------------------------------------------------------
    def updateRevisionToLatest(self):
        """ tries to get the latest revision
        """
        
        # get the asset object from fields
        asset = self.getAssetObjectFromSaveFields()
        
        if asset == None or not asset.isValidAsset():
            return
        
        maxRevAsset, maxRevNumber = asset.getLatestRevision()
        
        if maxRevNumber == None:
            maxRevNumber = 0
            
        # update the field
        self.revision_spinBox.setValue( maxRevNumber )
    
    
    
    #----------------------------------------------------------------------
    def updateVersionToLatest(self):
        """ tries to get the latest version
        """
        
        # get the asset objet from fields
        asset = self.getAssetObjectFromSaveFields()
        
        if asset == None or not asset.isValidAsset():
            return
        
        maxVerAsset, maxVerNumber = asset.getLatestVersion()
        
        if maxVerNumber == None:
            maxVerNumber = 0
        
        # update the field
        self.version_spinBox.setValue( maxVerNumber + 1 )
    
    
    
    #----------------------------------------------------------------------
    def setProjectName(self, projectName):
        """sets the project in the combobox
        """
        if projectName == None:
            return
        
        index = self.project_comboBox.findText( projectName )
        
        if index != -1:
            self.project_comboBox.setCurrentIndex( index )
        
        # be sure it is updated
        self.project_comboBox.update()
    
    
    
    #----------------------------------------------------------------------
    def setSequenceName(self, sequenceName):
        """sets the sequence in the combobox
        """
        if sequenceName == None:
            return
        
        currentIndex = self.sequence_comboBox.currentIndex()
        
        index = self.sequence_comboBox.findText( sequenceName )
        
        if index != -1:
            self.sequence_comboBox.setCurrentIndex( index )
        
        # be sure it is updated
        self.sequence_comboBox.update()
    
    
    
    #----------------------------------------------------------------------
    def getAssetObjectFromSaveFields(self):
        """returns the asset object from the fields
        """
        
        assetObj = Asset( self._project.getName(), self._sequence.getName() )
        
        # gather information
        typeName = self.getCurrentAssetTypeInSave()
        
        assetTypeObj = self._sequence.getAssetTypeWithName(typeName)
        
        if assetTypeObj == None:
            return
        
        isShotDependent = assetTypeObj.isShotDependent()
        if isShotDependent:
            baseName = self._sequence.convertToShotString( self.getCurrentShotStringInSave() )
        else:
            baseName = self.getCurrentBaseNameInSave()
        
        subName = self.getCurrentSubNameInSave()
        rev = self.getCurrentRevNumber()
        ver = self.getCurrentVerNumber()
        userInitials = self.getCurrentUserInitials()
        notes = self.getCurrentNote()
        
        # construct info variables
        infoVars = dict()
        infoVars['baseName'] = baseName
        infoVars['subName'] = subName
        infoVars['typeName'] = typeName
        infoVars['rev'] = rev
        infoVars['ver'] = ver
        infoVars['userInitials'] = userInitials
        infoVars['notes'] = notes
        
        assetObj.setInfoVariables( **infoVars )
        
        return assetObj
    
    
    #----------------------------------------------------------------------
    def getFileNameFromSaveFields(self):
        """returns the file name from the fields
        """
        # get the asset object from fields
        assetObject = self.getAssetObjectFromSaveFields()
        
        return assetObject.getPathVariables(), assetObject
    
    
    
    ##----------------------------------------------------------------------
    #def validateFieldInput(self, UIElement):
        #"""validates the fields input
        #"""
        #pass
        ##if type(UIElement) == type(QtGui.QComboBox):
            ### validate the item
            ##assert(isinstance(UIElement, QtGui.QComboBox))
            
            ##UIElement.a oyAux.file_name_conditioner( UIElement.currentText() )
    
    
    
    #----------------------------------------------------------------------
    def saveButton_action(self):
        """returns the asset file name from the fields and closes the interface
        """
        
        self.close()
        return self.getFileNameFromSaveFields()
    
    
    
    #----------------------------------------------------------------------
    def updateForNoSubName(self):
        """this method will be removed in later version, it is written just to support
        old types of assets those have no subName field
        """
        
        # if the current sequence has no support for subName fields disable them
        self._updateSequenceObject()
        currentSequence = self._sequence
        
        self.subName_comboBox1.setEnabled(not currentSequence._noSubNameField)
        self.subName_comboBox2.setEnabled(not currentSequence._noSubNameField)
    
    
    
    #----------------------------------------------------------------------
    def _updateProjectObject(self):
        """updates the project object if it is changed
        it is introduced to take advantege of the cache system
        """
        
        currentProjectName = self.getCurrentProjectName()
        
        #assert(isinstance(self._project,Project))
        
        if self._project == None or (self._project.getName() != currentProjectName and (currentProjectName != "" or currentProjectName != None ) ):
            self._project = Project( currentProjectName )
    
    
    
    #----------------------------------------------------------------------
    def _updateSequenceObject(self):
        """updates the sequence object if it is not
        """
        
        currentSequenceName = self.getCurrentSequenceName()
        
        #assert(isinstance(self._sequence,Sequence))
        
        if self._sequence == None or (self._sequence.getName() != currentSequenceName and (currentSequenceName != "" or currentSequenceName != None ) ):
            self._updateProjectObject()
            newSeq = Sequence( self._project.getName(), currentSequenceName )
            if newSeq._exists:
                self._sequence = newSeq






#----------------------------------------------------------------------
def UI(environment=None, fileName=None, path=None ):
    """the UI
    """
    global app
    global mainWindow
    app = QtGui.QApplication(sys.argv)
    mainWindow = MainWindow(environment, fileName, path)
    mainWindow.show()
    app.exec_()
    app.connect(app, QtCore.SIGNAL("lastWindowClosed()"), app, QtCore.SLOT("quit()"))





#----------------------------------------------------------------------
def main(argv=None):
    """The main procedure
    """
    if argv is None:
        argv = sys.argv
    
    # parse command line options
    try:
        shortopts = "h,f:,p:,u,v,e:"
        longopts = ["help","fileName=","path=","userInterface","version","environment="]
        opts, args = getopt.getopt(sys.argv[1:], shortopts, longopts)
    except getopt.error, msg:
        print msg
        print "for help use --help"
        sys.exit(2)
    
    environment = None
    userInterface = False
    fileName = None
    path = None
   
    # process options
    for o, a in opts:
        if o in ("-h", "--help"):
            print __doc__
            sys.exit(0)
        
        if o in ("-e", "--environment"):
            environment = a
            
        if o in ("-u", "--userInterface"):
            userInterface = True
        
        if o in ("-v", "--version"):
            print __version__
            sys.exit(0)
        
        if o in ("-f", "--fileName"):
            fileName = a
        
        if o in ("-p", "--path"):
            path = a
    
    if userInterface:
        return UI(environment, fileName, path)





if __name__ == "__main__":
    main()

