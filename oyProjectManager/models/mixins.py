# -*- coding: utf-8 -*-
# Copyright (c) 2009-2012, Erkan Ozgur Yilmaz
# 
# This module is part of oyProjectManager and is released under the BSD 2
# License: http://www.opensource.org/licenses/BSD-2-Clause

class IOMixin(object):
    """Adds the ability to be able to hold relations to :class:`~oyProjectManager.models.link.FileLink` instances.
    
    IOMixin adds the ability to be able to be related to
    :class:`~oyProjectManager.models.link.FileLink` instances as ``inputs`` and
    ``outputs``. It is different than a
    :class:`~oyProjectManager.models.version.Version` holding a
    :class:`~oyProjectManager.models.link.FileLink` for the source file link
    and different again from a Version holding a reference to another Version
    instance.
    
    Inputs are external files used to create the outputs of the mixed in class.
    It can be and EDL file for a Project or Sequence or can be a texture file
    for an Asset Version or can be a image file sequence for a Shot Version
    which is a composition scene may be.
    
    :param inputs: A list of :class:`~oyProjectManager.models.link.FileLink`
      instances holding the inputs (texture, image sequence, video, text etc.)
      those are considered as inputs to this mixed in class.
    
    :type inputs: a list of :class:`~oyProjectManager.models.link.FileLink`
      instances.
    
    :param outputs: A list of :class:`~oyProjectManager.models.link.FileLink`
      instances holding the outputs of this mixed in class. Outputs can be a
      sequence of images lets say for a Shot Version.
    """
    
    
