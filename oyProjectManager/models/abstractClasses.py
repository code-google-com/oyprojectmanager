


__version__ = "10.4.28"






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
    def __init__(self, asset=None, name='', extensions=[]):
        
        self._name = name
        self._asset = asset
        self._extensions = extensions
        self._project = None
        self._sequence = None
    
    
    
    #----------------------------------------------------------------------
    def __str__(self):
        """the string represantation of the environment
        """
        return self._name
    
    
    
    #----------------------------------------------------------------------
    def _getAsset(self):
        """returns the bound asset object
        """
        return self._asset
    
    
    
    #----------------------------------------------------------------------
    def _setAsset(self, asset):
        """sets the asset object
        """
        self._asset = asset
    
    asset = property( _getAsset, _setAsset )
    
    
    
    #----------------------------------------------------------------------
    def _getName(self):
        """returns the environment name
        """
        return self._name
    
    
    
    #----------------------------------------------------------------------
    def _setName(self, name):
        """sets the environment name
        """
        self._name = name
    
    name = property( _getName, _setName )
    
    
    
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
    def getProject(self):
        """returns the current project from environment
        """
        pass
    
    
    
    #----------------------------------------------------------------------
    def setProject(self, projectName, sequenceName):
        """sets the project and sequence names, thus the working environment
        of the current environment
        """
        pass
    
    
    
    #----------------------------------------------------------------------
    def setOutputFileName(self):
        """sets the output file names
        """
        pass
    
    
    
    #----------------------------------------------------------------------
    def appendToRecentFiles(self, path):
        """appends the given path to the recent files list
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
        return None, None
    
    
    
    #----------------------------------------------------------------------
    def setFrameRange(self, startFrame=1, endFrame=100):
        """sets the frame range in the environment
        """
        pass
    
    
    
    #----------------------------------------------------------------------
    def getTimeUnit(self):
        """returns the time unit of the environment
        """
        pass
    
    
    
    #----------------------------------------------------------------------
    def setTimeUnit(self, timeUnit='pal' ):
        """sets the frame rate of the environment
        """
        pass
        
    
    
    #----------------------------------------------------------------------
    def _getExtensions(self):
        """returns the extensions of environment
        """
        return self._extensions
    
    
    
    #----------------------------------------------------------------------
    def _setExtensions(self, extensions):
        """sets the extensions
        """
        self._extensions = extensions
    
    extensions = property(_getExtensions, _setExtensions)
    
    
    
    #----------------------------------------------------------------------
    def hasValidExtension(self, fileName):
        """returns true if the given fileNames extension is in the extensions
        list false otherwise
        
        accepts:
        - a full path with extension or not
        - a filen name with extension or not
        - an extension with a dot on the start or not
        """
        
        if fileName is None:
            return False
        
        if fileName.split('.')[-1].lower() in self._extensions:
            return True
        
        return False
    
    
    
    #----------------------------------------------------------------------
    def loadReferences(self):
        """loads all the references
        """
        pass
    
    
    
    #----------------------------------------------------------------------
    def replaceAssets(self, sourceAsset, targetAsset):
        """replaces the source asset with the target asset
        """
        pass
    