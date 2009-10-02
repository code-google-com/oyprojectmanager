"""
oyProjectManager.py by Erkan Ozgur Yilmaz (c) 2009

v0.1.4

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
v0.1.5
- added the ability to save under MAYA environment

v0.1.4
- finished converting the single script to a python package
- converted the window style to Plastique

v0.1.3
- added external settings file for the database
- scripts are moved to their own directory to make the system clean
- converted the single script to a python package

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



__version__ = "0.1.4"



import sys, getopt
from ui import mainWindow



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
        return mainWindow.UI(environment, fileName, path)





if __name__ == "__main__":
    main()


