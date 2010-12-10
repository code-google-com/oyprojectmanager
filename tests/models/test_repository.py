#!/usr/bin/env python
#coding:utf-8
# Author:  Erkan Ozgur Yilmaz
# Purpose: Testing the Repository
# Created: 11/21/2010

import sys
import unittest



if __name__=='__main__':
    unittest.main()
import os
import shutil
import tempfile
import mocker






########################################################################
class RepositoryTesterWithoutEnv(mocker.MockerTestCase):
    """tests the repository without the environment variables
    """
    
    
    #----------------------------------------------------------------------
    def setUp(self):
        """setting up the test
        """
        
        # check the environment and remove the OYPROJECTMANAGER_PATH variable
        # if there is one
        
        self.env_key = 'OYPROJECTMANAGER_PATH'
        self.env_value = None
        
        if os.environ.has_key(self.env_key):
            # store the variable in a local attribute and restore it later
            self.env_value = os.environ[self.env_key]
            os.environ.pop(self.env_key)
    
    
    
    #----------------------------------------------------------------------
    def tearDown(self):
        """revert everything back to normal
        """
        
        # add the environment value if there was any
        if self.env_value is not None:
            os.environ[self.env_key] = self.env_value
        
    
    
    
    #----------------------------------------------------------------------
    def test_repository_withoutEnv(self):
        """testing if the repository works without environment variables
        """
        
        from oyProjectManager.models import repository
        
        # create a repository object
        repo = repository.Repository()
        
        # do something
    
    
    
    #----------------------------------------------------------------------
    def test_getSettingsPath_without_environment_variable(self):
        """testing if the getSettingsPath returns the correct path when the
        environment variables is not set
        """
        from oyProjectManager.models import repository
        repo = repository.Repository()
        
        # this should return the default path
        
        
        package_path = os.path.abspath(
            os.path.dirname(
                os.path.dirname(
                    os.path.dirname(__file__)
                    )
                )
            )
        
        self.default_settings_path = os.path.join( package_path, 'settings' )
        
        self.assertEquals(repo.getSettingsPath(), self.default_settings_path)
    
    
    






########################################################################
class RepositoryTesterWithEnv(mocker.MockerTestCase):
    """tests the repository with environment variables
    """
    
    
    #----------------------------------------------------------------------
    def setUp(self):
        """testing the settings path from the environment variable
        """
        
        # -----------------------------------------------------------------
        # start of the setUp
        # create the environment variable and point it to a temp directory
        self.temp_settings_folder = tempfile.mkdtemp()
        self.temp_project_folder = tempfile.mkdtemp()
        
        os.environ['OYPROJECTMANAGER_PATH'] = self.temp_settings_folder
        
        
        # copy the default files to the folder
        self.package_path = os.path.abspath(
            os.path.dirname(
                os.path.dirname(
                    os.path.dirname(__file__)
                )
            )
        )
        
        self.default_settings_dir_path = os.path.join(
            self.package_path, 'settings' )
        
        # copy the setting files
        files = [ 'defaultProjectSettings.xml',
                  'environmentSettings.xml',
                  'repositorySettings.xml',
                  'users.xml',
                ]
        
        for file_ in files:
            shutil.copy2(
                os.path.join(
                    self.default_settings_dir_path,
                    file_)
                ,
                os.path.join(
                    self.temp_settings_folder,
                    file_)
                )
        
        # change the server path to a temp folder
        repository_settings_file_path = os.path.join(
            self.temp_settings_folder, 'repositorySettings.xml')
        
        repository_settings_file = file(repository_settings_file_path,
                                        mode='r+')
        
        lines = repository_settings_file.readlines()
        repository_settings_file.close()
        
        for i, line in enumerate(lines):
            if line.strip().startswith('serverPath='):
                lines[i] = 'serverPath="' + self.temp_project_folder + '"\n'
        
        repository_settings_file = file(repository_settings_file_path,
                                        mode='w')
        
        repository_settings_file.writelines( lines )
    
    
    
    #----------------------------------------------------------------------
    def test_getSettingsPath_with_environment_variable(self):
        """testing if the getSettingsPath returns the correct path when the
        environment variables is set
        """
        from oyProjectManager.models import repository
        repo = repository.Repository()
        
        # this should return the same path with the environment
        self.assertEqual(repo.getSettingsPath(), self.temp_settings_folder)
    
    
    
    #----------------------------------------------------------------------
    def test_create_project(self):
        """testing project creation
        """
        from oyProjectManager.models import repository
        repo = repository.Repository()
        
        project_name = 'TEST_PROJECT'
        
        newProject = repo.createProject(project_name)
        newProject.create()
        
        # lets check if there is a folder in the server path with the given
        # name
        self.assertTrue(
            os.path.exists(
                os.path.join(
                    repo.serverPath,
                    project_name
                    )
                )
            )
    
    
    
    #----------------------------------------------------------------------
    def tearDown(self):
        """remove the temp folders
        """
        
        # delete the temp folder
        shutil.rmtree(self.temp_settings_folder)
        shutil.rmtree(self.temp_project_folder)
    
    
    