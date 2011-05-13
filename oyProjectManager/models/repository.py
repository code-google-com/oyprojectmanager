# -*- coding: utf-8 -*-



import sys
import platform
import os
import shutil
import re
import oyAuxiliaryFunctions as oyAux
from xml.dom import minidom
from oyProjectManager.utils import cache
from oyProjectManager.models import user, abstractClasses






########################################################################
#class Repository(abstractClasses.Singleton):
class Repository(object):
    """Repository class gives informations about the servers, projects, users
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
    
    =============
    Settings File
    =============
    
    oyProjectManager uses the OYPROJECTMANAGER_PATH environment variable to
    track the settings, if there is no OYPROJECTMANAGER_PATH variable in your
    current environment the system will not work.
    
    You can set OYPROJECTMANAGER_PATH to a shared folder in your fileserver
    where all the users can access.
    
    oyProjectManager will look for these files in the
    OYPROJECTMANAGER_PATH:
    
       * defaultProjectSettings.xml
      
       * environmentSettings.xml
      
       * repositorySettings.xml
      
       * users.xml
    
    You can just duplicate the XML files under the settings folder of the
    package root to your own OYPROJECTMANAGER_PATH.
    
    These are the xml files that the oyProjectManager searches for:
    
     * defaultProjectSettings.xml: see
       :class:`~oyProjectManager.models.project.DefaultSettingsParser` for
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
    
    
    
    #----------------------------------------------------------------------
    def __init__(self):
        
        # initialize default variables
        
        # user name STALKER for forward compability
        self.repository_path_env_key = "STALKER_REPOSITORY_PATH"
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
        self._readUsers()
        # ---------------------------------------------------
    
    
    
    #----------------------------------------------------------------------
    def _init_repository_path_environment_variable(self):
        """initializes the environment variables
        """
        
        #print "initializing repository path env variable"
        
        # create the environment variable if there is no defined yet
        if not os.environ.has_key(self.repository_path_env_key):
            os.environ[self.repository_path_env_key] = ""
    
    
    
    #----------------------------------------------------------------------
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
            fps = timeNode.getAttribute('fps')
            self._time_units[ name ] = fps
        
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
    
    
    
    #----------------------------------------------------------------------
    #@cache.CachedMethod
    @property
    def projects(self):
        """returns projects names as a list
        """
        self.update_project_list()
        return self._projects
    
    
    
    #----------------------------------------------------------------------
    @cache.CachedMethod
    @property
    def valid_projects(self):
        """returns the projectNames only if they are valid projects.
        A project is only valid if there are some valid sequences under it
        """
        
        # get all projects and filter them
        self.update_project_list()
        
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
                    validProjectList.append(projName)
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
        return [ userObj.name for userObj in self._users ]
    
    
    
    #----------------------------------------------------------------------
    @property
    def userInitials(self):
        """returns the user intials
        """
        return sorted([userObj.initials for userObj in self._users])
    
    
    
    #----------------------------------------------------------------------
    def _readUsers(self):
        """parses the usersFile
        """
        
        # check if the usersFile exists
        if not os.path.exists( self._users_file_full_path ):
            return
        
        usersXML = minidom.parse( self._users_file_full_path )
        
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
    def update_project_list(self):
        """updates the project list variable
        """
        
        try:
            #self._projects = oyAux.getChildFolders(
                #self._projectsFolderFullPath
            #)
            self._projects = []
            
            child_folders = oyAux.getChildFolders(self.server_path)
            #print "self.server_path", self.server_path
            
            for folder in child_folders:
                filtered_folder_name = re.sub(
                    r".*?(^[^A-Z_]+)([A-Z0-9_]+)",
                    r"\2",
                    folder
                )
                #print filtered_folder_name, folder
                if filtered_folder_name == folder:
                    self._projects.append(folder)
                #self._projects.append(folder)
        
            self._projects.sort()
        
        except IOError:
            #print "server path doesn't exists, %s" % self._projectsFolderFullPath
            print "server path doesn't exists, %s" % self.server_path
    
    
    
    #----------------------------------------------------------------------
    def server_path():
        
        doc = """the server path"""
        
        def fget(self):
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
            
        
        def fset(self, server_path_in):
            
            # add a trailing separator
            # in any cases os.path.join adds a trailing seperator
            
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
        
        return locals()
    
    server_path = property( **server_path() )
    
    
    
    #----------------------------------------------------------------------
    def linux_path():
        def fget(self):
            return self._linux_path
        
        def fset(self, linux_path_in):
            #self._linux_path = self._validate_linux_path(linux_path_in)
            self._linux_path = linux_path_in
            #os.environ[self.repository_path_env_key] = linux_path_in
        
        doc = """the linux path of the jobs server"""
        
        return locals()
    
    linux_path = property(**linux_path())
    
    
    
    #----------------------------------------------------------------------
    def windows_path():
        def fget(self):
            return self._windows_path
        
        def fset(self, windows_path_in):
            #self._windows_path = self._validate_windows_path(windows_path_in)
            self._windows_path = windows_path_in
            #os.environ[self.repository_path_env_key] = windows_path_in
        
        doc = """the windows path of the jobs server"""
        
        return locals()
    
    windows_path = property(**windows_path())
    
    
    
    #----------------------------------------------------------------------
    def osx_path():
        def fget(self):
            return self._osx_path
        
        def fset(self, osx_path_in):
            #self._osx_path = self._validate_osx_path(osx_path_in)
            self._osx_path = osx_path_in
            #os.environ[self.repository_path_env_key] = osx_path_in
        
        doc = """the osx path of the jobs server"""
        
        return locals()
    
    osx_path = property(**osx_path())
    
    
    
    #----------------------------------------------------------------------
    def createProject(self, projectName):
        """Creates a new project on the server with the given project name.
        
        :returns: The newly created project.
        
        :rType: `~oyProjectManager.models.project.Project`
        """
        
        from oyProjectManager.models import project
        return project.Project(projectName)
    
    
    
    #----------------------------------------------------------------------
    @property
    def defaultFiles(self):
        """returns the default files list as list of tuples, the first element
        contains the file name, the second the project relative path, the third
        the source path
        
        this is the list that contains files those need to be copied to every
        project like workspace.mel for Maya
        """
        
        return self._default_files_list
    
    
    
    #----------------------------------------------------------------------
    @property
    def default_settings_file_full_path(self):
        """returns the default settings file full path
        """
        return self._default_settings_file_full_path
    
    
    
    #----------------------------------------------------------------------
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
    
    
    
    #----------------------------------------------------------------------
    def last_user():
        def fget(self):
            last_user_initials = None
            
            try:
                last_user_file = open( self._last_user_file_full_path )
            except IOError:
                pass
            else:
                last_user_initials = last_user_file.readline().strip()
                last_user_file.close()
            
            return last_user_initials
        
        def fset(self, userInitials):
            try:
                last_user_file = open(self._last_user_file_full_path, 'w')
            except IOError:
                pass
            else:
                last_user_file.write(userInitials)
                last_user_file.close()
        
        doc = """returns and saves the last user initials if the last_user_file file exists otherwise returns None"""
        
        return locals()
    
    last_user = property(**last_user())
    
    
    
    #----------------------------------------------------------------------
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
        
        #if not filePath.startswith( self._projectsFolderFullPath ):
        if not filePath.startswith( self.server_path ):
            return None, None
        
        #residual = filePath[ len(self._projectsFolderFullPath)+1 : ]
        residual = filePath[ len(self.server_path)+1 : ]
        
        parts = residual.split(os.path.sep)
        
        if len(parts) > 1:
            return parts[0], parts[1]
        
        return None, None
    
    
    
    #----------------------------------------------------------------------
    def settings_dir_path():
        def fget(self):
            if self._settings_dir_path is None:
                self._settings_dir_path = os.path.expandvars(
                    os.path.expanduser(
                        os.environ[self.settings_path_env_key]
                    )
                )
            
            return self._settings_dir_path
        
        doc = """Returns the settings dir path.
        """
        
        return locals()
    
    settings_dir_path = property(**settings_dir_path())
    
    
    
    
    #----------------------------------------------------------------------
    @property
    def time_units(self):
        """returns time_units as a dictionary
        """
        return self._time_units
    
    
    
    
    #----------------------------------------------------------------------
    def relative_path(self, path):
        """Converts the given path to repository relative path.
        
        If "M:/JOBs/EXPER/_PROJECT_SETUP_" is given it will return
        "$STALKER_REPOSITORY_PATH/EXPER/_PROJECT_SETUP_"
        
        The environment key name is read from the self.repository_path_env_key
        variable
        """
        
        return path.replace(self.server_path,
                            "$" + self.repository_path_env_key)
