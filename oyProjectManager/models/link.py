# -*- coding: utf-8 -*-
# Copyright (c) 2009-2012, Erkan Ozgur Yilmaz
# 
# This module is part of oyProjectManager and is released under the BSD 2
# License: http://www.opensource.org/licenses/BSD-2-Clause
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm.mapper import validates

from oyProjectManager.db.declarative import Base

class FileLink(Base):
    """Manages file links in :class:`~oyProjectManager.models.version.Version` instances.
    
    .. versionadded:: 0.2.5
       
       In previous versions of oyProjectManager, all the connections to the
       file system was handled by the
       :class:`~oyProjectManager.models.version.Version` class it self. But it
       was a little limiting, where the system was only be able to hold data
       about the Version file itself. With the addition of the FileLink class
       the system is now be able to hold any kind of file info, like; input
       files used in one Version file to outputs of that Version instance,
       which can be textures as inputs and render outputs as output. And not
       only Versions but also Projects, Sequences, Assets now are able to hold
       references to FileLinks.
    
    .. note::
       
       The ``type`` attribute can be simply a string, and in UI we can serve it
       as an editable comboBox where the users are able to select from distinct
       types of FileTypes.
    
    FileLinks are references to the files in the repository. Version instances
    use it to specify their source files, and any other class mixed with the
    :class:`~oyProjectManager.models.mixins.IOMixin` uses the FileLinks to
    specify their inputs and outputs.
    
    FileLink.filename attribute can be a sequence of files with the correct
    file name format, which is defined in studios config.py file.
    
    :param path: The path of this FileLink instance, it is $REPO relative.
    
    :param filename: The filename of this FileLink instance.
    
    :param type: An optional string to hold the type of this FileLink instance.
      Can be anything.
    """
    
    __tablename__ = "FileLinks"
    
    id = Column(Integer, primary_key=True)
    
    filename = Column(String(256))
    path = Column(String(1024))
    type = Column(String(32))
    
    def __init__(self, filename, path, type=""):
        self.filename = filename
        self.path = path
        self.type = type
    
    @validates('filename')
    def _validate_filename(self, key, filename):
        """validates the given filename value
        """
        if filename is None:
            raise TypeError("FileLink.filename can not be None")
        
        if not isinstance(filename, (str, unicode)):
            raise TypeError("FileLink.filename should be a str or unicode, "
                            "not %s" % filename.__class__.__name__)
        
        return filename
    
    @validates('path')
    def _validate_path(self, key, path):
        """validates the given path value
        """
        if path is None:
            raise TypeError("FileLink.path can not be None")
        
        if not isinstance(path, (str, unicode)):
            raise TypeError("FileLink.path should be a str or unicode, "
                            "not %s" % path.__class__.__name__)
        return path
    
    @validates('type')
    def _validate_type(self, key, type_):
        """validates the given type value
        """
        if type_ is None:
            type_ = ""
        
        if not isinstance(type_, (str, unicode)):
            raise TypeError("FileLink.type should be a str or unicode, "
                            "not %s" % type_.__class__.__name__)
        
        return type_

