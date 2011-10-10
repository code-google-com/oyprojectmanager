# -*- coding: utf-8 -*-

import os
import shutil
import glob
import re

from beaker import cache
import jinja2

from xml.dom import minidom
from sqlalchemy import Column, String, Integer, PickleType, ForeignKey, orm
from sqlalchemy.orm import relationship
from sqlalchemy.orm.mapper import validates

from oyProjectManager import utils, conf
from oyProjectManager import db
from oyProjectManager.db.declarative import Base
from oyProjectManager.models import asset, repository


# create a cache with the CacheManager
bCache = cache.CacheManager()

# disable beaker DEBUG messages
import logging

logger = logging.getLogger('beaker.container')
logger.setLevel(logging.WARNING)

logger = logging.getLogger(__name__)
logger.info("inside oyProjectManager.models.project")
logger.setLevel(logging.DEBUG)

class DefaultSettingsParser(object):
    """A parser for the default settings for the sequence.
    
    Parses the given settings xml and fills the attributes of the given
    :class:`~oyProjectManager.models.project.Sequence` class.
    
    :param sequence: a :class:`~oyProjectManager.models.project.Sequence`
      instance. The default is None and this causes a ValueError to be raised.
    
    :type sequence: :class:`~oyProjectManager.models.project.Sequence`
    
    :param str content: the settings content as a string. Default is None
      and this causes a ValueError to be raised.
    
    The version 1 specification of the default settings consists of the
    following nodes:
      
       * root: The root node
         
          * sequenceData node:
            
            Attributes:
              
               * shotPrefix: default is "SH", it is the prefix to be added
                 before the shot number
              
               * shotPadding: default is 3, it is the number of padding going
                 to be applied to find the string representation of the shot
                 number. If the shot number is 5 and the shotPadding is set to
                 3 and the shotPrefix is "SH" then the final shot name will be
                 SH005
               
               * revPrefix: default is "r", it is the revision variable prefix
              
               * revPadding: default is 2, it is the revision number padding,
                 for revision 3 the default values will output a string of
                 "r03" for the revision string variable
              
               * verPrefix: default is "v", it is the version variable prefix
              
               * verPadding: default is 3, it is the version number padding for
                 default values a file version of 14 will output a string of
                 "v014" for the version string variable.
              
               * timeUnit: default is pal, it is the time unit for the project,
                 possible values are "pal, film, ntsc, game". This variable
                 follows the Maya's time unit format.
            
            Child elements:
              
               * structure: it is the child of sequenceData. Structure element
                 holds the project structure information. Every project will be
                 created by using this project structure.
                 
                 Child elements:
                   
                    * shotDependent: show the shot dependent folders. A shot
                      dependent folder will contain shot folders. For example
                      a folder called ANIMATION could be defined under
                      shotDependent folders, then oyProjectManager will
                      automatically place folders for every shot of the project.
                      So if the project has three shots with shot numbers 10,
                      14, 21 then the structure of the ANIMATION folder will be
                      like:
                        
                        ANIMATION/
                        ANIMATION/SH010/
                        ANIMATION/SH013/
                        ANIMATION/SH021/
                   
                    * shotIndependent: show the shot independent folder, or the
                      rest of the project structure. So any other folder which
                      doesn't have a direct relation with shots can be placed
                      here. For example you can place folders for MODELS, RIGS,
                      OUTGOING_FILES etc.
                   
               * assetTypes: This element contains information about asset
                 types.
                 
                 Attributes: None
                 
                 Child elements:
                   
                    * type: this is an asset type
                      
                      Attributes:
                        
                         * name: the name of the type
                         
                         * path: the project relative path for the asset files
                           in this type.
                        
                         * shotDependent: it is a boolean value that specifies
                           if this asset type is shot dependent.
                        
                         * environments: this attribute lists the environment
                           names where this asset type is valid through. It
                           should list the environment names in a comma
                           separated value (CSV) format
                        
                         * output_path: shows the output folder of this asset
                           type. For example you can set the render output
                           folder by setting the output folder of the RENDER
                           asset type to a specific folder relative to the
                           project root.
              
              
               * shotData: This is the element that shows the current projects
                 shot information.
                 
                 Child Elements:
                   
                    * shot: The shot it self
                      
                      Attributes:
                        
                         * name: this is the name of the shot, it just shows
                           the number and alternate letter part of the shot
                           name, so for a shot named "SH001A" the name
                           attribute is "1A"
                        
                         * start: this is the global start frame of the shot
                        
                         * end: this is the global end frame of the shot
                        
                      Child Elements:
                        
                         * description: This is the text element that has the
                           description of the current shot. You can place any
                           amount of text inside this text element.
    """


    def __init__(self):
        pass


class Project(Base):
    """Manages project related data.
    
    A Project is simply a holder of Sequences.
    
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
    
    Creating a :class:`oyProjectManager.models.project.Project` instance is not
    enough to physically create the project folder. To make it happen the
    :meth:`~oyProjectManager.models.project.Project.create` should be called to
    finish the creation process.
    
    A Project can not be created without a name or with a name which is None or
    with an invalid name. For example, a project with name "'^+'^" can not be
    created because the name will become an empty string after the name
    validation process.
    
    Projects have a file called ".settings.xml" in their root. This settings
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
    
    def __new__(cls, *args):
        """the overridden __new__ method to manage the creation of a Project
        instance
        
        If the Project is created before than calling Project() for the second
        time will return the project from the database.
        """
        
        # check the name argument
        if len(args):
            
            print "there is an arg"
            
            name = args[0]
            
            repo = repository.Repository()
            path = repo.server_path
            fullPath = os.path.join(path, name)
            
            metadata_db_name = conf.DATABASE_FILE_NAME
            metadata_full_path = os.path.join(
                fullPath,
                metadata_db_name
            ).replace("\\", "/")
            
            # now get the instance from the db
            if os.path.exists(metadata_full_path):
                session = db.setup(metadata_full_path)
                
                proj_obj = session.query(Project).filter_by(name=name).first()
                
                if proj_obj is not None:
                    # return the database instance
                    print "found the project in the database"
                    print "returning the object from the database"
                    return proj_obj
            else:
                print "project doesn't exists"
        
        # just create it normally
        print "returning a normal Project instance"
        return super(Project, cls).__new__(cls, *args)
        
    
    
    def __init__(self, name=None):
        
        print "inside __init__"
        
        self.path = ""
        self.fullPath = ""
        
        self._repository = repository.Repository()
        self.session = None
        
        self.name = name
        
        self.metadata_db_name = conf.DATABASE_FILE_NAME
        self.metadata_full_path = os.path.join(
            self.fullPath,
            self.metadata_db_name
        ).replace("\\", "/")
        
        self._sequenceList = []
        
        self._exists = None
        
#        self.read_settings()
    
    
    @orm.reconstructor
    def __init_on_load__(self):
        """init when loaded from the db
        """
        
        self._repository = repository.Repository()
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
    
    
    def read_settings(self):
        """reads the settings from the database
        """
        
        if os.path.exists(self.metadata_full_path):
            print "project exists at %s" % self.fullPath
            
            if self.session is None:
                print "session is None creating one"
                self.session = db.setup(self.metadata_full_path)
            
            # get the project from the db
            proj_DB = self.session.query(Project).first()
            
            temp_session = self.session
            
            print "hex(id(self))", hex(id(self))
            self.__dict__ = proj_DB.__dict__
            print "hex(id(self))", hex(id(self))
            
            if self not in self.session:
                print "project is not attached to a session"
            
            self.session = temp_session
    
    
    def update_paths(self, name_in):
        self.path = self._repository.server_path
        self.fullPath = os.path.join(self.path, name_in)
    
    
    @validates("name")
    def _validate_name(self, key, name_in):
        """validates the given name_in value
        """

        if name_in is None:
            raise ValueError("The name can not be None")

        if name_in is "":
            raise ValueError("The name can not be an empty string")
        
        # strip the name
        name_in = name_in.strip()

        # convert all the "-" signs to "_"
        name_in = name_in.replace("-", "_")
        
        # replace camel case letters
        name_in = re.sub(r"(.+?[a-z]+)([A-Z])", r"\1_\2", name_in)

        # remove unnecessary characters from the string
        name_in = re.sub("([^a-zA-Z0-9\s_]+)", r"", name_in)
        
        # remove all the characters from the beginning which are not alphabetic
        name_in = re.sub("(^[^a-zA-Z]+)", r"", name_in)

        # substitute all spaces with "_" characters
        name_in = re.sub("([\s])+", "_", name_in)

        # convert it to upper case
        name_in = name_in.upper()

        # check if the name became empty string after validation
        if name_in is "":
            raise ValueError("The name is not valid after validation")

        self.update_paths(name_in)
        
        return name_in


    def create(self):
        """Creates the project directory in the repository.
        """
        
        # check if the folder already exists
        utils.mkdir(self.fullPath)
        self._exists = True
        
        # create the database
        if self.session is None:
            self.session = db.setup(self.metadata_full_path)
        
        self.session.add(self)
        self.session.commit()


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
        
#        self.session.add(newSequence)
#        self.commit()
        
        return newSequence


    @bCache.cache(expire=60)
    def sequenceNames(self):
        """returns the sequence names of that project
        """
        self.updateSequenceList()
        return self._sequenceList


#    @bCache.cache(expire=60)
#    def sequences(self):
#        """Returns the sequences of the project as sequence objects.
#        
#        It utilizes the caching system.
#        """
#
#        self.updateSequenceList()
#        sequences = [] * 0
#
#        for sequenceName in self._sequenceList:
#            sequences.append(Sequence(self, sequenceName))
#
#        return sequences


    def updateSequenceList(self):
        """updates the sequenceList variable
        """

        # filter other folders like .DS_Store
        try:
            for folder in os.listdir(self.fullPath):
                filtered_folder_name = re.sub(
                    r".*?(^[^A-Z_]+)([A-Z0-9_]+)",
                    r"\2",
                    folder
                )
                if filtered_folder_name == folder:
                    self._sequenceList.append(folder)

            self._sequenceList.sort()
        except OSError:
            # the path doesn't exist
            pass


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
    :class:`~oyProjectManager.models.project.Shot`\ s.
    
    The class should be initialized with a
    :class:`~oyProjectManager.models.project.Project` instance and a
    sequenceName.
    
    Two sequences are considered the same if their name and their project
    names are matching.
    
    .. versionadded:: 0.1.2
        SQLite3 Database:
        
        To hold the information about all the assets created, there is a
        ".metadata.db" file in the sequence root. This SQLite3 database has
        information about all the assets created within the sequence. So anytime
        a new asset is created the asset itself informs the Sequence about its
        existence and then all the related information is saved to the SQLite3
        database.
        
        To support previous projects, which doesn't have this technology,
        whenever a :class:`~oyProjectManager.models.project.Sequence` is created
        the it creates this SQLite3 database and fills it with the data that it
        can retrieve with old methods (ex: Sequence.getAllAssets).
        
        For the migrated sequences, the old ".settings.xml*" files will be
        removed from the sequence root folder.
    
    :param project: The owner
      :class:`~oyProjectManager.models.project.Project`. A sequence can not be
      created without a proper
      :class:`~oyProjectManager.models.project.Project`. If the
      :class:`~oyProjectManager.models.project.Project` instance is not created
      yet then a RuntimeError will be raised while creating a
      :class:`~oyProjectManager.models.project.Sequence` instance.
    
    :type project: :class:`~oyProjectManager.models.project.Project`
    
    :param str name: The name of the sequence. It is heavily formatted. Follows
      the same naming rules with the
      :class:`~oyProjectManager.models.project.Project`.
    """
    
    __tablename__ = "Sequences"
    id = Column(Integer, primary_key=True)
    name = Column(String(256), unique=True)
    
    project_id = Column(Integer, ForeignKey("Projects.id"))
    project = relationship("Project")
    
    shotPrefix = Column(String(16), default=conf.SHOT_PREFIX)
    shotPadding = Column(Integer, default=conf.SHOT_PADDING)
    
    revPrefix = Column(String(16), default=conf.REV_PREFIX)
    revPadding = Column(Integer, default=conf.REV_PADDING)
    
    verPrefix = Column(String(16), default=conf.VER_PREFIX)
    verPadding = Column(Integer, default=conf.VER_PADDING)
    
    timeUnit = Column(String(32), default=conf.TIME_UNIT)
    
    structure_id = Column(Integer, ForeignKey("Structures.id"))
    structure = relationship("Structure")
    
    
    def __init__(self, project, name):
        
        if not project.exists:
            raise RuntimeError(
                "the given project should exist in the system, please call "
                "Project.create() before passing it to a new Sequence instance"
            )
        
        self.project = project
        logging.debug("id(project.session): %s" % id(project.session))
        
        self.session = self.project.session
        logging.debug("id(sequence.session): %s" % id(self.session))
        
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
    
        
        
#        self._settingsFile = ".settings.xml"
#        self._settings_file_path = self._fullPath
#        self._settings_file_full_path = os.path.join(
#            self._settings_file_path,
#            self._settingsFile
#        ).replace("\\", "/")
        
#        self._settingsFileExists = False
#        self._settings_dirty = False
        
#        self.structure = Structure()
        self.structure = None
        self._assetTypes = []
        self._shotList = [] # should be a string
        self._shots = [] # the new shot objects
        
        #self._extensionsToIgnore = [] * 0
#        self._no_sub_name_field = False # to support the old types of projects
        
#        self._environment = None # the working environment
        
        self._exists = False
        
        # TODO: conversion from old sequence type to new sequence type with db
        #       try to read the database and if it doesn't exists convert the
        #       old
        #       project to a new one
        
        self.readSettings()
    
    
    @orm.reconstructor
    def __init_on_load__(self):
        """
        """
        
        self._path = self.project.fullPath
        self._fullPath = os.path.join(self._path, self.name).replace("\\", "/")


    def readSettings(self):
        """reads the settings either from the database for new type Sequences
        or from the .settings.xml file for older type Sequences
        """
        
        seq_db = self.session.query(Sequence).filter_by(name=self.name).first()
        
        if seq_db is not None:
            
            logging.debug("getting the Sequence from the database")
            # copy the data
            self.__dict__ = seq_db.__dict__
            self._exists = True
            
        else:
            logging.debug("the sequence is not created yet")
            logging.debug("creating the structure for the sequence")
            
            if self.structure is None:
                self.structure = Structure()
            
            self.structure.shotDependentFolders = conf.SHOT_DEPENDENT_FOLDERS
            self.structure.shotIndependentFolders =\
                conf.SHOT_INDEPENDENT_FOLDERS
            self._exists = False
        
        
        
#    def read_old_settings(self):
#        """parses the old XML settings file
#        """
#            
#            print "there is no db file"
#            # check if there is a settings file
#            if os.path.exists(self._settings_file_full_path):
#                print "there is a .settings.xml file"
#                self._settingsFileExists = True
#                self._exists = True
#                
#                #print (self._settings_file_full_path)
#                settingsAsXML = minidom.parse(self._settings_file_full_path)
#                
#                rootNode = settingsAsXML.childNodes[0]
#                
#                # -----------------------------------------------------
#                # get main nodes
#        
#                # remove databaseData if exists
#                doRemoveDatabaseDataNode = False
#                databaseDataNode = rootNode.getElementsByTagName('databaseData')
#        
#                if len(databaseDataNode) > 0:
#                    # there should be a databaseData node
#                    doRemoveDatabaseDataNode = True
#        
#                    # parse the databaseData nodes attributes as if it is a
#                    # sequenceDataNode
#                    self._parseSequenceDataNode(databaseDataNode[0])
#        
#                sequenceDataNode = rootNode.getElementsByTagName('sequenceData')[0]
#        
#                if not doRemoveDatabaseDataNode:
#                    self._parseSequenceDataNode(sequenceDataNode)
#        
#                    # -----------------------------------------------------
#                    # get sequence nodes
#                structureNode = sequenceDataNode.getElementsByTagName('structure')[0]
#                assetTypesNode = sequenceDataNode.getElementsByTagName('assetTypes')[0]
#                shotDataNodes = sequenceDataNode.getElementsByTagName('shotData')
#        
#                doConversionToShotData = False
#        
#                if not len(shotDataNodes):
#                    doConversionToShotData = True
#        
#                # parse all nodes
#                self._parseAssetTypesNode(assetTypesNode)
#                self._parseStructureNode(structureNode)
#        
#                if doConversionToShotData:
#                    # 
#                    # it should be an old type of settings file
#                    # convert it to the new shotData concept
#                    # 
#                    shotListNode = sequenceDataNode.getElementsByTagName('shotList')[0]
#                    #print "converting to shotData concept !!!"
#        
#                    # read the shot numbers from the shotList node and create appropriate
#                    # shot data nodes
#        
#                    # parse the shotListNode to get the shot list
#                    self._parseShotListNode(shotListNode)
#        
#                    self._convertShotListToShotData()
#        
#                    # update the settings file
#                    #self.saveSettings()
#                    self._settings_dirty = True
#                else:
#                    self._parseShotDataNode(shotDataNodes[0])
#        
#                if doRemoveDatabaseDataNode:
#                    # just save the settings over it self, it should be fine
#                    #self.saveSettings()
#                    self._settings_dirty = True

#        if self._settings_dirty:
#            print "re-saving settings"
#            self.saveSettings()

# check if there is a database file


    def _parseSequenceDataNode(self, sequenceDataNode ):
        """parses sequenceDataNode nodes attributes
        """

        #assert( isinstance( sequenceDataNode, minidom.Element) )

        self.shotPrefix = sequenceDataNode.getAttribute('shotPrefix')
        self.shotPadding = int(sequenceDataNode.getAttribute('shotPadding'))
        self.revPrefix = sequenceDataNode.getAttribute('revPrefix')
        self.revPadding = sequenceDataNode.getAttribute('revPadding')
        self.verPrefix = sequenceDataNode.getAttribute('verPrefix')
        self.verPadding = sequenceDataNode.getAttribute('verPadding')

        #if sequenceDataNode.hasAttribute('extensionsToIgnore'):
        #self._extensionsToIgnore = sequenceDataNode.getAttribute('extensionsToIgnore').split(',')
        
        if sequenceDataNode.hasAttribute('noSubNameField'):
            self._no_sub_name_field = bool(
                eval(sequenceDataNode.getAttribute('noSubNameField')))

        if sequenceDataNode.hasAttribute('timeUnit'):
            self.timeUnit = sequenceDataNode.getAttribute('timeUnit')


    def _parseStructureNode(self, structureNode):
        """parses structure node from the XML file
        """

        #assert( isinstance( structureNode, minidom.Element ) )

        # -----------------------------------------------------
        # get shot dependent/independent folders
        shotDependentFoldersNode = \
            structureNode.getElementsByTagName('shotDependent')[0]
        shotDependentFoldersList = \
            shotDependentFoldersNode.childNodes[0].wholeText.split('\n')

        shotIndependentFoldersNode = \
            structureNode.getElementsByTagName('shotIndependent')[0]
        shotIndependentFoldersList = shotIndependentFoldersNode.childNodes[
                                     0].wholeText.split('\n')

        # strip the elements and remove empty elements
        shotDependentFoldersList = [folder.strip() for folder in
                                    shotDependentFoldersList if
                                    folder.strip() != ""]
        shotIndependentFoldersList = [folder.strip() for folder in
                                      shotIndependentFoldersList if
                                      folder.strip() != ""]

        # fix path issues for windows
        osName = os.name

        if osName == 'nt':
            shotDependentFoldersList = \
            [utils.fixWindowsPath(path)
                for path in shotDependentFoldersList]
            
            shotIndependentFoldersList = \
                [utils.fixWindowsPath(path) \
                    for path in shotIndependentFoldersList]

        # set the structure
        self.structure.shotDependentFolders = shotDependentFoldersList
        self.structure.shotIndependentFolders = shotIndependentFoldersList

        try:
            # --------------------------------------------------------------------
            # THIS PART BELOW IS DEPRECATED REMOVE IT IN THE NEXT RELEASE
            # --------------------------------------------------------------------
            # read the output folders node
            outputFoldersNode =\
            structureNode.getElementsByTagName('outputFolders')[0]

            outputNodes = outputFoldersNode.getElementsByTagName('output')

            for outputNode in outputNodes:
                #assert(isinstance(outputNode, minidom.Element))
                name = outputNode.getAttribute('name')
                path = outputNode.getAttribute('path')

                # fix path issues for windows
                if osName == 'nt':
                    path = utils.fixWindowsPath(path)

                # instead add the output folder to the asset types
                # get the asset type by name and append the path to the
                # output folder of the found asset type
                aType = self.getAssetTypeWithName(name)
                try:
                    aType.output_path = path
                except AttributeError:
                    # it means there is no asset type with the given name
                    pass

            # do a saveSettings to save the settings in new format
            #self.saveSettings()
            self._settings_dirty = True

        except IndexError:
            # there is no output_folder in this project so don't parse it in
            # this way
            pass


    def _parseAssetTypesNode(self, assetTypesNode):
        """parses assetTypes node from the XML file
        """

        #assert( isinstance( assetTypesNode, minidom.Element) )

        # -----------------------------------------------------
        # read asset types
        self._assetTypes = [] * 0
        for node in assetTypesNode.getElementsByTagName('type'):
            #assert( isinstance( node, minidom.Element) )

            name = node.getAttribute('name')
            path = node.getAttribute('path')
            shotDependency = bool(int(node.getAttribute('shotDependent')))
            environments = node.getAttribute('environments').split(",")
            output_path = node.getAttribute("output_path")

            # fix path issues for windows
            if os.name == 'nt':
                path = utils.fixWindowsPath(path)

            self._assetTypes.append(
                asset.AssetType(name, path, shotDependency, environments,
                                output_path)
            )


    def _parseShotListNode(self, shotListNode):
        """parses shotList node from the XML file
        """

        #assert( isinstance( shotListNode, minidom.Element) )

        # -----------------------------------------------------
        # get shot list only if the current shot list is empty
        if not len(self._shotList):
            if len(shotListNode.childNodes):
                self._shotList = [shot.strip() for shot in
                                  shotListNode.childNodes[0].wholeText.split(
                                      '\n') if shot.strip() != ""]

        # sort the shot list
        self._shotList = utils.sort_string_numbers(self._shotList)


    def _parseShotDataNode(self, shotDataNode):
        """parses shotData node from the XML file
        """

        #assert( isinstance( shotDataNode, minidom.Element) )

        for shotNode in shotDataNode.getElementsByTagName('shot'):
            #assert( isinstance( shotNode, minidom.Element ) )

            startFrame = shotNode.getAttribute('startFrame')
            endFrame = shotNode.getAttribute('endFrame')
            name = shotNode.getAttribute('name')
            description = \
                shotNode.getElementsByTagName('description')[0].\
                    childNodes[0].wholeText.strip()

            if startFrame != '':
                startFrame = int(startFrame)
            else:
                startFrame = 0

            if endFrame != '':
                endFrame = int(endFrame)
            else:
                endFrame = 0

            # create shot objects with the data
            newShot = Shot(name, self, startFrame, endFrame, description)
            #newShot.startFrame = startFrame
            #newShot.endFrame = endFrame
            #newShot.name = name
            #newShot.description = description

            # append the shot to the self._shots
            self._shots.append(newShot)

            # also append the name to the shotList
            self._shotList.append(name)

        # sort the shot list
        self._sortShots()


    def _convertShotListToShotData(self):
        """converts the shot list node in the settings to shotData node
        """

        # now we should have the self._shotList filled
        # create the shot objects with default values and the shot names from
        # the shotList

        for shotName in self._shotList:
            newShot = Shot(shotName, self)
            #newShot.name = shotName
            self._shots.append(newShot)


    def saveSettings(self):
        """saves the settings as XML
        """
        logging.debug("saving self to the database")
        
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
            logging.debug("the sequence doesn't exist yet, creating the folder")
            
            # create a folder with sequenceName
            utils.mkdir(self._fullPath)
            self._exists = True
        
        # tell the sequence to create its own structure
        logging.debug("creating the structure")
        self.createStructure()
        
        # and create the shots
        logging.debug("creating the shots")
        self.createShots()
        
        # copy any file to the sequence
        # (like workspace.mel)
        logging.debug("copying default files")
        for _fileInfo in self.repository.defaultFiles:
            sourcePath = os.path.join(_fileInfo[2], _fileInfo[0])
            targetPath = os.path.join(self._fullPath, _fileInfo[1],
                                      _fileInfo[0])
            
            shutil.copy(sourcePath, targetPath)
        
        self.saveSettings()


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
        
        newShotsList = utils.convertRangeToList(shots)
        
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
        
#        # create shots
#        self.createShots()
        
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
        
        for now it can't convert properly if there is more than one letter at the end like:
        abc23defg --> SH023DEFG
        """

        pieces = utils.embedded_numbers(unicode(shotNumber))
        
        if len(pieces) <= 1:
            return None
        
        number = pieces[1]
        alternateLetter = pieces[2]
        
        print "shotNumber: ", shotNumber
        print "number: ", number
        print "self.shotPadding: ", self.shotPadding
        
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
        """beware that it returns a string, it returns the number plus the alternative
        letter (if exists) as a string
        
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

        # convert the numberAsStr to a number then to a string then add the alternate letter
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


    @bCache.cache()
    def getAssetTypes(self, environment):
        """returns a list of AssetType objects that this project has
        
        if the environment is set something other then None only the assetTypes
        for that environment is returned.
        
        :param environment: The name of the current environment. Ex: MAYA,
          NUKE, HOUDINI etc.
        
        :returns: 
        :rtype: oyProjectManager.models.asset.AssetType
        """

        if environment is None:
            return self._assetTypes
        else:
            aTypesList = [] * 0

            for aType in self._assetTypes:
                #assert(isinstance(aType, asset.AssetType) )
                if environment in aType.environments:
                    aTypesList.append(aType)

            return aTypesList


    @bCache.cache()
    def getAssetTypeWithName(self, typeName):
        """returns the assetType object that has the name typeName.
        if it can't find any assetType that has the name typeName it returns None
        """

        for aType in self._assetTypes:
            if aType.name == typeName:
                return aType

        return None


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


    @property
    def projectName(self):
        """returns the parent projects name
        """
        return self.project.name


    @bCache.cache(expire=60)
    def getAssetFolders(self):
        """returns all asset folders
        """

        # look at the assetType folders
        assetFolders = [] * 0

        for aType in self._assetTypes:
            #assert(isinstance(aType, AssetType))
            assetFolders.append(aType.path)

        return assetFolders


    @bCache.cache(expire=60)
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


        # optimization variables
        osPathJoin = os.path.join
        getChildFolders = utils.getChildFolders
        osPathBaseName = os.path.basename
        osPathIsDir = os.path.isdir
        globGlob = glob.glob
        assetAsset = asset.Asset
        assetsAppend = assets.append
        selfFullPath = self._fullPath
        selfProject = self.project

        # for each folder search child folders
        for folder in assetFolders:
            fullPath = osPathJoin(selfFullPath, folder)

            # 
            # skip if the folder doesn't exists
            # 
            # it is a big problem in terms of management but some old type 
            # projects has missing folders, because the folders will be 
            # created whenever somebody uses that folder while saving an 
            # asset, we don't care about its existence
            #
            #if not os.path.exists( fullPath ):
            ##            if not osPathExists( fullPath ):
            ##                continue

            # use glob instead of doing it by hand
            childFolders = getChildFolders(fullPath, True)

            for folder in childFolders:
                # get possible asset files directly by using glob
                pattern = osPathBaseName(folder) + '*'

                # files are in fullpath format
                matchedFiles = [file_ for file_ in
                                globGlob(osPathJoin(folder, pattern)) if
                                not osPathIsDir(file_)]

                matchedFileCount = len(matchedFiles)

                if matchedFileCount > 0:
                    # there should be some files matching the pattern
                    # check if they are valid assets

                    matchedAssets = map(assetAsset,
                                        [selfProject] * matchedFileCount,
                                        [self] * matchedFileCount,
                                        map(osPathBaseName, matchedFiles))

                    # append them to the main assets list
                    [assetsAppend(matchedAsset) for matchedAsset in
                     matchedAssets if matchedAsset.isValidAsset]

        return assets


    @bCache.cache()
    def getAllAssetsForType(self, typeName):
        """returns Asset objects for just the given type of the sequence
        """

        # get asset folders
        # look at the child folders
        # and then look at the files under the child folders
        # if a file starts with the folder name
        # mark it as an asset

        assets = [] * 0

        # get the asset folders
        #assetFolders = self.getAssetFolders()

        aType = self.getAssetTypeWithName(typeName)

        #assert(isinstance(aType,asset.AssetType))
        assetFolder = aType.path

        # optimization variables
        osPathExists = os.path.exists
        osPathJoin = os.path.join
        osPathIsDir = os.path.isdir
        getChildFolders = utils.getChildFolders
        osPathBaseName = os.path.basename
        globGlob = glob.glob
        assetAsset = asset.Asset
        assetsAppend = assets.append
        selfFullPath = self._fullPath
        selfProject = self.project

        fullPath = osPathJoin(selfFullPath, assetFolder)

        # 
        # skip if the folder doesn't exists
        # 
        # it is a big problem in terms of management but some old type projects
        # has missing folder, because the folders will be created whenever 
        # somebody uses that folder while saving an asset, 
        # we don't care about its existence
        #
        #if not os.path.exists( fullPath ):
        
        if not osPathExists(fullPath):
            return []

        # use glob instead of doing it by hand
        childFolders = getChildFolders(fullPath, True)

        for folder in childFolders:
            # get possible asset files directly by using glob
            pattern = osPathBaseName(folder) + '*'

            # files are in fullpath format
            matchedFiles = [file_ for file_ in
                            globGlob(osPathJoin(folder, pattern)) if
                            not osPathIsDir(file_)]

            matchedFileCount = len(matchedFiles)

            if matchedFileCount > 0:
                # there should be some files matching the pattern
                # check if they are valid assets

                matchedAssets = map(assetAsset, [selfProject] * matchedFileCount
                                    , [self] * matchedFileCount,
                                    map(osPathBaseName, matchedFiles))

                # append them to the main assets list
                [assetsAppend(matchedAsset) for matchedAsset in matchedAssets if
                 matchedAsset.isValidAsset]
        return assets


    @bCache.cache()
    def getAllAssetFileNamesForType(self, typeName):
        """returns Asset objects for just the given type of the sequence
        """

        # get asset folders
        # look at the child folders
        # and then look at the files under the child folders
        # if a file starts with the folder name
        # mark it as an asset

        assetFiles = []

        # get the asset folders
        aType = self.getAssetTypeWithName(typeName)

        #assert(isinstance(aType,asset.AssetType))
        assetFolder = aType.path

        # optimization variables
        osPathExists = os.path.exists
        osPathJoin = os.path.join
        osPathBaseName = os.path.basename
        osPathIsDir = os.path.isdir
        globGlob = glob.glob
#        assetFilesAppend = assetFiles.append
        selfFullPath = self._fullPath
#        selfProject = self.project

        fullPath = osPathJoin(selfFullPath, assetFolder)

        # 
        # skip if the folder doesn't exists
        # 
        # it is a big problem in terms of management but some old type projects
        # has missing folder, because the folders will be created whenever
        # somebody uses that folder while saving an asset, 
        # we don't care about its existence
        #
        #if not os.path.exists( fullPath ):
        if not osPathExists(fullPath):
            return []

        childFolders = utils.getChildFolders(fullPath, True)

        for folder in childFolders:
            pattern = osPathBaseName(folder) + '_*'

            matchedFiles = [file_ for file_ in
                            globGlob(osPathJoin(folder, pattern)) if
                            not osPathIsDir(file_)]

            matchedFileCount = len(matchedFiles)

            if matchedFileCount > 0:
                #[ assetFilesAppend(matchedFile) for matchedFile in matchedFiles if self.isValidExtension( os.path.splitext(matchedFile)[1].split('.')[1] ) ]
                #map( assetFilesAppend, matchedFiles )
                assetFiles.extend(matchedFiles)

        assetFiles = map(os.path.basename, assetFiles)

        return assetFiles


    def getAssetBaseNamesForType(self, typeName):
        """returns all asset baseNames for the given type
        """

        # get the asset files of that type
        allAssetFileNames = self.getAllAssetFileNamesForType(typeName)

        # filter for base name
        sGFIV = self.generateFakeInfoVariables
        baseNamesList = [sGFIV(assetFileName)['baseName'] for assetFileName in
                         allAssetFileNames]

        # remove duplicates
        baseNamesList = utils.unique(baseNamesList)

        return baseNamesList


    @bCache.cache()
    def getAllAssetsForTypeAndBaseName(self, typeName, baseName):
        """returns Asset objects of the sequence for just the given type and
        basename
        """

        # get asset folders
        # look at the child folders
        # and then look at the files under the child folders
        # if a file starts with the folder name
        # mark it as an asset

        assets = [] * 0

        # get the asset folder
        aType = self.getAssetTypeWithName(typeName)
        assetFolder = aType.path

        # optimization variables
        osPathJoin = os.path.join
        osPathExists = os.path.exists
        osPathIsDir = os.path.isdir
        selfFullPath = self._fullPath
        assetAsset = asset.Asset
        selfProject = self.project
        assetsAppend = assets.append

        osPathBaseName = os.path.basename
        globGlob = glob.glob

        fullPath = osPathJoin(selfFullPath, assetFolder)

        # 
        # skip if the folder doesn't exists
        # 
        # it is a big problem in terms of management but some old type projects
        # has missing folder, because the folders will be created whenever 
        # somebody uses that folder while saving an asset, 
        # we don't care about its existence
        #
        if not osPathExists(fullPath):
            return []

        childFolder = baseName
        childFolderFullPath = osPathJoin(fullPath, childFolder)

        # use glob instead of doing it by hand

        # get possible asset files directly by using glob
        pattern = osPathBaseName(baseName) + '_*'

        # files are in fullpath format
        matchedFiles = [file_ for file_ in
                        globGlob(osPathJoin(childFolderFullPath, pattern)) if
                        not osPathIsDir(file_)]

        matchedFileCount = len(matchedFiles)

        if matchedFileCount > 0:
            # there should be some files matching the pattern
            # check if they are valid assets

            matchedAssets = map(assetAsset, [selfProject] * matchedFileCount,
                                [self] * matchedFileCount,
                                map(osPathBaseName, matchedFiles))

            # append them to the main assets list
            [assetsAppend(matchedAsset) for matchedAsset in matchedAssets if
             matchedAsset.isValidAsset]

        return assets



        #
        #def getAllBaseNamesForType(self, typeName):
        #"""
        #"""

        #aType = self.getAssetTypeWithName( typeName )

        ##assert(isinstance(aType,asset.AssetType))

        #typeFolder = aType.path

        #os.listdir( typeFolder )


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
        assetInfos = map(asset.Asset.infoVariables, assetList)

        filteredAssetInfos = self.aFilter(assetInfos, **kwargs)

        # recreate assets and return
        # TODO: return without recreating the assets
        return [asset.Asset(self.project, self, x['fileName']) for x in
                filteredAssetInfos]


    def filterAssetNames(self, assetFileNames, **kwargs):
        """a fake filter for quick retrieval of info from asset file names
        
        use filterAsset for filtering with asset objects as input
        
        the kwargs should have at least on of these keywords:
        
        baseName
        subName
        typeName
        """

        # generate dictionaries
        assetInfos = map(self.generateFakeInfoVariables, assetFileNames)

        filteredAssetFileNames = self.aFilter(assetInfos, **kwargs)

        return [info['fileName'] for info in filteredAssetFileNames]


    @bCache.cache()
    def generateFakeInfoVariables(self, assetFileName):
        """generates fake info variables from assetFileNames by splitting the file name
        from '_' characters and trying to get information from those splits
        """
        #assert(isinstance(assetFileName, str))
        splits = assetFileName.split('_') # replace it with data separator

        infoVars = dict()

        infoVars['fileName'] = assetFileName
        infoVars['baseName'] = ''
        infoVars['subName'] = ''
        infoVars['typeName'] = ''

        if not self._no_sub_name_field:
            if len(splits) > 3:
                infoVars['baseName'] = splits[0]
                infoVars['subName'] = splits[1]
                infoVars['typeName'] = splits[2]
        else:
            if len(splits) > 2:
                infoVars['baseName'] = splits[0]
                infoVars['subName'] = ''
                infoVars['typeName'] = splits[1]

        return infoVars


    def aFilter(self, dicts, **kwargs):
        """filters dictionaries for criteria
        dicts is a list of dictionaries
        the function returns the dictionaries that has all the kwargs
        """
        return [d for d in dicts if all(d.get(k) == kwargs[k] for k in kwargs)]



        #
        #@property
        #def invalidExtensions(self):
        #"""returns invalid extensions for the sequence
        #"""
        #return self._extensionsToIgnore



        #
        #@bCache.cache()
        #def isValidExtension(self, extensionString):
        #"""checks if the given extension is in extensionsToIgnore list
        #"""

        #if len(self._extensionsToIgnore) == 0 :
        ## no extensions to ignore
        #return True

        ##assert(isinstance(extensionString,str))

        #if extensionString.lower() in self._extensionsToIgnore:
        #return False

        #return True


    def isValid(self):
        """checks if the sequence is valid
        """

        # a valid should:
        # - be exist
        # - have a .settings.xml file inside it

        if self._exists and self._settingsFileExists:
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
            newAType = asset.AssetType(name, path, shotDependent, environments)

            # add it to the list
            self._assetTypes.append(newAType)

    @property
    def exists(self):
        """returns True if the sequence itself exists, False otherwise
        """
        return self._exists

    @property
    def no_sub_name_field(self):
        """returns True if the sequence doesn't support subName fields (old-style)
        """
        return self._no_sub_name_field

#    def undoChange(self):
#        """undoes the last change to the .settings.xml file if there is a
#        backup of the .settings.xml file
#        """
#
#        # get the backup files of the .settings.xml
#        backupFiles = utils.getBackupFiles(self._settings_file_full_path)
#
#        if len(backupFiles) > 0:
#            #print backupFiles
#            # there is at least one backup file
#            # delete the current .settings.xml
#            # and rename the last backup to .settings.xml
#
#            print "replacing with : ", os.path.basename(backupFiles[-1])
#
#            shutil.copy(backupFiles[-1], self._settings_file_full_path)
#            os.remove(backupFiles[-1])


    def __eq__(self, other):
        """The equality operator
        """
        return isinstance(other, Sequence) and other.name == self.name and\
               other.projectName == self.projectName


    def __ne__(self, other):
        """The in equality operator
        """
        return not self.__eq__(other)
    
    @validates("name")
    def _validate_name(self, key, name):
        """validates the given name
        """
        
        return utils.stringConditioner(
            name,
            allowUnderScores=True,
            upperCaseOnly=True,
            capitalize=False
        )


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
        
        self.shotDependentFolders = shotDependentFolders # should be a list of str or unicode
        self.shotIndependentFolders = shotIndependentFolders # should be a list of str or unicode


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


class Shot(object):
    """The class that enables the system to manage shot data.
    """

    def __init__(self, name, sequence=None, startFrame=1, endFrame=1,
                 description=''):
        self._name = name
        self._duration = 1
        self._startFrame = startFrame
        self._endFrame = endFrame
        self._description = description
        self._sequence = sequence
        #self._cutSummary = ''


    def __str__(self):
        """returns the string representation of the object
        """
        return self._name

#    def __repr__(self):
#        """returns the representation of the class
#        """
#        return "< oyProjectManager.models.project.Shot object: " + self._name + ">"

    @property
    def startFrame(self):
        """the start frame of the shot
        """
        return self._startFrame

    @startFrame.setter
    def startFrame(self, frame):
        self._startFrame = frame
        # update the duration
        self._updateDuration()

    @property
    def endFrame(self):
        """the end frame of the shot
        """
        return self._endFrame

    @endFrame.setter
    def endFrame(self, frame):
        self._endFrame = frame
        # update the duration
        self._updateDuration()

    def _updateDuration(self):
        """updates the duration
        """
        self._duration = self._endFrame - self._startFrame + 1

    @property
    def description(self):
        """the shots description
        """
        return self._description

    @description.setter
    def description(self, description):
        self._description = description

    @property
    def sequence(self):
        """The sequence of the current Shot instance.
        :returns: :class:`~oyProjectManager.models.project.Sequence`
        """
        return self._sequence

    @sequence.setter
    def sequence(self, seq):
        self._sequence = seq

    @property
    def name(self):
        """The name of the current Shot.
        
        :returns: str
        """
        return self._name

    @name.setter
    def name(self, name):
        self._name = name

    @property
    def duration(self):
        """the duration
        """
        return self._duration
