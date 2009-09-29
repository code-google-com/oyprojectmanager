########################################################################
class AssetType(object):
    """Holds data like:\n
    - the asset type name
    - relative path of that type
    - the shot dependency of that AssetType
    """
    
    
    
    #----------------------------------------------------------------------
    def __init__(self, name='', path='', shotDependent=False, playblastFolder=''):
        self._name = name
        self._path = path
        self._shotDependency = shotDependent
        self._playblastFolder = playblastFolder
    
    
    
    #----------------------------------------------------------------------
    def getName(self):
        """return AssetType name
        """
        return self._name
    
    
    
    #----------------------------------------------------------------------
    def getPath(self):
        """returns AssetType path
        """
        return self._path
    
    
    
    #----------------------------------------------------------------------
    def isShotDependent(self):
        """returns True or False depending on to the shot dependency
        """
        return self._shotDependency
    
    
    
    #----------------------------------------------------------------------
    def getPlayblastFolder(self):
        """returns playblast folder of that asset type
        """
        return self._playblastFolder
    
    
    
    #----------------------------------------------------------------------
    def setName(self, name):
        """sets asset type name
        """
        self._name = name
    
    
    
    #----------------------------------------------------------------------
    def setPath(self, path):
        """sets asset type path
        """
        self._path = path
    
    
    
    #----------------------------------------------------------------------
    def setShotDependency(self, shotDependency):
        """sets shot dependency of that asset type
        """
        self._shotDependency = shotDependency

