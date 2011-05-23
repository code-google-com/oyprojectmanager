# -*- coding: utf-8 -*-
"""
photoshopEnv by Erkan Ozgur Yilmaz (c) 2009-2010


Description:
------------
The environment script that should handle assetManager and photoshop
interaction

It should only work in 32bit Windows systems or under linux with wine (not
tested)

it also needs the comtypes to be installed to the current python environment

http://sourceforge.net/projects/comtypes/
"""



from comtypes import client
import oyAuxiliaryFunctions as oyAux
from oyProjectManager.models import asset, project, repository, abstractClasses






########################################################################
class PhotoshopEnvironment(abstractClasses.Environment):
    """the photoshop environment class
    """
    
    
    
    pass
    
    