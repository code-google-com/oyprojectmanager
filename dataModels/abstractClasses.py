
__version__ = "9.12.27"






#######################################################################
class Singleton(object):
    _instance = None
    
    #----------------------------------------------------------------------
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(Singleton, cls).__new__(cls, *args, **kwargs)
            
        return cls._instance





########################################################################
class Environment(object):
    """the environment base class
    """
    
    #----------------------------------------------------------------------
    def __init__(self, asset=None):
        
        self._asset = asset
        #assert(isinstance( self._asset, assetModel.Asset) )
    
    
    #----------------------------------------------------------------------
    def save(self):
        """the save action
        """
        pass
    
    
    
    #----------------------------------------------------------------------
    def export(self):
        """the export action
        """
        pass
    
    
    
    #----------------------------------------------------------------------
    def open_(self, force=False):
        """the open action
        """
        pass
    
    
    
    #----------------------------------------------------------------------
    def import_(self):
        """the import action
        """
        pass
    
    
    
    #----------------------------------------------------------------------
    def reference(self):
        """the reference action
        """
        pass
    
    
    
    #----------------------------------------------------------------------
    def getPathVariables(self):
        """gets the file name from environment
        """
        pass
    
    
    
    #----------------------------------------------------------------------
    def setOutputFileName(self):
        """sets the output file names
        """
        pass
    
    
    
    #----------------------------------------------------------------------
    def checkReferenceVersions(self):
        """checks the referenced asset versions
        
        returns list of asset objects
        """
        pass
    
    
    
    #----------------------------------------------------------------------
    def getReferencedAssets(self):
        """returns the assets those been referenced to the current asset
        
        returns list of asset objects
        """
        pass
    
    
    
    #----------------------------------------------------------------------
    def updateAssets(self, assetTupleList):
        """updates the assets to the latest versions
        """
        pass
    
    
    
    #----------------------------------------------------------------------
    def getFrameRange(self):
        """returns the frame range from the environment
        """
        pass
    
    
    
    #----------------------------------------------------------------------
    def setFrameRange(self, startFrame, endFrame):
        """sets the frame range in the environment
        """
        pass
    