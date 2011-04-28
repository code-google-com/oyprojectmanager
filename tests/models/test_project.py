# -*- coding: utf-8 -*-


import sys
import os
import shutil
import tempfile
import unittest
from xml.dom import minidom

from oyProjectManager.models import project, repository, asset






########################################################################
class ProjectTester(unittest.TestCase):
    """tests the Project class
    """
    
    
    
    #----------------------------------------------------------------------
    def setUp(self):
        """testing the settings path from the environment variable
        """
        
        # -----------------------------------------------------------------
        # start of the setUp
        # create the environment variable and point it to a temp directory
        #self.temp_settings_folder = tempfile.mkdtemp()
        self.temp_settings_folder = tempfile.mktemp()
        self.temp_projects_folder = tempfile.mkdtemp()
        
        os.environ["OYPROJECTMANAGER_PATH"] = self.temp_settings_folder
        os.environ["STALKER_REPOSITORY_PATH"] = self.temp_projects_folder
        
        # copy the default files to the folder
        self.package_path = os.path.abspath(
            os.path.dirname(
                os.path.dirname(
                    os.path.dirname(__file__)
                )
            )
        )
        
        self.default_settings_dir_path = os.path.join(
            self.package_path, "oyProjectManager", "settings" )
        
        shutil.copytree(
            self.default_settings_dir_path,
            self.temp_settings_folder,
        )
        
        # change the server path to a temp folder
        repository_settings_file_path = os.path.join(
            self.temp_settings_folder, 'repositorySettings.xml')
        
        # change the repositorySettings.xml by using the minidom
        xmlDoc = minidom.parse(repository_settings_file_path)
        
        serverNodes = xmlDoc.getElementsByTagName("server")
        for serverNode in serverNodes:
            serverNode.setAttribute("windows_path", self.temp_projects_folder)
            serverNode.setAttribute("linux_path", self.temp_projects_folder)
            serverNode.setAttribute("osx_path", self.temp_projects_folder)
        
        repository_settings_file = file(repository_settings_file_path,
                                        mode='w')
        xmlDoc.writexml(repository_settings_file, "\t", "\t", "\n")
    
    
    
    #----------------------------------------------------------------------
    def tearDown(self):
        """remove the temp folders
        """
        
        # delete the temp folder
        shutil.rmtree(self.temp_settings_folder)
        shutil.rmtree(self.temp_projects_folder)
    
    
    
    #----------------------------------------------------------------------
    def test_name_argument_formating(self):
        """testing if the name will be formatted correctly when creating a
        new project.
        """
        
        test_values = [
            ("test project", "TEST_PROJECT"),
            ("123123 test_project", "TEST_PROJECT"),
            ("123432!+!'^+Test_PRoject323^+'^%&+%&324", "TEST_PROJECT323324"),
            ("    ---test 9s_project", "TEST_9S_PROJECT"),
            ("    ---test 9s-project", "TEST_9S_PROJECT"),
            (" multiple     spaces are    converted to under     scores",
             "MULTIPLE_SPACES_ARE_CONVERTED_TO_UNDER_SCORES"),
            ("camelCase", "CAMEL_CASE"),
            ("CamelCase", "CAMEL_CASE"),
        ]
        
        for test_value in test_values:
            
            project_name = test_value[0]
            expected_project_name = test_value[1]
            
            new_project = project.Project(project_name)
            
            self.assertEqual(new_project.name, expected_project_name)
    
    
    
    #----------------------------------------------------------------------
    def test_name_property_formating(self):
        """testing if the name property will be formatted correctly.
        """
        
        test_values = [
            ("test project", "TEST_PROJECT"),
            ("123123 test_project", "TEST_PROJECT"),
            ("123432!+!'^+Test_PRoject323^+'^%&+%&324", "TEST_PROJECT323324"),
            ("    ---test 9s_project", "TEST_9S_PROJECT"),
            ("    ---test 9s-project", "TEST_9S_PROJECT"),
            (" multiple     spaces are    converted to under     scores",
             "MULTIPLE_SPACES_ARE_CONVERTED_TO_UNDER_SCORES"),
            ("camelCase", "CAMEL_CASE"),
            ("CamelCase", "CAMEL_CASE"),
        ]
        
        new_project = project.Project("TEST_NAME")
        
        for test_value in test_values:
            
            new_project.name = test_value[0]
            expected_project_name = test_value[1]
            
            self.assertEqual(new_project.name, expected_project_name)
    
    
    
    