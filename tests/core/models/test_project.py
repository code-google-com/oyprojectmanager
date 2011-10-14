# -*- coding: utf-8 -*-

import os
import shutil
import tempfile
import unittest
from xml.dom import minidom
from sqlalchemy.exc import IntegrityError

from oyProjectManager import db
from oyProjectManager.core.models import Project, Sequence, Repository

import logging
logger = logging.getLogger("oyProjectManager.core.models")
logger.setLevel(logging.DEBUG)


class ProjectTester(unittest.TestCase):
    """tests the Project class
    """
    
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
        repository_settings_file.close()
        
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
    
    def tearDown(self):
        """remove the temp folders
        """
        
        # delete the temp folder
        shutil.rmtree(self.temp_settings_folder)
        shutil.rmtree(self.temp_projects_folder)
    
    def test_name_argument_formatting(self):
        """testing if the name will be formatted correctly when creating a
        new project.
        """
        
        for test_value in self._name_test_values:
            
            project_name = test_value[0]
            expected_project_name = test_value[1]
            
            new_project = Project(project_name)
            
            self.assertEqual(new_project.name, expected_project_name)
    
    def test_name_attribute_formatting(self):
        """testing if the name property will be formatted correctly.
        """
        
        new_project = Project("TEST_NAME")
        
        for test_value in self._name_test_values:
            
            new_project.name = test_value[0]
            expected_project_name = test_value[1]
            
            self.assertEqual(new_project.name, expected_project_name)
    
    def test_name_argument_is_None(self):
        """testing if a TypeError will be raised when the name argument is
        None.
        """
        self.assertRaises(TypeError, Project, None)
    
    def test_name_attribute_is_None(self):
        """testing if a TypeError will be raised when the name property is
        tried to be set to None
        """
        proj = Project("TEST_PROJECT")
        self.assertRaises(TypeError, setattr, proj, "name", None)
    
    def test_name_argument_is_empty_string(self):
        """testing if a ValueError will be raised when the name arugment is
        an empty string
        """
        self.assertRaises(ValueError, Project, "")
    
    def test_name_attribute_is_set_to_empty_string(self):
        """testing if a ValueError will be raised when the name property is
        tried to be set to empty string
        """
        proj = Project("TEST_PROJECT")
        self.assertRaises(ValueError, setattr, proj, "name", "")
    
    def test_name_argument_is_empty_string_after_validation(self):
        """testing if a ValueError will be raised when the name argument is not
        None nor empty string but an empty string after validation
        """
        
        # this is obviously not a valid name for a project
        test_name = "+++++^^^"
        self.assertRaises(ValueError, Project, test_name)
    
    def test_name_attribute_is_empty_string_after_validation(self):
        """testing if a ValueError will be raised when the name property is
        an empty string after validation
        """
        
        # this is again not a valid name for a project
        test_names = [
            "^^+'^+'%^+%",
            "__",
        ]
        
        proj = Project("TEST_PROJECT")
        
        for test_name in test_names:
            self.assertRaises(ValueError, setattr, proj, "name", test_name)
    
#    def test_create_sequence_raises_RuntimeError_if_the_project_is_not_created_yet(self):
#        """testing createSequence raises a RuntimeError if the project is not
#        created yet
#        """
#        
#        # create a new project and create a sequence
#        
#        test_proj = Project("TEST_PROJECT1221")
##        print "test_proj.fullPath", test_proj.fullPath
##        print "test_proj.exists:", test_proj.exists
#        
#        self.assertRaises(RuntimeError, test_proj.createSequence, "TEST_SEQ",
#                          "1")
#        
#        # and not when the test_proj is created
#        test_proj2 = Project("TEST_PROJECT13")
#        test_proj2.create()
#        test_proj2.createSequence("TEST_SEQ2", "1")
    
    def test___eq__operator(self):
        """testing the __eq__ (equal) operator
        """
        
        # create two projects
        proj1 = Project(name="TEST_PROJ1")
        proj2 = Project(name="TEST_PROJ1")
        
        self.assertEqual(proj1, proj2)

   
class Project_DB_Tester(unittest.TestCase):
    """Tests the design of the Projects after v0.2.0
    """
    
    
    #----------------------------------------------------------------------
    def setUp(self):
        
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
            self.temp_settings_folder
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
    
    def tearDown(self):
        """clean up the test
        """
        
        # delete the temp folder
        shutil.rmtree(self.temp_settings_folder)
        shutil.rmtree(self.temp_projects_folder)
    
    def test_project_initialization_with_database(self):
        """testing the project initialization occurs without any problem
        """

        test_value = "TEST_PROJECT"
        new_proj = Project(test_value)
        self.assertEqual(new_proj.name, test_value)

    def test_project_creation_for_new_project(self):
        """testing if the project creation occurs without any problem
        """

        new_proj = Project("TEST_PROJECT")
        new_proj.create()

        # now check if the folder is created
        self.assertTrue(os.path.exists(new_proj.fullPath))

        # and there is a .metadata.db file in that path
        self.assertTrue(os.path.exists(new_proj.metadata_full_path))

    def test_project_stored_and_retrieved_correctly(self):
        """testing if the project is stored and retrieved correctly
        """

        new_proj = Project(name="TEST_PROJECT")
        new_proj.create()

        name = new_proj.name
        path = new_proj.path
        fullPath = new_proj.fullPath

        del new_proj

        new_proj_DB = db.query(Project).first()
        
        self.assertEqual(new_proj_DB.name, name)
        self.assertEqual(new_proj_DB.path, path)
        self.assertEqual(new_proj_DB.fullPath, fullPath)
    
    def test_project_restores_from_database_1(self):
        """testing if a project restores it self from the database with all its
        connections
        """
        
        # we need to create a new project and a sequence
        new_proj = Project("TEST_PROJECT")
        new_proj.create()
        
        test_description = "test description"
        new_proj.description = test_description
        new_proj.save()
        
        del new_proj
        
        # now retrieve the project by recreating it
        new_proj2 = Project("TEST_PROJECT")
        
        self.assertEqual(new_proj2.description, test_description)

    def test_project_restores_from_database_2(self):
        """testing if a project restores it self from the database with all its
        connections
        """
        
        # we need to create a new project and a sequence
        new_proj = Project("TEST_PROJECT")
        new_proj.create()
        
        new_seq = Sequence(new_proj, "TEST_SEQ")
        new_seq.create()
        
        db.session.add(new_proj)
        db.session.commit()
        
        del new_proj
        del new_seq
        
        # now retrieve the project by recreating it
        new_proj2 = Project(name="TEST_PROJECT")
        
        self.assertEqual(new_proj2.sequences[0].name, "TEST_SEQ")
    
    def test_calling_create_over_and_over_again_will_not_cause_any_problem(self):
        """testing if calling the create over and over again will not create a
        problem
        """
        
        # we need to create a new project and a sequence
        new_proj = Project("TEST_PROJECT")
        new_proj.create()
        new_proj.create()
        new_proj.create()
        new_proj.create()
        new_proj.create()
        new_proj.create()
    
    def test_creating_two_different_projects_and_calling_create_in_mixed_order(self):
        """testing no error will be raised when creating two Project instances
        and calling their create method in mixed order
        """
        
        new_proj1 = Project("TEST_PROJECT1")
        new_proj2 = Project("TEST_PROJECT2")
        
        new_proj1.create()
        new_proj2.create()
    
    def test_creating_two_different_projects_with_same_name_and_calling_create_in_mixed_order(self):
        """testing no error will be raised when creating two Project instances
        and calling their create method in mixed order
        """
        
        new_proj1 = Project("TEST_PROJECT1")
        new_proj2 = Project("TEST_PROJECT1")
        
        new_proj1.create()
        self.assertRaises(IntegrityError, new_proj2.create)
    
    def test_calling_commit_multiple_times(self):
        """testing if there is no problem of calling Project.save() multiple
        times
        """
        
        new_proj = Project("TEST_PROJECT")
        new_proj.create()
        new_proj.save()
        new_proj.save()
    
    def test_calling_create_on_a_project_which_is_retrieved_from_db(self):
        """testing if there will be no error messages generated when the new
        project is retrieved from the database and the create method of this
        project is called
        """
        
        project_name = "TEST_PROJECT1"
        new_proj1 = Project(project_name)
        new_proj1.create()
        
        new_proj2 = Project(project_name)
        new_proj2.create()
