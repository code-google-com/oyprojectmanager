
from oyProjectManager.dataModels import abstractClasses



__version__ = "10.1.11"




########################################################################
class EnvironmentFactory( abstractClasses.Singleton ):
    """creates environments
    """
    
    
    
    #----------------------------------------------------------------------
    @classmethod
    def create(cls, asset=None, environmentName=''):
        
        env = None
        
        if environmentName == 'MAYA':
            from oyProjectManager.environments import mayaEnv
            env = mayaEnv.MayaEnvironment( asset, 'MAYA' )
            
        elif environmentName == 'NUKE':
            from oyProjectManager.environments import nukeEnv
            env = nukeEnv.NukeEnvironment( asset, 'NUKE' )
            
        elif environmentName == 'HOUDINI':
            from oyProjectManager.environments import houdiniEnv
            env = houdiniEnv.HoudiniEnvironment( asset, 'HOUDINI' )
        
        return env