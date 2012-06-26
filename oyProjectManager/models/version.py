# -*- coding: utf-8 -*-
# Copyright (c) 2009-2012, Erkan Ozgur Yilmaz
# 
# This module is part of oyProjectManager and is released under the BSD 2
# License: http://www.opensource.org/licenses/BSD-2-Clause

import os
import re

from copy import copy

import jinja2

from sqlalchemy import (UniqueConstraint, Column, Integer, ForeignKey, String,
                        Boolean, Enum, Table)
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.ext.declarative import synonym_for
from sqlalchemy.ext.hybrid import Comparator, hybrid_property
from sqlalchemy.orm import relationship, validates, synonym, backref
from oyProjectManager import db
from oyProjectManager import conf
from oyProjectManager.db.declarative import Base
from oyProjectManager.models.auth import User
from oyProjectManager.models.errors import CircularDependencyError

# create a logger
import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)

class VersionStatusComparator(str, Comparator):
    """The comparator class for Version.status
    """
    
    def __new__(cls, status):
        
        if isinstance(status, VersionStatusComparator):
            status = status.status
        elif isinstance(status, basestring):
            status_list_long_names = conf.status_list_long_names
            if status in status_list_long_names:
                index = status_list_long_names.index(status)
                status = conf.status_list[index]
            status = status   
        
        obj = str.__new__(cls, status)
        obj.status = status
        return obj
    
    #def __init__(self, status):
    #    if isinstance(status, VersionStatusComparator):
    #        self.status = status.status
    #    elif isinstance(status, basestring):
    #        status_list_long_names = conf.status_list_long_names
    #        if status in status_list_long_names:
    #            index = status_list_long_names.index(status)
    #            status = conf.status_list[index]
    #        self.status = status
    
    def __eq__(self, other):
        if not isinstance(other, VersionStatusComparator):
            other = VersionStatusComparator(other)
        return self.__clause_element__() == other.status
   
    def __clause_element__(self):
        return self.status
    
#    def __set__(self, instance, value):
    #def __str__(self):
    #    return self.status


class Version(Base):
    """Holds versions of assets or shots.
    
    In oyProjectManager a Version is the file created for an
    :class:`~oyProjectManager.models.asset.Asset` or
    :class:`~oyProjectManager.models.shot.Shot`\ . The placement of this file
    is automatically handled by the connected
    :class:`~oyProjectManager.models.version.VersionType` instance.
    
    The values given for
    :attr:`~oyProjectManager.models.version.Version.base_name` and
    :attr:`~oyProjectManager.models.version.Version.take_name` are conditioned
    as follows:
      
      * Each word in the string should start with an upper-case letter (title)
      * It can have all upper-case letters
      * CamelCase is allowed
      * Valid characters are ([A-Z])([a-zA-Z0-9\_])
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
    :attr:`~oyProjectManager.models.version.Version.filename` and the
    :attr:`~oyProjectManager.models.version.Version.path` attributes are
    rendered from the associated
    :class:`~oyProjectManager.models.version.VersionType` instance. The
    resultant
    :attr:`~oyProjectManager.models.version.Version.filename` and
    :attr:`~oyProjectManager.models.version.Version.path` values are stored and
    retrieved back from the Version instance itself, no re-rendering happens.
    It means, the Version class depends the
    :class:`~oyProjectManager.models.version.VersionType` class only at the
    initialization, any change made to the
    :class:`~oyProjectManager.models.version.VersionType` instance (like
    changing the :attr:`~oyProjectManager.models.version.VersionType.name` or
    :attr:`~oyProjectManager.models.version.VersionType.code` of the
    :class:`~oyProjectManager.models.version.VersionType`) will not effect the
    Version instances created before this change. This is done in that way to
    be able to freely change the
    :class:`~oyProjectManager.models.version.VersionType` attributes and
    prevent loosing the connection between a Version and a file on the
    repository for previously created Versions.
    
    .. versionadded:: 0.2.2
      Published Versions:
      
      After v0.2.2 Versions can be set published. It is a bool attribute
      holding information about if this Version is published or not.
    
    :param version_of: A
      :class:`~oyProjectManager.models.entity.VersionableBase` instance
      (:class:`~oyProjectManager.models.asset.Asset` or
      :class:`~oyProjectManager.models.shot.Shot`) which is the owner of this
      version. Can not be skipped or set to None.
    
    :type type: :class:`~oyProjectManager.models.asset.Asset`,
      :class:`~oyProjectManager.models.shot.Shot` or
      :class:`~oyProjectManager.models.entity.VersionableBase`
    
    :param type: A :class:`~oyProjectManager.models.version.VersionType`
      instance which is showing the type of the current version. The type is
      also responsible of the placement of this Version in the repository. So
      the :attr:`~oyProjectManager.models.version.Version.filename` and the
      :attr:`~oyProjectManager.models.version.Version.path` is defined by the
      related :class:`~oyProjectManager.models.version.VersionType` and the
      :class:`~oyProjectManager.models.project.Project` settings. Can not be
      skipped or can not be set to None.
    
    :type type: :class:`~oyProjectManager.models.version.VersionType`
    
    :param str base_name: A string showing the base name of this Version
      instance. Generally used to create an appropriate 
      :attr:`~oyProjectManager.models.version.Version.filename` and a
      :attr:`~oyProjectManager.models.version.Version.path` value. Can not be
      skipped, can not be None or empty string.
    
    :param str take_name: A string showing the take name. The default value is
      "MAIN" and it will be used in case it is skipped or it is set to None
      or an empty string. Generally used to create an appropriate
      :attr:`~oyProjectManager.models.version.Version.filename` and a
      :attr:`~oyProjectManager.models.version.Version.path` value. 
    
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
    
    :param created_by: A :class:`~oyProjectManager.models.auth.User` instance
      showing who created this version. It can not be skipped or set to None or
      anything other than a :class:`~oyProjectManager.models.auth.User`
      instance.
    
    :type created_by: :class:`~oyProjectManager.models.auth.User`
    
    :param str extension: A string holding the file extension of this version.
      It may or may not include a dot (".") sign as the first character.
    
    :param bool is_published: A bool value defining this Version as a published
      one.
    """

    # TODO: add audit info like date_created, date_updated, created_at and updated_by
    # TODO: add needs_update flag, primarily need to be used with renamed versions
    
    # file_size_format = "%.2f MB"
    # timeFormat = '%d.%m.%Y %H:%M'

    __tablename__ = "Versions"
    
    __table_args__  = (
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
    
    is_published = Column(Boolean, default=False)
    
    _status = Column(
        Enum(*conf.status_list, name='StatusNames'),
    )
    
    def __init__(self,
                 version_of,
                 base_name,
                 type,
                 created_by,
                 take_name="MAIN",
                 version_number=1,
                 note="",
                 extension="",
                 is_published=False,
                 status=None,
                 ):
        self.is_published = is_published
        
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
        
        self.status = status
    
    def __repr__(self):
        """The representation of this version
        """
        return "<Version: %s>" % self.filename
    
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
        
        from oyProjectManager.models.entity import VersionableBase
        
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
        
        from oyProjectManager.models.shot import Shot
        
        kwargs = {
            "project": self.version_of.project,
            "sequence": self.version_of.sequence if isinstance(self.version_of, Shot) else "",
            "shot": self.version_of,
            "asset": self.version_of,
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
        :class`~oyProjectManager.models.version.Version`\.
        :attr:`~oyProjectManager.models.version.VersionType.path` of the with
        the information supplied by this
        :class:`~oyProjectManager.models.version.Version` instance.
        
        The resultant path is an absolute one. But the stored path in the
        database is just the relative portion to the
        :class:`~oyProjectManager.models.repository.Repository`\ .\ 
        :attr:`~oyProjectManager.models.repository.Repository.server_path`
        """
        return os.path.join(
            self.project.path,
            self._path
        ).replace("\\", "/")
    
    @property
    def full_path(self):
        """The full_path of this version.
        
        It is the join of
        :class:`~oyProjectManager.models.repository.Repository`.\ 
        :attr:`~oyProjectManager.models.repository.Repository.server_path` and
        :class:`~oyProjectManager.models.version.Version`.\
        :attr:`~oyProjectManager.models.version.Version.path` and
        :class:`~oyProjectManager.models.version.Version`.\
        :attr:`~oyProjectManager.models.version.Version.filename` attributes.
        
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
        :class:`~oyProjectManager.models.version.VersionType`\ .\ 
        :attr:`~oyProjectManager.models.version.VersionType.output_path`
        template with the information supplied with this ``Version`` instance.
        
        The resultant path is an absolute one. But the stored path in the
        database is just the relative portion to the
        :class:`~oyProjectManager.models.repository.Repository`\ .\ 
        :attr:`~oyProjectManager.models.repository.Repository.server_path`.
        """
        return os.path.join(
            self.project.path,
            self._output_path
        ).replace("\\", "/")

    def _condition_name(self, name):
        """conditions the base name, see the
        :class:`~oyProjectManager.models.version.Version` documentation for
        details
        """

        # strip the name
        name = name.strip()
        # convert all the "-" signs to "_" at the beginning and the at the end
        # of the string
        #name = name.replace("-", "_")
        #name = re.sub(r"^[\-]+", r"", name)
        #name = re.sub(r"[\-]+$", r"", name)
        # remove unnecessary characters from the string
        name = re.sub(r"([^a-zA-Z0-9\s_\-]+)", r"", name)
        # remove all the characters from the beginning which are not alphabetic
        name = re.sub(r"(^[^a-zA-Z0-9]+)", r"", name)
        # substitute all spaces with "_" characters
        name = re.sub(r"([\s])+", "_", name)
        # make each words first letter uppercase
        name = "_".join([ word[0].upper() + word[1:]
                          for word in name.split("_")
                          if len(word)
        ])
        name = "-".join([ word[0].upper() + word[1:]
                          for word in name.split("-")
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
        
        :returns: :class:`~oyProjectManager.models.version.Version` instance
        """
        #            .filter(Version.base_name == self.base_name)\
        return db.session\
            .query(Version)\
            .filter(Version.type==self.type)\
            .filter(Version.version_of==self.version_of)\
            .filter(Version.take_name==self.take_name)\
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
                            "set it to oyProjectManager.models.auth.User "
                            "instance")

        if not isinstance(created_by, User):
            raise TypeError("Version.created_by should be an instance of"
                            "oyProjectManager.models.auth.User")

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
        """The :class:`~oyProjectManager.models.project.Project` instance that
        this Version belongs to
        """
        
        return self.version_of.project
    
    def is_latest_version(self):
        """returns True if this is the latest Version False otherwise
        """
        return self.max_version == self.version_numberd
    
    def is_latest_published_version(self):
        """returns True if this is the latest published Version False otherwise
        """
        if not self.is_published:
            return False
        
        return self == self.latest_published_version()
    
    def latest_published_version(self):
        """Returns the last published version.
        
        :return: :class:`~oyProjectManager.models.version.Version`
        """
        
        return db.session\
            .query(Version)\
            .filter(Version.type==self.type)\
            .filter(Version.version_of==self.version_of)\
            .filter(Version.take_name==self.take_name)\
            .filter(Version.is_published==True)\
            .order_by(Version.version_number.desc())\
            .first()
    
    @property
    def dependency_update_list(self, published_only=True):
        """Calculates a list of
        :class:`~oyProjectManager.models.version.Version` instances, which are
        referenced by this Version and has a newer version.
        
        Also checks the references in the referenced Version and appends the
        resultant list to the current dependency_update_list. Resulting a much
        deeper update info.
        
        :return: list of :class:`~oyProjectManager.models.version.Version`
            instances.
        """
        
        # loop through the referenced Version instances and check if they have
        # newer Versions
        
        update_list = []
        
#        for ref in self.references:
#            if not ref.is_latest_version():
#                update_list.append(ref)
#            # also loop in their references
#            update_list.extend(ref.dependency_update_list)
        
        # for now just search for published versions for the first references
        # do not search the children of it
        for ref in self.references:
            # get the last published versions of the references
            published_version = ref.latest_published_version()
            # if the version number is bigger add it to the update list
            if published_version:
                if published_version.version_number > ref.version_number:
                    update_list.append(ref)
        
        return update_list
    
#    @validates('status')
    def _validate_status(self, status):
        """validates the given status value
        """
        if isinstance(status, VersionStatusComparator):
            status = status.status
        
        if status is None:
            latest_version = self.latest_version()
            if latest_version:
                status = latest_version.status
            else:
                # set it to status[0]
                status = conf.status_list[0]
        
        if not isinstance(status, (str, unicode)):
            raise TypeError('Version.status should be one an instance of '
                            'string and the value should be one of of %s not '
                            '%s' %
                            (conf.status_list, status.__class__.__name__)
            )
        
        all_statuses = copy(conf.status_list)
        all_statuses.extend(conf.status_list_long_names)
        if status not in all_statuses:
            raise ValueError('Version.status should be one of %s not %s' %
                (conf.status_list, status))
        
        if status in conf.status_list_long_names:
            index = conf.status_list_long_names.index(status)
            status = conf.status_list[index]
        
        return status

    @hybrid_property
    def status(self):
        return VersionStatusComparator(self._status)
    
    @status.setter
    def status(self, status):
        self._status = self._validate_status(status)


class VersionType(Base):
    """A template for :class:`~oyProjectManager.models.version.Version` class.
    
    A VersionType is basically a template object for the
    :class:`~oyProjectManager.models.version.Version` instances. It gives the
    information about the filename template, path template and output path
    template for the :class:`~oyProjectManager.models.version.Version` class.
    Then the :class:`~oyProjectManager.models.version.Version` class renders
    this Jinja2 templates and places itself (or the produced files) in to the
    appropriate folders in the
    :class:`~oyProjectManager.models.repository.Repository`.
    
    All the template variables (
    :attr:`~oyProjectManager.models.version.VersionType.filename`,
    :attr:`~oyProjectManager.models.version.VersionType.path`,
    :attr:`~oyProjectManager.models.version.VersionType.output_path`) can use
    the following variables in their template codes.
    
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
    config.py file and the :class:`~oyProjectManager.models.project.Project`
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
      until :meth:`~oyProjectManager.models.version.VersionType.save` is
      called.
    
    :param str code: The code is a shorthand form of the name. For example,
      if the name is "Animation" than the code can be "ANIM" or "Anim" or
      "anim". Because the code is generally used in filename, path or
      output_path templates it is going to be a part of the filename or path,
      so be careful about what you give as a code. The code attribute should be
      unique. Be careful that even specifying a non unique code VersionType
      instance will not raise an error until
      :meth:`~oyProjectManager.models.version.VersionType.save` is called. For
      formatting, these rules are current:
        
        * no white space characters are allowed
        * can not start with a number
        * can not start or end with an underscore character
        * both lowercase or uppercase letters are allowed
        
      A good code is the short form of the
      :attr:`~oyProjectManager.models.version.VersionType.name` attribute.
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
      :class:`~oyProjectManager.models.version.Version` which is using this
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
      :class:`~oyProjectManager.models.version.Version` instance. Look for the
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
      :class:`~oyProjectManager.models.version.Version`\ s. An output is simply
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
      generally created in the
      :class:`~oyProjectManager.models.project.Project` creation phase.
      
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
#      which :class:`~oyProjectManager.models.project.Project` it belongs to. So
#      it can not be None or anything other than a
#      :class:`oyProjectManager.models.project.Project` instance.
#    
#    :type project: :class:`~oyProjectManager.models.project.Project`

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
        :class:`~oyProjectManager.models.version.Version`\ s of this type. Any
        :class:`~oyProjectManager.models.version.Version` which is created
        prior to this change will not be effected. But be careful about the
        older and newer :class:`~oyProjectManager.models.version.Version`\ s of
        the same :class:`~oyProjectManager.models.asset.Asset` or
        :class:`~oyProjectManager.models.shot.Shot` may placed to different
        folders according to your new template.
        
        The template **should not** include a dot (".") sign before the
        extension, it is handled by the
        :class:`~oyProjectManager.models.version.Version` instance.
        """
    )

    path = Column(
        String,
        doc="""The path template for this Type of Version instance.
        
        You can freely change the path template attribute after creating
        :class:`~oyProjectManager.models.version.Version`\ s of this type. Any
        :class:`~oyProjectManager.models.version.Version` which is created
        prior to this change will not be effected. But be careful about the
        older and newer :class:`~oyProjectManager.models.version.Version`\ s of
        the same :class:`~oyProjectManager.models.asset.Asset` or
        :class:`~oyProjectManager.models.shot.Shot` may placed to different
        folders according to your new template.
        
        The path template should be an relative one to the
        :attr:`~oyProjectManager.models.repository.Repository.server_path`, so
        don't forget to place ``{{project.code}}`` at the beginning of you
        template if you are storing all your asset and shots inside the project
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
        Enum("Asset", "Shot", name="ckEnumType"),
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
#                            "oyProjectManager.models.project.Project")
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

# secondary tables
Version_References = Table(
    "Version_References", Base.metadata,
    Column("referencer_id", Integer, ForeignKey("Versions.id"), primary_key=True),
    Column("reference_id", Integer, ForeignKey("Versions.id"), primary_key=True),
    extend_existing=True
)
