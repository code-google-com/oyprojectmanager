"""
oyProjectManager by Erkan Ozgur Yilmaz (c) 2009

v9.11.9

Description :
-------------
The oyProjectManager is created to manage our animation studios own projects,
within a predefined project structure. It is also a simple asset management
system. The main purpose of this system is to create projects, sequences and
to allow users to save their files in correct folders with correct names. So
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

Another advantage of oyProjectManager is, it gives a framework to the project
manager, to edit all the project and sequences with very simple Python scripts.



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
           another can choose not to have one or can change the name. So while
           working for a project the creator of the project can freely decide
           the structure of the new project. This was one of the missing
           properties in the previous systems.
           
           Most of the child folders are for assets. So some specific types
           of assets are placed under the folders for those asset types.

Asset    : Assets are any files those the users have created. They have
           several information those needs to be carried with the asset file.
           Generally these information called the Metadata.
           
           In our current system, the metadata is saved in the file name. So
           the file system is used as the source of data.
           
           When the users want to save their files, the system automatically
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

SubName      : For assets that doesn't have a subName it is MAIN, for other
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

{projectsPath}/{projectName}/{sequenceName}/{typeFolder}/{baseName}/
{assetFileName}



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

-u, --userInterface  displays the user interface (needs PyQt4)

-v, --version        displays version information



Version History :
-----------------
v9.11.9
- fixed an error, occurred when a new type asset name is send to an old type
  project

v9.11.7
- when an asset object is initialized with a wrong file name, guessing the
  fields from file name will result index error, it is now fixed

v9.11.6
- mayaEnv now saves the asset file path to the recent files list in save and
  open actions, and retrieves the data from that list if there is currently
  no file opened

v9.11.3
- fixed, houdini was not opening files with asset manager

v9.11.2
- switched to a new versioning scheme, where the date is used as the version
  number like in ubuntu/kubuntu
- added houdini support

v0.7.8
- the asset manager ui now updates the revision and version to the latest if
  any of the sequence, assetType, shotNumber, baseName or subName field changes
- in asset manager ui, the subName field is reset if the assetType changed
- in asset manager ui, the subName field is cleared if there is no valid asset
  found from the input fields
- in asset manager ui, if there is no valid asset found in
  updateRevisionToLatest and updateVersionToLatest the fields are set to
  default values which are 0 and 1 respectly

v0.7.7
- the baseName and subName fields now are conditioned so that only the first
  letter is forced to be uppercase but the others can both be upper and lower
  case characters, and they are not validating any string if the length of the
  string is zero
- the Sequence classes getAllAssetFileNamesForType, getAllAssets and
  getAllAssetsForType methods now compares the lowercase fileName with the
  asset folders lowercase name to prevent case issues while retrieving assets
- Asset classes getAllVersions uses the fileName instead of the asset objects,
  to introduce some speed increases in long versioned asset objects
- Asset class now has a new method called getAllVersionNames, which returns all
  the version names as a list of string, it is much faster than getAllVersions
  because it doesn't create any asset object
- Asset class now has two new methods for getting the latest version and
  revision numbers and assets, which uses the getAllVersionNames to quickly get
  the version and revision numbers
- AssetManager interface class now uses the fast methods to retrieve asset
  names, versions and revisions quickly

v0.7.6
- Structure class now initializes the variables with list() not with None
- Structure class now has a method called fixPathIssues, to fix the path issues
- Structure class now has a method called removeDuplicate to remove duplicate
  entries
- Structure classes addShotDependentFolder, addShotIndependentFolder and 
  addOutputFolder now checks if the given folderName allready exists in the
  structure to prevent duplicate entries
- fixed a bug in Sequence class, where it adds outputFolders to the list
  without first clearing the list while saving the settings

v0.7.5
- added isValid method to Sequence class to check if the sequence is valid
- added getValidProjects method to Database class to get valid projects only
  (valid projects are the projects that has at least one valid sequence, and a
  valid sequence is the sequence that exists and has a .settings.xml file)
- the assetManager UI now only lists valid projects
- added the Singleton class
- the Database class is now derived from Singleton class
- to fix the update problem in the projectManager the cache in Database classes
  getProject method has been removed
- the assetManager now replaces the user initials with the first in the list if
  Database.getLastUser method returns None, thus no last user record has been
  found
- the baseName and subName fields are now have sorted data
- the Database.getUserInitials now returns a sorted user initials list

v0.7.2
- fixed nuke file path problem under windows, while querying the file name and
  recent file list, nuke was sending the path with wrong path seperator, it is
  now replaced with correct path seperator

v0.7.1
- InputBasedCachedMethod now supports methods with both arguments and keyword
  arguments
- fixed assetManager_UI and projectManager_UI was using __init__ from QDialog
  instead of QMainWindow
- added printing of the info of the operation while saving an asset

v0.7.0
- reorganized the interface of assetManager to have a more optimized look, and
  to reduce the code duplication
- Project and Sequence objects are now conditioned so they can not have numbers
  at the begining of their names
- Updated the projectManager ui so no numbers are allowed at the begining of
  the project and sequence names

v0.6.3
- now baseName and subName fields allow numbers to be used but not at the
  beggining of the string
- in assetManager ui, both the save and open asset tabs are now updated with
  the incomming asset infos from the environment

v0.6.2
- baseName is now capitalized after validation
- fixed _validateRevString and _validateVerString in Asset class
- added assetStatus to save and export methods of the assetManager interface to
  check if the current asset from the fields is a valid asset
- fixed path issues for '/' under windows, it was caused by the settings file
  separating the paths always with '/'

v0.6.1
- fixed __main__ function for the package, now the project manager user
  interface pops up by default
- fixed window title in projectManager ui
- added asset validation check in the assetManager ui before trying to get any
  variable from the asset, to prevent errors
- added removeOutputFolder to structure class
- removed some of the methods from the Sequence object, because they were just
  simple wraps of Structure objects corresponding methods. One can use directly
  the structure object by using Sequence.getStructure and then calling the same
  methods
- added these methods to Structure object
    removeOutputFolder
    removeShotDependentFolder
    removeShotIndependentFolder

v0.6.0
- connected the assetType_comboBox1 index change signal to assetList_widget1's
  update method, and re-enabled assetType_comboBox2's update signal being
  invoked from assetType_comboBox2
- added an input based cache system to the cache module
- added whatIsThis help to the interface elements
- renamed assetIO_mainWindow to assetManager (and the other two files are
  renamed too)
- renamed projectManament_mainWindow to projectManager (and the other two files
  renamed are too)

v0.5.6
- the assetList_widget1 is now listing all the versions of the currently
  selected asset

v0.5.5
- in nuke, if there is no file opened, thus no file name found, the script
  now tries to get the path variables from the recent file list
- to be able to mass process the sequences in the server, these new functions
  has been added:
    addExtensionToIgnoreList
    addNewAssetType
    addNewOutputFolder
    addNewShotDependentFolder
    addNewShotIndependentFolder
    exists
    removeExtensionFromIgnoreList
  because these functions edits the settings of the sequence, to make the
  changes permenant, the Sequence.saveSettings() should be invoked afterwards,
  and for the folder functions, Sequence.createStructure() and a following
  Sequence.saveSettings() should be invoked
- the functions saveSettings and readSettings in Sequence object are now
  public

v0.5.1
- fixed file paths for windows environment in NUKE environment
- fixed initialization of envStatus variables in some functions in the
  assetIO_mainWindow

v0.5.0
- to prevent name clashes all the environment scripts are renamed by adding Env
  to the name of the script ( ex: maya.py -> mayaEnv.py )
- added support to Nuke environment
- listing of non-asset objects or files with unwanted extensions are fixed now

v0.4.2
- fixed the revision check in the interface
- tried to remove Turkish characters from the interface fields but it is not
  working properly for now

v0.4.1
- fixed the wrong widget sizes assetIO UI

v0.4.0
- range tools now works properly with unicode inputs
- maya now always gets the path from the workspace
- fixed getting and setting the user initials in the interface
- fixed getting of the HOME path of the user for Windows
- added the ability to export the selected content as a new asset instead of
  just saving them

v0.3.4
- introduced a lot of speed optimizations, eliminated all the unnecessary asset
  object creations in the interface, but this introduced listing of non-asset
  objects (like smr files) in the interface, this will be fixed in next
  versions
- the interface tries to get all the asset information from the asset file
  names instead of asset objects
- fixed asset retrieval in open tab in the interface, caused by switching from
  a sequence that supports subNames to another which doesn't. The subName field
  was left in 'MAIN' and the code was trying to get asset file names with a
  subName of 'MAIN' in a sequence which doesn't support subName fields.
- getting the latest version or revision for an asset is now much faster
- cleaned the code a little bit

v0.3.3
- introduced some Pythonic optimizations to the code
- added getAllAssetsForType method to the Sequence object
- removed valid asset checks in the getAllAssetsForType method
- added getAllAssetFileNamesForType method to the Sequence object to quickly
  get the asset fils
- to retrieve asset file names very quickly, now all the filtering done over
  string variables, not in Asset objects

v0.3.2
- all str's are converted to unicode

v0.3.1
- added check for unsaved changes in current scene while oppening an asset
- the environment script maya, now tries to fix the path seperator for windows

v0.3.0
- added check for the asset path while saving, it was giving errors for
  non-existing asset paths
- added open functionalities
- fixed wrong fileName creation in Asset objects
- for sequences that doesn't support subName fields, int the Asset object,
  asset file name was not including the notes part of the file name, it is now
  fixed
- asset interface now ask the user permission to overwrite a file, instead of
  canceling the saving process ( it is not allowed though to save over a file )
- updated the render file name in MAYA environment to hold the subName field in
  case the sequence supports it
- added interface for project management (ie. creaeting projects, adding shots
  etc. )

v0.2.0
- now the Database object reads the settings from the databaseSettings.xml
  in the project root
- added half support for multiple servers (full support will be in near future)
- fixed the creation of a sequence from a project object
- removed the project management functionalities to another interface
- renamed the current mainWindow to assetIO_mainWindow
- added the environment variable to the AssetType object
- added the output attribute to the Structure node, and updated the
  defaultSettings.xml. The output attribute will hold the output folder
  poperties for types like render and comp.
- created environment module, that holds a environment specific scripts for
  actions like save, open, import

v0.1.5
- added the ability to save under MAYA environment

v0.1.4
- finished converting the single script to a python package
- converted the window style to Plastique

v0.1.3
- scripts are moved to their own directory to make the system clean
- started to convert the single script to a python package

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
- convert the system to a full featured Production Asset Management System
- add a user login window
- add access control
- add the ability of a user to review an asset
- add asset approval system
- add a publishing system
- add thumbnails to assets
- add a messaging system
- add a resource management system
- switch to a database stored metadata system
- use the user class to define if the user can change the project
- keep track of the project timings, progress of the project, with another
  module
- create appropriate Error classes for errors
- for environments supporting referencing, check the references for new
  versions while opening the asset
- an asset object should contain all the versions, revisions, of the same asset
  , or there should be an superAsset class that holds all the versions,
  revisions and any subNames of the same asset, so the group of the files
  should be counted as one asset with multi versions
- programs should not list the files those they can not open, for example
  houdini shouldn't list ma files, and maya should not list hip files
+ reduce the code duplication in MainDialog
+ try to add another type of caching system, which is input dependent, so for
  the same input it should return the same value without evaluating anything
+ add program names attribute to the assetType objects, so they can be
  listed for specific programs only (e.g. MAYA, NUKE, PHOTOSHOP, HOUDINI etc.)
+ use external settings file in XML format for the database, instead of
  burrying the data to the class
+ separate the project management to another ui
+ save all xml in pretty xml format
+ to get benefit from the caching system in the MainDialog class, add a project
  and sequence attribute and fill them whenever the project and sequence is
  changed to something else
+ add an interface with PyQt4
+ add an Asset class

-------------------------------------------------------------------------------
"""



__version__ = "9.11.9"