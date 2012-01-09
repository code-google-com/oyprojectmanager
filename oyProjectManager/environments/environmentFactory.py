# -*- coding: utf-8 -*-
# Copyright (c) 2009-2012, Erkan Ozgur Yilmaz
# 
# This module is part of oyProjectManager and is released under the BSD 2
# License: http://www.opensource.org/licenses/BSD-2-Clause

import os
from xml.dom import minidom
from oyProjectManager.core.abstractClasses import Singleton
from oyProjectManager.core.models import Repository


class EnvironmentFactory(Singleton):
    """creates environments
    """
    
    
    def __init__(self):
        
        # create the repository and then delete it
        self._repo = Repository()
        
        # we should know where the settings file is
        # get the settings dir path
        self._settings_file_name = 'environmentSettings.xml'
        self._settings_file_path = self._repo.settings_dir_path
        self._settings_file_full_path = os.path.join(self._settings_file_path,
                                                     self._settings_file_name)
        
        # store environment settings in virtual environments
        self._virtualEnvironments = dict()
        
        self._hasReadSettings = False
        
        # now parse the settings file
        self._parseSettings()
        
    
    
    
    def _parseSettings(self):
        """parses the setting file
        """
        
        if not self._hasReadSettings:
            
            xmlNodes = minidom.parse( self._settings_file_full_path )
            
            rootNode = xmlNodes.childNodes[0]
            
            for environment in rootNode.getElementsByTagName('environment'):
                envName = environment.getAttribute( 'name' )
                
                # get lower extensions
                extensions = map(
                    unicode.lower,
                    environment.getAttribute('extensions').split(',')
                )
                
                self._virtualEnvironments[envName] = \
                    VirtualEnvironment(envName, extensions)
            
            # don't parse it over and over again
            self._hasReadSettings = True
    
    
    
    
    def create(self, asset=None, environmentName=''):
        """creates an environment with given name
        """
        
        envClass = None
        env = None
        
        if environmentName == 'MAYA':
            from oyProjectManager.environments import mayaEnv
            envClass = mayaEnv.Maya
            
        elif environmentName == 'NUKE':
            from oyProjectManager.environments import nukeEnv
            envClass = nukeEnv.Nuke
            
        elif environmentName == 'HOUDINI':
            from oyProjectManager.environments import houdiniEnv
            envClass = houdiniEnv.Houdini
        
        # create the environment if the envClass is not None
        if envClass is not None:
            # get the virtual environment and set variables
            extensions = self._virtualEnvironments[ environmentName ].extensions
            env = envClass( asset, environmentName, extensions)
            
        return env







class VirtualEnvironment(object):
    """this is a class just to hold environment settings
    """
    
    
    
    
    def __init__(self, name=None, _extensions=None):
        
        if _extensions is None:
            _extensions = []
        
        self._name = name
        self._extensions = _extensions # the list of extensions that this environment supports
    
    
    
    
    def __str__(self):
        """the string
        """
        return self._name
    
    
    
    
    def _getExtensions(self):
        """returns the extensions
        """
        return self._extensions
    
    
    
    
    def _setExtensions(self, extensions):
        """sets the extensions
        """
        self._extensions = extensions
    
    extensions = property( _getExtensions, _setExtensions )
    
    
    
    
    def _getName(self):
        """returns teh name of the environment
        """
        return self._name
    
    
    
    
    def _setName(self, name):
        """sets the virtual environment name
        """
        self._name = name
    
    name = property( _getName, _setName )
    
    
