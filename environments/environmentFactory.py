import os
from xml.dom import minidom
from oyProjectManager.dataModels import abstractClasses, repositoryModel



__version__ = "10.3.10"






########################################################################
class EnvironmentFactory( abstractClasses.Singleton ):
    """creates environments
    """
    
    
    
    #----------------------------------------------------------------------
    def __init__(self):
        
        # create the repository and then delete it
        self._repo = repositoryModel.Repository()
        
        # we should know where the settings file is
        # get the settings dir path
        self._settingsFileName = 'environmentSettings.xml'
        self._settingsFilePath = self._repo.settingsDirPath
        self._settingsFileFullPath = os.path.join( self._settingsFilePath, self._settingsFileName )
        
        # store environment settings in virutual environments
        self._virtualEnvironments = dict()
        
        self._hasReadSettings = False
        
        # now parse the settings file
        self._parseSettings()
        
    
    
    #----------------------------------------------------------------------
    def _parseSettings(self):
        """parses the setting file
        """
        
        if not self._hasReadSettings:
            
            xmlNodes = minidom.parse( self._settingsFileFullPath )
            
            rootNode = xmlNodes.childNodes[0]
            
            for environment in rootNode.getElementsByTagName('environment'):
                envName = environment.getAttribute( 'name' )
                
                # get lower extensions
                extensions = map( unicode.lower, environment.getAttribute( 'extensions' ).split(','))
                
                self._virtualEnvironments[ envName ] = VirtualEnvironment( envName, extensions )
            
            # don't reparse it over and over again
            self._hasReadSettings = True
    
    
    
    #----------------------------------------------------------------------
    def create(self, asset=None, environmentName=''):
        """creates an environment with given name
        """
        
        envClass = None
        env = None
        
        if environmentName == 'MAYA':
            from oyProjectManager.environments import mayaEnv
            #env = mayaEnv.MayaEnvironment( asset, environmentName )
            envClass = mayaEnv.MayaEnvironment
            
        elif environmentName == 'NUKE':
            from oyProjectManager.environments import nukeEnv
            #env = nukeEnv.NukeEnvironment( asset, environmentName )
            envClass = nukeEnv.NukeEnvironment
            
        elif environmentName == 'HOUDINI':
            from oyProjectManager.environments import houdiniEnv
            #env = houdiniEnv.HoudiniEnvironment( asset, environmentName )
            envClass = houdiniEnv.HoudiniEnvironment
        
        # create the environment if the envClass is not None
        
        if envClass is not None:
            # get the virtual environment and set variables
            extensions = self._virtualEnvironments[ environmentName ].extensions
            env = envClass( asset, environmentName, extensions )
            
        return env






########################################################################
class VirtualEnvironment(object):
    """this is a class just to hold environment settings
    """
    
    
    
    #----------------------------------------------------------------------
    def __init__(self, name=None, _extensions=[]):
        self._name = name
        self._extensions = _extensions # the list of extensions that this environment supports
    
    
    
    #----------------------------------------------------------------------
    def __str__(self):
        """the string
        """
        return self._name
    
    
    
    #----------------------------------------------------------------------
    def _getExtensions(self):
        """returns the extensions
        """
        return self._extensions
    
    
    
    #----------------------------------------------------------------------
    def _setExtensions(self, extensions):
        """sets the extensions
        """
        self._extensions = extensions
    
    extensions = property( _getExtensions, _setExtensions )
    
    
    
    #----------------------------------------------------------------------
    def _getName(self):
        """returns teh name of the environment
        """
        return self._name
    
    
    
    #----------------------------------------------------------------------
    def _setName(self, name):
        """sets the virtual environment name
        """
        self._name = name
    
    name = property( _getName, _setName )
    
    
    