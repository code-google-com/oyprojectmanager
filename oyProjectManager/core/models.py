# -*- coding: utf-8 -*-
from exceptions import IndexError, ValueError, OSError, AttributeError, IOError

import os
import time
import platform
import re
import jinja2
from beaker import cache

from xml.dom import minidom
from sqlalchemy import (orm, Column, String, Integer, PickleType, ForeignKey,
                        Table, UniqueConstraint)
from sqlalchemy.ext.declarative import synonym_for
from sqlalchemy.orm import relationship, synonym
from sqlalchemy.orm.mapper import validates

from oyProjectManager import db
from oyProjectManager.db.declarative import Base
from oyProjectManager import utils, config

# create a cache with the CacheManager
bCache = cache.CacheManager()

# disable beaker DEBUG messages
import logging

logger = logging.getLogger('beaker.container')
logger.setLevel(logging.WARNING)

# create a logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# get the config
conf = config.Config()


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
      file is set to "/Volumes/Fileserver/Projects/TestProject/Textrue1". This
      is obviously a path for OSX, but what happens when you are under linux
      and open the file, in this case oyProjectManager will try to replace the
      path with the environment variable by checking if the path matches any of
      the oses repository path settings and it will reproduce the path as
      "$REPO/TestProject" in case the repository settings is
      "/Volumes/Fileserver/Projects" for OSX.
    
    There are no parameters that needs to be set to initialize a Repository
    instance.
    """

    def __init__(self):
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
                conf.repository["windows_path"].replace("\\", "/")
        except AttributeError:
            pass
        
        try:
            self._linux_path = conf.repository["linux_path"].replace("\\", "/")
        except AttributeError:
            pass
        
        try:
            self._osx_path = conf.repository["osx_path"].replace("\\", "/")
        except AttributeError:
            pass
        
#        # set the repository path from the environment
#        self.server_path = os.environ[conf.repository_env_key]
    
    def _validate_repository_env_key(self):
        """validates the repository env key environment variable
        """
        
        # raise a RuntimeError if there is no REPO environment var set
        if not os.environ.has_key(conf.repository_env_key):
            raise RuntimeError("Please set an environment variable with the "
                               "name %s and set it to your repository path" %
                               conf.repository_env_key)
        
        if os.environ[conf.repository_env_key] == "":
            raise ValueError("The %s environment variable can not be an "
                             "empty string" % conf.repository_env_key)
    
    @property
    @bCache.cache()
    def project_names(self):
        """returns a list of project names
        """
        self.update_project_list()
        return self._project_names
    
    def update_project_list(self):
        """updates the project list variable
        """
        try:
            self._project_names = []
            child_folders = utils.getChildFolders(self.server_path)
            
            for folder in child_folders:
                
                # check if the .metadata.db file exists under the folder
                if os.path.exists(
                    os.path.join(
                        self.server_path,
                        folder,
                        conf.database_file_name
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
        
#        platform_system = platform.system()
#        python_version = platform.python_version()
#        
#        windows_string = "Windows"
#        linux_string = "Linux"
#        osx_string = "Darwin"
#        
#        if python_version.startswith("2.5"):
#            windows_string = "Microsoft"
#
#        if platform_system == linux_string:
#            return self._linux_path
#        elif platform_system == windows_string:
#            return self._windows_path
#        elif platform_system == osx_string:
#            return self._osx_path
        
        return os.environ[conf.repository_env_key]
        
    
#    @server_path.setter
#    def server_path(self, server_path):
#        """setter for the server_path
#        
#        :param server_path: a string showing the server path
#        """
#        
#        # TODO: check if the given path is not matching the REPO env var
#        
#        # add a trailing separator
#        # in any cases os.path.join adds a trailing separator
#        
#        server_path = os.path.expanduser(
#            os.path.expandvars(
#                os.path.expandvars(
#                    os.path.expandvars(
#                        server_path
#                    )
#                )
#            )
#        )
#        
#        platform_system = platform.system()
#        
#        windows_string = "Windows"
#        linux_string = "Linux"
#        osx_string = "Darwin"
#        
#        if platform_system == linux_string:
#            self.linux_path = server_path.replace("\\", "/")
#        elif platform_system == windows_string:
#            self.windows_path = server_path.replace("\\", "/")
#        elif platform_system == osx_string:
#            self.osx_path = server_path.replace("\\", "/")
#        
##        # set also the environment variables
##        os.environ[conf.repository_env_key] = str(server_path)
#        
#        self._project_names = []
#        self.update_project_list()
    
    @property
    def linux_path(self):
        return self._linux_path.replace("\\", "/")
    
#    @linux_path.setter
#    def linux_path(self, linux_path_in):
#        """The linux path of the jobs server
#        """
#        self._linux_path = linux_path_in.replace("\\", "/")
    
    @property
    def windows_path(self):
        """The windows path of the jobs server
        """
        return self._windows_path.replace("\\", "/")
    
#    @windows_path.setter
#    def windows_path(self, windows_path_in):
#        self._windows_path = windows_path_in.replace("\\", "/")
    
    @property
    def osx_path(self):
        """The osx path of the jobs server
        """
        return self._osx_path.replace("\\", "/")
        
#    @osx_path.setter
#    def osx_path(self, osx_path_in):
#        self._osx_path = osx_path_in.replace("\\", "/")
    
    def get_project_name(self, filePath):
        """Returns the project name from the given path or fullPath.
        
        Calculates the project name from the given file or folder full path.
        It returns None if it can not get a suitable name.
        
        :param str filePath: The file or folder path.
        
        :returns: Returns a string containing the name of the project
        
        :rtype: str
        """
        
        #assert(isinstance(filePath, (str, unicode)))
        if filePath is None:
            return None
        
        filePath = os.path.expandvars(
                       os.path.expanduser(
                           os.path.normpath(filePath)
                       )
                   ).replace("\\", "/")
        
        if not filePath.startswith(self.server_path.replace("\\", "/")):
            return None
        
        residual = filePath[len(self.server_path.replace("\\", "/"))+1:]
        
        parts = residual.split("/")
        
        if len(parts) > 1:
            return parts[0]
        
        return None
    
    def relative_path(self, path):
        """Converts the given path to repository relative path.
        
        If "M:/JOBs/EXPER/_PROJECT_SETUP_" is given it will return
        "$REPO/EXPER/_PROJECT_SETUP_"
        """
        
        return path.replace(self.server_path, "$" + conf.repository_env_key)

class Project(Base):
    """Manages project related data.
    
    The Project class is in the center of the Asset Management system.
    Everything starts with the Project instance.
    
    .. versionadded:: 0.2.0
        SQLite3 Database:
        
        To hold the information about all the data created, there is a
        ".metadata.db" file in the project root. This SQLite3 database has
        information about all the
        :class:`~oyProjectManager.core.models.Sequence`\ s,
        :class:`~oyProjectManager.core.models.Shot`\ s,
        :class:`~oyProjectManager.core.models.Asset`\ s and
        :class:`~oyProjectManager.core.models.VersionType` created within
        the Project, the settings of the Project. So anytime a new
        :class:`~oyProjectManager.core.models.Sequence`,
        :class:`~oyProjectManager.core.models.Shot`,
        :class:`~oyProjectManager.core.models.Asset` or
        :class:`~oyProjectManager.core.models.Version` 
        :class:`~oyProjectManager.core.models.VersionType` is created the
        related data is saved to this SQLite3 database.
        
        With this new extension it is much faster to query any data needed.
    
    Querying data is very simple and fun. To get any kind of data from the
    database, first create a Project instance with the desired project name
    then use the ``Project.query`` attribute to query any information needed.
    For a simple example, lets get all the shots for a Sequence called
    "TEST_SEQ" in the "TEST_PROJECT"::
      
      from oyProjectManager.core.models import Project, Sequence, Shot
      
      proj = Project("TEST_PROJECT") # a previously created project
      all_shots = proj.query(Shot).filter(Shot.sequence.name=="TEST_SEQ").all()
    
    thats it.
    
    .. note::
      All the connection to the database is created over an
      ``sqlalchemy.orm.Session`` instance and the session created by the
      Project instance and all the other classes retrieve the session from
      their related Project class.
    
    **Creating a Project**
    
    All Projects have their own folder structure in the repository. Creating a
    :class:`~oyProjectManager.core.models.Project` instance is not enough to
    physically create the project folder structure. To make it happen the
    :meth:`~oyProjectManager.core.models.Project.create` should be called to
    finish the creation process. This will both create the main folder and the
    general structure of the project and a ``.metadata.db`` file. Any Project,
    which has a ``.metadata.db`` file (thus a folder with a name of
    ``Project.name``) considered an existing Project and ``Project.exists``
    returns ``True``.
    
    A Project can not be created without a `name` or with a name which is None
    or with an invalid name. For example, a project with name "'^+'^" can not
    be created because the name will become an empty string after the name
    validation process.
    
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
    """
    
    __tablename__ = "Projects"
    
    id = Column(Integer, primary_key=True)
    
    # TODO: add doc strings for all the attributes
    
    name = Column(String(256), unique=True)
    code = Column(String(256), unique=True)
    description = Column(String)
    path = Column(String)
    fullPath = Column(String)
    
    shot_number_prefix = Column(String(16), default=conf.shot_number_prefix)
    shot_number_padding = Column(Integer, default=conf.shot_number_padding)
    
    rev_number_prefix = Column(String(16), default=conf.rev_number_prefix)
    rev_number_padding = Column(Integer, default=conf.rev_number_padding)
    
    ver_number_prefix = Column(String(16), default=conf.ver_number_prefix)
    ver_number_padding = Column(Integer, default=conf.ver_number_padding)
    
    fps = Column(
        String(32),
        default=conf.fps,
        doc="""The frames per second setting of this project. The default value
        is %s
        """ % conf.fps
    )
    
    width = Column(String, default=conf.resolution_width)
    height = Column(String, default=conf.resolution_height)
    pixel_aspect = Column(String, default=conf.resolution_pixel_aspect)
    
    structure = Column(PickleType)
    
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
            name = Project._condition_name(name)
            
            repo = Repository()
            path = repo.server_path
            fullPath = os.path.join(path, name)
            
            metadata_db_name = conf.database_file_name
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
                    proj_db.query = session.query
                    logger.debug("attaching session to the created project "
                                 "instance, the session id is: %s" % 
                                 id(session))
                    
                    # skip the __init__
                    proj_db.__skip_init__ = None
                    
                    return proj_db
            else:
                logger.debug("Project doesn't exists")
        
        # just create it normally
        logger.debug("returning a normal Project instance")
        return super(Project, cls).__new__(cls, name=name)
    
    def __init__(self, name=None):
        # TODO: Projects needs code attribute
        
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
        
        if not hasattr(self, "query"):
            self.query = None
        
        self.name = name
        
        self.metadata_db_name = conf.database_file_name
        self.metadata_full_path = os.path.join(
            self.fullPath,
            self.metadata_db_name
        ).replace("\\", "/")
        
        self.shot_number_prefix = conf.shot_number_prefix
        self.shot_number_padding = conf.shot_number_padding
        
        self.rev_number_prefix = conf.rev_number_prefix
        self.rev_number_padding = conf.rev_number_padding
        
        self.ver_number_prefix = conf.ver_number_prefix
        self.ver_number_padding = conf.ver_number_padding
        
        self.fps = conf.fps
        self.width = conf.resolution_width
        self.height = conf.resolution_height
        self.pixel_aspect = conf.resolution_pixel_aspect
        
        self.structure = conf.project_structure
        
        self._exists = None
    
    @orm.reconstructor
    def __init_on_load__(self):
        """init when loaded from the db
        """
        
        self._repository = Repository()
        self.session = None
        self.query = None
        
        self.metadata_db_name = conf.database_file_name
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
    def _condition_name(cls, name):
        
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
        
        name_in = self._condition_name(name_in)
        
        self.update_paths(name_in)
        
        return name_in

    def save(self):
        """Saves the Project related information to the database.
        
        If there is no ``.metadata.db`` file it will be created, but be
        careful that the project structure will not be created. The safest way
        to both create the project structure and the .metadata.db file is to
        call the :meth:`~oyProjectManager.core.models.Project.create` method.
        """
        
        logger.debug("saving project settings to %s" % self.metadata_full_path)
        
        # create the database
        if self.session is None:
            logger.debug("there is no session, creating a new one")
            self.session = db.setup(self.metadata_full_path)
            self.query = self.session.query
        
        if self not in self.session:
            self.session.add(self)
        
        self.session.commit()
    
    def create(self):
        """Creates the project directory structure and saves the project, thus
        creates the ``.metadata.db`` file in the repository.
        """
        
        # check if the folder already exists
        utils.mkdir(self.fullPath)
        
        # create the structure if it is not present
        
        rendered_structure = jinja2.Template(self.structure).\
                             render(project=self)
        
        for folder in rendered_structure.split("\n"):
            utils.createFolder(os.path.join(self.fullPath, folder.strip()))
        
        self._exists = True
        
        self.save()

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
            self._exists = os.path.exists(self.metadata_full_path)
        
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
    
    :type project: :class:`~oyProjectManager.core.models.Project` or string
    
    :param str name: The name of the sequence. It is heavily formatted. Follows
      the same naming rules with the
      :class:`~oyProjectManager.core.models.Project`.
    """
    
    __tablename__ = "Sequences"
    id = Column(Integer, primary_key=True)
    name = Column(String(256), unique=True)
    code = Column(String(256), unique=True)
    
    project_id = Column(Integer, ForeignKey("Projects.id"))
    _project = relationship("Project")
    
    shots = relationship("Shot")
    
    def __new__(cls, project=None, name=None, code=None):
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
        return super(Sequence, cls).__new__(cls, project, name, code)
    
    def __init__(self, project=None, name=None, code=None):
        
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
        
        if code is None:
            code = name
        
        self.code = code
        
#        self._path = self.project.fullPath
#        self._fullPath = os.path.join(self._path, self.name).replace("\\", "/")
        
        self._exists = False
    
    # TODO: there should be a create() method which saves the sequence and
    # than calls the Project.create() which will create the necessary folder
    # structure

    def save(self):
        """persists the sequence in the database
        """
        
        logger.debug("saving self to the database")
        
        # there should be a session
        # because a Sequence can not be created
        # without an already created Project instance
        
        self.session.add(self)
        self.session.commit()

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
        
        # TODO: update this method
        
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
        
        # TODO: update this method
        
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
        
        # TODO: update this method

        # get the shot list
        shotList = self.shotList
        alternateLetters = 'ABCDEFGHIJKLMNOPRSTUVWXYZ'
        
        for letter in alternateLetters:
            #check if the alternate is in the list
            
            newShotNumber = str(shot) + letter
            
            if not newShotNumber in shotList:
                return newShotNumber

        return None
    
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
    
    :param number: A string or integer holding the number of this shot. Can not
      be None or can not be skipped, a TypeError will be raised either way. It
      will be used to create the
      :attr:`~oyProjectManager.core.models.Shot.code` attribute.
    
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
        UniqueConstraint("sequence_id", "number"), {}
    )
    __mapper_args__ = {"polymorphic_identity": "Shot"}
    
    shot_id =  Column("id", Integer, ForeignKey("Versionables.id") ,primary_key=True)
    
    number = Column(String)
    _code = Column(String)
    start_frame = Column(Integer, default=1)
    end_frame = Column(Integer, default=1)
    description = Column(String)
    
    sequence_id = Column(Integer, ForeignKey("Sequences.id"))
    _sequence = relationship("Sequence")
    
    def __init__(self,
                 sequence=None,
                 number=None,
                 start_frame=1,
                 end_frame=1,
                 description=''):
        
        self._sequence = self._validate_sequence(sequence)
        self.number = number
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
        return self.code

#    def __repr__(self):
#        """returns the representation of the class
#        """
#        return "< oyProjectManager.core.models.Shot object: " + self._name + ">"
    
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
    
    
    @validates("number")
    def _validates_number(self, key, number):
        """validates the given number value
        """
        
        if not isinstance(number, (int, str, unicode)):
            raise TypeError("Shot.number should be and instance of integer, "
                            "string or unicode")
        
        # first convert it to a string
        number = str(number)
        
        # then format it
        # remove anything which is not a number or letter
        number = re.sub(r"[^0-9a-zA-Z]+", "", number)
        
        # remove anything which is not a number from the beginning
        number = re.sub(
            r"(^[^0-9]*)([0-9]*)([a-zA-Z]{0,1})([a-zA-Z0-9]*)",
            r"\2\3",
            number
        ).upper()
        
        if number == "":
            raise ValueError("Shot.number is not in good format, please "
                             "supply something like 1, 2, 3A, 10B")
        
        # now check if the number is present for the current Sequence
        shot_instance = self.sequence.session.query(Shot).\
            filter(Shot.number==number).\
            filter(Shot.sequence_id==self.sequence.id).\
            first()
        
        if shot_instance is not None:
            raise ValueError("Shot.number already exists for the given "
                             "sequence please give a unique shot code")
        
        return number
    
    def save(self):
        """commits the shot to the database
        """
        logger.debug("saving shot to the database")
        if self not in self.sequence.session:
            self.sequence.session.add(self)
        
        self.sequence.session.commit()
    
    @synonym_for("_code")
    @property
    def code(self):
        """Returns the code of this shot by composing the
         :attr:`~oyProjectManager.core.models.Shot.number` with the
        :attr:`~oyProjectManager.core.models.Project.shot_prefix` attribute of
        the :class:`~oyProjectManager.core.models.Project` ::
          
          >> shot.number
            "1"
          >> shot.code
            "SH001"
          >> shot.number
            "12A"
          >> shot.code
            "SH012A"
        """
        number = re.sub(r"[A-Z]+", "", self.number)
        alter = re.sub(r"[0-9]+", "", self.number)
        
        return self.project.shot_prefix + \
               number.zfill(self.project.shot_padding) + \
               alter
        
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

    @property
    def latestVersion(self):
        """returns the lastest version of an asset as an asset object and the number as an integer
        if the asset file doesn't exists yet it returns None, None
        """
        
        # TODO: update this
        return None

    @property
    def latestRevision(self):
        """returns the latest revision of an asset as an asset object and the number as an integer
        if the asset doesn't exists yet it returns None, None
        """
        # TODO: update this
        return None

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
    
    For a newly created Version the
    :attr:`~oyProjectManager.core.models.Version.filename` and the
    :attr:`~oyProjectManager.core.models.Version.path` attributes are rendered
    from the associated :class:`~oyProjectManager.core.models.VersionType`
    instance. The resultant
    :attr:`~oyProjectManager.core.models.Version.filename` and
    :attr:`~oyProjectManager.core.models.Version.path` values are stored and
    retrieved back from the Version instance itself, no re-rendering happens.
    It means, the Version class depends the
    :class:`~oyProjectManager.core.models.VersionType` class only at the
    initialization, any change made to the
    :class:`~oyProjectManager.core.models.VersionType` instance (like changing
    the :attr:`~oyProjectManager.core.models.VersionType.name` or
    :attr:`~oyProjectManager.core.models.VersionType.code` of the
    :class:`~oyProjectManager.core.models.VersionType`) will not effect the
    Version instances created before this change. This is done in that way to
    be able to freely change the
    :class:`~oyProjectManager.core.models.VersionType` attributes and prevent
    loosing the connection between a Version and a file on the repository for
    previously created Versions.
    
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
    
    # TODO: add relation attributes like, references and referenced_by
    
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
    
    _filename = Column(String)
    _path = Column(String)
    
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
        # TODO: base_name should be get from VersionableBase.name
        self.base_name = base_name
        self.take_name = take_name
        self.version_number = version_number
        self.note = note
        self.created_by = created_by
        
        kwargs = self._template_variables()
        self._filename = jinja2.Template(self.type.filename).render(**kwargs)
        self._path = jinja2.Template(self.type.path).render(**kwargs)
    
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

    def _template_variables(self):
        kwargs = {
            "project": self.version_of.project,
            "sequence": self.version_of.sequence\
            if isinstance(self.version_of, Shot) else "",
            "version": self,
            "type": self.type
        }
        return kwargs

    @synonym_for("_filename")
    @property
    def filename(self):
        """The filename of this version.
        
        It is automatically created by rendering the VersionType.filename
        template with the information supplied with this Version instance.
        """
        return self._filename
    
    @synonym_for("_path")
    @property
    def path(self):
        """The path of this version.
        
        It is automatically created by rendering the VersionType.path template
        with the information supplied with this Version instance.
        """
        return self._path
    
    @property
    def fullpath(self):
        """The fullpath of this version.
        
        It is the join of the
        :attr:`~oyProjectManager.core.models.Version.filename` and
        :attr:`~oyProjectManager.core.models.Version.path`.
        """
        return os.path.join(self.path, self.filename).replace("\\", "/")
    
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
            take_name = conf.take_name
        
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
    """A template for :class:`~oyProjectManager.core.models.Version` class.
    
    A VersionType is basically a template object for the
    :class:`~oyProjectManager.core.models.Version` instances. It gives the
    information about the filename template, path template and output path
    template for the :class:`~oyProjectManager.core.models.Version` class. Then
    the :class:`~oyProjectManager.core.models.Version` class renders this
    Jinja2 templates and places itself (or the produced files) in to the
    appropriate folders in the
    :class:`~oyProjectManager.core.models.Repository`.
    
    All the template variables (
    :attr:`~oyProjectManager.core.models.VersionType.filename`,
    :attr:`~oyProjectManager.core.models.VersionType.path`,
    :attr:`~oyProjectManager.core.models.VersionType.output_path`) can use the
    following variables in their template codes.
    
    .. _table:
    
    +---------------+-----------------------------+--------------------------+
    | Variable Name | Variable Source             | Description              |
    +===============+=============================+==========================+
    | project       | version.version_of.project  | The project that the     |
    |               |                             | Version belongs to       |
    +---------------+-----------------------------+--------------------------+
    | sequence      | version.version_of.sequence | Only available for Shot  |
    |               |                             | versions                 |
    +---------------+-----------------------------+--------------------------+
    | version       | version                     | The version itself       |
    +---------------+-----------------------------+--------------------------+
    | type          | version.type                | The VersionType instance |
    |               |                             | attached to the this     |
    |               |                             | Version                  |
    +---------------+-----------------------------+--------------------------+
    
    :param str name: The name of this template. The name is not formatted in
      anyway. It can not be skipped or it can not be None or it can not be an
      empty string. The name attribute should be unique.
    
    :param str code: The code is a shorthand form of the name. For example,
      if the name is "Animation" than the code can be "ANIM" or "Anim" or
      "anim". Because the code is generally used in filename, path or
      output_path templates it is going to be a part of the filename or path,
      so be careful about what you give as a code. The code attribute should be
      unique. For formatting, these rules are current:
        
        * no white space characters are allowed
        * can not start with a number
        * can not start or end with an underscore character
        * both lowercase or uppercase letters are allowed
        
      A good code is the short form of the
      :attr:`~oyProjectManager.core.models.VersionType.name` attribute.
      Examples:
        
        +----------------+----------------------+
        | Name           | Code                 |
        +================+======================+
        | Animation      | Anim or ANIM         | 
        +----------------+----------------------+
        | Composition    | Comp or COMP         | 
        +----------------+----------------------+
        | Match Move     | MM                   |
        +----------------+----------------------+
        | Camera Track   | Track or TACK        |
        +----------------+----------------------+
        | Model          | Model or MODEL       |
        +----------------+----------------------+
        | Rig            | Rig or RIG           |
        +----------------+----------------------+
        | Scene Assembly | Asmbly or ASMBLY     |
        +----------------+----------------------+
        | Lighting       | Lighting or LIGHTING |
        +----------------+----------------------+
        | Camera         | Cam or CAM           |
        +----------------+----------------------+
    
    :param filename: The filename template. It is a single line Jinja2 template
      showing the filename of the
      :class:`~oyProjectManager.core.models.Version` which is using this
      VersionType. Look for the above `table`_ for possible variables those can
      be used in the template code.
      
      For an example the following is a nice example for Asset version
      filename::
      
        {{version.base_name}}_{{version.take_name}}_{{type.code}}_\\
           v{{'%03d'|format(version.version_number)}}_{{version.created_by.initials}}
      
      Which will render something like that::
        
        Car_Main_Model_v001_oy
      
      Now all the versions for the same asset will have a consistent name.
    
    :param str path: The path template. It is a single line Jinja2 template
      showing the path of the :class:`~oyProjectManager.core.models.Version`
      instance. Look for the above `table`_ for possible variables those can be
      used in the template code.
        
      For an example the following is a nice template for a Shot version::
      
        Sequences/{{sequence.code}}/Shots/{{version.base_name}}/{{type.code}}
      
      This will place a Shot Version whose base_name is SH001 and let say that
      the type is Animation (where the code is ANIM) to a path like::
      
        Sequences/SEQ1/Shots/SH001/ANIM
      
      All the animation files will be saved inside that folder.
    
    :param str output_path: It is a single line Jinja2 template which shows
      where to place the outputs of this kind of
      :class:`~oyProjectManager.core.models.Version`\ s. An output is simply
      anything that is rendered out from the source file, it can be the renders
      or playblast/flipbook outputs for Maya, Nuke or Houdini and can be
      different file type versions (tga, jpg, etc.) for Photoshop files.
      
      Generally it is a good idea to store the output right beside the source
      file. So for a Shot the following is a good example::
      
        {{version.path}}/Outputs
      
      Which will render as::
        
        Sequences/SEQ1/Shots/SH001/ANIM/Outputs
    
    :param str extra_folders: It is a list of single line Jinja2 template codes
      which are showing the extra folders those need to be created. It is
      generally created in the :class:`~oyProjectManager.core.models.Project`
      creation phase.
      
      The following is an extra folder hierarchy created for the FX version
      type::
        
        {{version.path}}/cache
    
    :param environments: A list of environments that this VersionType is valid
      for. The idea behind is to limit the possible list of types for the
      program that the user is working on. So let say it may not possible to
      create a camera track in Photoshop then what one can do is to add a
      Camera Track type but exclude the Photoshop from the list of environments
      that this type is valid for.
    
    :type environments: list of
      :class:`~oyProjectManager.core.models.Environment`\ s
    """
    
    __tablename__ = "VersionTypes"
    id = Column(Integer, primary_key=True)
    
    name = Column(String)
    code = Column(String)
    filename = Column(String)
    path = Column(String)
    output_path = Column(String)
    extra_folders = Column(String)
    environments = relationship("EnvironmentBase",
                                secondary="VersionType_Environments")
    
    def __init__(self,
                 name="",
                 code="",
                 filename="",
                 path="",
                 output_path="",
                 extra_folders="",
                 environments=None):
        self.name = name
        self.code = code
        self.filename = filename   
        self.path = path
        self.output_path = output_path
        self.environments = environments
        self.extra_folders = extra_folders
    
    @validates("name")
    def _validate_name(self, key, name):
        """validates the given name value
        """
        
        if name is None:
            raise RuntimeError("VersionType.name can not be None, please "
                               "supply a string or unicode instance")
        
        if not isinstance(name, (str, unicode)):
            raise TypeError("VersionType.name should be an instance of "
                            "string or unicode")
        
        return name


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

class EnvironmentBase(Base):
    """Holds information related to the program running the oyProjectManager.
    
    In oyProjectManager, an Environment is a host application like Maya, Nuke,
    Houdini etc.
    
    Generally a GUI for the end user is given an environment which helps
    the Qt Gui to be able to open, save, import or export an Asset without
    knowing the details of the environment.
    """
    
    __tablename__ = "Environments"
    id = Column(Integer, primary_key=True)
    
    def __init__(self, name='', extensions=[]):
        
        self._name = name
        self._extensions = extensions
        
        self._asset = None
        self._project = None
        self._sequence = None
    
    def __str__(self):
        """the string representation of the environment
        """
        return self._name
    
    @property
    def asset(self):
        """returns the bound asset object
        """
        return self._asset
    
    @asset.setter
    def asset(self, asset):
        """sets the asset object
        """
        self._asset = asset
    
    @property
    def name(self):
        """returns the environment name
        """
        return self._name
    
    @name.setter
    def name(self, name):
        """sets the environment name
        """
        self._name = name
    
    def save(self):
        """the save action
        """
        raise NotImplemented
    
    def export(self, asset):
        """the export action
        """
        raise NotImplemented
    
    def open_(self, force=False):
        """the open action
        """
        raise NotImplemented
    
    def import_(self, asset):
        """the import action
        """
        raise NotImplemented
    
    def reference(self, asset):
        """the reference action
        """
        raise NotImplemented
    
    def getPathVariables(self):
        """gets the file name from environment
        """
        raise NotImplemented
    
    def getProject(self):
        """returns the current project from environment
        """
        raise NotImplemented
    
    def setProject(self, projectName, sequenceName):
        """sets the project and sequence names, thus the working environment
        of the current environment
        """
        raise NotImplemented
    
    def setOutputFileName(self):
        """sets the output file names
        """
        raise NotImplemented
    
    def appendToRecentFiles(self, path):
        """appends the given path to the recent files list
        """
        raise NotImplemented
    
    def checkReferenceVersions(self):
        """checks the referenced asset versions
        
        returns list of asset objects
        """
        raise NotImplemented
    
    def getReferencedAssets(self):
        """returns the assets those been referenced to the current asset
        
        returns list of asset objects
        """
        raise NotImplemented
    
    def updateAssets(self, assetTupleList):
        """updates the assets to the latest versions
        """
        raise NotImplemented
    
    def getFrameRange(self):
        """returns the frame range from the environment
        """
        raise NotImplemented
    
    def setFrameRange(self, startFrame=1, endFrame=100):
        """sets the frame range in the environment
        """
        raise NotImplemented
    
    def getTimeUnit(self):
        """returns the time unit of the environment
        """
        raise NotImplemented
    
    def setTimeUnit(self, timeUnit='pal' ):
        """sets the frame rate of the environment
        """
        raise NotImplemented
    
    @property
    def extensions(self):
        """returns the extensions of environment
        """
        return self._extensions
    
    @extensions.setter
    def extensions(self, extensions):
        """sets the extensions
        """
        self._extensions = extensions
    
    def hasValidExtension(self, fileName):
        """returns true if the given fileNames extension is in the extensions
        list false otherwise
        
        accepts:
        - a full path with extension or not
        - a filen name with extension or not
        - an extension with a dot on the start or not
        """
        
        if fileName is None:
            return False
        
        if fileName.split('.')[-1].lower() in self._extensions:
            return True
        
        return False
    
    def loadReferences(self):
        """loads all the references
        """
        raise NotImplemented
    
    def replaceAssets(self, sourceAsset, targetAsset):
        """replaces the source asset with the target asset
        """
        raise NotImplemented

VersionType_Environments = Table(
    "VersionType_Environments", Base.metadata,
    Column("versionType_id", Integer, ForeignKey("VersionTypes.id"),
           primary_key=True),
    Column("resource_id", Integer, ForeignKey("Environments.id"),
           primary_key=True)
)
