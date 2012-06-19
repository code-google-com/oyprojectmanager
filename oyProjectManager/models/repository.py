# -*- coding: utf-8 -*-
# Copyright (c) 2009-2012, Erkan Ozgur Yilmaz
# 
# This module is part of oyProjectManager and is released under the BSD 2
# License: http://www.opensource.org/licenses/BSD-2-Clause

from exceptions import AttributeError, RuntimeError, ValueError, IOError
import os
from oyProjectManager import utils
from oyProjectManager.utils import cache

# create a logger
import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)

class Repository(object):
    """Repository class gives information about the repository and projects in
    that repository.
    
    The Repository class helps:
    
      * Get a list of project names in the current repository
      * Find server paths
      * and some auxiliary things like:
        
        * convert the given path to repository relative path which contains
          the environment variable key in the repository path.
    
    In the current design of the system there can only be one repository where
    all the projects are saved on. It is a little bit hard or adventurous to
    build a system which supports multiple repositories.
    
    .. note::
      In future may there be support for multiple repositories by using
      repository specific environment variables, like $REPO1 for repository in
      the first index of the config.repository settings and $REPO2 for the
      second and etc. But in the current design it was a little bit an overkill
      to add this support.
    
    .. warning::
      The repository setting (``repository``) in the users own config.py file
      is useless for getting the repository path. It is the $REPO environment
      variable that oyProjectManager uses. The ``repository`` setting in the
      ``config.py`` is there to be able replace the path values for one
      operating system in another, for example, think that a path for a texture
      file is set to "/mnt/Projects/TestProject/Texture1". This
      is obviously a path for OSX or linux, but what happens when you are under
      Windows and open the file, in this case oyProjectManager will try to
      replace the path with the environment variable by checking if the path
      matches any of the oses repository path settings and it will reproduce
      the path as "$REPO/TestProject" in case the repository settings is
      "/mnt/Projects" for OSX.
    
    There are no parameters that needs to be set to initialize a Repository
    instance.
    """

    def __init__(self):
        
        logger.debug("initializing repository instance")
        
        # get the config
        from oyProjectManager import conf
        self.conf = conf
        
        self._server_path = ""
        self._windows_path = ""
        self._osx_path = ""
        self._linux_path = ""
        self._project_names = []
        
        self._validate_repository_env_key()
        
        # -----------------------------------------------------
        # read the repository settings and assign the defaults
        try:
            self._windows_path = \
                self.conf.repository["windows_path"].replace("\\", "/")
        except AttributeError:
            pass
        
        try:
            self._linux_path = \
                self.conf.repository["linux_path"].replace("\\", "/")
        except AttributeError:
            pass
        
        try:
            self._osx_path = \
                self.conf.repository["osx_path"].replace("\\", "/")
        except AttributeError:
            pass
        
        logger.debug("finished initializing repository instance")
    
    def _validate_repository_env_key(self):
        """validates the repository env key environment variable
        """
        
        # raise a RuntimeError if no REPO environment var is set
        if not os.environ.has_key(self.conf.repository_env_key):
            raise RuntimeError("Please set an environment variable with the "
                               "name %s and set it to your repository path" %
                               self.conf.repository_env_key)
        
        if os.environ[self.conf.repository_env_key] == "":
            raise ValueError("The %s environment variable can not be an "
                             "empty string" % self.conf.repository_env_key)
    
#    @property
#    @bCache.cache()
    @cache.CachedMethod
    @property
    def project_names(self):
        """returns a list of project names
        """
        self.update_project_list()
        return self._project_names
    
    def update_project_list(self):
        """updates the project list variable
        """
        logger.debug("updating projects list")
        
        try:
            self._project_names = []
            child_folders = utils.getChildFolders(self.server_path)
            
            for folder in child_folders:
                
                # check if the .metadata.db file exists under the folder
                if os.path.exists(
                    os.path.join(
                        self.server_path,
                        folder,
                        self.conf.database_file_name
                    )
                ):
                    # it should be a valid project
                    self._project_names.append(folder)
            
            self._project_names.sort()
        
        except IOError:
            logger.warning("server path doesn't exists, %s" % self.server_path)
    
    @property
    def server_path(self):
        """The server path
        """
        return os.path.expandvars(
            os.path.expandvars(
                os.path.expanduser(
                    os.environ[self.conf.repository_env_key]
                )
            )
        )
    
    @property
    def linux_path(self):
        return self._linux_path.replace("\\", "/")
    
    @property
    def windows_path(self):
        """The windows path of the jobs server
        """
        return self._windows_path.replace("\\", "/")
    
    @property
    def osx_path(self):
        """The osx path of the jobs server
        """
        return self._osx_path.replace("\\", "/")
    
    def get_project_name(self, file_path):
        """Returns the project name from the given path or full path.
        
        Calculates the project name from the given file or folder full path.
        It returns None if it can not get a suitable name.
        
        :param str file_path: The file or folder path.
        
        :returns: Returns a string containing the name of the project
        
        :rtype: str
        """
        
        #assert(isinstance(file_path, (str, unicode)))
        if file_path is None:
            return None
        
        file_path = os.path.expandvars(
                       os.path.expanduser(
                           os.path.normpath(file_path)
                       )
                   ).replace("\\", "/")
        
        if not file_path.startswith(self.server_path.replace("\\", "/")):
            return None
        
        residual = file_path[len(self.server_path.replace("\\", "/"))+1:]
        
        parts = residual.split("/")
        
        if len(parts) > 1:
            return parts[0]
        
        return None
    
    def relative_path(self, path):
        """Converts the given path to repository relative path.
        
        If "M:/JOBs/EXPER/_PROJECT_SETUP_" is given it will return
        "$REPO/EXPER/_PROJECT_SETUP_"
        """
        
        return path.replace(self.server_path,
                            "$" + self.conf.repository_env_key)
