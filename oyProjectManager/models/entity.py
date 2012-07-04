# -*- coding: utf-8 -*-
# Copyright (c) 2009-2012, Erkan Ozgur Yilmaz
# 
# This module is part of oyProjectManager and is released under the BSD 2
# License: http://www.opensource.org/licenses/BSD-2-Clause

from exceptions import TypeError
import os
import jinja2
from sqlalchemy import UniqueConstraint, Column, String, Integer, ForeignKey
from sqlalchemy.ext.declarative import synonym_for
from sqlalchemy.orm import relationship, validates
from oyProjectManager import conf
from oyProjectManager.db import Base
from oyProjectManager.models.repository import Repository
from oyProjectManager.models.version import Version

# create a logger
import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)

class VersionableBase(Base):
    """A base class for :class:`~oyProjectManager.models.shot.Shot` and
    :class:`~oyProjectManager.models.asset.Asset` classes.
    
    It will supply the base attributes to be able to attach a
    :class:`~oyProjectManager.models.version.Version` to the
    :class:`~oyProjectManager.models.shot.Shot` and
    :class:`~oyProjectManager.models.asset.Asset` instances.
    
    It doesn't need any parameter while initialization.
    
    It supplies only one read-only attribute called
    :attr:`~oyProjectManager.models.entity.VersionableBase.versions` which is a
    list and holds :class:`~oyProjectManager.models.version.Version` instances.
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
    
    project_id = Column(
        Integer, ForeignKey("Projects.id"),
        nullable=False
    )
    _project = relationship(
        "Project",
        #cascade="all"
    )
    
    _code = Column(
        String(128),
        doc="""The nicely formatted version of the
        :attr:`~oyProjectManager.models.asset.Asset.name` attribute or
        :attr:`~oyProjectManager.models.shot.Shot.number` attribute. It will
        be overloaded in the :class:`~oyProjectManager.models.asset.Asset` or
        :class:`~oyProjectManager.models.shot.Shot` class.
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
    
    @property
    def thumbnail_full_path(self):
        """returns the thumbnail full path for this versionable
        """
        
        from oyProjectManager.models.asset import Asset
        from oyProjectManager.models.shot import Shot
        
        # just render a thumbnail path
        template_vars = {}
        
        # define the template for the versionable type (asset or shot)
        path_template = ''
        filename_template = ''
        if isinstance(self, Asset):
            path_template = jinja2.Template(conf.asset_thumbnail_path)
            filename_template = jinja2.Template(conf.asset_thumbnail_filename)
            
            template_vars.update(
                {
                    "project": self.project,
                    "asset": self,
                    "extension": conf.thumbnail_format
                }
            )
        elif isinstance(self, Shot):
            path_template = jinja2.Template(conf.shot_thumbnail_path)
            filename_template = jinja2.Template(conf.shot_thumbnail_filename)
            
            template_vars.update(
                {
                    "project": self.project,
                    "sequence": self.sequence,
                    "shot": self,
                    "extension": conf.thumbnail_format
                }
            )
        
        # render the templates
        path = path_template.render(**template_vars)
        filename = filename_template.render(**template_vars)
        
        # the path should be $REPO relative
        thumbnail_full_path = os.path.join(
            os.environ[conf.repository_env_key], path, filename
        ).replace('\\', '/')
        
        return thumbnail_full_path


class EnvironmentBase(object):
    """Connects the environment (the host program) to the oyProjectManager.
    
    In oyProjectManager, an Environment is a host application like Maya, Nuke,
    Houdini etc.
    
    Generally a GUI for the end user is given an environment which helps
    the QtGui to be able to open, save, import or export a Version without
    knowing the details of the environment.
    
    .. note::
      For now the :class:`~oyProjectManager.models.entity.EnvironmentBase`
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
    :class:`~oyProjectManager.models.version.Version` instance in any other
    case.
    
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
        
        return self.get_current_version()

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
        
        :param version: A :class:`~oyProjectManager.models.version.Version`
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
        
        Finds and returns the :class:`~oyProjectManager.models.version.Version`
        instances from the given path value.
        
        Returns an empth list if it can't find any matching.
        
        This method is different than
        :meth:`~oyProjectManager.models.entity.EnvironmentBase.get_version_from_full_path`
        because it returns a list of
        :class:`~oyProjectManager.models.version.Version` instances which are
        residing in that path. The list is ordered by the ``id``\ s of the
        instances.
        
        :param path: A path which has possible
            :class:`~oyProjectManager.models.version.Version` instances.
        
        :return: A list of :class:`~oyProjectManager.models.version.Version`
            instances.
        """
        if path is None or path=="":
            return None
        
        # get the path by trimming the server_path
        path = self.trim_server_path(path)
        
        # get all the version instance at that path
        return Version.query()\
            .filter(Version.path.startswith(path))\
            .order_by(Version.id.desc())\
            .all()
    
    def get_version_from_full_path(self, full_path):
        """Finds the Version instance from the given full_path value.
        
        Finds and returns a :class:`~oyProjectManager.models.version.Version`
        instance from the given full_path value.
        
        Returns None if it can't find any matching.
        
        :param full_path: The full_path of the desired
            :class:`~oyProjectManager.models.version.Version` instance.
        
        :return: :class:`~oyProjectManager.models.version.Version`
        """

        path, filename = os.path.split(full_path)
        path = self.trim_server_path(path)
        
        # try to get a version with that info
        version = Version.query()\
            .filter(Version.path==path)\
            .filter(Version.filename==filename)\
            .first()
        
        return version
    
    def get_current_version(self):
        """Returns the current Version instance from the environment.
        
        :returns: :class:`~oyProjectManager.models.version.Version` instance or
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
        
        :returns: :class:`~oyProjectManager.models.version.Version` instance or
            None
        """
        raise NotImplemented
    
    def get_project(self):
        """returns the current project from environment
        """
        raise NotImplemented
    
    def set_project(self, version):
        """Sets the project to the given Versions project.
        
        :param version: A :class:`~oyProjectManager.models.version.Version`.
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
        """Returns the :class:`~oyProjectManager.models.version.Version`
        instances which are referenced in to the current scene
        
        :returns: list of :class:`~oyProjectManager.models.version.Version`
            instances
        """
        raise NotImplemented

#    def update_versions(self, version_tuple_list):
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
        """Returns True if the given file names extension is in the extensions
        list false otherwise.
        
        accepts:
        * a full path with extension or not
        * a file name with extension or not
        * an extension with a dot on the start or not
        
        :param filename: A string containing the filename
        """
        
        if filename is None:
            return False
        
        return filename.split('.')[-1].lower() in self.extensions
    
    def load_referenced_versions(self):
        """loads all the references
        """
        raise NotImplemented

    def replace_version(self, source_version, target_version):
        """Replaces the source_version with the target_version
        
        :param source_version: A
          :class:`~oyProjectManager.models.version.Version` instance holding
          the version to be replaced
        
        :param target_version: A
          :class:`~oyProjectManager.models.version.Version`
          instance holding the new version replacing the source one
        """
        raise NotImplemented
    
    def replace_external_paths(self, mode=0):
        """Replaces the external paths (which are not starting with the
        environment variable) with a proper path. The mode controls if the
        resultant path should be absolute or relative to the project dir.
        
        :param mode: Controls the resultant path is absolute or relative.
          
          mode 0: absolute (a path which starts with $REPO)
          mode 1: relative (to project path)
        
        :return:
        """
        raise NotImplemented

