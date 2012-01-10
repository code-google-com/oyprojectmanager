# -*- coding: utf-8 -*-
# Copyright (c) 2009-2012, Erkan Ozgur Yilmaz
# 
# This module is part of oyProjectManager and is released under the BSD 2
# License: http://www.opensource.org/licenses/BSD-2-Clause

import os
import re
import logging
#import datetime
import jinja2
#from beaker import cache

from sqlalchemy import (orm, Column, String, Integer, Float, Enum, PickleType,
                        ForeignKey, UniqueConstraint, Boolean)
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.ext.declarative import synonym_for
from sqlalchemy.orm import relationship, synonym, backref
from sqlalchemy.orm.mapper import validates
from sqlalchemy.schema import Table

from oyProjectManager import utils
from oyProjectManager.utils import cache
from oyProjectManager import db
from oyProjectManager.db.declarative import Base
from oyProjectManager.core.errors import CircularDependencyError

# create a cache with the CacheManager
#bCache = cache.CacheManager()

# disable beaker DEBUG messages
logger = logging.getLogger('beaker.container')
logger.setLevel(logging.WARNING)

# create a logger
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

class Project(Base):
    """Manages project related data.
    
    The Project class is in the center of the Asset Management system.
    Everything starts with the Project instance.
    
    **Creating a Project**
    
    All Projects have their own folder structure in the repository. Creating a
    :class:`~oyProjectManager.core.models.Project` instance is not enough to
    physically create the project folder structure. To make it happen the
    :meth:`~oyProjectManager.core.models.Project.create` should be called to
    finish the creation process. This will both create the project folder and
    the general structure of the project and a ``.metadata.db`` file. Any
    Project, which has a ``.metadata.db`` file (thus a folder with a name of
    ``Project.name``) considered an existing Project and ``Project.exists``
    returns ``True``.
    
    A Project can not be created without a `name` or with a name which is None
    or with an invalid name. For example, a project with name "'^+'^" can not
    be created because the name will become an empty string after the name
    validation process.
    
    The name of the project can freely be changed, but the path of the project
    will not change after the name of the project is changed.
    
    :param name: The name of the project. Should be a string or unicode. Name
      can not be None, a TypeError will be raised when it is given as None,
      can not be an empty string, a ValueError will be raised when it is an
      empty string.
      
      The given project name is validated against the following rules:
      
        * The name can only have a-z, A-Z, 0-9 and "-_" characters, all the
          other characters will be filtered out.
        * The name can only start with literals, no spaces, no numbers or any
          other character is not allowed.
        * Numbers and underscores are only be allowed if they are not the first
          letter.
    
    :param code: The code of the project. Should be a string or unicode. If
      given as None it will be generated from the
      :attr:`~oyProjectManager.core.models.Project.name` attribute. If it an
      empty string or become an empty string after validation a ValueError will
      be raised.
      
        * The name can only have A-Z and 0-9 and "_" characters, all the other
          chars are going to be filtered out.
        * The name can only start with literals, no spaces, no numbers or any
          other character is not allowed.
        * Numbers and underscores are only be allowed if they are not the first
          letter.
        * All the letters should be upper case.
        * All the minus ("-") signs will be converted to underscores ("_")
        * All the CamelCase formatting are expanded to underscore (CAMEL_CASE)
        
      The :attr:`~oyProjectManager.core.models.Project.code` is a read only
      attribute.
    
    :param int fps: The frame rate in frame per second format. It is an 
      integer. The default value is 25. It can be skipped. If set to None. 
      The default value will be used.
    """
    
    __tablename__ = "Projects"
    __table_args__  = (
        {"extend_existing":True}
    )
    
    id = Column(Integer, primary_key=True)
    
    active = Column(Boolean, default=True)
    
    # TODO: add doc strings for all the attributes
    
    name = Column(String(256), unique=True)
    _code = Column(String(256), unique=True)
    description = Column(String)
    
    shot_number_prefix = Column(String(16))
    shot_number_padding = Column(Integer)
    
    rev_number_prefix = Column(String(16))
    rev_number_padding = Column(Integer)
    
    ver_number_prefix = Column(String(16))
    ver_number_padding = Column(Integer)
    
    fps = Column(
        Integer,
        doc="""The frames per second setting of this project. The default value
        is 25   
        """
    )
    
    width = Column(Integer)
    height = Column(Integer)
    pixel_aspect = Column(Float)
        
    structure = Column(PickleType)
    
    sequences = relationship(
        "Sequence",
        primaryjoin="Sequences.c.project_id==Projects.c.id"
    )
    
#    version_types = relationship("VersionType")
    
    def __new__(cls, name=None, code=None):
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
            
            # now get the instance from the db
            if db.session is None:
                # create the session first
                logger.debug("db.session is None, setting up a new session")
                db.setup()
            
            proj_db = db.query(Project).filter_by(name=name).first()
            
            if proj_db is not None:
                # return the database instance
                logger.debug("found the project in the database")
                logger.debug("returning the Project instance from the "
                              "database")
                
                # skip the __init__
                proj_db.__skip_init__ = None
                
                from oyProjectManager import conf
                proj_db.conf = conf
                
                return proj_db
            else:
                logger.debug("Project doesn't exists")
        
        # just create it normally
        logger.debug("returning a normal Project instance")
        return super(Project, cls).__new__(cls, name, code)
        
    def __init__(self, name, code=None):
        # do not initialize if it is created from the DB
        if hasattr(self, "__skip_init__"):
            logging.debug("skipping the __init__ on Project")
            return
        
        logger.debug("initializing the Project")
        
        # get the config
        from oyProjectManager import conf
        self.conf = conf
        
        self.repository = Repository()
        
        self.name = name

        if code is None:
            code = self.name
        
        self._code = self._condition_code(code)
        
        self.shot_number_prefix = self.conf.shot_number_prefix
        self.shot_number_padding = self.conf.shot_number_padding
        
        self.rev_number_prefix = self.conf.rev_number_prefix
        self.rev_number_padding = self.conf.rev_number_padding
        
        self.ver_number_prefix = self.conf.ver_number_prefix
        self.ver_number_padding = self.conf.ver_number_padding
        
        # set the default resolution
        default_resolution_key = conf.default_resolution_preset
        default_resolution = conf.resolution_presets[default_resolution_key]
        
        self.fps = self.conf.default_fps
        self.width = default_resolution[0]
        self.height = default_resolution[1]
        self.pixel_aspect = default_resolution[2]
        
        # and the structure
        self.structure = self.conf.project_structure
    
    @orm.reconstructor
    def __init_on_load__(self):
        """init when loaded from the db
        """
        
        self.repository = Repository()
        
        from oyProjectManager import conf
        self.conf = conf
        
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
    
    @classmethod
    def _condition_name(cls, name):
        
        if name is None:
            raise TypeError("The Project.name can not be None")
        
        if not isinstance(name, (str, unicode)):
            raise TypeError("Project.name should be an instance of string or "
                            "unicode not %s" % type(name))
        
        if name is "":
            raise ValueError("The Project.name can not be an empty string")
        
        # strip the name
        name = name.strip()
        # remove unnecessary characters from the string
        name = re.sub("([^a-zA-Z0-9\s_\-]+)", r"", name)
        # remove all the characters from the beginning which are not alphabetic
        name = re.sub("(^[^a-zA-Z]+)", r"", name)
        
        # check if the name became empty string after validation
        if name is "":
            raise ValueError("The Project.name is not valid after validation")
        
        return name

    @classmethod
    def _condition_code(cls, code):
        
        if code is None:
            raise TypeError("The Project.code can not be None")
        
        if not isinstance(code, (str, unicode)):
            raise TypeError("Project.code should be an instance of string or "
                            "unicode not %s" % type(code))
        
        if code is "":
            raise ValueError("The Project.code can not be an empty string")
        
        # strip the code
        code = code.strip()
        # convert all the "-" signs to "_"
        code = code.replace("-", "_")
        # replace camel case letters
        code = re.sub(r"(.+?[a-z]+)([A-Z])", r"\1_\2", code)
        # remove unnecessary characters from the string
        code = re.sub("([^a-zA-Z0-9\s_]+)", r"", code)
        # remove all the characters from the beginning which are not alphabetic
        code = re.sub("(^[^a-zA-Z]+)", r"", code)
        # substitute all spaces with "_" characters
        code = re.sub("([\s])+", "_", code)
        # convert it to upper case
        code = code.upper()
        
        # check if the code became empty string after validation
        if code is "":
            raise ValueError("The Project.code is not valid after validation")
        
        return code
    
    @validates("name")
    def _validate_name(self, key, name_in):
        """validates the given name_in value
        """
        name_in = self._condition_name(name_in)
        return name_in

    def _validate_code(self, code):
        """validates the given code_in value
        """
        
        if code is None:
            code = self.name
        
        if not isinstance(code, (str, unicode)):
            raise TypeError("Project.code should be an instance of string or "
                            "unicode not %s" % type(code))
        
        if code is "":
            raise ValueError("Project.code can not be an empty string")
        
        code = self._condition_code(code)
        
        # check if the code became empty string after validation
        if code is "":
            raise ValueError("Project.code is not valid after validation")
        
        return code
    
    def save(self):
        """Saves the Project related information to the database.
        
        If there is no ``.metadata.db`` file it will be created, but be
        careful that the project structure will not be created. The safest way
        to both create the project structure and the .metadata.db file is to
        call the :meth:`~oyProjectManager.core.models.Project.create` method.
        """
        
        logger.debug("saving project settings to %s" % db.database_url)
        
        # create the database
        if db.session is None:
            logger.debug("there is no session, creating a new one")
        
        if self not in db.session:
            db.session.add(self)
        
        db.session.commit()
    
    def create(self):
        """Creates the project directory structure and saves the project, thus
        creates the ``.metadata.db`` file in the repository.
        """
        
        # check if the folder already exists
        utils.mkdir(self.full_path)

        # create the structure if it is not present
        rendered_structure = jinja2.Template(self.structure).\
                             render(project=self)
        
        folders = rendered_structure.split("\n")
        
        if len(folders):
            for folder in rendered_structure.split("\n"):
                try:
                    utils.createFolder(folder.strip())
                except OSError:
                    pass
        
        self._exists = True
        
        self.save()
    
    @property
    def path(self):
        """The path of this project instance. Basically it is the same value
        with what $REPO env variable holds
        """
        return self.repository.server_path
    
    @property
    def full_path(self):
        """The full_path of this project instance.
        """
        return os.path.join(self.path, self.code)
    
    @synonym_for("_code")
    @property
    def code(self):
        """Returns the code of this Project instance.
        
        The ``code`` attribute is read-only.
        
        :return: str
        """
        
        return self._code
        

class Sequence(Base):
    """Sequence object to help manage sequence related data.
    
    By definition a Sequence is a group of
    :class:`~oyProjectManager.core.models.Shot`\ s.
    
    The class should be initialized with a
    :class:`~oyProjectManager.core.models.Project` instance and a
    sequenceName.
    
    When a Sequence instance is created it is not persisted in the project
    database. To do it the :meth:`~oyProjectManager.core.models.Sequence.save`
    should be called.
    
    The structure of the Sequence should be created by calling its
    :meth:`~oyProjectManager.core.models.Sequence.create` method after it is
    saved.
    
    Two sequences are considered to be the same if their name and their project
    names are matching.
    
    :param project: The owner
      :class:`~oyProjectManager.core.models.Project`. A Sequence instance
      can not be created without a proper
      :class:`~oyProjectManager.core.models.Project` instance passed to it
      with the ``project`` argument.
    
    :type project: :class:`~oyProjectManager.core.models.Project` or string
    
    :param str name: The name of the sequence. It is heavily formatted. Follows
      the same naming rules with the
      :class:`~oyProjectManager.core.models.Project`.
    """
    
    __tablename__ = "Sequences"
    __table_args__  = (
        {"extend_existing":True}
    )
    
    id = Column(Integer, primary_key=True)
    name = Column(String(256), unique=True)
    code = Column(String(256), unique=True)
    description = Column(String)
    
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
            name = Sequence._condition_name(name)
            
            # now get it from the database
            seq_db = db.session.query(Sequence).\
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
    
    def __init__(self, project, name, code=None):
        
        # skip initialization if this is coming from DB
        if hasattr(self, "__skip_init__"):
            return
        
        logger.debug("initializing the Sequence")
        
        self._project = self._check_project(project)
        logger.debug("id(project.session): %s" % id(db.session))
        
#        self.session = self.project.session
#        logger.debug("id(sequence.session): %s" % id(self.session))
        
        self.name = name
        
        if code is None:
            code = name
        
        self.code = code
        
        self._exists = False
    
    @orm.reconstructor
    def __init_on_load__(self):
        """method that will run for database loaded instances
        """
#        self.session = self.project.session
    
#    def create(self):
#        """creates the sequence structure by calling self.save() and then a
#        self.project.create()
#        """
#        self.save()
#        self.project.create()

    def create(self):
        """creates the sequence structure
        """
        
        # create the sequence structure by calling the self.project.create
        self.project.create()
    
    def save(self):
        """persists the sequence in the database
        """
        
        logger.debug("saving self to the database")
        
        # there should be a session
        # because a Sequence can not be created
        # without an already created Project instance
        
        if self not in db.session:
            db.session.add(self)
        
        db.session.commit()
    
    def add_shots(self, shot_range_formula):
        """adds new shots to the sequence
        
        shot_range_formula should be a range in on of the following format:
        #
        #,#
        #-#
        #,#-#
        #,#-#,#
        #-#,#
        etc.
        """
        
        # for now consider the shot_range_formula as a string of range
        # do the hard work later
        
        new_shot_numbers = utils.uncompress_range(shot_range_formula)
        
        # convert the list to strings
        new_shot_numbers = map(str, new_shot_numbers)
        
        new_shots = []
        for shot_number in new_shot_numbers:
            # create a new shot instance
            new_shots.append(Shot(self, shot_number))
        
        db.session.add_all(new_shots)
        db.session.commit()

    def add_alternative_shot(self, shot_number):
        """adds a new alternative to the given shot
        
        returns the alternative shot number
        """
        
        # TODO: this functionality should be shifted to the Shot class
        
        # shot_number could be an int convert it to str
        # get the first integer as int in the string
        shot_number = utils.embedded_numbers(str(shot_number))[1]
        
        # get the next available alternative shot number for that shot
        alternative_shot_number = \
            self.get_next_alternate_shot_number(shot_number)
        
        # add that alternative shot to the shot list
        if alternative_shot_number is not None:
            new_alternative_shot = Shot(self, alternative_shot_number)
            db.session.add(new_alternative_shot)
            db.session.commit()
        
        return alternative_shot_number

    def get_next_alternate_shot_number(self, shot_number):
        """returns the next alternate shot_number number for the given shot_number number
        """
        
        # get the shot_number list
        alternate_letters = 'ABCDEFGHIJKLMNOPRSTUVWXYZ'
        
        for letter in alternate_letters:
            #check if the alternate is in the list
            
            new_shot_number = str(shot_number) + letter
            
            shot_from_db = db.query(Shot).\
                filter(Shot.sequence_id==self.id).\
                filter(Shot.number==new_shot_number).\
                first()
            
            if not shot_from_db:
                return new_shot_number
        
        return None
    
    def __eq__(self, other):
        """The equality operator
        """
        return isinstance(other, Sequence) and other.name == self.name and\
               other.project == self.project

    def __ne__(self, other):
        """The in equality operator
        """
        return not self.__eq__(other)

    @validates("name")
    def _validate_name(self, key, name):
        """validates the given name
        """
        
        name = Project._condition_name(name)
        
        return name
    
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
        
        if not isinstance(project, Project):
            raise TypeError("The project should be and instance of "
                            "oyProjectManager.core.models.Project")
        
        return project
    
    @synonym_for("_project")
    @property
    def project(self):
        """a read-only attribute to return the related Project of this Sequence
        instance
        """
        return self._project
    
    @validates("code")
    def _validate_code(self, key, code):
        """validates the given code value
        """
        
        if code is None:
            code = self.name
        
        if not isinstance(code, (str, unicode)):
            raise TypeError("Sequence.code should be an instance of str or "
                            "unicode, not %s" % type(code))
        
        code = Project._condition_code(code)
        
        return code
    
    @classmethod
    def _condition_name(cls, name):
        """Formats the given name value
        
        :param name: The name value to be conditioned 
        :return: str
        """

        if name is None:
            raise TypeError("The Sequence.name can not be None")

        if not isinstance(name, (str, unicode)):
            raise TypeError("Sequence.name should be an instance of string or "
                            "unicode not %s" % type(name))
        
        if name is "":
            raise ValueError("The Sequence.name can not be an empty string")
        
        name = Project._condition_name(name)

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
    __table_args__  = (
        UniqueConstraint("_code", "project_id"),
        UniqueConstraint("_name", "project_id"),
        {"extend_existing":True}
    )
    
    versionable_type = Column(String(64), nullable=False)
    
    __mapper_args__ = {
        "polymorphic_on": versionable_type,
        "polymorphic_identity": "VersionableBase"
    }
    
    id = Column(Integer, primary_key=True)
    
    _versions = relationship("Version")
    project_id = Column(Integer, ForeignKey("Projects.id"), nullable=False)
    _project = relationship("Project")
    
    _code = Column(
        String(128),
        doc="""The nicely formatted version of the
        :attr:`~oyProjectManager.core.models.Asset.name` attribute or
        :attr:`~oyProjectManager.core.models.Shot.number` attribute. It will
        be overloaded in the :class:`~oyProjectManager.core.models.Asset` or
        :class:`~oyProjectManager.core.models.Shot` class.
        """
    )

    _name = Column(String(128))
    
    description = Column(String)
    
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

    @validates("description")
    def _validate_description(self, key, description):
        """validates the given description value
        """
        if not isinstance(description, (str, unicode)):
            raise TypeError("Asset.description should be an instance of "
                            "string or unicode")
        
        return description



class Shot(VersionableBase):
    """The class that enables the system to manage shot data.
    
    .. note::
      
      There is a design flaw, which I've recognized at the day I'll release
      version 0.2.0. The ``_code`` of the Shot is not stored in the database,
      whereas the ``_code`` of a the Asset is. So one can not query Shot's by
      using the ``_code`` attribute, but it is easy to get the same effect by
      using the ``number`` attribute. So you need to create you queries with
      ``number`` instead of ``_code``.
      
      I hope I'll fix it in a later version.
    
    :param sequence: The :class:`~oyProjectManager.core.models.Sequence`
      instance that this Shot should belong to. The Sequence may not be created
      yet. Skipping it or passing None will raise TypeError, and anything
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
        UniqueConstraint("sequence_id", "number"),
        {"extend_existing":True}
    )
    __mapper_args__ = {"polymorphic_identity": "Shot"}

    shot_id =  Column("id", Integer, ForeignKey("Versionables.id") ,primary_key=True)

    number = Column(String)
    
    start_frame = Column(Integer, default=1)
    end_frame = Column(Integer, default=1)
    
    sequence_id = Column(Integer, ForeignKey("Sequences.id"))
    _sequence = relationship(
        "Sequence",
        primaryjoin="Shots.c.sequence_id==Sequences.c.id"
    )
    
    def __init__(self,
                 sequence,
                 number,
                 start_frame=1,
                 end_frame=1,
                 description=''):

        self._sequence = self._validate_sequence(sequence)
        # update the project attribute
        self._project = self._sequence.project
        
        self.number = number
        
        self.description = description

        self._duration = 1
        self.start_frame = start_frame
        self.end_frame = end_frame
        
        #self._cutSummary = ''
    
    def __eq__(self, other):
        """the equality operator
        """
        
        return isinstance(other, Shot) and other.number == self.number and \
            other.sequence == self.sequence
    
    def __ne__(self, other):
        """the inequality operator
        """
        
        return not self.__eq__(other)
    
    def __str__(self):
        """returns the string representation of the object
        """
        return self.code
    
    def __repr__(self):
        """returns the representation of the class
        """
        return "< oyProjectManager.core.models.Shot object: " + self.code + ">"

    def _validate_sequence(self, sequence):
        """validates the given sequence value
        """

        if sequence is None:
            raise TypeError("Shot.sequence can not be None")

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
        shot_instance = db.session.query(Shot).\
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
        if self not in db.session:
            db.session.add(self)
        
        db.session.commit()

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
        
        return self.project.shot_number_prefix +\
               number.zfill(self.project.shot_number_padding) + alter

class Asset(VersionableBase):
    """Manages Assets in a given :class:`~oyProjectManager.core.models.Project`
    
    Assets are the data created to finish a
    :class:`~oyProjectManager.core.models.Project`. It can be a Character or a
    Vehicle or anything that participate in to a
    :class:`~oyProjectManager.core.models.Shot`.
    
    Assets have :class:`~oyProjectManager.core.models.Versions`\ s to hold
    every change made to that asset file.
    
    The name attribute will be copied to the code attribute if the code
    
    
    :param project: The :class:`~oyProjectManager.core.models.Project` instance
      that this Asset belongs to. It is not possible to initialize an Asset
      without defining its :class:`~oyProjectManager.core.models.Project`.
    
    :param name: The name of this asset. It can not be None or an empty string.
      Anything is possible to be used as a name but it is recommended to keep
      it brief. The name attribute will be formatted and the result will be
      copied to the :attr:`~oyProjectManager.core.models.Asset.code`
      attribute. The name should be unique among all the asset in the current
      :class:`~oyProjectManager.core.models.Project`.
      
      The following rules will apply for the formatting of the name:
        
        * Spaces are allowed.
        * It should start with an upper case letter (A-Z)
        * Only the following characters are allowed (-_ a-zA-Z0-9)
    
    :param code: The code of this asset. If it is given as None or empty string
      the value will be get from the name attribute.
      
      The following rules will apply for the formatting of the code:
      
        * No spaces are allowed, all the spaces will be replaced with "_"
          (underscore) characters
        * It should start with upper case letter (A-Z)
        * Only the following characters are allowed (a-zA-Z0-9_)
        * All the "-" (minus) signs are converted to "_" (under score)
      
      If the code becomes an empty string after formatting a ValueError will be
      raised. The code should be unique among all the Assets in the current
      :class:`~oyProjectManager.core.models.Project`.
    """

    __tablename__ = "Assets"
    __table_args__  = (
        {"extend_existing":True}
    )
    
    __mapper_args__ = {"polymorphic_identity": "Asset"}
    
    asset_id = Column("id", Integer, ForeignKey("Versionables.id"),
                      primary_key=True)
    
    def __init__(self, project, name, code=None):
        self._project = project
        self.name = name
        self.code = code
    
    def __eq__(self, other):
        """equality operator
        """
        return isinstance(other, Asset) and self.name == other.name and \
            self.project==other.project
    
    def __ne__(self, other):
        return not self.__eq__(other)
    
    def __repr__(self):
        """the string representation of the object
        """
        return "<Asset, %s in %s>" % (self.name, self.project.name)
    
    def _validate_code(self, code):
        """validates the given code value
        """
        if code is None:
            code = self.name
        
        if not isinstance(code, (str, unicode)):
            raise TypeError("Asset.code should be an instance of string or "
                            "unicode not %s" % type(code))
        
        if code is "":
            raise ValueError("The Asset.code can not be an empty string")
        
        # strip the code
        code = code.strip()
        # remove unnecessary characters from the string
        code = re.sub("([^a-zA-Z0-9\s_]+)", r"", code)
        # remove all the characters from the beginning which are not alphabetic
        code = re.sub("(^[^a-zA-Z]+)", r"", code)
        # substitute all spaces with "_" characters
        code = re.sub("([\s])+", "_", code)
        
        # check if the code became empty string after validation
        if code is "":
            raise ValueError("Asset.code is not valid after validation")
        
        # convert the first letter to uppercase
        code = code[0].upper() + code[1:]
        
        return code
        
    def _code_getter(self):
        """The nicely formatted version of the
        :attr:`~oyProjectManager.core.models.Asset.name` attribute
        """
        return self._code
    
    def _code_setter(self, code):
        """Sets the code of this Asset instance
        """
        self._code = self._validate_code(code)

    code = synonym(
        "_code",
        descriptor=property(
            _code_getter,
            _code_setter
        )
    )
    
    def _validate_name(self, name):
        """validates the given name value
        """
        if name is None:
            raise TypeError("")
        
        if not isinstance(name, (str, unicode)):
            raise TypeError("Asset.name should be an instance of string or "
                            "unicode not %s" % type(name))
        
        if name is "":
            raise ValueError("The Asset.name can not be an empty string")
        
        # strip the name
        name = name.strip()
        # remove unnecessary characters from the string
        name = re.sub("([^a-zA-Z0-9\s_-]+)", r"", name)
        # remove all the characters from the beginning which are not alphabetic
        name = re.sub("(^[^a-zA-Z]+)", r"", name)
#        # substitute all spaces with "_" characters
#        name = re.sub("([\s])+", "_", name)
        
        # check if the name became empty string after validation
        if name == "":
            raise ValueError("Asset.name is not valid after validation")
        
        # convert the first letter to uppercase
        name = name[0].upper() + name[1:]
        
        return name
    
    def _name_getter(self):
        """getter for the name attribute
        """
        return self._name
    
    def _name_setter(self, name):
        """setter for the name attribute
        """
        name = self._validate_name(name)
        self._name = name
    
    name = synonym(
        "_name",
        descriptor=property(
            _name_getter,
            _name_setter,
            doc="""The name of this Asset instance, try to be brief."""
        )
    )
    
    def save(self):
        """saves the asset to the related projects database
        """
        if self not in db.session:
            logger.debug("adding %s to the session" % self)
            db.session.add(self)
        
        logger.debug("saving the asset %s" % self)
        db.session.commit()

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
      showing who created this version. It can not be skipped or set to None or
      anything other than a :class:`~oyProjectManager.core.models.User`
      instance.
    
    :type created_by: :class:`~oyProjectManager.core.models.User`
    
    :param str extension: A string holding the file extension of this version.
      It may or may not include a dot (".") sign as the first character.
    """

    # TODO: add audit info like date_created, date_updated, created_at and updated_by
    # TODO: add needs_update flag, primarily need to be used with renamed versions
    
    # file_size_format = "%.2f MB"
    # timeFormat = '%d.%m.%Y %H:%M'

    __tablename__ = "Versions"
    
    __table_args__  = (
#        UniqueConstraint("base_name", "take_name", "_version_number", "type_id"),
        UniqueConstraint("version_of_id", "take_name", "_version_number", "type_id"),
        {"extend_existing":True}
    )

    id = Column(Integer, primary_key=True)
    version_of_id = Column(Integer, ForeignKey("Versionables.id"),
                           nullable=False)
    _version_of = relationship("VersionableBase")

    type_id = Column(Integer, ForeignKey("VersionTypes.id"))
    _type = relationship("VersionType")
    
    _filename = Column(String)
    _path = Column(String)
    _output_path = Column(String)
    _extension = Column(String)
    
    base_name = Column(String)
    take_name = Column(String, default="MAIN")
    revision_number = Column(Integer, default=0)
    _version_number = Column(Integer, default=1, nullable=False)
    
    note = Column(String)
    created_by_id = Column(Integer, ForeignKey("Users.id"))
    created_by = relationship("User")
    
    references = relationship(
        "Version",
        secondary="Version_References",
        primaryjoin="Versions.c.id==Version_References.c.referencer_id",
        secondaryjoin="Version_References.c.reference_id==Versions.c.id",
        backref="referenced_by"
    )
    
    def __init__(self,
                 version_of,
                 base_name,
                 type,
                 created_by,
                 take_name="MAIN",
                 version_number=1,
                 note="",
                 extension=""):
        self._version_of = version_of
        self._type = type
        self.base_name = base_name
        self.take_name = take_name
        self.version_number = version_number
        self.note = note
        self.created_by = created_by
        
        self._filename = ""
        self._path = ""
        self._output_path = ""
        
        # setting the extension will update the path variables already
        self.extension = extension
    
    def __eq__(self, other):
        """the equality operator
        """
        return isinstance(other, Version) and \
               self.base_name==other.base_name and \
               self.version_of==other.version_of and \
               self.type==other.type and self.take_name==other.take_name and \
               self.version_number==other.version_number
    
    def __ne__(self, other):
        """the not equal operator
        """
        return not self.__eq__(other)

    def update_paths(self):
        """updates the path variables
        """
        kwargs = self._template_variables()
        self._filename = jinja2.Template(self.type.filename).render(**kwargs)
        self._path = jinja2.Template(self.type.path).render(**kwargs)
        self._output_path = jinja2.Template(self.type.output_path).\
        render(**kwargs)
    
    @validates("_version_of")
    def _validate_version_of(self, key, version_of):
        """validates the given version of value
        """
        if version_of is None:
            raise TypeError("Version.version_of can not be None")

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
            raise TypeError("Version.type can not be None")
        
        if not isinstance(type, VersionType):
            raise TypeError("Version.type should be an instance of "
                            "VersionType class")
        
        # raise a TypeError if the given VersionType is not suitable for the
        # given version_of instance
        if self.version_of.__class__.__name__ != type.type_for:
            raise TypeError("The VersionType instance given for Version.type "
                            "is not suitable for the given VersionableBase "
                            "instance, the version_of is a %s and the "
                            "version_type is for %s" % 
                            (self.version_of.__class__.__name__,
                             type.type_for
                            )
            )
        
        return type
    
    def _validate_extension(self, extension):
        """Validates the given extension value
        """
        
        if not isinstance(extension, (str, unicode)):
            raise TypeError("Version.extension should be an instance of "
                            "string or unicode")
        
        if extension != "":
            if not extension.startswith("."):
                extension = "." + extension
        
        return extension
    
    def _extension_getter(self):
        """Returns the extension attribute value
        """
        return self._extension
    
    def _extension_setter(self, extension):
        """Sets the extension attribute
        
        :param extension: The new extension should be a string or unicode value
          either starting with a dot sign or not.
        """
        
        self._extension = self._validate_extension(extension)
        
        # now update the filename
        self.update_paths()
    
    extension = synonym(
        "_extension",
        descriptor=property(fget=_extension_getter, fset=_extension_setter),
        doc="""The extension of this version file, updating the extension will
        also update the filename
        """
    )
    
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
            "sequence": self.version_of.sequence \
            if isinstance(self.version_of, Shot) else "",
            "version": self,
            "type": self.type,
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
        
        It is automatically created by rendering the template in
        :class`~oyProjectManager.core.models.Version`\.
        :attr:`~oyProjectManager.core.models.VersionType.path` of the with the
        information supplied by this
        :class:`~oyProjectManager.core.models.Version` instance.
        
        The resultant path is an absolute one. But the stored path in the
        database is just the relative portion to the
        :class:`~oyProjectManager.core.models.Repository`\ .\ 
        :attr:`~oyProjectManager.core.models.Repository.server_path`
        """
        return os.path.join(
            self.project.path,
            self._path
        ).replace("\\", "/")
    
    @property
    def full_path(self):
        """The full_path of this version.
        
        It is the join of
        :class:`~oyProjectManager.core.models.Repository`.\ 
        :attr:`~oyProjectManager.core.models.Repository.server_path` and
        :class:`~oyProjectManager.core.models.Version`.\
        :attr:`~oyProjectManager.core.models.Version.path` and
        :class:`~oyProjectManager.core.models.Version`.\
        :attr:`~oyProjectManager.core.models.Version.filename` attributes.
        
        So, it is an absolute path. The value of the ``full_path`` is not stored
        in the database.
        """
        return os.path.join(
            self.path,
            self.filename
        ).replace("\\", "/")
    
    @synonym_for("_output_path")
    @property
    def output_path(self):
        """The output_path of this version.
        
        It is automatically created by rendering the
        :class:`~oyProjectManager.core.models.VersionType`\ .\ 
        :attr:`~oyProjectManager.core.models.VersionType.output_path`
        template with the information supplied with this ``Version`` instance.
        
        The resultant path is an absolute one. But the stored path in the
        database is just the relative portion to the
        :class:`~oyProjectManager.core.models.Repository`\ .\ 
        :attr:`~oyProjectManager.core.models.Repository.server_path`.
        """
        return os.path.join(
            self.project.path,
            self._output_path
        ).replace("\\", "/")

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
            raise TypeError("Version.base_name can not be None, please "
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
        
        # get the config
#        from oyProjectManager import config
#        conf = config.Config()
        from oyProjectManager import conf
        
        if take_name is None:
            take_name = conf.default_take_name
        
        if not isinstance(take_name, (str, unicode)):
            raise TypeError("Version.take_name should be an instance of "
                            "string or unicode")
        
        take_name = self._condition_name(take_name)
        
        if take_name == "":
            raise ValueError("Version.take_name is either given as an empty "
                             "string or it became empty after formatting")

        return take_name

    def latest_version(self):
        """returns the Version instance with the highest version number in this
        series
        
        :returns: :class:`~oyProjectManager.core.models.Version` instance
        """
        #            .filter(Version.base_name == self.base_name)\
        return db.session\
            .query(Version)\
            .filter(Version.type==self.type)\
            .filter(Version.version_of == self.version_of)\
            .filter(Version.take_name == self.take_name)\
            .order_by(Version.version_number.desc())\
            .first()
    
    @property
    def max_version(self):
        """returns the maximum version number for this Version from the
        database.
        
        :returns: int
        """
        last_version = self.latest_version()
        
        if last_version:
            max_version = last_version.version_number
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
        if self not in db.session:
            db.session.add(self)
        db.session.commit()

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
            raise TypeError("Version.created_by can not be None, please "
                            "set it to oyProjectManager.core.models.User "
                            "instance")

        if not isinstance(created_by, User):
            raise TypeError("Version.created_by should be an instance of"
                            "oyProjectManager.core.models.User")

        return created_by
    
    @validates("references")
    def _validate_references(self, key, reference):
        """validates the given reference value
        """
        
        if reference is self:
            raise ValueError("Version.references can not have a reference to "
                             "itself")
       
        # check circular dependency
        _check_circular_dependency(reference, self)
        
        return reference
    
    @property
    def project(self):
        """The :class:`~oyProjectManager.core.models.Project` instance that
        this Version belongs to
        """
        
        return self.version_of.project
    
    def is_latest_version(self):
        """returns True if this is the latest Version False otherwise
        """
        return self.max_version == self.version_number
    
    @property
    def dependency_update_list(self):
        """Calculates a list of :class:`~oyProjectManager.core.models.Version`
        instances, which are referenced by this Version and has a newer
        version.
        
        Also checks the references in the referenced Version and appends the
        resultant list to the current dependency_update_list. Resulting a much
        deeper update info.
        
        :return: list of :class:`~oyProjectManager.core.models.Version`
            instances.
        """
        
        # loop through the referenced Version instances and check if they have
        # newer Versions
        
        update_list = []
        
        for ref in self.references:
            if not ref.is_latest_version():
                update_list.append(ref)
            # also loop in their references
            update_list.extend(ref.dependency_update_list)
        
        return update_list

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
    
    In oyProjectManager, generally you don't need to create VersionType
    instances by hand. Instead, add all the version types you need to your
    config.py file and the :class:`~oyProjectManager.core.models.Project`
    instance will create all the necessary VersionTypes from this config.py
    configuration file. For more information about the the config.py please see
    the documentation of config.py.
    
    For previously created projects, where a new type is needed to be added you
    can still create a new VersionType instance and save it to the Projects'
    database.
    
    
    :param str name: The name of this template. The name is not formatted in
      anyway. It can not be skipped or it can not be None or it can not be an
      empty string. The name attribute should be unique. Be careful that even
      specifying a non unique name VersionType instance will not raise an error
      until :meth:`~oyProjectManager.core.models.VersionType.save` is called.
    
    :param str code: The code is a shorthand form of the name. For example,
      if the name is "Animation" than the code can be "ANIM" or "Anim" or
      "anim". Because the code is generally used in filename, path or
      output_path templates it is going to be a part of the filename or path,
      so be careful about what you give as a code. The code attribute should be
      unique. Be careful that even specifying a non unique code VersionType
      instance will not raise an error until
      :meth:`~oyProjectManager.core.models.VersionType.save` is called. For
      formatting, these rules are current:
        
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
          v{{'%03d'|format(version.version_number)}}_\\
          {{version.created_by.initials}}
      
      Which will render something like that::
        
        Car_Main_Model_v001_oy
      
      Now all the versions for the same asset will have a consistent name.
      
      When the filename argument is skipped or is an empty string is given a
      TypeError will be raised to prevent creation of files with no names.
    
    :param str path: The path template. It is a single line Jinja2 template
      showing the absolute path of this
      :class:`~oyProjectManager.core.models.Version` instance. Look for the
      above `table`_ for possible variables those can be used in the template
      code.
        
      For an example the following is a nice template for a Shot version::
      
        {{project.full_path}}/Sequences/{{sequence.code}}/Shots/\\
          {{version.base_name}}/{{type.code}}
      
      This will place a Shot Version whose base_name is SH001 and let say that
      the type is Animation (where the code is ANIM) to a path like::
      
        M:/JOBs/PROJ1/Sequences/SEQ1/Shots/SH001/ANIM
      
      All the animation files realted to this shot will be saved inside that
      folder.
    
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
        
        M:/JOBs/PROJ1/Sequences/SEQ1/Shots/SH001/ANIM/Outputs
    
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
      
      The given value should be a list of environment names, be careful about
      not to pass just a string for the environments list, python will convert
      the string to a list by putting all the letters in separate elements in
      the list. And probably this is not something one wants.
    
    :type environments: list of strings
    
    :param type_for: An enum value specifying what this VersionType instance is
      for, is it for an "Asset" or for an "Shot". The two acceptable values are
      "Asset" or "Shot". Any other value will raise an IntegrityError. It can
      not be skipped.
    
    """
#    :param project: A VersionType instance can not be created without defining
#      which :class:`~oyProjectManager.core.models.Project` it belongs to. So it
#      can not be None or anything other than a
#      :class:`oyProjectManager.core.models.Project` instance.
#    
#    :type project: :class:`~oyProjectManager.core.models.Project`

    __tablename__ = "VersionTypes"
    __table_args__  = (
        {"extend_existing":True}
    )
    
    id = Column(Integer, primary_key=True)

#    project_id = Column(Integer, ForeignKey("Projects.id"))
#    _project = relationship("Project")

    name = Column(String, unique=True)
    code = Column(String, unique=True)

    filename = Column(
        String,
        doc="""The filename template for this type of version instances.
        
        You can freely change the filename template attribute after creating
        :class:`~oyProjectManager.core.models.Version`\ s of this type. Any
        :class:`~oyProjectManager.core.models.Version` which is created prior
        to this change will not be effected. But be careful about the older and
        newer :class:`~oyProjectManager.core.models.Version`\ s of
        the same :class:`~oyProjectManager.core.models.Asset` or
        :class:`~oyProjectManager.core.models.Shot` may placed to different
        folders according to your new template.
        
        The template **should not** include a dot (".") sign before the
        extension, it is handled by the
        :class:`~oyProjectManager.core.models.Version` instance.
        """
    )

    path = Column(
        String,
        doc="""The path template for this Type of Version instance.
        
        You can freely change the path template attribute after creating
        :class:`~oyProjectManager.core.models.Version`\ s of this type. Any
        :class:`~oyProjectManager.core.models.Version` which is created prior
        to this change will not be effected. But be careful about the older and
        newer :class:`~oyProjectManager.core.models.Version`\ s of
        the same :class:`~oyProjectManager.core.models.Asset` or
        :class:`~oyProjectManager.core.models.Shot` may placed to different
        folders according to your new template.
        
        The path template should be an relative one to the
        :attr:`~oyProjectManager.core.models.Repository.server_path`, so don't
        forget to place ``{{project.code}}`` at the beginning of your template
        if you are storing all your asset and shots inside the project
        directory.
        
        If you want to store your assets in one place and use them in several
        projects, you can do it by starting the ``path`` of the VersionType
        with something like that::
            
            "Assets/{{version.base_name}}/{{type.code}}"
        
        and if your repository path is "/mnt/M/JOBs" then your assets will be
        stored in::
            
            "/mnt/M/JOBs/Assets"
        
        """
    )

    output_path = Column(
        String,
        doc="""The output path template for this Type of Version instances.
        
        To place your output path right beside the original version file you
        can set the ``output_path`` to::
            
            "{{version.path}}/Outputs/{{version.take_name}}"
        """
    )

    extra_folders = Column(
        String,
        doc="""A string containing the extra folder names those needs to be
        created"""
    )

    environments = association_proxy(
        "version_type_environments",
        "environment_name"
    )
    
    _type_for = Column(
        Enum("Asset", "Shot"),
        doc="""A enum value showing if this version type is valid for Assets or
        Shots.
        """
    )

    def __init__(self,
                 name,
                 code,
                 path,
                 filename,
                 output_path,
                 environments,
                 type_for,
                 extra_folders=None
    ):
        self.name = name
        self.code = code
        self.filename = filename
        self.path = path
        self.output_path = output_path
        self.environments = environments
        self.extra_folders = extra_folders
        self._type_for = type_for
    
    def __eq__(self, other):
        """equality operator
        """
        return isinstance(other, VersionType) and self.name == other.name
    
    def __ne__(self, other):
        """inequality operator
        """
        return not self.__eq__(other)
    
    @validates("name")
    def _validate_name(self, key, name):
        """validates the given name value
        """

        if name is None:
            raise TypeError("VersionType.name can not be None, please "
                            "supply a string or unicode instance")

        if not isinstance(name, (str, unicode)):
            raise TypeError("VersionType.name should be an instance of "
                            "string or unicode")

        return name

    @validates("code")
    def _validate_code(self, key, code):
        """validates the given code value
        """

        if code is None:
            raise TypeError("VersionType.code can not be None, please "
                            "specify a proper string value")

        if not isinstance(code, (str, unicode)):
            raise TypeError("VersionType.code should be an instance of "
                            "string or unicode, please supply one")
        return code

    @validates("extra_folders")
    def _validate_extra_folders(self, key, extra_folders):
        """validates the given extra_folders value
        """
        if extra_folders is None:
            extra_folders = ""
        
        if not isinstance(extra_folders, (str, unicode)):
            raise TypeError("VersionType.extra_folders should be a string or "
                            "unicode value showing the extra folders those "
                            "needs to be created with the Version of this "
                            "type.")

        return extra_folders

    @validates("filename")
    def _validate_filename(self, key, filename):
        """validates the given filename
        """

        if filename is None:
            raise TypeError("VersionType.filename can not be None, please "
                            "specify a valid filename template string by "
                            "using Jinja2 template syntax")

        if not isinstance(filename, (str, unicode)):
            raise TypeError("VersionType.filename should be an instance of"
                            "string or unicode")

        if filename=="":
            raise ValueError("VersionType.filename can not be an empty "
                             "string, it should be a string containing a "
                             "Jinja2 template code showing the file naming "
                             "convention of Versions of this type.")

        return filename

    @validates("path")
    def _validate_path(self, key, path):
        """validates the given path
        """

        if path is None:
            raise TypeError("VersionType.path can not be None, please "
                            "specify a valid path template string by using "
                            "Jinja2 template syntax")

        if not isinstance(path, (str, unicode)):
            raise TypeError("VersionType.path should be an instance of string "
                            "or unicode")

        if path=="":
            raise ValueError("VersionType.path can not be an empty "
                             "string, it should be a string containing a "
                             "Jinja2 template code showing the file naming "
                             "convention of Versions of this type.")

        return path

    @validates("output_path")
    def _validate_output_path(self, key, output_path):
        """Validates the given output_path value
        """
        if output_path is None:
            raise TypeError("VersionType.output_path can not be None")

        if not isinstance(output_path, (str, unicode)):
            raise TypeError("VersionType.output_path should be an instance "
                            "of string or unicode, not %s" % type(output_path))

        if output_path == "":
            raise ValueError("VersionType.output_path can not be an empty "
                             "string")

        return output_path

#    @classmethod
#    def _check_project(cls, project):
#        """A convenience function which checks the given project argument value
#        
#        It is a ``classmethod``, so can be called both in ``__new__`` and other
#        methods like ``_validate_project``.
#        
#        Checks the given project for a couple of conditions, like being None or
#        not being an Project instance etc.
#        """
#
#        if project is None:
#            raise TypeError("VersionType.project can not be None")
#
#        if not isinstance(project, Project):
#            raise TypeError("The project should be and instance of "
#                            "oyProjectManager.core.models.Project")
#
#        return project

#    @synonym_for("_project")
#    @property
#    def project(self):
#        """A read-only attribute to return the related Project of this Sequence
#        instance
#        """
#
#        return self._project

    def save(self):
        """Saves the current VersionType to the database
        """
        if self not in db.session:
            db.session.add(self)
        db.session.commit()

    @validates("_type_for")
    def _validate_type_for(self, key, type_for):
        """Validates the given type_for value
        """

        if type_for is None:
            raise TypeError("VersionType.type_for can not be None, it should "
                            "be a string or unicode value")

        if not isinstance(type_for, (str, unicode)):
            raise TypeError("VersionType.type_for should be an instance of "
                            "string or unicode, not %s" % type(type_for))

        return type_for

    @synonym_for("_type_for")
    @property
    def type_for(self):
        """An enum attribute holds what is this VersionType created for, a Shot
        or an Asset.
        """

        return self._type_for

class VersionTypeEnvironments(Base):
    """An association object for VersionType.environments
    """

    __tablename__ = "VersionType_Environments"
    __table_args__  = (
        {"extend_existing":True}
    )
    
    versionType_id = Column(Integer, ForeignKey("VersionTypes.id"),
                            primary_key=True)
    environment_name = Column(
        String,
        primary_key=True,
        doc="""The name of the environment which the VersionType instance is
        valid for
        """
    )

    version_type = relationship(
        "VersionType",
        backref=backref(
            "version_type_environments",
            cascade="all, delete-orphan"
        )
    )

    def __init__(self, environment_name):
        self.environment_name = environment_name

    @validates("environment_name")
    def _validate_environment_name(self, key, environment_name):
        """validates the given environment_name value
        """

        if environment_name is None or\
           not isinstance(environment_name, (str, unicode)):
            raise TypeError("VersionType.environments should be a list of "
                            "strings containing the environment names")

        return environment_name

class User(Base):
    """Manages users
    
    The user class is the representation of the users in the system.
    
    Because there is no central database in the current implementation of
    oyProjectManager, a user is stored in the
    :class:`~oyProjectManager.core.models.Project`\ 's database only if the
    user has created some data. So creating a user and querying the
    :class:`~oyProjectManager.core.models.Project`\ s that this user has worked
    has no direct way.
    
    :param name: The name of the user.
    
    :param initials: Initials of the user. If skipped the initials will be
      extracted from the :attr:`~oyProjectManager.core.models.User.name`
      attribute.
    
    :param email: The email address of the user.
    """

    __tablename__ = "Users"
    __table_args__  = (
        {"extend_existing":True}
    )

    id = Column(Integer, primary_key=True)

    name = Column(String)
    initials = Column(String)
    email = Column(String)
    
    active = Column(Boolean, default=True)
    
    versions_created = relationship("Version")
    
    def __init__(self, name, initials=None, email=None, active=True):
        self.name = name
        self.initials = initials
        self.email = email
        self.active = True
    
    def __eq__(self, other):
        """the equality operator
        """
        return isinstance(other, User) and self.name == other.name

class EnvironmentBase(object):
    """Connects the environment (the host program) to the oyProjectManager.
    
    In oyProjectManager, an Environment is a host application like Maya, Nuke,
    Houdini etc.
    
    Generally a GUI for the end user is given an environment which helps
    the QtGui to be able to open, save, import or export a Version without
    knowing the details of the environment.
    
    .. note::
      For now the :class:`~oyProjectManager.core.models.EnvironmentBase`
      inherits from the Python object class. There were no benefit to inherit
      it from the ``DeclarativeBase``.
    
    To create a new environment for you own program, just instantiate this
    class and override the methods as necessary. And call the UI with by
    giving an environment instance to it, so the interface can call the correct
    methods as needed.
    
    Here is an example how to create an environment for a program and use the
    GUI::
      
        from oyProjectManager.core import EnvironmentBase
        
        class MyProgram(EnvironmentBase):
            \"""This is a class which will be used by the UI
            \"""
            
            def open():
                \"""uses the programs own Python API to open a version of an
                asset
                \"""
                
                # do anything that needs to be done before opening the file
                my_programs_own_python_api.open(filepath=self.version.full_path)
            
            def save():
                \"""uses the programs own Python API to save the current file
                as a new version.
                \"""
                
                # do anything that needs to be done before saving the file
                my_programs_own_python_api.save(filepath=self.version.full_path)
                
                # do anything that needs to be done after saving the file
    
    and that is it.
    
    The environment class by default has a property called ``version``.
    Holding the current open version. It is None for a new scene and a
    :class:`~oyProjectManager.core.models.Version` instance in any other case.
    
    :param name: To initialize the class the name of the environment should be
        given in the name argument. It can not be skipped or None or an empty
        string.
    
    
    """
    
    #    __tablename__ = "Environments"
    #    id = Column(Integer, primary_key=True)
    
    name = "EnvironmentBase"
    
#    def __init__(self, name=""):
#        self._name = name
#        self._extensions = []
#        self._version = None

    def __str__(self):
        """the string representation of the environment
        """
        return self._name
    
    @property
    def version(self):
        """returns the current Version instance which is open in the
        environment
        """
        return self._version
    
#    @version.setter
#    def version(self, version):
#        """sets the version of the environment
#        """
#        self._version = version

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

    def save_as(self, version):
        """The save as action of this environment. It should save the current
        scene or file to the given version.full_path
        """
        raise NotImplemented

    def export_as(self, version):
        """Exports the contents of the open document as the given version.
        
        :param version: A :class:`~oyProjectManager.core.models.Version`
            instance holding the desired version.
        """
        raise NotImplemented

    def open_(self, version, force=False):
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
    
    def trim_server_path(self, path_in):
        """Trims the server_path value from the given path_in
        
        :param path_in: The path that wanted to be trimmed
        :return: str
        """
        repo = Repository()
        
        server_path = repo.server_path
        if path_in.startswith(server_path):
            path_in = path_in[len(os.path.normpath(server_path))+1:]
        
        return path_in
    
    def get_versions_from_path(self, path):
        """Finds Version instances from the given path value.
        
        Finds and returns the :class:`~oyProjectManager.core.models.Version`
        instances from the given path value.
        
        Returns an empth list if it can't find any matching.
        
        This method is different than
        :meth:`~oyProjectManager.core.models.EnvironmentBase.get_version_from_full_path`
        because it returns a list of
        :class:`~oyProjectManager.core.models.Version` instances which are
        residing in that path. The list is ordered by the ``id``\ s of the
        instances.
        
        :param path: A path which has possible
            :class:`~oyProjectManager.core.models.Version` instances.
        
        :return: A list of :class:`~oyProjectManager.core.models.Version`
            instances.
        """

        # get the path by trimming the server_path
        path = self.trim_server_path(path)
        
        # get all the version instance at that path
        return db.query(Version)\
            .filter(Version.path.startswith(path))\
            .order_by(Version.id.desc())\
            .all()
    
    def get_version_from_full_path(self, full_path):
        """Finds the Version instance from the given full_path value.
        
        Finds and returns a :class:`~oyProjectManager.core.models.Version`
        instance from the given full_path value.
        
        Returns None if it can't find any matching.
        
        :param full_path: The full_path of the desired
            :class:`~oyProjectManager.core.models.Version` instance.
        
        :return: :class:`~oyProjectManager.core.models.Version`
        """

        path, filename = os.path.split(full_path)
        path = self.trim_server_path(path)
        
        # try to get a version with that info
        version = db.query(Version)\
            .filter(Version.path==path)\
            .filter(Version.filename==filename)\
            .first()
        
        return version
    
    def get_current_version(self):
        """Returns the current Version instance from the environment.
        
        :returns: :class:`~oyProjectManager.core.models.Version` instance or
            None
        """
        raise NotImplemented

    def get_last_version(self):
        """Returns the last opened Version instance from the environment.
        
        * It first looks at the current open file full path and tries to match
          it with a Version instance.
        * Then searches for the recent files list.
        * Still not able to find any Version instances, will return the version
          instance with the highest id which has the current workspace path in
          its path
        * Still not able to find any Version instances returns None
        
        :returns: :class:`~oyProjectManager.core.models.Version` instance or
            None
        """
        raise NotImplemented
    
    def getProject(self):
        """returns the current project from environment
        """
        raise NotImplemented
    
    def set_project(self, version):
        """Sets the project to the given versions project.
        
        Because the projects are related to the created Version instances
        instead of passing a Project instance it is much meaningful to pass a
        Version instance which will have a reference to the Project instance
        already.
        
        :param project: A :class:`~oyProjectManager.core.models.Version`.
        """
        raise NotImplemented
    
#    def setOutputFileName(self):
#    def set_output_path(self):
#        """sets the output file names
#        """
#        raise NotImplemented

#    def append_to_recent_files(self, path):
#        """appends the given path to the recent files list
#        """
#        raise NotImplemented

    def check_referenced_versions(self):
        """Checks the referenced versions
        
        returns list of asset objects
        """
        raise NotImplemented

    def get_referenced_versions(self):
        """Returns the :class:`~oyProjectManager.core.models.Version` instances
        which are referenced in to the current scene
        
        :returns: list of :class:`~oyProjectManager.core.models.Version`
            instances
        """
        raise NotImplemented

#    def update_versions(self, assetTupleList):
#        """updates the assets to the latest versions
#        """
#        raise NotImplemented

    def get_frame_range(self):
        """Returns the frame range from the environment
        
        :returns: a tuple of integers containing the start and end frame
            numbers
        """
        raise NotImplemented

    def set_frame_range(self, start_frame=1, end_frame=100,
                        adjust_frame_range=False):
        """Sets the frame range in the environment to the given start and end
        frames
        """
        raise NotImplemented

    def get_fps(self):
        """Returns the frame rate of this current environment
        """
        raise NotImplemented

    def set_fps(self, fps=25):
        """Sets the frame rate of the environment. The default value is 25.
        """
        raise NotImplemented

    @property
    def extensions(self):
        """Returns the valid native extensions for this environment.
        
        :returns: a list of strings
        """
        return self._extensions

    @extensions.setter
    def extensions(self, extensions):
        """Sets the valid native extensions of this environment.
        
        :param extensions: A list of strings holding the extensions. Ex:
            ["ma", "mb"] for Maya
        """
        self._extensions = extensions

    def has_extension(self, filename):
        """Returns True if the given filenames extension is in the extensions
        list false otherwise.
        
        accepts:
        * a full path with extension or not
        * a file name with extension or not
        * an extension with a dot on the start or not
        
        :param filename: A string containing the filename
        """

        if fileName is None:
            return False

        if fileName.split('.')[-1].lower() in self._extensions:
            return True

        return False

    def load_referenced_versions(self):
        """loads all the references
        """
        raise NotImplemented

    def replace_version(self, source_version, target_version):
        """Replaces the source_version with the target_version
        
        :param source_version: A :class:`~oyProjectManager.core.models.Version`
            instance holding the version to be replaced
        
        :param target_version: A :class:`~oyProjectManager.core.models.Version`
            instance holding the new version replacing the source one
        """
        raise NotImplemented

# secondary tables
Version_References = Table(
    "Version_References", Base.metadata,
    Column("referencer_id", Integer, ForeignKey("Versions.id"), primary_key=True),
    Column("reference_id", Integer, ForeignKey("Versions.id"), primary_key=True),
    extend_existing=True
)

def _check_circular_dependency(version, check_for_version):
    """checks the circular dependency in version if it has check_for_version in
    its depends list
    """
    
    for reference in version.references:
        if reference is check_for_version:
            raise CircularDependencyError(
                "version %s can not reference %s, this creates a circular "
                "dependency" % (version, check_for_version)
            )
        else:
            _check_circular_dependency(reference, check_for_version)
