# -*- coding: utf-8 -*-
"""
oyProjectManager by Erkan Ozgur Yilmaz (c) 2009-2010

Description :
-------------
The oyProjectManager is created to manage our animation studios own projects,
within a predefined project structure. It is also a simple asset management
system. The main purpose of this system is to create projects, sequences and
to allow users to save their files in correct folders with correct names. So
anyone can find their files later on by using this system. But again it is not
a complete Project Asset Management System.

This system uses a repository, and extracts the information from the folder and
file names. And because it uses a consistent structure while creating both the
projects, sequences and assets, it works very fine for small groups of artists.

Another aim of this code is to prevent the user to use the OSes own file
manager (ie. Windows Explorer on Windows ) to define the name and placement of
the asset file. In normal circumstances the user is not allowed to defien the
file name.

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
           (this folder can be queried by using a repository object), and every
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
               assets it is user dependent. It always starts with capital
               letter, numbers are not allowed in the begginging

SubName      : For assets that doesn't have a subName it is MAIN, for other
               assets it is user dependent. The main purpose of SubName field
               is to distinguish asset parts that merges in to a much bigger
               asset. The best example is the Animation type: every character
               in a shot ( SH001 for example ) saved with different SubNames
               but same BaseName ( the shot name ). For example:
               
               SH001_Kopil_ANIMATION_r00_v100_hg.ma
               SH001_Muslum_ANIMATION_r00_v045_ec.ma
               SH001_Selin_ANIMATION_r00_v076_kk.ma
               
               all of these can be combined to gather in:
               SH001_MAIN_ANIMATION_r00_v001_oy.ma
               
               so all of them kept under the same folder ( _ANIMATIONS_/SH001 )
               because they are the sub assets of the main animation asset of
               shot 1...

TypeName     : The asset types are defined in the sequence settings, and the
               typeName takes its string representation from that settings
               file. There is no default value, it can completely be changed
               from project to project, examples to asset type names are MODEL,
               ANIMATION, RENDER, PREVIS etc.
               
               Basically the asset type defines two things:
               * the place it needs to be saved under
               * desides whether to show the asset to the current environment
                 ( the application itself, MAYA, NUKE, HOUDINI etc. ) or not
               
               The second feature exists to prevent the applications to try to
               open wrong types of assets ( MAYA opening NUKE files or vice
               versa )
               
               For more information about asset types look to the documentation
               of Sequence class

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



When an assets is saved, it is placed under:

{projectsPath}/{projectName}/{sequenceName}/{typeFolder}/{baseName}/
{assetFileName}.{extension}

So, by following that format one can easily find all the asset file under the
given project path.


Command Line Options :
----------------------

The system can be used under shell ( command line in Windows ) with this flags,
without runnning the python interpreter exclusively.

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

-------------------------------------------------------------------------------
"""



__version__ = "10.7.17"
