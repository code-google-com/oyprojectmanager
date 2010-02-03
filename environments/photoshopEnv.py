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
from oyProjectManager.dataModels import assetModel, projectModel, repositoryModel, abstractClasses



__version__ = "10.1.5"







########################################################################
class PhotoshopEnv(abstractClasses.Environment):
    """the photoshop environment class
    """
    
    
    
    pass
    
    