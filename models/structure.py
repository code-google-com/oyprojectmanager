########################################################################
class Structure(object):
    _shotDependentFolders = [] * 0
    _shotIndependentFolders = [] * 0
    
    
    
    
    #----------------------------------------------------------------------
    def __init__(self, shotDependentFolders=None, shotIndependentFolders=None):
        self._shotDependentFolders = shotDependentFolders
        self._shotIndependentFolders = shotIndependentFolders
    
    
    
    #----------------------------------------------------------------------
    def setShotDependentFolders(self, folders):
        """sets shot dependent folders
        """
        self._shotDependentFolders = folders
    
    
    
    #----------------------------------------------------------------------
    def setShotIndependentFolders(self, folders):
        """sets shot independent folders
        """
        self._shotIndependentFolders = folders
    
    
    
    #----------------------------------------------------------------------
    def getShotDependentFolders(self):
        """returns shot dependent folders as list
        """
        return self._shotDependentFolders
    
    
    
    #----------------------------------------------------------------------
    def getShotIndependentFolders(self):
        """returns shot independent folders as list
        """
        return self._shotIndependentFolders