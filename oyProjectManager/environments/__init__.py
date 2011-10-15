#-*- coding: utf-8 -*-








class EnvironmentBase(object):
    """the environment base class
    
    In oyProjectManager, an Environment is a host application like Maya, Nuke,
    Houdini etc.
    
    Generally a GUI for the end user is given an environment which helps
    the Qt Gui to be able to open, save, import or export an Asset without
    knowing the details of the environment.
    """
    
    def __init__(self, asset=None, name='', extensions=[]):
        
        self._name = name
        self._asset = asset
        self._extensions = extensions
        self._project = None
        self._sequence = None
    
    def __str__(self):
        """the string representation of the environment
        """
        return self._name
    
    def _getAsset(self):
        """returns the bound asset object
        """
        return self._asset
    
    def _setAsset(self, asset):
        """sets the asset object
        """
        self._asset = asset
    
    asset = property( _getAsset, _setAsset )
    
    def _getName(self):
        """returns the environment name
        """
        return self._name
    
    def _setName(self, name):
        """sets the environment name
        """
        self._name = name
    
    name = property( _getName, _setName )
    
    def save(self):
        """the save action
        """
        raise NotImplemented
    
    def export(self, asset):
        """the export action
        """
        raise NotImplemented
    
    def open_(self, force=False):
        """the open action
        """
        raise NotImplemented
    
    def import_(self, asset):
        """the import action
        """
        raise NotImplemented
    
    def reference(self, asset):
        """the reference action
        """
        raise NotImplemented
    
    def getPathVariables(self):
        """gets the file name from environment
        """
        raise NotImplemented
    
    def getProject(self):
        """returns the current project from environment
        """
        raise NotImplemented
    
    def setProject(self, projectName, sequenceName):
        """sets the project and sequence names, thus the working environment
        of the current environment
        """
        raise NotImplemented
    
    def setOutputFileName(self):
        """sets the output file names
        """
        raise NotImplemented
    
    def appendToRecentFiles(self, path):
        """appends the given path to the recent files list
        """
        raise NotImplemented
    
    def checkReferenceVersions(self):
        """checks the referenced asset versions
        
        returns list of asset objects
        """
        raise NotImplemented
    
    def getReferencedAssets(self):
        """returns the assets those been referenced to the current asset
        
        returns list of asset objects
        """
        raise NotImplemented
    
    def updateAssets(self, assetTupleList):
        """updates the assets to the latest versions
        """
        raise NotImplemented
    
    def getFrameRange(self):
        """returns the frame range from the environment
        """
        raise NotImplemented
    
    def setFrameRange(self, startFrame=1, endFrame=100):
        """sets the frame range in the environment
        """
        raise NotImplemented
    
    def getTimeUnit(self):
        """returns the time unit of the environment
        """
        raise NotImplemented
    
    def setTimeUnit(self, timeUnit='pal' ):
        """sets the frame rate of the environment
        """
        raise NotImplemented
    
    def _getExtensions(self):
        """returns the extensions of environment
        """
        return self._extensions
    
    def _setExtensions(self, extensions):
        """sets the extensions
        """
        self._extensions = extensions
    
    extensions = property(_getExtensions, _setExtensions)
    
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
    
    def loadReferences(self):
        """loads all the references
        """
        raise NotImplemented
    
    def replaceAssets(self, sourceAsset, targetAsset):
        """replaces the source asset with the target asset
        """
        raise NotImplemented