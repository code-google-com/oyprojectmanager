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
        self.temp_settings_folder = tempfile.mktemp()
        self.temp_projects_folder = tempfile.mkdtemp()
        
        # copy the test settings
        import oyProjectManager
        
        self._test_settings_folder = os.path.join(
            os.path.dirname(
                os.path.dirname(
                    oyProjectManager.__file__
                )
            ),
            "tests", "test_settings"
        )
        
        os.environ["OYPROJECTMANAGER_PATH"] = self.temp_settings_folder
        os.environ["STALKER_REPOSITORY_PATH"] = self.temp_projects_folder
        
        # copy the default files to the folder
        shutil.copytree(
            self._test_settings_folder,
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
        
        
        self._name_test_values = [
            ("test project", "TEST_PROJECT"),
            ("123123 test_project", "TEST_PROJECT"),
            ("123432!+!'^+Test_PRoject323^+'^%&+%&324", "TEST_PROJECT323324"),
            ("    ---test 9s_project", "TEST_9S_PROJECT"),
            ("    ---test 9s-project", "TEST_9S_PROJECT"),
            (" multiple     spaces are    converted to under     scores",
             "MULTIPLE_SPACES_ARE_CONVERTED_TO_UNDER_SCORES"),
            ("camelCase", "CAMEL_CASE"),
            ("CamelCase", "CAMEL_CASE"),
            ("_Project_Setup_", "PROJECT_SETUP_"),
            ("_PROJECT_SETUP_", "PROJECT_SETUP_"),
            ("FUL_3D", "FUL_3D"),
        ]
    
    
    
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
        
        for test_value in self._name_test_values:
            
            project_name = test_value[0]
            expected_project_name = test_value[1]
            
            new_project = project.Project(project_name)
            
            self.assertEqual(new_project.name, expected_project_name)
    
    
    
    #----------------------------------------------------------------------
    def test_name_property_formating(self):
        """testing if the name property will be formatted correctly.
        """
        
        new_project = project.Project("TEST_NAME")
        
        for test_value in self._name_test_values:
            
            new_project.name = test_value[0]
            expected_project_name = test_value[1]
            
            self.assertEqual(new_project.name, expected_project_name)
    
    
    
    #----------------------------------------------------------------------
    def test_name_argument_is_None(self):
        """testing if a ValueError will be raised when the name argument is
        None.
        """
        
        self.assertRaises(ValueError, project.Project, None)
    
    
    
    #----------------------------------------------------------------------
    def test_name_property_is_None(self):
        """testing if a ValueError will be raised when the name property is
        tried to be set to None
        """
        
        proj = project.Project("TEST_PROJECT")
        
        self.assertRaises(ValueError, setattr, proj, "name", None)
    
    
    
    #----------------------------------------------------------------------
    def test_name_argument_is_empty_string(self):
        """testing if a ValueError will be raised when the name arugment is
        an empty string
        """
        
        self.assertRaises(ValueError, project.Project, "")
    
    
    
    #----------------------------------------------------------------------
    def test_name_property_is_set_to_empty_string(self):
        """testing if a ValueError will be raised when the name property is
        tried to be set to empty string
        """
        
        proj = project.Project("TEST_PROJECT")
        
        self.assertRaises(ValueError, setattr, proj, "name", "")
    
    
    
    #----------------------------------------------------------------------
    def test_name_argument_is_empty_string_after_validation(self):
        """testing if a ValueError will be raised when the name argument is not
        None nor empty string but an empty string after validation
        """
        
        # this is obviously not a valid name for a project
        test_name = "+++++^^^"
        
        self.assertRaises(ValueError, project.Project, test_name)
    
    
    
    #----------------------------------------------------------------------
    def test_name_property_is_empty_string_after_validation(self):
        """testing if a ValueError will be raised when the name property is
        an empty string after validation
        """
        
        # this is again not a valid name for a project
        test_names = [
            "^^+'^+'%^+%",
            "__",
        ]
        
        proj = project.Project("TEST_PROJECT")
        
        for test_name in test_names:
            self.assertRaises(ValueError, setattr, proj, "name", test_name)
    
    
    
    #----------------------------------------------------------------------
    def test_updateSequenceList_working_properly(self):
        """testing if updateSequenceList is working properly
        """
        
        # create a new project and create a sequence
        
        proj_and_seq_names = [("B", "FUL_3D")]
        
        repo = repository.Repository()
        
        # create the projects
        for proj_and_seq_name in proj_and_seq_names:
            proj_name = proj_and_seq_name[0]
            seq_name = proj_and_seq_name[1]
            
            # create the project
            newProj = repo.createProject(proj_name)
            newSeq = newProj.createSequence(seq_name, "1")
            
            # now create another project instance to get the sequences
            newProj2 = project.Project(proj_name)
            
            self.assertEqual(newProj2.sequences(), [newSeq])
    
    
    
    #----------------------------------------------------------------------
    def test___eq__operator(self):
        """testing the __eq__ (equal) operator
        """
        
        # create two projects
        