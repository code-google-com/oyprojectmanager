# -*- coding: utf-8 -*-
from exceptions import IndexError, ValueError, OSError, AttributeError, IOError

import os
import time
import platform
import shutil
import glob
import re
from twisted.python.filepath import FilePath
import jinja2
from beaker import cache

from xml.dom import minidom
from sqlalchemy import func, orm, Column, String, Integer, PickleType, ForeignKey
from sqlalchemy.ext.declarative import synonym_for
from sqlalchemy.orm import relationship, synonym
from sqlalchemy.orm.mapper import validates
from sqlalchemy.schema import UniqueConstraint

from oyProjectManager import db
from oyProjectManager.db.declarative import Base
from oyProjectManager import utils, conf


# create a cache with the CacheManager
bCache = cache.CacheManager()

# disable beaker DEBUG messages
import logging

logger = logging.getLogger('beaker.container')
logger.setLevel(logging.WARNING)

# create a logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class Repository(object):
    """Repository class gives information about the servers, projects, users
    etc.
    
    The Repository class helps:
    
     * Get a list of projects in the current repository
     * Parse several settings like:
     
        * environmentSettings.xml
        * repositorySettings.xml
        * users.xml
    
     * Get the last logged in user
     * Find server paths
     * and some auxiliary things like:
    
        * convert the given path to repository relative path which contains
          the environment variable key in the repository path.
    
    **Settings File**
    
    oyProjectManager uses the ``OYPROJECTMANAGER_PATH`` environment variable to
    track the settings, if there is no ``OYPROJECTMANAGER_PATH`` variable in
    your current environment the system will not work.
    
    You can set ``OYPROJECTMANAGER_PATH`` to a shared folder in your fileserver
    where all the users can access.
    
    oyProjectManager will look for these files in the
    ``OYPROJECTMANAGER_PATH``:
    
       * defaultProjectSettings.xml
      
       * environmentSettings.xml
      
       * repositorySettings.xml
      
       * users.xml
    
    You can just duplicate the XML files under the settings folder of the
    package root to your own ``OYPROJECTMANAGER_PATH``.
    
    These are the xml files that the oyProjectManager searches for:
    
     * defaultProjectSettings.xml: see
       :class:`~oyProjectManager.core.models.DefaultSettingsParser` for
       details.
       
     * environmentSettings.xml:
       
       Shows the general environment settings. An environment in
       oyProjectManager terminology is a host application like Maya, Houdini,
       Nuke or Photoshop.
       
       Structure of the XML file:
       
          * environments: this node holds the environment objects and doesn't
            have any attribute
            
            children:
            
               * environment: this is a specific environment and has these
                 
                 attributes:
                 
                    * name: the name of the environment. It should be all upper
                      case
                   
                    * extensions: the list of native file format extensions for
                      the environment. For example, for Maya it should be
                      "ma,mb", for Nuke it should be "nk", for Houdini it
                      should be "hip" etc.
    
     * repositorySettings.xml: holds the fileserver and general unit
       information
       
       structure:
       
          * settings:
            
            children:
            
               * server: defines a file server, so you can use multiple servers in
                 your studio and oyProjectManager will be able to manage the
                 projects in different servers. (omitted for now)
                 
                 attributes:
                   
                    * name: the name of the server
                   
                    * server_path: the path of the project folder in this server
                   
                    * projectFoldersName: the project folder name in this
                      server
            
          * units: holds the default units for the system
            
            children:
            
               * time_units:
                 
                 children:
                 
                    * time:
                      
                      attributes:
                      
                         * name: the name of the unit
                        
                         * fps: the corresponding FPS value for this unit
              
               * linearUnits:
                 
                 children:
                 
                    * linear:
                      
                      attributes:
                       
                         * name: the name of the unit, like centimeters
                         
                         * short: the short name of the unit, like cm for
                           centimeters
                    
               * angularUnits:
                 
                 children:
                 
                  * angle:
                    
                    attributes:
                    
                       * name: the name of the unit
                      
                       * short: the short name of the unit
       
        * defaultFiles: this shows the 
          
          children:
          
             * file:
               
               attributes:
               
                  * name: the name of the file with the extension
                 
                  * projectRelativePath: the project relative path of the file
    
     * users.xml: this file holds the user data
       
       nodes:
       
          * users: holds user nodes
            
            children:
            
               * user: a user node
                 
                 attributes:
                 
                    * initials: the initials of the users
                    * name: the full name of the user
    """
    
    
    
    
    def __init__(self):
        
        # initialize default variables
        self.repository_path_env_key = "REPO"
        self.settings_path_env_key = "OYPROJECTMANAGER_PATH"
        
        self._init_repository_path_environment_variable()
        
        # ---------------------------------------------------
        # READ REPOSITORY SETTINGS
        # ---------------------------------------------------
        
        self._settings_dir_path = None
        
        # fill the data
        self._settings_dir_path = self.settings_dir_path
        
        # Repository Settings File (repositorySettings.xml)
        self._repository_settings_file_name = 'repositorySettings.xml'
        self._repository_settings_file_path = self.settings_dir_path
        
        self._repository_settings_file_full_path = os.path.join(
            self._repository_settings_file_path,
            self._repository_settings_file_name
        )
        # ---------------------------------------------------
        
        
        
        # ---------------------------------------------------
        # READ DEFAULT SETTINGS
        # ---------------------------------------------------
        self._default_project_settings_file_name = 'defaultProjectSettings.xml'
        self._default_project_settings_file_path = self.settings_dir_path
        
        self._default_settings_file_full_path = os.path.join(
            self._default_project_settings_file_path,
            self._default_project_settings_file_name
        )
        
        # Default Files Folder Path (_defaultFiles_)
        self._default_files_folder_full_path = os.path.join(
            self.settings_dir_path, '_defaultFiles_'
        )
        # ---------------------------------------------------
        
        
        # ---------------------------------------------------
        # JOBs folder settings ( M:/, JOBs )
        # ---------------------------------------------------
        self._server_path = ""
        self._windows_path = ""
        self._osx_path = ""
        self._linux_path = ""
        # ---------------------------------------------------
        
        
        # ---------------------------------------------------
        # Last User File
        # ---------------------------------------------------
        self._last_user_file_name = '.last_user'
        self._last_user_file_path = self.home_path
        self._last_user_file_full_path = os.path.join(
            self._last_user_file_path, self._last_user_file_name
        )
        # ---------------------------------------------------
        
        
        
        # ---------------------------------------------------
        # Users Settings File
        # ---------------------------------------------------
        self._users_file_name = 'users.xml'
        self._users_file_path = self.settings_dir_path
        self._users_file_full_path = os.path.join(
            self._users_file_path, self._users_file_name
        )
        self._users = [] * 0
        
        self._projects = [] * 0
        self._default_files_list = [] * 0
        # ---------------------------------------------------
        
        
        
        
        # ---------------------------------------------------
        # UNITS
        # ---------------------------------------------------
        # 
        # Only time units are implemented for now,
        # the rest will be added when they are first needed
        # 
        self._time_units = {}
        
        # ---------------------------------------------------
        self._parse_repository_settings()
        self._parse_users()
        # ---------------------------------------------------
    
    
    def _init_repository_path_environment_variable(self):
        """initializes the environment variables
        """
        
        # create the environment variable if there is no defined yet
        if not os.environ.has_key(self.repository_path_env_key):
            os.environ[self.repository_path_env_key] = ""
    
    
    
    
    def _parse_repository_settings(self):
        """Parses the repository_settings.xml file.
        """
        
        # open the repository settings file
        xmlFile = minidom.parse(self._repository_settings_file_full_path)
        
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
            fps = int(timeNode.getAttribute('fps'))
            self._time_units[name] = fps
        
        # -----------------------------------------------------
        # read the server settings
        # for now just assume one server
        
        try:
            self.windows_path = serverNodes[0].getAttribute('windows_path')
            self.windows_path.replace("/", "\\")
        except AttributeError:
            pass
        
        try:
            self.linux_path = serverNodes[0].getAttribute('linux_path')
        except AttributeError:
            pass
        
        try:
            self.osx_path = serverNodes[0].getAttribute('osx_path')
        except AttributeError:
            pass
        
        # force setting the environment
        self.server_path = self.server_path
        
        # read and create the default files list
        for fileNode in defaultFilesNode.getElementsByTagName('file'):
            #assert(isinstance(fileNode, minidom.Element))
            self._default_files_list.append(
                (
                    fileNode.getAttribute('name'),
                    fileNode.getAttribute('projectRelativePath'),
                    self._default_files_folder_full_path
                )
            )
    
    
    
    
    @property
    def projects(self):
        """returns projects names as a list
        """
        self.update_project_list()
        return self._projects
    
    
    
    
    @property
    @bCache.cache()
    def valid_projects(self):
        """returns the projectNames only if they are valid projects.
        A project is only valid if there are some valid sequences under it
        """
        
        # get all projects and filter them
        self.update_project_list()
        
        validProjectList = [] * 0
        
        for projName in self._projects:
            
            # get sequences of that project
            projObj = Project(projName)
            
            seqList = projObj.sequences()
            
            for seq in seqList:
                #assert(isinstance(seq, Sequence))
                if seq.isValid():
                    # it has at least one valid sequence
                    validProjectList.append(projName)
                    break
        
        return validProjectList
    
    
    
    
    @property
    def users(self):
        """returns users as a list of User objects
        """
        return self._users
    
    
    
    
    @property
    def user_names(self):
        """returns the user names
        """
        return [userObj.name for userObj in self._users]
    
    
    
    
    @property
    def user_initials(self):
        """returns the user initials
        """
        return sorted([userObj.initials for userObj in self._users])
    
    
    
    
    def _parse_users(self):
        """parses the usersFile
        """
        
        # check if the usersFile exists
        if not os.path.exists(self._users_file_full_path):
            raise OSError("There is no users.xml file")
        
        usersXML = minidom.parse(self._users_file_full_path)
        
        rootNode = usersXML.childNodes[0]
        
        # -----------------------------------------------------
        # get the users node
        userNodes = rootNode.getElementsByTagName('user')
        
        self._users = [] * 0
        
        for node in userNodes:
            name = node.getAttribute('name')
            initials = node.getAttribute('initials')
            self._users.append(User(name, initials))
    
    
    
    
    def update_project_list(self):
        """updates the project list variable
        """
        try:
            self._projects = []
            child_folders = utils.getChildFolders(self.server_path)
            
            for folder in child_folders:
                filtered_folder_name = re.sub(
                    r".*?(^[^A-Z_]+)([A-Z0-9_]+)",
                    r"\2", folder
                )
                
                if filtered_folder_name == folder:
                    self._projects.append(folder)
            
            self._projects.sort()
        
        except IOError:
            logger.warning("server path doesn't exists, %s" % self.server_path)
    
    
    
    @property
    def server_path(self):
        """The server path
        """
        
        platform_system = platform.system()
        python_version = platform.python_version()
        
        windows_string = "Windows"
        linux_string = "Linux"
        osx_string = "Darwin"
        
        if python_version.startswith("2.5"):
            windows_string = "Microsoft"

        if platform_system == linux_string:
            return self.linux_path
        elif platform_system == windows_string:
            #self.windows_path.replace("/", "\\")
            return self.windows_path
        elif platform_system == osx_string:
            return self.osx_path
    
    @server_path.setter
    def server_path(self, server_path_in):
        """setter for the server_path
        
        :param server_path_in: a string showing the server path
        """
        
        # add a trailing separator
        # in any cases os.path.join adds a trailing separator

        server_path_in = os.path.expanduser(
            os.path.expandvars(
                server_path_in
            )
        )
        
        platform_system = platform.system()

        python_version = platform.python_version()
        
        windows_string = "Windows"
        linux_string = "Linux"
        osx_string = "Darwin"
        
        if platform_system == linux_string:
            self.linux_path = server_path_in
        elif platform_system == windows_string:
            server_path_in = server_path_in.replace("/", "\\")
            self.windows_path = server_path_in
        elif platform_system == osx_string:
            self.osx_path = server_path_in
        
        # set also the environment variables
        os.environ[self.repository_path_env_key] = str(server_path_in)
        
        self._projects = [] * 0
        
        self.update_project_list()
    
    @property
    def linux_path(self):
        return self._linux_path
    
    @linux_path.setter
    def linux_path(self, linux_path_in):
        """The linux path of the jobs server
        """
        self._linux_path = linux_path_in
    
    @property
    def windows_path(self):
        """The windows path of the jobs server
        """
        return self._windows_path
    
    @windows_path.setter
    def windows_path(self, windows_path_in):
        self._windows_path = windows_path_in
    
    @property
    def osx_path(self):
        """The osx path of the jobs server
        """
        return self._osx_path
        
    @osx_path.setter
    def osx_path(self, osx_path_in):
        self._osx_path = osx_path_in
    
    def createProject(self, projectName):
        """Creates a new project on the server with the given project name.
        
        :returns: The newly created project.
        
        :rType: :class:`~oyProjectManager.core.models.Project`
        """
        
        newProject = Project(projectName)
        newProject.create()
        return newProject
    
    
    
    
    @property
    def defaultFiles(self):
        """returns the default files list as list of tuple, the first element
        contains the file name, the second the project relative path, the third
        the source path
        
        this is the list that contains files those need to be copied to every
        project like workspace.mel for Maya
        """
        
        return self._default_files_list
    
    
    
    
    @property
    def default_settings_file_full_path(self):
        """returns the default settings file full path
        """
        
        return self._default_settings_file_full_path
    
    
    
    
    @property
    def home_path(self):
        """returns the home_path environment variable
        it is :
        /home/userName/ for linux
        C:\Documents and Settings\userName\My Documents for Windows
        C:/Users/userName/Documents for Windows 7 (be careful about the slashes)
        """
        
        home_path_as_str = os.path.expanduser("~")
        
        #if os.name == 'nt':
            #home_path_as_str = home_path_as_str.replace('/','\\')
        
        return home_path_as_str
    
    
    
    @property
    def last_user(self):
        """returns and saves the last user initials if the last_user_file file
        exists otherwise returns None
        """
        last_user_initials = None
        
        try:
            last_user_file = open( self._last_user_file_full_path )
        except IOError:
            pass
        else:
            last_user_initials = last_user_file.readline().strip()
            last_user_file.close()
        
        return last_user_initials
    
    @last_user.setter
    def last_user(self, userInitials):
        try:
            last_user_file = open(self._last_user_file_full_path, 'w')
        except IOError:
            pass
        else:
            last_user_file.write(userInitials)
            last_user_file.close()
    
    
    def get_project_and_sequence_name_from_file_path(self, filePath):
        """Returns the project name and sequence name from the path or fullPath.
        
        Calculates the project and sequence names from the given file or folder
        full path. Returns a tuple containing the project and sequence names.
        In case no suitable project or sequence can be retrieved it returns
        (None, None).
        
        :param str filePath: The file or folder path.
        
        :returns: Returns a tuple containing the project and sequence names.
        
        :rtype: (str, str)
        """
        
        #assert(isinstance(filePath, (str, unicode)))
        
        if filePath is None:
            return None, None
        
        filePath = os.path.expandvars(
                       os.path.expanduser(
                           os.path.normpath(filePath)
                       )
                   ).replace("\\", "/")
        
        #if not filePath.startswith(self._projectsFolderFullPath):
        if not filePath.startswith(self.server_path.replace("\\", "/")):
            return None, None
        
        #residual = filePath[ len(self._projectsFolderFullPath)+1 : ]
        residual = filePath[len(self.server_path.replace("\\", "/"))+1:]
        
        parts = residual.split("/")
        
        if len(parts) > 1:
            return parts[0], parts[1]
        
        return None, None
    
    
    
    @property
    def settings_dir_path(self):
        """Returns the settings dir path.
        """
        
        if self._settings_dir_path is None:
            self._settings_dir_path = os.path.expandvars(
                os.path.expanduser(
                    os.environ[self.settings_path_env_key]
                )
            )
            
        return self._settings_dir_path
    
    
    
    @property
    def time_units(self):
        """returns time_units as a dictionary
        """
        return self._time_units
    
    
    
    
    
    def relative_path(self, path):
        """Converts the given path to repository relative path.
        
        If "M:/JOBs/EXPER/_PROJECT_SETUP_" is given it will return
        "$REPO/EXPER/_PROJECT_SETUP_"
        
        The environment key name is read from the self.repository_path_env_key
        variable
        """
        
        return path.replace(self.server_path,
                            "$" + self.repository_path_env_key)

class Project(Base):
    """Manages project related data.
    
    A Project is simply a holder of Sequences.
    
    .. versionadded:: 0.2.0
        SQLite3 Database:
        
        To hold the information about all the data created, there is a
        ".metadata.db" file in the project root. This SQLite3 database has
        information about all the
        :class:`~oyProjectManager.core.models.Sequence`\ s,
        :class:`~oyProjectManager.core.models.Shot`\ s,
        :class:`~oyProjectManager.core.models.Asset`\ s and
        :class:`~oyProjectManager.core.models.VersionType` created within
        the Project. So anytime a new
        :class:`~oyProjectManager.core.models.Sequence`\ s,
        :class:`~oyProjectManager.core.models.Shot`\ s,
        :class:`~oyProjectManager.core.models.Asset`\ s or
        :class:`~oyProjectManager.core.models.VersionType` is created the
        related data is saved to this SQLite3 database.
        
        For previously created objects, the retrieving of the data from the
        database is transparent. Thus creating lets say a Sequence object which
        is created and saved to the database before, the data retrieved
        automatically.
        
        With this new extension it is much faster to query any data needed.
        
        To support previous projects, which doesn't have this technology,
        whenever a :class:`~oyProjectManager.core.models.Project`
        instance is created to an old project, all the ``.settings.xml`` files
        from all the child Sequences are parsed and then the data is written to
        the newly created database.
        
        For the migrated sequences, the old ".settings.xml*" files will be
        removed from the sequence root folder.
    
    :param name: The name of the project. Should be a string or unicode. Name
      can not be None, a TypeError will be raised when it is given as None.
      The default value is None, so it will raise a TypeError.
      
      TODO: update the error messages for project.name=None, it should return
            TypeError instead of ValueErrors.
      
      The given project name is validated against the following rules:
        
        * The name can only have A-Z and 0-9 and "_" characters, all the other
          chars are going to be filtered out.
        * The name can only start with literals, no spaces, no numbers or any
          other character is not allowed.
        * Numbers and underscores are only allowed if they are not the first
          letter.
        * All the letters should be upper case.
        * All the "-" (minus) signs are converted to "_" (under score)
        * All the CamelCase formatting are expanded to underscore (Camel_Case)
    
    :param int fps: The frame rate in frame per second format. It is an 
      integer. The default value is 25. It can be skipped. If set to None. 
      The default value will be used.
    
    Creating a :class:`oyProjectManager.core.models.Project` instance is
    not enough to physically create the project folder. To make it happen the
    :meth:`~oyProjectManager.core.models.Project.create` should be called
    to finish the creation process.
    
    A Project can not be created without a name or with a name which is None or
    with an invalid name. For example, a project with name "'^+'^" can not be
    created because the name will become an empty string after the name
    validation process.
    
    Projects have a file called ".metadata.db" in their root. This SQL
    file holds information about:
    
      * The general folder structure of the project.
      * The sequences that this project has.
      * The shots that all the individual sequences have.
      * The placement code of the asset files.
      * etc.
    
    Every project has its own settings file to hold the different and evolving
    directory structure of the projects and the data created in that project.
    
    The pre version 0.1.2 projects are going to be converted from sequence
    based project structure to project based project structure upon parsing
    the project.
    """
    
    __tablename__ = "Projects"
    id = Column(Integer, primary_key=True)
    name = Column(String(256), unique=True)
    description = Column(String)
    path = Column(String)
    fullPath = Column(String)
    
    sequences = relationship(
        "Sequence",
        primaryjoin="Sequences.c.project_id==Projects.c.id"
    )
    
    def __new__(cls, name=None):
        """the overridden __new__ method to manage the creation of a Project
        instances.
        
        If the Project is created before then calling Project() for a second
        time, may be in another Python session will return the Project instance
        from the database.
        """
        
        # check the name argument
        if name:
            # condition the name
            name = Project.condition_name(name)
            
            repo = Repository()
            path = repo.server_path
            fullPath = os.path.join(path, name)
            
            metadata_db_name = conf.DATABASE_FILE_NAME
            metadata_full_path = os.path.join(
                fullPath,
                metadata_db_name
            ).replace("\\", "/")
            
            # now get the instance from the db
            if os.path.exists(metadata_full_path):
                logger.debug("Project metadata exists in %s" %
                              metadata_full_path)
                
                logger.debug("creating a new session")
                session = db.setup(metadata_full_path)
                
                proj_db = session.query(Project).filter_by(name=name).first()
                
                if proj_db is not None:
                    # return the database instance
                    logger.debug("found the project in the database")
                    logger.debug("returning the Project instance from the "
                                  "database")
                    
                    proj_db.session = session
                    logger.debug("attaching session to the created project "
                                 "instance, the session id is: %s" % 
                                 id(session))
                    
                    # skip the __init__
                    # TODO: find a good way to skip __init__
                    proj_db.__skip_init__ = None
                    
                    return proj_db
            else:
                logger.debug("Project doesn't exists")
        
        # just create it normally
        logger.debug("returning a normal Project instance")
        return super(Project, cls).__new__(cls, name=name)
    
    
    def __init__(self, name=None):
        
        # do not initialize if it is created from the DB
        if hasattr(self, "__skip_init__"):
            return
        
        self.path = ""
        self.fullPath = ""
        
        self._repository = Repository()
        
        # if the project is not retrieved from the database it doesn't have a
        # session attribute, so create one
        
        if not hasattr(self, "session"):
            self.session = None
        
        self.name = name
        
        self.metadata_db_name = conf.DATABASE_FILE_NAME
        self.metadata_full_path = os.path.join(
            self.fullPath,
            self.metadata_db_name
        ).replace("\\", "/")
        
        self._sequenceList = []
        
        self._exists = None
    
    
    @orm.reconstructor
    def __init_on_load__(self):
        """init when loaded from the db
        """
        
        self._repository = Repository()
        self.session = None
        
        self.metadata_db_name = conf.DATABASE_FILE_NAME
        self.metadata_full_path = os.path.join(
            self.fullPath,
            self.metadata_db_name
        ).replace("\\", "/")
        
        self._sequenceList = []
        
        self._exists = None
    
    
    
    def __str__(self):
        """the string representation of the project
        """
        return self.name


    def __eq__(self, other):
        """equality of two projects
        """

        return isinstance(other, Project) and self.name == other.name
    
    
    def update_paths(self, name_in):
        self.path = self._repository.server_path
        self.fullPath = os.path.join(self.path, name_in)


    @classmethod
    def condition_name(cls, name):
        
        if name is None:
            raise TypeError("The name can not be None")
        
        if name is "":
            raise ValueError("The name can not be an empty string")
        
        # strip the name
        name = name.strip()
        # convert all the "-" signs to "_"
        name = name.replace("-", "_")
        # replace camel case letters
        name = re.sub(r"(.+?[a-z]+)([A-Z])", r"\1_\2", name)
        # remove unnecessary characters from the string
        name = re.sub("([^a-zA-Z0-9\s_]+)", r"", name)
        # remove all the characters from the beginning which are not alphabetic
        name = re.sub("(^[^a-zA-Z]+)", r"", name)
        # substitute all spaces with "_" characters
        name = re.sub("([\s])+", "_", name)
        # convert it to upper case
        name = name.upper()
        
        # check if the name became empty string after validation
        if name is "":
            raise ValueError("The name is not valid after validation")
        
        return name
    
    
    @validates("name")
    def _validate_name(self, key, name_in):
        """validates the given name_in value
        """
        
        name_in = self.condition_name(name_in)
        
        self.update_paths(name_in)
        
        return name_in


    def save(self):
        
        logger.debug("saving project settings to %s" % self.metadata_full_path)
        
        # create the database
        if self.session is None:
            logger.debug("there is no session, creating a new one")
            self.session = db.setup(self.metadata_full_path)
        
        if self not in self.session:
            self.session.add(self)
        
        self.session.commit()
    
    
    def create(self):
        """Creates the project directory in the repository.
        """
        
        # check if the folder already exists
        utils.mkdir(self.fullPath)
        self._exists = True
        
        self.save()


    def createSequence(self, sequenceName, shots):
        """creates a sequence and returns the sequence object.
        
        Raises a RuntimeError if the project is not created yet.
        
        :param sequenceName: The name of the newly created Sequence
        
        :param shots: A string showing the shot list. Ex: "1-5"
        
        :returns: Sequence
        """
        
        # raise a RuntimeError if the project is not created yet
        if not self.exists:
            raise RuntimeError("A Sequence can not be created for a Project "
                               "which is not created yet, please call "
                               "Project.create() before creating any new "
                               "Sequences")
        
        newSequence = Sequence(self, sequenceName)
        newSequence.addShots(shots)
        newSequence.create()
        
        return newSequence


    @property
    def repository(self):
        """the repository object
        """
        return self._repository

    @repository.setter
    def repository(self, repo):
        self._repository = repo

    @property
    def exists(self):
        """returns True if the project folder exists
        """
        if self._exists is None:
            self._exists = os.path.exists(self.fullPath)
        
        return self._exists

class Sequence(Base):
    """Sequence object to help manage sequence related data.
    
    By definition a Sequence is a group of
    :class:`~oyProjectManager.core.models.Shot`\ s.
    
    The class should be initialized with a
    :class:`~oyProjectManager.core.models.Project` instance and a
    sequenceName.
    
    Two sequences are considered the same if their name and their project
    names are matching.
    
    :param project: The owner
      :class:`~oyProjectManager.core.models.Project`. A Sequence instance
      can not be created without a proper
      :class:`~oyProjectManager.core.models.Project` instance passed to it
      with the ``project`` argument. If the passed
      :class:`~oyProjectManager.core.models.Project` instance is not created
      yet then a RuntimeError will be raised while creating a
      :class:`~oyProjectManager.core.models.Sequence` instance. Because a
      :class:`~oyProjectManager.core.models.Project` instance can be created
      only with a string which has the desired project name, the ``project``
      argument also accepts a string value holding the name of the
      :class:`~oyProjectManager.core.models.Project`.
    
    :type project: :class:`~oyProjectManager.core.models.Project`
    
    :param str name: The name of the sequence. It is heavily formatted. Follows
      the same naming rules with the
      :class:`~oyProjectManager.core.models.Project`.
    """
    
    __tablename__ = "Sequences"
    id = Column(Integer, primary_key=True)
    name = Column(String(256), unique=True)
    
    project_id = Column(Integer, ForeignKey("Projects.id"))
    _project = relationship("Project")
    
    shots = relationship("Shot")
    
    # TODO: move all the settings variables to Project class
    
    shotPrefix = Column(String(16), default=conf.SHOT_PREFIX)
    shotPadding = Column(Integer, default=conf.SHOT_PADDING)
    
    revPrefix = Column(String(16), default=conf.REV_PREFIX)
    revPadding = Column(Integer, default=conf.REV_PADDING)
    
    verPrefix = Column(String(16), default=conf.VER_PREFIX)
    verPadding = Column(Integer, default=conf.VER_PADDING)
    
    timeUnit = Column(String(32), default=conf.TIME_UNIT)
    
    structure_id = Column(Integer, ForeignKey("Structures.id"))
    structure = relationship("Structure")
    
    def __new__(cls, project=None, name=None):
        """the overridden __new__ method to manage the creation of Sequence
        instances.
        
        If the Sequence is created before then calling Sequence() for a second
        time, may be in another Python session will return the Sequence
        instance from the database.
        """
        
        if project and name:
            
            project = Sequence._check_project(project)
            
            # condition the name
            name = Sequence.condition_name(name)
            
            # now get it from the database
            seq_db = project.session.query(Sequence).\
                                     filter_by(name=name).first()
            
            if seq_db is not None:
                logger.debug("found the sequence in the database")
                logger.debug("returning the Sequence instance from the "
                              "database")
                
                seq_db.__skip_init__ = None
                return seq_db
            else:
                logger.debug("the Sequence should be new, there is no such "
                              "Sequence in the database")
        
        # in any other case just return the normal __new__
        logger.debug("returning a normal Sequence instance")
        return super(Sequence, cls).__new__(cls, project, name)
    
    def __init__(self, project=None, name=None):
        
        # skip initialization if this is coming from DB
        if hasattr(self, "__skip_init__"):
            return
        
        logger.debug("initializing the Sequence")
        
        self._project = self._check_project(project)
        logger.debug("id(project.session): %s" % id(self.project.session))
        
        self.session = self.project.session
        logger.debug("id(sequence.session): %s" % id(self.session))
        
        self.repository = self.project.repository
        
        self.name = name
        
        self._path = self.project.fullPath
        self._fullPath = os.path.join(self._path, self.name).replace("\\", "/")
        
        self.shotPrefix = conf.SHOT_PREFIX
        self.shotPadding = conf.SHOT_PADDING
        
        self.revPrefix = conf.REV_PREFIX
        self.revPadding = conf.REV_PADDING
        
        self.verPrefix = conf.VER_PREFIX
        self.verPadding = conf.VER_PADDING
        
        self.timeUnit = conf.TIME_UNIT
        
#        self.structure = Structure()
        self.structure = None
        
        self.structure = Structure()
        self.structure.shotDependentFolders = conf.SHOT_DEPENDENT_FOLDERS
        self.structure.shotIndependentFolders = conf.SHOT_INDEPENDENT_FOLDERS
        
        self._assetTypes = []
        self._shotList = [] # should be a string
        self._shots = [] # the new shot objects
        
#        self._environment = None # the working environment
        
        self._exists = False
    
    @orm.reconstructor
    def __init_on_load__(self):
        """run when an object is get from the db
        """
        self._path = self.project.fullPath
        self._fullPath = os.path.join(self._path, self.name).replace("\\", "/")

    def save(self):
        """persists the sequence in the database
        """
        
        logger.debug("saving self to the database")
        
        # there should be a session
        # because a Sequence can not be created
        # without an already created Project instance
        
        self.session.add(self)
        self.session.commit()

    def create(self):
        """creates the sequence
        """
        
        # if the sequence doesn't exist create the folder
        
        if not self._exists:
            logger.debug("the sequence doesn't exist yet, creating the folder")
            
            # create a folder with sequenceName
            utils.mkdir(self._fullPath)
            self._exists = True
        
        # tell the sequence to create its own structure
        logger.debug("creating the structure")
        self.createStructure()
        
        # and create the shots
        logger.debug("creating the shots")
        self.createShots()
        
        # copy any file to the sequence
        # (like workspace.mel)
        logger.debug("copying default files")
        for _fileInfo in self.repository.defaultFiles:
            sourcePath = os.path.join(_fileInfo[2], _fileInfo[0])
            targetPath = os.path.join(self._fullPath, _fileInfo[1],
                                      _fileInfo[0])
            
            shutil.copy(sourcePath, targetPath)
        
        self.save()

    def addShots(self, shots):
        """adds new shots to the sequence
        
        shots should be a range in on of the following format:
        #
        #,#
        #-#
        #,#-#
        #,#-#,#
        #-#,#
        etc.
        
        you need to invoke self.createShots to make the changes permanent
        """
        
        # for now consider the shots as a string of range
        # do the hard work later
        
        newShotsList = utils.uncompress_range(shots)
        
        # convert the list to strings
        newShotsList = map(str, newShotsList)
        
        # add the shotList to the current _shotList
        self._shotList.extend(newShotsList)
        self._shotList = utils.unique(self._shotList)
        
        # sort the shotList
        self._shotList = utils.sort_string_numbers(self._shotList)
        
        # just create shot objects with shot name and leave the start and end
        # frame and description empty, it will be edited later
        newShotObjects = []
        
        # create a shot names buffer
        shotNamesBuffer = [shot.name for shot in self.shots]
        
        for shotName in newShotsList:
            # check if the shot already exists
            if shotName not in shotNamesBuffer:
                shot = Shot(shotName, self)
                newShotObjects.append(shot)
        
        # add the new shot objects to the existing ones
        self._shots.extend(newShotObjects)
        
        # sort the shot objects
        self._shots = utils.sort_string_numbers(self._shots)

    def addAlternativeShot(self, shotNumber):
        """adds a new alternative to the given shot
        
        you need to invoke self.createShots to make the changes permanent
        
        returns the alternative shot number
        """

        # shotNumber could be an int convert it to str
        shotNumberAsString = str(shotNumber)

        # get the first integer as int in the string
        shotNumber = utils.embedded_numbers(shotNumberAsString)[1]

        # get the next available alternative shot number for that shot
        alternativeShotName = self.getNextAlternateShotName(shotNumber)

        # add that alternative shot to the shot list
        if alternativeShotName is not None:
            self._shotList.append(alternativeShotName)

            # create a new shot object
            alternativeShot = Shot(alternativeShotName, self)
            self._shots.append(alternativeShot)

        return alternativeShotName

    def getNextAlternateShotName(self, shot):
        """returns the next alternate shot number for the given shot number
        """

        # get the shot list
        shotList = self.shotList
        alternateLetters = 'ABCDEFGHIJKLMNOPRSTUVWXYZ'
        
        for letter in alternateLetters:
            #check if the alternate is in the list
            
            newShotNumber = str(shot) + letter
            
            if not newShotNumber in shotList:
                return newShotNumber

        return None

    def createShots(self):
        """creates the shot folders in the structure
        """
        
        if not self._exists:
            logging.warning("seq doesn't exist, not creating the shot folders")
            return
        
        # TODO: Update creation of shot folders from Jinja2 template
        
        # create the shot structure
        for folder in self.structure.shotDependentFolders:
            # render jinja2 templates if necessary
            if "{{" in folder:
                for shotNumber in self._shotList:
                    template = jinja2.Template(
                        os.path.join(self._fullPath, folder)
                    )
                    
                    path = template.render(
                        assetBaseName=self.convertToShotString(shotNumber)
                    )

                    utils.createFolder(path)
            else:
                path = os.path.join(self._fullPath, folder)
                utils.createFolder(path)
    
    @property
    def shots(self):
        """returns the shot objects as a list
        """
        return self._shots

    def _sortShots(self):
        """sorts the internal shot list
        """
        self._shots = sorted(self._shots, key=utils.embedded_numbers)

    def getShot(self, shotNumber):
        """returns the shot with given shotNumber
        """

        for shot in self._shots:
            assert(isinstance(shot, Shot))
            if shot.name == shotNumber:
                return shot

        return None

    @property
    def shotList(self):
        """returns the shot list object
        """
        return self._shotList 

    def createStructure(self):
        """creates the folders defined by the structure
        """
        if not self._exists:
            return
        
        # create the structure if it is not present
        if self.structure is None:
            self.structure = Structure()
        
        for folder in self.structure.shotIndependentFolders:
            utils.createFolder(os.path.join(self._fullPath, folder))

    def convertToShotString(self, shotNumber ):
        """ converts the input shot number to a padded shot string
        
        for example it converts:
        1   --> SH001
        10  --> SH010
        
        if there is an alternate letter it will add it to the end of the
        shot string, like:
        1a  --> SH001A
        10S --> SH010S
        
        it also properly converts inputs like this
        abc92a --> SH092A
        abc323d432e --> SH323D
        abc001d --> SH001D
        
        if the shotNumber argument is None it will return None
        
        for now it can't convert properly if there is more than one letter at
        the end like:
        abc23defg --> SH023DEFG
        """

        pieces = utils.embedded_numbers(unicode(shotNumber))
        
        if len(pieces) <= 1:
            return None
        
        number = pieces[1]
        alternateLetter = pieces[2]
        
        return_value = self.shotPrefix + utils.padNumber(
            number,
            self.shotPadding
        ) + alternateLetter.upper()
        
        return return_value

    def convertToRevString(self, revNumber):
        """converts the input revision number to a padded revision string
        
        for example it converts:
        1  --> r01
        10 --> r10
        """
        return self.revPrefix + utils.padNumber(revNumber, self.revPadding)

    def convertToVerString(self, verNumber):
        """converts the input version number to a padded version string
        
        for example it converts:
        1  --> v001
        10 --> v010
        """
        return self.verPrefix + utils.padNumber(verNumber, self.verPadding)

    def convertToShotNumber(self, shotString):
        """beware that it returns a string, it returns the number plus the
        alternative letter (if exists) as a string
        
        for example it converts:
        
        SH001 --> 1
        SH041a --> 41a
        etc.
        """

        # remove the shot prefix
        remainder = shotString[len(self.shotPrefix): len(shotString)]

        # get the integer part
        matchObj = re.match('[0-9]+', remainder)

        if matchObj:
            numberAsStr = matchObj.group()
        else:
            return None

        alternateLetter = ''
        if len(numberAsStr) < len(remainder):
            alternateLetter = remainder[len(numberAsStr):len(remainder)]

        # convert the numberAsStr to a number then to a string then add the
        # alternate letter
        return unicode(int(numberAsStr)) + alternateLetter

    def convertToRevNumber(self, revString):
        """converts the input revision string to a revision number
        
        for example it converts:
        r01 --> 1
        r10 --> 10
        """
        return int(revString[len(self.revPrefix):len(revString)])

    def convertToVerNumber(self, verString):
        """converts the input version string to a version number
        
        for example it converts:
        v001 --> 1
        v010 --> 10
        """
        return int(verString[len(self.verPrefix):len(verString)])

    @property
    def path(self):
        """returns the path of the sequence
        """
        return self._path

    @property
    def fullPath(self):
        """returns the full path of the sequence
        """
        return self._fullPath

    def isValid(self):
        """checks if the sequence is valid
        """

        # a valid should:
        # - be exist
        # - have a .settings.xml file inside it

        if self._exists:
            return True

        return False

    def addNewAssetType(self, name='', path='', shotDependent=False,
                        environments=None, output_path=""):
        """adds a new asset type to the sequence
        
        you need to invoke self.saveSettings to make the changes permanent
        """

        assert(isinstance(environments, list))

        # check if there is already an assetType with the same name

        # get the names of the asset types and convert them to upper case
        assetTypeName = [assetType.name.upper()
                         for assetType in self._assetTypes]

        if name.upper() not in assetTypeName:
            # create the assetType object with the input
            newAType = VersionType(name, path, shotDependent, environments)

            # add it to the list
            self._assetTypes.append(newAType)

    @property
    def exists(self):
        """returns True if the sequence itself exists, False otherwise
        """
        return self._exists

    def __eq__(self, other):
        """The equality operator
        """
        return isinstance(other, Sequence) and other.name == self.name and\
               other.project.name == self.project.name

    def __ne__(self, other):
        """The in equality operator
        """
        return not self.__eq__(other)

    @classmethod
    def condition_name(cls, name):
        return utils.stringConditioner(
            name,
            allowUnderScores=True,
            upperCaseOnly=True,
            capitalize=False
        )

    @validates("name")
    def _validate_name(self, key, name):
        """validates the given name
        """
        
        return self.condition_name(name)
    
    @classmethod
    def _check_project(cls, project):
        """A convenience function which checks the given project argument value
        
        It is a ``classmethod``, so can be called both in ``__new__`` and other
        methods like ``_validate_project``.
        
        Checks the given project for a couple of conditions, like being None or
        not being an Project instance etc.
        """
        
        if project is None:
            raise TypeError("Sequence.project can not be None")
        
        if isinstance(project, (str, unicode)):
            # a string is passed as the project name
            # check if we are able to create a project out of this name
            logger.debug("string is passed as project, converting to a "
                         "Project instance")
            
            project = Project(project)
            logger.debug(str(project))
            logger.debug(type(project))
            logger.debug("project.session: %s" % str(project.session))
        
        if not isinstance(project, Project):
            raise TypeError("The project should be and instance of "
                            "oyProjectManager.core.models.Project")
            
        if not project.exists:
            raise RuntimeError(
                "the given project should exist in the system, please call "
                "Project.create() before passing it to a new Sequence instance"
            )
        
        logger.debug("type of the project is: %s" % type(project))
        
        return project
    
    @synonym_for("_project")
    @property
    def project(self):
        """a read-only attribute to return the related Project of this Sequence
        instance
        """
        
        return self._project


class Structure(Base):
    """The class that helps to hold data about structures in a sequence.
    
    Structure holds data about shot dependent and shot independent folders.
    Shot dependent folders has shot folders, and the others not.
    
    This class is going to change a lot in the future releases and it is going
    to handle all the `project folder template` by using Jinja2 templates.
    """
    
    __tablename__ = "Structures"
    id = Column(Integer, primary_key=True)
    shotDependentFolders = Column(PickleType)
    shotIndependentFolders = Column(PickleType)
    
    def __init__(self,
                 shotDependentFolders=None,
                 shotIndependentFolders=None):
        
        self.shotDependentFolders = shotDependentFolders
        self.shotIndependentFolders = shotIndependentFolders


    def addShotDependentFolder(self, folderPath):
        """adds new shot dependent folder
        
        folderPath should be relative to sequence root
        """
        if folderPath not in self.shotDependentFolders:
            self.shotDependentFolders.append(folderPath)
            self.shotDependentFolders = sorted(self.shotDependentFolders)


    def addShotIndependentFolder(self, folderPath):
        """adds new shot independent folder
        
        folderPath should be relative to sequence root
        """

        if folderPath not in self.shotIndependentFolders:
            self.shotIndependentFolders.append(folderPath)
            self.shotIndependentFolders = sorted(self.shotIndependentFolders)


    def removeShotDependentFolder(self, folderPath):
        """removes the shot dependent folder from the structure
        beware that if the parent sequence uses that folder as a assetType folder
        you introduce an error to the sequence
        """
        self.shotDependentFolders.remove(folderPath)


    def removeShotIndependentFolder(self, folderPath):
        """removes the shot independent folder from the structure
        
        beware that if the parent sequence uses that folder as a assetType folder
        you introduce an error to the sequence
        """
        self.shotIndependentFolders.remove(folderPath)


    def fixPathIssues(self):
        """fixes path issues in the folder data variables
        """
        # replaces "\" with "/"
        for i, folder in enumerate(self.shotDependentFolders):
            self.shotDependentFolders[i] = folder.replace('\\', '/')

        for i, folder in enumerate(self.shotIndependentFolders):
            self.shotIndependentFolders[i] = folder.replace('\\', '/')


    def removeDuplicate(self):
        """removes any duplicate entry
        """
        # remove any duplicates
        self.shotDependentFolders = sorted(
            utils.unique(self.shotDependentFolders))
        self.shotIndependentFolders = sorted(
            utils.unique(self.shotIndependentFolders))

class VersionableBase(Base):
    """A base class for :class:`~oyProjectManager.core.models.Shot` and
    :class:`~oyProjectManager.core.models.Asset` classes.
    
    It will supply the base attributes to be able to attach a
    :class:`~oyProjectManager.core.models.Version` to the
    :class:`~oyProjectManager.core.models.Shot` and
    :class:`~oyProjectManager.core.models.Asset` instances.
    
    It doesn't need any parameter while initialization.
    
    It supplies only one read-only attribute called
    :attr:`~oyProjectManager.core.models.VersionableBase.versions` which is a
    list and holds :class:`~oyProjectManager.core.models.Version` instances.
    """
    
    __tablename__ = "Versionables"
    __mapper_args__ = {"polymorphic_identity": "VersionableBase"}
    
    id = Column(Integer, primary_key=True)
    
    version_id = Column(Integer)
    _versions = relationship("Version")
    
    project_id = Column(Integer, ForeignKey("Projects.id"))
    _project = relationship("Project")
    
    @synonym_for("_versions")
    @property
    def versions(self):
        """the Version instances attached to this object
        
        It is a read-only attribute
        """
        
        return self._versions
    
    @synonym_for("_project")
    @property
    def project(self):
        """the Project instance which this object is related to
        
        It is a read-only attribute
        """
        
        return self._project


class Shot(VersionableBase):
    """The class that enables the system to manage shot data.
    
    :param sequence: The :class:`~oyProjectManager.core.models.Sequence`
      instance that this Shot should belong to. The Sequence may not be created
      yet. Skipping it or passing None will raise RuntimeError, and anything
      other than a :class:`~oyProjectManager.core.models.Sequence` will raise
      a TypeError.
    
    :param name: A string holding the name of this shot. Can not be None or
      can not be skipped, a TypeError will be raised either way.
    
    :param start_frame: The start frame of this shot. Should be an integer, any
      other type will raise TypeError. The default value is 1 and skipping it
      will result the start_frame to be set to 1.
    
    :param end_frame: The end frame of this shot. Should be an integer, any
      other type will raise TypeError. The default value is 1 and skipping it
      will result the end_frame to be set to 1.
    
    :param description: A string holding the short description of this shot.
      Can be skipped.
    """
    
    __tablename__ = "Shots"
    __table_args__  = (
        UniqueConstraint("sequence_id", "name"), {}
    )
    __mapper_args__ = {"polymorphic_identity": "Shot"}
    
    shot_id =  Column("id", Integer, ForeignKey("Versionables.id") ,primary_key=True)
    
    name = Column(String)
    start_frame = Column(Integer, default=1)
    end_frame = Column(Integer, default=1)
    description = Column(String)
    
    sequence_id = Column(Integer, ForeignKey("Sequences.id"))
    _sequence = relationship("Sequence")
    
    _versions = relationship("Version")
    
    def __init__(self,
                 sequence=None,
                 name=None,
                 start_frame=1,
                 end_frame=1,
                 description=''):
        
#        super(Shot, self).__init__()
        
        self._sequence = self._validate_sequence(sequence)
        self.name = name
        self.description = description
        
        # update the project attribute
        self._project = self._sequence.project
        
        self._duration = 1
        self.start_frame = start_frame
        self.end_frame = end_frame
        
        #self._cutSummary = ''


    def __str__(self):
        """returns the string representation of the object
        """
        return self.name

#    def __repr__(self):
#        """returns the representation of the class
#        """
#        return "< oyProjectManager.core.models.Shot object: " + self._name + ">"

    @validates("name")
    def _validate_name(self, key, name):
        """validates the given name value
        """
        
        if name is None:
            raise TypeError("Shot.name can not be None")
        
        if not isinstance(name, (str, unicode)):
            raise TypeError("Shot.name should be an instance of str or "
                            "unicode")
        
        if name == "":
            raise ValueError("Shot.name can not be empty string")
        
        # now check if the name is present for the current Sequence
        shot_instance = self.sequence.session.query(Shot).\
            filter(Shot.name==name).\
            filter(Shot.sequence_id==self.sequence.id).\
            first()
        
        if shot_instance is not None:
            raise ValueError("Shot.name already exists for the given sequence "
                             "please give a unique shot name")
        
        return name
    
    def _validate_sequence(self, sequence):
        """validates the given sequence value
        """
        
        if sequence is None:
            raise RuntimeError("Shot.sequence can not be None")
        
        if not isinstance(sequence, Sequence):
            raise TypeError("Shot.sequence should be an instance of "
                            "oyProjectManager.core.models.Sequence")
        
        return sequence
    
    @validates("description")
    def _validate_description(self, key, description):
        """validates the given description value
        """
        
        if description is None:
            description = ""
        
        if not isinstance(description, (str, unicode)):
            raise TypeError("Shot.description should be an instance of str "
                            "or unicode")
        
        return description
    
    
    @validates("start_frame")
    def _validate_start_frame(self, key, start_frame):
        """validates the given start_frame value
        """
        
        if start_frame is None:
            start_frame = 1
        
        if not isinstance(start_frame, int):
            raise TypeError("Shot.start_frame should be an instance of "
                            "integer")
        
        if self.end_frame is not None:
            self._update_duration(start_frame, self.end_frame)
        
        return start_frame
    
    @validates("end_frame")
    def _validate_end_frame(self, key, end_frame):
        """validates the given end_frame value
        """
        
        if end_frame is None:
            end_frame = 1
        
        if not isinstance(end_frame, int):
            raise TypeError("Shot.end_frame should be an instance of "
                            "integer")
        
        if self.end_frame is not None:
            self._update_duration(self.start_frame, end_frame)
        
        return end_frame

    def _update_duration(self, start_frame, end_frame):
        """updates the duration
        """
        self._duration = end_frame - start_frame + 1

    @synonym_for("_sequence")
    @property
    def sequence(self):
        """The sequence of the current Shot instance.
        :returns: :class:`~oyProjectManager.core.models.Sequence`
        """
        return self._sequence
    

    @property
    def duration(self):
        """the duration
        """
        return self._duration
    
    
    @property
    def number(self):
        """Returns the number part of the shot name::
          
          >> shot.name
            "SH001"
          >> shot.number
            "1"
          >> shot.name
            "SH012A"
          >> shot.number
            "12A"
        """
        
        pass
    
    @synonym_for("_versions")
    @property
    def versions(self):
        """returns the list of versions of this Shot instance
        """
        
        return self._versions
    
    def save(self):
        """commits the shot to the database
        """
        logger.debug("saving shot to the database")
        if self not in self.sequence.session:
            self.sequence.session.add(self)
        
        self.sequence.session.commit()


class Asset(VersionableBase):
    """to work properly it needs a valid project and sequence objects
    
    an Assets folder is something like that:
    
    ProjectsFolder / ProjectName / SequenceName / TypePath / BaseName / assetFileName
    """


    def __init__(self, project, sequence, fileName=None):
        self._project = project
        self._sequence = sequence

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
        self._extension = u''
        self._dateCreated = None
        self._dateUpdated = None
        self._fileSize = None
        self._fileSizeString = None
        self._fileSizeFormat = "%.2f MB"

        # path variables
        self._fileName = None
        self._path = None
        self._fullPath = None

        self._hasFullInfo = False
        self._hasBaseInfo = False

        self._dataSeparator = u'_'

        self._timeFormat = '%d.%m.%Y %H:%M'

        self._exists = False
        self._baseExists = False

        if fileName is not None:
            self._fileName = unicode(
                os.path.splitext(unicode(fileName))[0]) # remove the extension
            self._extension = \
                unicode(
                    os.path.splitext(
                        unicode(fileName)
                    )[1]
                ).split(os.path.extsep)[-1] # remove the . in extension
            self.guessInfoVariablesFromFileName()

        self.updateExistence()
    
    
    def __repr__(self):
        """the string representation of the object
        """
        return "<Asset, %s in %s of %s>" % (self.fileName,
                                            self.sequence.name,
                                            self.project.name)
    

    @property
    def infoVariables(self):
        """returns the info variables as a dictionary
        """

        infoVars = dict()
        infoVars['baseName'] = self._baseName
        infoVars['subName'] = self._subName
        infoVars['typeName'] = self._type.name
        infoVars['rev'] = self._rev
        infoVars['revString'] = self._revString
        infoVars['ver'] = self._ver
        infoVars['verString'] = self._verString
        infoVars['userInitials'] = self._userInitials
        infoVars['notes'] = self._notes
        infoVars['fileName'] = self._fileName

        return infoVars


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
        #assert(isinstance(keys,dict))

        if keys.has_key('baseName'):
            self._baseName = keys['baseName']

        if keys.has_key('subName'):
            self._subName = keys['subName']

        if keys.has_key('typeName'):
            self._typeName = keys['typeName']
            self._type = self._sequence.getAssetTypeWithName(self._typeName)

        # convert revision and version strings to number
        if keys.has_key('revString'):
            self._revString = keys['revString']
            self._rev = self._sequence.convertToRevNumber(self._revString)
        elif keys.has_key('rev'):
            self._rev = int(keys['rev'])
            self._revString = self._sequence.convertToRevString(self._rev)

        if keys.has_key('verString'):
            self._verString = keys['verString']
            self._ver = self._sequence.convertToVerNumber(self._verString)
        elif keys.has_key('ver'):
            self._ver = int(keys['ver'])
            self._verString = self._sequence.convertToVerString(self._ver)

        if keys.has_key('userInitials'):
            self._userInitials = keys['userInitials']

        if keys.has_key('notes'):
            self._notes = keys['notes']

        if keys.has_key('extension'):
            self._extension = keys['extension']

        if not self._sequence._noSubNameField:
            if self._baseName is not None and self._subName is not None and \
               self._type is not None and self._baseName != '' and \
               self._subName != '' and self._type != '':
                self._hasBaseInfo = True
                if self._rev is not None and self._ver is not None and \
                   self._userInitials is not None and self._rev != '' and \
                   self._ver != '' and self._userInitials != '':
                    self._hasFullInfo = True
        else:  # remove this block when the support for old version becomes obsolute
            if self._baseName is not None and self._type is not None and\
               self._baseName != '' and self._type != '':
                self._hasBaseInfo = True
                if self._rev is not None and self._ver is not None and \
                   self._userInitials is not None and self._rev != '' and \
                   self._ver != '' and self._userInitials != '':
                    self._hasFullInfo = True

        # get path variables
        self._initPathVariables()
        self.updateExistence()


    def guessInfoVariablesFromFileName(self):
        """tries to get all the info variables from the file name
        """

        # check if there is a valid project
        if self._project is None or self._sequence is None:
            return

        parts = self._fileName.split(self._dataSeparator)

        if not self._sequence._noSubNameField:
            if len(parts) < 5:
                return

            try:
                self._baseName = parts[0]
                self._subName = parts[1]
                self._typeName = parts[2]
                self._revString = parts[3]
                self._verString = parts[4]
                self._userInitials = parts[5]
            except IndexError:
                # the given file name is not valid
                self._fileName = ''
                return

            if len(parts) > 6: # there should be a notes part
                self._notes = self._dataSeparator.join(parts[6:len(parts)])
            else:
                self._notes = ""

        else: # remove this block when the support for old version becomes obsolute
            if len(parts) < 4:
                return

            self._baseName = parts[0]
            self._typeName = parts[1]
            self._revString = parts[2]
            self._verString = parts[3]
            self._userInitials = parts[4]

            if len(parts) > 5: # there should be a notes part
                self._notes = self._dataSeparator.join(parts[5:len(parts)])
            else:
                self._notes = ""

        # get the type object
        self._type = self._sequence.getAssetTypeWithName(self._typeName)

        # sometimes the file name matches the format but it is not neccessarly
        # an asset file if the type is None
        if self._type is None:
            return

        try:
            self._rev = self._sequence.convertToRevNumber(self._revString)
            self._ver = self._sequence.convertToVerNumber(self._verString)
        except ValueError:
            # the pattern is not compatible with the current project
            return

        self._hasFullInfo = self._hasBaseInfo = True

        self._initPathVariables()

        #self._updateFileSizes()
        #self._updateFileDates()


    @property
    def fullPath(self):
        """returns the fullPath of the asset
        """
        return self._fullPath


    @property
    def sequence(self):
        """returns the parent sequence
        """
        return self._sequence


    @property
    def path(self):
        """The path of the asset
        """

        return self._path


    @property
    def extension(self):
        """the file extension
        """
        return self._extension

    @extension.setter
    def extension(self, extension):
        """sets the extension of the asset object
        """
        #assert( isinstance(extension, str))
        # remove any extension separators from the input extension
        finalExtension = extension.split(os.path.extsep)[-1]

        self._extension = finalExtension
        self._initPathVariables()

    @property
    def fileName(self):
        """gathers the info variables to a fileName
        """

        fileName = self.fileNameWithoutExtension

        if self._extension is not None and self._extension != '' and \
           fileName is not None:
            fileName = fileName + os.extsep + self._extension

        return fileName


    @property
    def fileNameWithoutExtension(self):
        """returns the file name without extension
        """

        if not self.isValidAsset:
            return None

        parts = [] * 0
        parts.append(self._baseName)

        if not self._sequence._noSubNameField:
            parts.append(self._subName)

        parts.append(self._type.name)
        parts.append(self._revString)
        parts.append(self._verString)
        parts.append(self._userInitials)

        # check if there is a note
        if self._notes is not None and self._notes != '':
            parts.append(self._notes)

        fileName = self._dataSeparator.join(parts)

        return fileName


    @property
    def fileSize(self):
        """returns the fileSize as a float
        """
        return self._fileSize


    @property
    def fileSizeFormated(self):
        """returns the fileSize as a formatted string
        """
        return self._fileSizeString


    @property
    def pathVariables(self):
        """returns the path variables which are
        fullPath
        path
        fileName
        """
        return self.fullPath, self.path, self.fileName


    @property
    def project(self):
        """returns the project of the asset
        """
        return self._project


    def _initPathVariables(self):
        """sets path variables
        needs the info variables to be set before
        """

        # if it has just the base info update some of the variables
        if self._hasBaseInfo:
            seqFullPath = self._sequence.fullPath

            typePath = self._type.path

            assert(isinstance(typePath, (str, unicode)))

            # check if it has any jinja2 template variable
            if "{{" in typePath:
                self._path = os.path.join(seqFullPath, typePath)

                # and render the jinja2 template
                self._path = jinja2.Template(self._path).render(
                    assetBaseName=self.baseName,
                    assetSubName=self.subName,
                    assetTypeName=self.typeName,
                    assetRevNumber=self.revisionNumber,
                    assetRevString=self.revisionString,
                    assetVerNumber=self.versionNumber,
                    assetVerString=self.versionString,
                    assetUserInitials=self.userInitials,
                    assetExtension=self.extension
                )
            else:
                # fallback to the previous design where there is no
                # jinja2 template support
                self._path = os.path.join(seqFullPath, typePath)
                self._path = os.path.join(self._path, self._baseName)

            # if it has full info update the rest of the variables
            if self._hasFullInfo:
                self._fileName = self.fileName
                self._fullPath = os.path.join(self._path, self._fileName)

                self.updateExistence()


    @property
    def allVersions(self):
        """returns all versions as a list of asset objects
        """
        # return if we can't even get some little information
        if not self._baseExists and not self._hasBaseInfo:
            return []

        # use the Sequence object instead of letting the Asset object to dive
        # in to the file system to get other versions

        #import project
        sProj = self._project
        sSeq = self._sequence
        #assert(isinstance(selfseq, Sequence))

        assetVersionNames = self.allVersionNames

        sProjList = [sProj] * len(assetVersionNames)
        sSeqList = [sSeq] * len(assetVersionNames)

        return map(Asset, sProjList, sSeqList, assetVersionNames)


    @property
    def allVersionNames(self):
        """returns all version names for that asset as a list of string
        """

        if not self._baseExists and not self._hasBaseInfo:
            return []

        sSeq = self._sequence

        sSeqFAN = sSeq.filterAssetNames
        sSeqGAAFNFT = sSeq.getAllAssetFileNamesForType

        typeName = self._typeName
        baseName = self._baseName
        subName = self._subName

        if not self._sequence._noSubNameField:
            return sorted([assetFileName for assetFileName in
                           sSeqFAN(sSeqGAAFNFT(typeName), baseName=baseName,
                                   subName=subName)])
        else:
            return sorted([assetFileName for assetFileName in
                           sSeqFAN(sSeqGAAFNFT(typeName), baseName=baseName)])


    def _getCritiqueName(self):
        """returns the critique part of the asset name, which is:
        BaseName_SubName_TypeName
        """

        if not self._sequence._noSubNameField:
            if self._baseName is None or self._subName is None or \
               self._typeName is None:
                return None

            return self._dataSeparator.join(
                [self._baseName, self._subName, self._typeName])

        else: # remove this block when the support for old version becomes
              # obsolete
            if self._baseName is None or self._typeName is None:
                return None

            return self._dataSeparator.join([self._baseName, self._typeName])


    @property
    def sequenceFullPath(self):
        """returns the parent sequence full path
        """
        return self._sequence.fullPath



    #
    #def getProjectPath(self):
        #"""returns the parent project path

        #beware that it is the project path not the sequence path
        #"""
        #return self.project.fullPath


    @property
    def latestVersion(self):
        """returns the lastest version of an asset as an asset object and the number as an integer
        if the asset file doesn't exists yet it returns None, None
        """

        if not self._baseExists:
            return None, None

        allVersions = self.allVersions

        if len(allVersions) == 0:
            return None, None

        maxVerNumber = -1
        currentVerNumber = -1
        maxVerAsset = self

        for asset in allVersions:
            currentVerNumber = asset.versionNumber

            if currentVerNumber > maxVerNumber:
                maxVerNumber = currentVerNumber
                maxVerAsset = asset

        return maxVerAsset, maxVerNumber


    @property
    def latestVersion2(self):
        """the second version of the older one, it uses file names instead of
        asset objects.
        
        returns the latest version of an asset as an asset object and the
        number as an integer
        """

        if not self._baseExists:
            return None, None

        # get all version names
        allVersionNames = self.allVersionNames

        # return the last one as an asset
        if len(allVersionNames) > 0:
            assetObj = Asset(self._project, self._sequence, allVersionNames[-1])
        else:
            return None, None

        return assetObj, assetObj.versionNumber


    @property
    def latestRevision(self):
        """returns the latest revision of an asset as an asset object and the number as an integer
        if the asset doesn't exists yet it returns None, None
        """

        if not self._baseExists:
            return None, None

        allVersions = self.allVersions

        if len(allVersions) == 0:
            return None, None

        maxRevNumber = -1
        currentRevNumber = -1
        maxRevAsset = self

        for asset in allVersions:
            currentRevNumber = asset.revisionNumber

            if currentRevNumber > maxRevNumber:
                maxRevNumber = currentRevNumber
                maxRevAsset = asset

        return maxRevAsset, maxRevNumber


    @property
    def latestRevision2(self):
        """the second version of the older one, it uses file names instead of
        asset objects.
        
        returns the latest revision of an asset as an asset object and the
        number as an integer
        """

        if not self._baseExists:
            return None, None

        # get all version names
        allVersionNames = self.allVersionNames

        # return the last one as an asset
        assetObj = Asset(self._project, self._sequence, allVersionNames[-1])

        return assetObj, assetObj.revisionNumber


    def isLatestVersion(self):
        """checks if the asset is the latest version in its series
        """

        # return False if there is no such asset initialized yet
        if not self._baseExists:
            return True

        latestAssetObject, latestVersionNumber = self.latestVersion2

        # return True if it is the last in the list
        if self.versionNumber < latestVersionNumber:
            return False

        return True


    def isNewVersion(self):
        """checks if the asset is a new version in its series
        """
        # return True if there is no such asset initialized yet
        if not self._baseExists:
            return True

        latestAssetObject, latestVersionNumber = self.latestVersion2

        if self.versionNumber <= latestVersionNumber:
            return False

        return True


    def isLatestRevision(self):
        """checks if the asset is the latest revision in its series
        """

        # return False if there is no such asset initialized yet
        if not self._baseExists:
            return True

        latestAssetObject, latestRevisionNumber = self.latestRevision2

        # return True if it is the last in the list
        if self.revisionNumber < latestRevisionNumber:
            return False

        return True


    def isNewRevision(self):
        """checks if the asset is a new revision in its series
        """

        # return True if there is no such asset initialized yet
        if not self._baseExists:
            return True

        latestAssetObject, latestRevisionNumber = self.latestRevision2

        if self.revisionNumber <= latestRevisionNumber:
            return False

        return True


    def setVersionToNextAvailable(self):
        """sets the version number to the latest number + 1
        """

        latestAsset, latestVersionNumber = self.latestVersion2
        self._ver = latestVersionNumber + 1
        self._verString = self._sequence.convertToVerString(self._ver)
        self._initPathVariables()


    def setRevisionToNextAvailable(self):
        """sets the revision number to the latest number
        """

        latestAsset, latestRevisionNumber = self.latestRevision2
        self._rev = latestRevisionNumber
        self._revString = self._sequence.convertToRevString(self._rev)
        self._initPathVariables()


    def increaseVersion(self):
        """increases the version by 1
        """
        self._ver += 1
        self._verString = self._sequence.convertToVerString(self._ver)
        self._initPathVariables()


    def increaseRevision(self):
        """increases the revision by 1
        """
        self._rev += 1
        self._revString = self._sequence.convertToRevString(self._rev)
        self._initPathVariables()


    @property
    def isShotDependent(self):
        """returns True if the asset is shot dependent
        """
        return self.type.isShotDependent


    @property
    def isValidAsset(self):
        """returns True if this file is an Asset False otherwise
        
        being a valid asset doesn't necessarily mean the asset file exists
        
        """
        # if it has a baseName, subName, typeName, revString, 
        # verString and a userInitial string
        # and the parent folder for the asset starts with assets baseName
        # then it is considered as a valid asset

        if not self._sequence._noSubNameField:
            # check the fileName
            validFileName = bool(
                self._baseName != '' and self._baseName is not None and
                self._subName != '' and self._subName is not None and
                self._typeName != '' and self._typeName is not None and
                self._revString != '' and self._revString is not None and
                self._verString != '' and self._verString is not None and
                self._userInitials != '' and self._userInitials is not None and
                self._validateRevString() and self._validateVerString())

        else: # remove this block when the support for old version becomes
              # obsolete
            # check the fileName
            validFileName = bool(
                self._baseName != '' and self._baseName is not None and
                self._typeName != '' and self._typeName is not None and
                self._revString != '' and self._revString is not None and
                self._verString != '' and self._verString is not None and
                self._userInitials != '' and self._userInitials is not None and
                self._validateRevString() and self._validateVerString())

        return validFileName


    def _validateRevString(self):
        """validates if the revision string follows the format
        """
        if self._revString is None or self._revString == '':
            return False

        revPrefix = self._sequence._revPrefix

        matchObj = re.match(revPrefix + '[0-9]+', self._revString)

        if matchObj is None:
            return False
        else:
            return True


    def _validateVerString(self):
        """validates if the version string follows the format
        """
        if self._verString is None or self._verString == '':
            return False

        verPrefix = self._sequence._verPrefix

        matchObj = re.match(verPrefix + '[0-9]+', self._verString)

        if matchObj is None:
            return False
        else:
            return True


    def _updateFileDates(self):
        """updates the file creation and update dates
        """

        # get the file dates
        try:
            self._dateCreated = time.strftime(self._timeFormat, time.localtime(
                os.path.getctime(self._fullPath)))
            self._dateUpdated = time.strftime(self._timeFormat, time.localtime(
                os.path.getmtime(self._fullPath)))
        except OSError:
            pass


    def _updateFileSizes(self):
        """updates the file sizes as megabytes
        """

        # get the file dates
        try:
            self._fileSize = os.path.getsize(self._fullPath)
            self._fileSizeString = self._fileSizeFormat % (
            self._fileSize * 9.5367431640625e-07 )
        except OSError:
            pass




            #
            #def _validateExtension(self):
            #"""check if the extension is in the ignore list in the parent
            #sequence
            #"""


    @property
    def versionNumber(self):
        """returns the version number of the asset
        """
        return self._ver


    @property
    def revisionNumber(self):
        """returns the revision number of the asset
        """
        return self._rev


    @property
    def shotNumber(self):
        """returns the shot number of the asset if the asset is shot dependent
        """

        if self.isShotDependent:
            return self._sequence.convertToShotNumber(self._baseName)


    @property
    def versionString(self):
        """returns the version string of the asset
        """
        return self._verString


    @property
    def revisionString(self):
        """returns the revision string of the asset
        """
        return self._revString


    @property
    def type(self):
        """returns the asset type as an assetType object
        """
        return self._type


    @property
    def typeName(self):
        """returns the asset type name
        """
        return self._typeName


    @property
    def dateCreated(self):
        """returns the date that the asset is created
        """
        
        return self._dateCreated


    @property
    def dateUpdated(self):
        """returns the date that the asset is updated
        """
        return self._dateUpdated


    @property
    def userInitials(self):
        """returns user initials
        """
        return self._userInitials


    @property
    def baseName(self):
        """returns the base name of the asset
        """
        return self._baseName


    @property
    def subName(self):
        """returns the sub name of the asset
        """
        return self._subName


    @property
    def notes(self):
        """returns 
        """
        return self._notes


    @property
    def output_path(self):
        """returns the output path of the current asset
        """

        # render all variables like:
        # assetBaseName
        # assetSubName
        # assetTypeName
        # assetRevNumber
        # assetRevString
        # assetVerNumber
        # assetVerString
        # assetUserInitials
        # assetExtension

        return jinja2.Template(self.type.output_path).render(
            assetBaseName=self.baseName,
            assetSubName=self.subName,
            assetTypeName=self.typeName,
            assetRevNumber=self.revisionNumber,
            assetRevString=self.revisionString,
            assetVerNumber=self.versionNumber,
            assetVerString=self.versionString,
            assetUserInitials=self.userInitials,
            assetExtension=self.extension
        )


    @property
    def exists(self):
        """returns True if the asset file exists
        """
        return self._exists


    def updateExistence(self):
        """updates the self._exists variable
        """

        if self._hasBaseInfo:
            if os.path.exists(self._path):
                files = os.listdir(self._path)
                critiquePart = self._getCritiqueName()

                # update baseExistancy
                for _file in files:
                    if _file.startswith(critiquePart):
                        self._baseExists = True
                        break

            if self._hasFullInfo:
                self._exists = os.path.exists(self._fullPath)

                self._updateFileSizes()
                self._updateFileDates()

        else:
            self._exists = False
            self._baseExists = False



            #
            #def publishAsset(self):
            #"""publishes the asset by adding its name to the _publishInfo.xml
            #"""
            #pass



            #
            #def isPublished(self):
            #"""checks if the current asset is a published asset
            #"""
            #pass

class Version(Base):
    """Holds versions of assets or shots.
    
    In oyProjectManager a Version is the file created for an
    :class:`~oyProjectManager.core.models.Asset` or
    :class:`~oyProjectManager.core.models.Shot`\ . The placement of this file
    is automatically handled by the connected
    :class:`~oyProjectManager.core.models.VersionType` instance.
    
    The values given for
    :attr:`~oyProjectManager.core.models.Version.base_name` and
    :attr:`~oyProjectManager.core.models.Version.take_name` are conditioned as
    follows:
      
      * Each word in the string should start with an upper-case letter (title)
      * It can have all upper-case letters
      * CamelCase is allowed
      * Valid characters are ([A-Z])([a-zA-Z0-9_])
      * No white space characters are allowed, if a string is given with
        white spaces, it will be replaced with underscore ("_") characters.
      * No numbers are allowed at the beginning of the string
      * No leading or trailing underscore character is allowed
    
    So, with these rules are given, the examples for input and conditioned
    strings are as follows:
      
      * "BaseName" -> "BaseName"
      * "baseName" -> "BaseName"
      * " baseName" -> "BaseName"
      * " base name" -> "Base_Name"
      * " 12base name" -> "Base_Name"
      * " 12 base name" -> "Base_Name"
      * " 12 base name 13" -> "Base_Name_13"
      * ">£#>$#£½$ 12 base £#$£#$£½¾{½{ name 13" -> "Base_Name_13"
      * "_base_name_" -> "Base_Name"
    
    :param version_of: A :class:`~oyProjectManager.core.models.VersionableBase`
      instance (:class:`~oyProjectManager.core.models.Asset` or
      :class:`~oyProjectManager.core.models.Shot`) which is the owner of this
      version. Can not be skipped or set to None.
    
    :type type: :class:`~oyProjectManager.core.models.Asset`,
      :class:`~oyProjectManager.core.models.Shot` or
      :class:`~oyProjectManager.core.models.VersionableBase`
    
    :param type: A :class:`~oyProjectManager.core.models.VersionType` instance
      which is showing the type of the current version. The type is also
      responsible of the placement of this Version in the repository. So the
      :attr:`~oyProjectManager.core.models.Version.filename` and the
      :attr:`~oyProjectManager.core.models.Version.path` is defined by the
      related :class:`~oyProjectManager.core.models.VersionType` and the
      :class:`~oyProjectManager.core.models.Project` settings. Can not be
      skipped or can not be set to None.
    
    :type type: :class:`~oyProjectManager.core.models.VersionType`
    
    :param str base_name: A string showing the base name of this Version
      instance. Generally used to create an appropriate 
      :attr:`~oyProjectManager.core.models.Version.filename` and a
      :attr:`~oyProjectManager.core.models.Version.path` value. Can not be
      skipped, can not be None or empty string.
    
    :param str take_name: A string showing the take name. The default value is
      "MAIN" and it will be used in case it is skipped or it is set to None
      or an empty string. Generally used to create an appropriate
      :attr:`~oyProjectManager.core.models.Version.filename` and a
      :attr:`~oyProjectManager.core.models.Version.path` value. 
    
    :param int revision_number: It is an integer number showing the client
      revision number. The default value is 0 and it is used when the argument
      is skipped or set to None. It should be an increasing number with the
      newly created versions.
    
    :param int version_number: An integer number showing the current version
      number. It should be an increasing number among the Versions with the
      same base_name and take_name values. If skipped a proper value will be
      used by looking at the previous versions created with the same base_name
      and take_name values from the database. If the given value already exists
      then it will be replaced with the next available version number from the
      database.
    
    :param str note: A string holding the related note for this version. Can be
      used for anything the user desires.
    
    :param created_by: A :class:`~oyProjectManager.core.models.User` instance
      showing who created this version. It can not be skipepd or set to None or
      anything other than a :class:`~oyProjectManager.core.models.User`
      instance.
    
    :type created_by: :class:`~oyProjectManager.core.models.User`
    """



    __tablename__ = "Versions"
    
    __table_args__  = (
        UniqueConstraint("base_name", "take_name", "_version_number"), {}
    )

    id = Column(Integer, primary_key=True)
    version_of_id = Column(Integer, ForeignKey("Versionables.id"),
                           nullable=False)
    _version_of = relationship("VersionableBase")
    
    type_id = Column(Integer, ForeignKey("VersionTypes.id"))
    _type = relationship("VersionType")
    
    filename = Column(String)

    path = Column(String)
    base_name = Column(String)
    take_name = Column(String, default="MAIN")
    revision_number = Column(Integer, default=0)
    _version_number = Column(Integer, default=1, nullable=False)

    note = Column(String)
    created_by_id = Column(Integer, ForeignKey("Users.id"))
    created_by = relationship("User")
    
    def __init__(
        self,
        version_of=None,
        type=None,
        base_name=None,
        take_name="MAIN",
        version_number=1,
        note="",
        created_by=None,
    ):
        self._version_of = version_of
        self._type = type
        self.base_name = base_name
        self.take_name = take_name
        self.version_number = version_number
        self.note = note
        self.created_by = created_by
        
    
    @validates("_version_of")
    def _validate_version_of(self, key, version_of):
        """validates the given version of value
        """
        if version_of is None:
            raise RuntimeError("Version.version_of can not be None")
        
        if not isinstance(version_of, VersionableBase):
            raise TypeError("Version.version_of should be an Asset or Shot "
                            "or anything derives from VersionableBase class")
        
        return version_of
    
    @synonym_for("_version_of")
    @property
    def version_of(self):
        """The instance that this version belongs to.
        
        Generally it is a Shot or an Asset instance or anything which derives
        from VersionableBase class
        """
        return self._version_of
    
    @validates("_type")
    def _validate_type(self, key, type):
        """validates the given type value
        """
        if type is None:
            raise RuntimeError("Version.type can not be None")
        
        if not isinstance(type, VersionType):
            raise TypeError("Version.type should be an instance of "
                            "VersionType class")
        
        return type
    
    @synonym_for("_type")
    @property
    def type(self):
        """The type of this Version instance.
        
        It is a VersionType object.
        """
        
        return self._type
    
    @property
    def filename(self):
        """The filename of this version.
        
        It is automatically created by rendering the VersionType.filename
        template with the information supplied with this Version instance.
        """
        pass
    
    @property
    def path(self):
        """The path of this version.
        
        It is automatically created by rendering the VersionType.path template
        with the information supplied with this Version instance.
        """
        pass
    
    @property
    def fullpath(self):
        """The fullpath of this version.
        
        It is the join of the
        :attr:`~oyProjectManager.core.models.Version.filename` and
        :attr:`~oyProjectManager.core.models.Version.path`.
        """
        pass
    
    def _condition_name(self, name):
        """conditions the base name, see the
        :class:`~oyProjectManager.core.models.Version` documentation for
        details
        """
        
        # strip the name
        name = name.strip()
        # convert all the "-" signs to "_"
        name = name.replace("-", "_")
        # remove unnecessary characters from the string
        name = re.sub("([^a-zA-Z0-9\s_]+)", r"", name)
        # remove all the characters from the beginning which are not alphabetic
        name = re.sub("(^[^a-zA-Z]+)", r"", name)
        # substitute all spaces with "_" characters
        name = re.sub("([\s])+", "_", name)
        # make each words first letter uppercase
        name = "_".join([ word[0].upper() + word[1:]
                               for word in name.split("_")
                               if len(word)
        ])
        
        return name
        
    
    @validates("base_name")
    def _validate_base_name(self, key, base_name):
        """validates the given base_name value
        """
        if base_name is None:
            raise RuntimeError("Version.base_name can not be None, please "
                               "supply a proper string or unicode value")
        
        if not isinstance(base_name, (str, unicode)):
            raise TypeError("Version.base_name should be an instance of "
                            "string or unicode")
        
        base_name = self._condition_name(base_name)
        
        if base_name == "":
            raise ValueError("Version.base_name is either given as an empty "
                             "string or it became empty after formatting")
        
        return base_name
    
    @validates("take_name")
    def _validate_take_name(self, key, take_name):
        """validates the given take_name value
        """
        
        if take_name is None:
            take_name = conf.TAKE_NAME
        
        if not isinstance(take_name, (str, unicode)):
            raise TypeError("Version.take_name should be an instance of "
                            "string or unicode")
        
        take_name = self._condition_name(take_name)
        
        if take_name == "":
            raise ValueError("Version.take_name is either given as an empty "
                             "string or it became empty after formatting")
        
        return take_name
    
    @property
    def max_version(self):
        """returns the maximum version number for this Version from the
        database.
        """
        
        a_version = self.version_of.project.session.\
        query(
            Version
        ).filter(
            Version.base_name == self.base_name
        ).filter(
            Version.take_name == self.take_name
        ).order_by(
            Version.version_number.desc() # sort descending
        ).first()
        if a_version:
            max_version = a_version.version_number
        else:
            max_version = 0
        
        return max_version

    def _validate_version_number(self, version_number):
        """validates the given version number
        """

        max_version = self.max_version
        
        if version_number is None:
            # get the smallest possible value for the version_number
            # from the database
            version_number = max_version + 1
        
        if version_number <= max_version:
            version_number = max_version + 1
        
        return version_number
    
    def _version_number_getter(self):
        """returns the version_number of this Version instance
        """
        return self._version_number
    
    def _version_number_setter(self, version_number):
        """sets the version_number of this Version instance
        """
        self._version_number = self._validate_version_number(version_number)
    
    version_number = synonym(
        "_version_number",
        descriptor=property(
            _version_number_getter,
            _version_number_setter
        )
    )
    
    def save(self):
        """commits the changes to the database
        """
        
        session = self.version_of.project.session
        
        if self not in session:
            session.add(self)
        
        session.commit()
    
    @validates("note")
    def _validate_note(self, key, note):
        """validates the given note value
        """
        
        if note is None:
            note = ""
        
        if not isinstance(note, (str, unicode)):
            raise TypeError("Version.note should be an instance of "
                            "string or unicode")
        return note
    
    @validates("created_by")
    def _validate_created_by(self, key, created_by):
        """validates the created_by value
        """
        if created_by is None:
            raise RuntimeError("Version.created_by can not be None, please "
                               "set it to oyProjectManager.core.models.User "
                               "instance")
        
        if not isinstance(created_by, User):
            raise TypeError("Version.created_by should be an instance of"
                               "oyProjectManager.core.models.User")
        
        return created_by
    
    


class VersionType(Base):
    """Holds data like:\n
    - the asset type name
    - relative path of that type
    - the shot dependency of that VersionType
    - the environments (list) that the asset is available to
    """
    
    __tablename__ = "VersionTypes"
    id = Column(Integer, primary_key=True)
    
    def __init__(self,
                 name="",
                 code="",
                 path="",
                 filename="",
                 shotDependent=False,
                 environments=None,
                 output_path=""):
        self._name = name
        self._code = code
        self._path = path
        self._shotDependency = shotDependent
        self._environments = environments
        self._output_path = output_path

    def __repr__(self):
        """string representation of the asset type
        """

        return "<VersionType %s %s>" % (self.name, self.path)
    
    @property
    def name(self):
        """the asset type name
        """
        return self._name
    
    @name.setter
    def name(self, name):
        self._name = name

    @property
    def path(self):
        """assets types path
        """
        return self._path

    @path.setter
    def path(self, path):
        self._path = path

    @property
    def environments(self):
        """the environments that this asset type is available for
        """
        return self._environments

    @environments.setter
    def environments(self, environments):
        self._environments = environments

    @property
    def isShotDependent(self):
        """defines if the asset type is shot dependent or not
        """
        return self._shotDependency

    @isShotDependent.setter
    def isShotDependent(self, shotDependency):
        self._shotDependency = shotDependency

    @property
    def output_path(self):
        """The output path of this asset type
        """
        return self._output_path

    @output_path.setter
    def output_path(self, output_path_in):
        self._output_path = output_path_in

class User(Base):
    """a class for managing users
    """
    
    __tablename__ = "Users"
    
    id = Column(Integer, primary_key=True)
    
    name = Column(String)
    initials = Column(String)
    email = Column(String)
    
    versions_created = relationship("Version")
    
    def __init__(self, name=None, initials=None, email=None):
        self.name = name
        self.initials = initials
        self.email = email
