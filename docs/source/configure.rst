.. _configuration_toplevel:

.. _configuring_oyProjectManager:

Configuring oyProjectManager
============================

To configure oyProjectManager and make it fit to your studios need you should
use the ``config.py`` file as mentioned in next sections.

config.py File
--------------

oyProjectManager uses the ``config.py`` to let one to customize the system
config.

The ``config.py`` file is searched in a couple of places through the
system:
    
  * under "~/.oypmrc/" directory (not yet)
  * under "$OYPROJECTMANAGER_PATH"

The first path is a folder in the users home dir. The second one is a path
defined by the ``OYPROJECTMANAGER_PATH`` environment variable.

Defining the ``config.py`` by using the environment variable gives the most
customizable and consistent setup through the studio. You can set
``OYPROJECTMANAGER_PATH`` to a shared folder in your fileserver where all
the users can access.

Because, ``config.py`` is a regular Python code which is executed by
oyProjectManager, you can do anything you were doing in a normal Python
script. This is very handy if you have another source of information which
is reachable by a Python script.

In config.py you can:
  
  * Add new users
  * Customize default project structure
  * Customize file naming convention
  * Customize path naming convention
  * Customize the database file name
  * Customize server paths
  * Customize environments (host programs running oyProjectManager)
  * and many more

If there is no ``OYPROJECTMANAGER_PATH`` variable in your current
environment or it is not showing an existing path or there is no
``config.py`` file the system will use the system defaults and it is
probably not going to work as desired.

Config Variables
----------------

Variables which can be set in ``config.py`` are as follows:

.. confval:: asset_thumbnail_filename
   
   A Jinja2 template showing the filename of
   :class:`~oyProjectManager.models.asset.Asset` thumbnails. The default
   value is::
     
     asset_thumbnail_filename = "{{asset.code}}_thumbnail.{{extension}}"

.. confval:: asset_thumbnail_path
   
   A Jinja2 template showing the path of
   :class:`~oyProjectManager.models.asset.Asset` thumbnails. The default
   value is::
   
     asset_thumbnail_path = "{{project.code}}/Assets/{{asset.type}}/{{asset.code}}/Thumbnail"

.. confval:: database_url
   
   The URL of the database the default value is::
   
     "sqlite:///$OYPROJECTMANAGER_PATH/project_manager.db"
  
   in which the database is a SQLite3 file based database and it is placed
   right beside the config path.

.. confval:: default_asset_type_name
   
   The default type name for newly created
   :class:`~oyProjectManager.models.asset.Asset` instances, not used if
   another value is passed with the ``type`` argument. The default value is
   "Generic".

.. confval:: default_fps
   
   The default fps value for newly created
   :class:`~oyProjectManager.models.project.Project` instances, not used if
   another value is supplied with the ``fps`` argument. The default value
   is "25".

.. confval:: default_resolution_preset
   
   The name of the default resolution preset used in newly created
   :class:`~oyProjectManager.models.project.Project` instances. Not used if
   the ``width``, ``height`` and ``aspect_ratio`` arguments are used. The
   default value is "HD 1080", the default value should exists in
   :confval:`resolution_presets` config value.

.. confval:: default_take_name
   
   The default take name value for newly created
   :class:`~oyProjectManager.models.version.Version` instances, not used if
   another value is supplied with the ``take`` argument. The default value
   is "MAIN".

.. confval:: environments
   
   A list of dictionaries holding environments info. Environments are the
   host programs (Maya, Houdini, Nuke etc.) that oyProjectManager is
   running on. This config value holds the name and the native extensions
   of that environment. The default value is::
   
     environments = [
        {
            "name":"Maya",
            "extensions":["ma", "mb"]
        },
        {
            "name":"Houdini",
            "extensions":["hip"]
        },
        {
            "name":"Nuke",
            "extensions": ["nk"],
        },
        {
            "name":"Photoshop",
            "extensions": ["psd", "pdd"],
            "export_extensions": ["tif", "tga", "bmp", "jpg", "iff"],
        },
        {
            "name":"3DEqualizer",
            "extensions": ["3te"]
        },
        {
            "name":"Fusion",
            "extensions": ["comp"]
        }
     ]

.. confval:: file_size_format
   
   The string formatting used in version file size info columns in UI. The
   default value is::
   
     file_size_format = '%.2f MB'

.. confval:: project_structure
   
   The default project structure template for newly created
   :class:`~oyProjectManager.models.project.Project` instances. It is a
   Jinja2 template where every line is a definition of a folder in the
   project structure. The default value is::
     
     project_structure = '''{% for sequence in project.sequences %}
         {% set seq_path = project.full_path + '/Sequences/' + sequence.code %}
         {{seq_path}}/Edit/Offline
         {{seq_path}}/Edit/Sound
         {{seq_path}}/References/Artworks
         {{seq_path}}/References/Text/Scenario
         {{seq_path}}/References/Photos_Images
         {{seq_path}}/References/Videos
         {{seq_path}}/References/Others
         {% for shot in sequence.shots %}
             {{seq_path}}/Shots/{{shot.code}}
             {{seq_path}}/Shots/{{shot.code}}/Plate
             {{seq_path}}/Shots/{{shot.code}}/Ref
             {{seq_path}}/Shots/{{shot.code}}/Texture
         {% endfor %}
     {% endfor %}
     '''
   
   oyProjectManager will supply the ``project`` variable to the Jinja2
   template engine.

.. confval:: repository_env_key
   
   The name of the environment variable showing the repository path. The
   default value is "REPO". If you change this, you should also update the
   environment variables of all the computers using oyProjectManager with
   that value.

.. confval:: resolution_presets
   
   A dictionary holding resolution presets. This info is used while
   creating :class:`~oyProjectManager.models.project.Project` instances. The
   default value is::
   
      resolution_presets = {
        "PC Video": [640, 480, 1.0],
        "NTSC": [720, 486, 0.91],
        "NTSC 16:9": [720, 486, 1.21],
        "PAL": [720, 576, 1.067],
        "PAL 16:9": [720, 576, 1.46],
        "HD 720": [1280, 720, 1.0],
        "HD 1080": [1920, 1080, 1.0],
        "1K Super 35": [1024, 778, 1.0],
        "2K Super 35": [2048, 1556, 1.0],
        "4K Super 35": [4096, 3112, 1.0],
        "A4 Portrait": [2480, 3508, 1.0],
        "A4 Landscape": [3508, 2480, 1.0],
        "A3 Portrait": [3508, 4960, 1.0],
        "A3 Landscape": [4960, 3508, 1.0],
        "A2 Portrait": [4960, 7016, 1.0],
        "A2 Landscape": [7016, 4960, 1.0],
        "50x70cm Poster Portrait": [5905, 8268, 1.0],
        "50x70cm Poster Landscape": [8268, 5905, 1.0],
        "70x100cm Poster Portrait": [8268, 11810, 1.0],
        "70x100cm Poster Landscape": [11810, 8268, 1.0],
        "1k Square": [1024, 1024, 1.0],
        "2k Square": [2048, 2048, 1.0],
        "3k Square": [3072, 3072, 1.0],
        "4k Square": [4096, 4096, 1.0],
      }

.. confval:: rev_number_padding
   
   The amount of padding applied to the
   :attr:`~oyProjectManager.models.version.Version.revision_number` attribute
   of :class:`~oyProjectManager.models.version.Version` class while generating
   filename of that Version instance. In default filename and path
   templates the revision_number attribute is not used. The default value
   is "2".

.. confval:: rev_number_prefix
   
   The prefix of
   :attr:`~oyProjectManager.models.version.Version.revision_number` attribute
   of :class:`~oyProjectManager.models.version.Version` class while generating
   filename of that Version instance. In default filename and path
   templates the revision_number attribute is not used. The default value
   is "r".

.. confval:: shot_number_padding
   
   The amount of padding applied to the
   :class:`~oyProjectManager.models.shot.Shot` number while generating the
   Shot code, the default value is 3 and for non standard shot numbers
   (like "46AB-4-B") use 0 or 1 to prevent your shot number padded with
   zeros::
     
     conf.shot_number_prefix = "SH"
     conf.shot_number_padding = 3
     shot1 = Shot(seq1, 1)
     # will result
     # shot1.code = "SH001"
     
     conf.shot_number_padding = 5
     shot2 = Shot(seq1, 2)
     # will result
     # shot2.code = "SH00002"

.. confval:: shot_number_prefix
   
   The prefix for :class:`~oyProjectManager.models.shot.Shot` numbers. The
   default value is "SH". So with the default configuration a Shot with
   number 1 will have a code of "SH001"

.. confval:: shot_thumbnail_filename
   
   A Jinja2 template showing the filename of
   :class:`~oyProjectManager.models.shot.Shot` thumbnails. The default
   value is::
     
     shot_thumbnail_filename = "{{shot.code}}_thumbnail.{{extension}}"

.. confval:: shot_thumbnail_path
   
   A Jinja2 template showing the path of
   :class:`~oyProjectManager.models.shot.Shot` thumbnails. The default 
   value is::
     
     shot_thumbnail_path = "{{project.code}}/Sequences/{{sequence.code}}/Shots/{{shot.code}}/Thumbnail"

.. confval:: status_bg_colors
   
   A python list of tuple showing the background color of each statuses,
   it should correlate with the :confval:`status_list` config value, the
   default is::
     
     status_bg_colors = [
        (192,  80,  77), #WTS
        (255, 192,   0), #WIP
        ( 89, 141, 213), #REV
        (155, 187,  89), #APP
        (155, 187,  89), #CMP
     ]

.. confval:: status_fg_colors
   
   A python list of tuple showing the foreground (font) color of each
   statuses, it should correlate with the :confval:`status_list` config
   value, the default is::
     
     status_fg_colors = [
        (255, 255, 255), #WTS
        (  0,   0,   0), #WIP
        (  0,   0,   0), #REV
        (  0,   0,   0), #APP
        (  0,   0,   0), #CMP
     ]

.. confval:: status_list
   
   A python list containing the short names of the status values, the
   default is::
     
     status_list = [
        'WTS',
        'WIP',
        'REV',
        'APP',
        'CMP'
     ]

.. confval:: status_list_long_names
   
   A python list containing the long names of the status values, it should
   correlate with the :confval:`status_list` config value, the default is::
     
     status_list_long_names = [
        'Waiting To Start',
        'Work In Progress',
        'For Review',
        'Approved',
        'Completed'
     ]

.. confval:: thumbnail_format
   
   The default thumbnail format for Asset and Shot thumbnails. The default
   value is "jpg".

.. confval:: thumbnail_quality
   
   An integer value for the image compression quality between 0-100 for
   Asset and Shot thumbnails. Lower values will create small file sizes
   while higher values will create higher quality images. The default value
   is 70.

.. confval:: thumbnail_size
   
   A list with length of 2 where the first elements represents the default
   width and the second represents the default height of the thumbnails of
   Assets and Shots. The default value is::
     
     thumbnail_size = [320, 180]

.. confval:: time_format
   
   The string formatting used in version file date info columns in UI. The
   default value is::
     
     time_format = '%d.%m.%Y %H:%M'

.. confval:: ver_number_padding
   
   The amount of padding applied to the
   :attr:`~oyProjectManager.models.version.Version.version_number` attribute
   of :class:`~oyProjectManager.models.version.Version` class while generating
   filename of that Version instance. In default filename and path
   templates the ver_number_padding value is not used. The default value is
   "3".

.. confval:: ver_number_prefix
   
   The prefix of
   :attr:`~oyProjectManager.models.version.Version.version_number` attribute
   of :class:`~oyProjectManager.models.version.Version` class while generating
   filename of that Version instance. In default filename and path
   templates the ver_number_prefix value is not used. The default value is
   "v".

.. confval:: version_types
   
   A list of dictionaries holding all the available
   :class:`~oyProjectManager.models.version.VersionType` info in the system.
   Again oyProjectManager will create
   :class:`~oyProjectManager.models.version.VersionType` instances upon
   database initialization. But it will not update the values for
   VersionType instances already in the database. So this value is only
   used when creating VersionType instances for the first time. You should
   update the values in the database if you need to make changes to any
   VersionType instances. The default value is::
   
     version_types = [
         {
             "name": "Animation",
             "code": "Anim",
             "path": "{{project.code}}/Sequences/{{sequence.code}}/Shots/{{version.base_name}}/{{type.code}}",
             "filename": "{{version.base_name}}_{{version.take_name}}_{{type.code}}_v{{'%03d'|format(version.version_number)}}_{{version.created_by.initials}}{{version.extension}}",
             "output_path": "{{version._path}}/Output/{{version.take_name}}",
             "extra_folders": "",
             "environments": ["Maya", "Houdini"],
             "type_for": "Shot"
         },
         {
             "name": "Camera",
             "code": "Cam",
             "path": "{{project.code}}/Sequences/{{sequence.code}}/Shots/{{version.base_name}}/{{type.code}}",
             "filename": "{{version.base_name}}_{{version.take_name}}_{{type.code}}_v{{'%03d'|format(version.version_number)}}_{{version.created_by.initials}}{{version.extension}}",
             "output_path": "{{version._path}}/Output/{{version.take_name}}",
             "extra_folders": "",
             "environments": ["Maya", "Houdini"],
             "type_for": "Shot"
         },
         {
             "name": "Composition",
             "code": "Comp",
             "path": "{{project.code}}/Sequences/{{sequence.code}}/Shots/{{version.base_name}}/{{type.code}}",
             "filename": "{{version.base_name}}_{{version.take_name}}_{{type.code}}_v{{'%03d'|format(version.version_number)}}_{{version.created_by.initials}}{{version.extension}}",
             "output_path": "{{version._path}}/Output/{{version.take_name}}",
             "extra_folders": "",
             "environments": ["Nuke", "Fusion"],
             "type_for": "Shot"
         },
         {
             "name":"FX",
             "code": "FX",
             "path": "{{project.code}}/Sequences/{{sequence.code}}/Shots/{{version.base_name}}/{{type.code}}",
             "filename": "{{version.base_name}}_{{version.take_name}}_{{type.code}}_v{{'%03d'|format(version.version_number)}}_{{version.created_by.initials}}{{version.extension}}",
             "output_path": "{{version._path}}/Output/{{version.take_name}}",
             "extra_folders": '''{{version.path}}/anim
                     {{version.path}}/cache
                     {{version.path}}/exports''',
             "environments": ["Maya", "Houdini"],
             "type_for": "Shot"
         },
         {
             "name":"Model",
             "code": "Model",
             "path": "{{project.code}}/Assets/{{asset.type}}/{{version.base_name}}/{{type.code}}",
             "filename": "{{version.base_name}}_{{version.take_name}}_{{type.code}}_v{{'%03d'|format(version.version_number)}}_{{version.created_by.initials}}{{version.extension}}",
             "output_path": "{{version._path}}/Output/{{version.take_name}}",
             "extra_folders": "",
             "environments": ["Maya", "Houdini"],
             "type_for": "Asset"
         },
         {
             "name": "Other",
             "code": "Other",
             "path": "{{project.code}}/Assets/{{asset.type}}/{{version.base_name}}/{{type.code}}",
             "filename": "{{version.base_name}}_{{version.take_name}}_{{type.code}}_v{{'%03d'|format(version.version_number)}}_{{version.created_by.initials}}{{version.extension}}",
             "output_path": "{{version._path}}/Output/{{version.take_name}}",
             "extra_folders": "",
             "environments": ["Maya", "Houdini", "Nuke", "Fusion", "Photoshop"],
             "type_for": "Asset"
         },
         {
             "name": "Previs",
             "code": "Previs",
             "path": "{{project.code}}/Sequences/{{sequence.code}}/Shots/{{version.base_name}}/{{type.code}}",
             "filename": "{{version.base_name}}_{{version.take_name}}_{{type.code}}_v{{'%03d'|format(version.version_number)}}_{{version.created_by.initials}}{{version.extension}}",
             "output_path": "{{version._path}}/Output/{{version.take_name}}",
             "extra_folders": "",
             "environments": ["Maya", "Houdini"],
             "type_for": "Shot"
         },
         {
             "name": "Lighting",
             "code": "Lighting",
             "path": "{{project.code}}/Sequences/{{sequence.code}}/Shots/{{version.base_name}}/{{type.code}}",
             "filename": "{{version.base_name}}_{{version.take_name}}_{{type.code}}_v{{'%03d'|format(version.version_number)}}_{{version.created_by.initials}}{{version.extension}}",
             "output_path": "{{version._path}}/Output/{{version.take_name}}",
             "extra_folders": "",
             "environments": ["Maya", "Houdini"],
             "type_for": "Shot"
         },
         {
             "name": "Rig",
             "code": "Rig",
             "path": "{{project.code}}/Assets/{{asset.type}}/{{version.base_name}}/{{type.code}}",
             "filename": "{{version.base_name}}_{{version.take_name}}_{{type.code}}_v{{'%03d'|format(version.version_number)}}_{{version.created_by.initials}}{{version.extension}}",
             "output_path": "{{version._path}}/Output/{{version.take_name}}",
             "extra_folders": "",
             "environments": ["Maya", "Houdini"],
             "type_for": "Asset"
         },
         {
             "name": "Roto",
             "code": "Roto",
             "path": "{{project.code}}/Sequences/{{sequence.code}}/Shots/{{version.base_name}}/{{type.code}}",
             "filename": "{{version.base_name}}_{{version.take_name}}_{{type.code}}_v{{'%03d'|format(version.version_number)}}_{{version.created_by.initials}}{{version.extension}}",
             "output_path": "{{version._path}}/Output/{{version.take_name}}",
             "extra_folders": "",
             "environments": ["Nuke", "Fusion"],
             "type_for": "Shot"
         },
         {
             "name": "Scene Assembly",
             "code": "SceneAss",
             "path":"{{project.code}}/Sequences/{{sequence.code}}/Shots/{{version.base_name}}/{{type.code}}",
             "filename": "{{version.base_name}}_{{version.take_name}}_{{type.code}}_v{{'%03d'|format(version.version_number)}}_{{version.created_by.initials}}{{version.extension}}",
             "output_path": "{{version._path}}/Output/{{version.take_name}}",
             "extra_folders": "",
             "environments": ["Maya", "Houdini"],
             "type_for": "Shot"
         },
         {
             "name": "Matte",
             "code": "Matte",
             "path": "{{project.code}}/Sequences/{{sequence.code}}/Shots/{{version.base_name}}/{{type.code}}",
             "filename": "{{version.base_name}}_{{version.take_name}}_{{type.code}}_v{{'%03d'|format(version.version_number)}}_{{version.created_by.initials}}{{version.extension}}",
             "output_path": "{{version._path}}/Output/{{version.take_name}}",
             "extra_folders": "",
             "environments": ["Photoshop"],
             "type_for": "Shot"
         },
         {
             "name": "Texture",
             "code": "Texture",
             "path": "{{project.code}}/Assets/{{asset.type}}/{{version.base_name}}/{{type.code}}",
             "filename": "{{version.base_name}}_{{version.take_name}}_{{type.code}}_v{{'%03d'|format(version.version_number)}}_{{version.created_by.initials}}{{version.extension}}",
             "output_path": "{{version._path}}/Output/{{version.take_name}}",
             "extra_folders": "",
             "environments": ["Photoshop", "Nuke", "Fusion"],
             "type_for": "Asset",
         },
         {
             "name": "Illustration",
             "code": "Illust",
             "path": "{{project.code}}/Assets/{{asset.type}}/{{version.base_name}}/{{type.code}}",
             "filename": "{{version.base_name}}_{{version.take_name}}_{{type.code}}_v{{'%03d'|format(version.version_number)}}_{{version.created_by.initials}}{{version.extension}}",
             "output_path": "{{version._path}}/Output/{{version.take_name}}",
             "extra_folders": "",
             "environments": ["Photoshop"],
             "type_for": "Asset"
         },
         {
             "name": "Look Development",
             "code": "LookDev",
             "path": "{{project.code}}/Assets/{{asset.type}}/{{version.base_name}}/{{type.code}}",
             "filename": "{{version.base_name}}_{{version.take_name}}_{{type.code}}_v{{'%03d'|format(version.version_number)}}_{{version.created_by.initials}}{{version.extension}}",
             "output_path": "{{version._path}}/Output/{{version.take_name}}",
             "extra_folders": "",
             "environments": ["Maya", "Houdini"],
             "type_for": "Asset"
         },
         {
             "name": "Match Move",
             "code": "MM",
             "path": "{{project.code}}/Sequences/{{sequence.code}}/Shots/{{version.base_name}}/{{type.code}}",
             "filename": "{{version.base_name}}_{{version.take_name}}_{{type.code}}_v{{'%03d'|format(version.version_number)}}_{{version.created_by.initials}}{{version.extension}}",
             "output_path": "{{version._path}}/Output/{{version.take_name}}",
             "extra_folders": "",
             "environments": ["3DEqualizer"],
             "type_for": "Shot"
         }
     ] 

.. confval:: users_data
   
   A list of dictionaries which is holding user info. It gives a place to
   enter user info, so the studio can add new users by adding their names
   to the ``config.py`` file. oyProjectManager will create a corresponding
   :class:`~oyProjectManager.models.auth.User` objects in the database upon
   every initialization of the database session. And deleting a user from
   this list will not delete the user from the database. The default value
   is::
     
     users_data = [
        {
            'name': 'Administrator',
            'initials': 'adm',
        },
     ]
   
   The format of the dictionary should be::
     
     users_data = [
        {
            'name': 'The User Name',
            'initials': 'tun', # Initials of the user name
            'email': the@user.email'
        },
     ]
