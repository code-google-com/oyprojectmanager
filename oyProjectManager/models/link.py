# -*- coding: utf-8 -*-
# Copyright (c) 2009-2012, Erkan Ozgur Yilmaz
# 
# This module is part of oyProjectManager and is released under the BSD 2
# License: http://www.opensource.org/licenses/BSD-2-Clause

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
    
    :param path: The path of this FileLink instance, it is $REPO relative.
    
    :param filename: The filename of this FileLink instance.
    
    :param type: An optional string to hold the type of this FileLink instance.
      Can be anything.
    """
    
    
