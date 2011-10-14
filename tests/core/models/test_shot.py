import os
import shutil
import tempfile
import unittest
from xml.dom import minidom
from sqlalchemy.exc import IntegrityError
import oyProjectManager
from oyProjectManager.core.models import Project, Sequence, Shot, Version


class ShotTester(unittest.TestCase):
    """tests the Shot class
    """
    
    def setUp(self):
        """setup the test settings with environment variables
        """
        
        # -----------------------------------------------------------------
        # start of the setUp
        # create the environment variable and point it to a temp directory
        self.temp_settings_folder = tempfile.mktemp()
        self.temp_projects_folder = tempfile.mkdtemp()
        
        # copy the test settings
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
        
        
        self.test_proj = Project("TEST_PROJ1")
        self.test_proj.create()
        
        self.test_seq = Sequence(self.test_proj, "TEST_SEQ")
        self.test_seq.create()
        
        self.kwargs = {
            "sequence": self.test_seq,
            "name": "SH001",
            "start_frame": 1,
            "end_frame": 100,
            "description": "Test shot"
        }
        
        self.test_shot = Shot(**self.kwargs)
        
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
    
    def test_name_argument_is_skipped(self):
        """testing if a TypeError will be raised when the name argument is
        skipped
        """
        self.kwargs.pop("name")
        self.assertRaises(TypeError, Shot, **self.kwargs)
    
    def test_name_argument_is_None(self):
        """testing if a TypeError will be raised when the name argument is None
        """
        self.kwargs["name"] = None
        self.assertRaises(TypeError, Shot, **self.kwargs)

    def test_name_attribute_is_None(self):
        """testing if a TypeError will be raised when the name attribute is set
        to None
        """
        self.assertRaises(TypeError, setattr, self.test_shot, "name", None)
    
    def test_name_argument_is_empty_string(self):
        """testing if a ValueError will be raised when the name argument is an
        empty string
        """
        self.kwargs["name"] = ""
        self.assertRaises(ValueError, Shot, **self.kwargs)
    
    def test_name_attribute_is_set_to_empty_string(self):
        """testing if a ValueError will be raised when the name attribute is
        set to an empty string
        """
        self.assertRaises(ValueError, setattr, self.test_shot, "name", "")
    
    def test_name_argument_is_not_a_string(self):
        """testing if a TypeError will be raised when the name argument is not
        a string
        """
        self.kwargs["name"] = 1231
        self.assertRaises(TypeError, Shot, **self.kwargs)
    
    def test_name_attribute_is_not_a_string(self):
        """testing if a TypeError will be raised when the name attribute is not
        a string
        """
        self.assertRaises(TypeError, setattr, self.test_shot, "name", 123)
    
    def test_name_argument_formatted_correctly(self):
        """testing if the name attribute is formatted correctly when the class
        is initialized
        """
        self.fail("test is not implemented yet")
    
    def test_name_attribute_formatted_correctly(self):
        """testing if the name attribute is formatted correctly
        """
        self.fail("test is not implemented yet")
    
    def test_name_is_already_defined_in_the_sequence(self):
        """testing if an IntegrityError will be raised when the shot name is
        already defined in the given Sequence
        """
        self.kwargs["name"] = "SH101"
        new_shot1 = Shot(**self.kwargs)
        new_shot2 = Shot(**self.kwargs)
        new_shot2.sequence.session.add_all([new_shot1, new_shot2])
        self.assertRaises(IntegrityError, new_shot3.sequence.session.commit)
    
    def test_name_is_already_defined_in_the_sequence_for_an_already_created_one(self):
        """testing if a ValueError will be raised when the name is already
        defined for a Shot in the same Sequence instance
        """
        self.kwargs["name"] = "SH101"
        new_shot1 = Shot(**self.kwargs)
        new_shot1.save()
        
        self.assertRaises(ValueError, Shot, **self.kwargs)
    
    def test_sequence_argument_is_skipped(self):
        """testing if a RuntimeError will be raised when the sequence argument
        is skipped
        """
        self.kwargs.pop("sequence")
        self.assertRaises(RuntimeError, Shot, **self.kwargs)
    
    def test_sequence_argument_is_None(self):
        """testing if a RuntimeError will be raised when the sequence argument
        is None
        """
        self.kwargs["sequence"] = None
        self.assertRaises(RuntimeError, Shot, **self.kwargs)
    
    def test_sequence_argument_is_not_a_Sequence_instance(self):
        """testing if a TypeError will be raised when the sequence argument is
        not a Sequence instance
        """
        self.kwargs["sequence"] = "not a sequence instance"
        self.assertRaises(TypeError, Shot, **self.kwargs)
    
    def test_sequence_argument_is_working_properly(self):
        """testing if the sequence argument is working correctly
        """
        self.assertIs(self.test_shot.sequence, self.test_seq)
    
    def test_sequence_attribute_is_read_only(self):
        """testing if the sequence attribute is read-only
        """
        new_seq = Sequence(self.test_proj, "TEST_SEQ2")
        new_seq.create()
        self.assertRaises(AttributeError, setattr, self.test_shot, "sequence",
                          new_seq)
    
    def test_start_frame_argument_is_skipped(self):
        """testing if the start_frame attribute will be set to the default
        value when the start_frame argument is skipped
        """
        self.kwargs.pop("start_frame")
        new_shot = Shot(**self.kwargs)
        self.assertEqual(new_shot.start_frame, 1)
    
    def test_start_frame_argument_is_None(self):
        """testing if the start_frame attribute will be set to the default
        value when the start_frame argument is skipped
        """
        self.kwargs["start_frame"] = None
        new_shot = Shot(**self.kwargs)
        self.assertEqual(new_shot.start_frame, 1)
    
    def test_start_frame_attribute_is_None(self):
        """testing if the start_frame attribute will be set to the default
        value when it is set to None
        """
        self.test_shot.start_frame = None
        self.assertEqual(self.test_shot.start_frame, 1)
        
    
    def test_start_frame_argument_is_not_integer(self):
        """testing if a TypeError will be raised when the start_frame argument
        is not an integer
        """
        self.kwargs["start_frame"] = "asdfa"
        self.assertRaises(TypeError, Shot, **self.kwargs)
    
    def test_start_frame_attribute_is_not_integer(self):
        """testing if a TypeError will be raised when the start_frame attribute
        is not set to an integer value
        """
        self.assertRaises(TypeError, setattr, self.test_shot, "start_frame",
                          "asdfs")
    
    def test_start_frame_attribute_is_working_properly(self):
        """testing if the start_frame attribute is working properly
        """
        test_value = 10
        self.test_shot.start_frame = test_value
        self.assertEqual(self.test_shot.start_frame, test_value)
    
    def test_start_frame_attribute_updates_the_duration_attribute(self):
        """testing if the start_frame attribute updates the duration attribute
        value
        """
        self.test_shot.start_frame = 10
        self.assertEqual(self.test_shot.end_frame, 100)
        self.assertEqual(self.test_shot.duration, 91)
    
    def test_end_frame_argument_is_skipped(self):
        """testing if the end_frame attribute will be set to the default
        value when the end_frame argument is skipped
        """
        self.kwargs.pop("end_frame")
        new_shot = Shot(**self.kwargs)
        self.assertEqual(new_shot.end_frame, 1)
    
    def test_end_frame_argument_is_None(self):
        """testing if the end_frame attribute will be set to the default
        value when the end_frame argument is skipped
        """
        self.kwargs["end_frame"] = None
        new_shot = Shot(**self.kwargs)
        self.assertEqual(new_shot.end_frame, 1)
    
    def test_end_frame_attribute_is_Non(self):
        """testing if the end_frame attribute will be set to the default
        value when it is set to None
        """
        self.test_shot.end_frame = None
        self.assertEqual(self.test_shot.end_frame, 1)
    
    def test_end_frame_argument_is_not_integer(self):
        """testing if a TypeError will be raised when the end_frame argument
        is not an integer
        """
        self.kwargs["end_frame"] = "asdfa"
        self.assertRaises(TypeError, Shot, **self.kwargs)
    
    def test_end_frame_attribute_is_not_integer(self):
        """testing if a TypeError will be raised when the end_frame attribute
        is not set to an integer value
        """
        self.assertRaises(TypeError, setattr, self.test_shot, "end_frame",
                          "asdfs")
    
    def test_end_frame_attribute_is_working_properly(self):
        """testing if the end_frame attribute is working properly
        """
        test_value = 10
        self.test_shot.end_frame = test_value
        self.assertEqual(self.test_shot.end_frame, test_value)
    
    def test_end_frame_attribute_updates_the_duration_attribute(self):
        """testing if the end_frame attribute updates the duration attribute
        value
        """
        self.test_shot.end_frame = 200
        self.assertEqual(self.test_shot.start_frame, 1)
        self.assertEqual(self.test_shot.duration, 200)
       
    def test_description_argument_is_skipped(self):
        """testing if the description attribute will be set to an empty string
        when the description argument is skipped
        """
        self.kwargs.pop("description")
        new_shot = Shot(**self.kwargs)
        self.assertEqual(new_shot.description, "")
    
    def test_description_argument_is_None(self):
        """testing if the description attribute will be set to an empty string
        when the description argument is None
        """
        self.kwargs["description"] = None
        new_shot = Shot(**self.kwargs)
        self.assertEqual(new_shot.description, "")
    
    def test_description_attribute_is_None(self):
        """testing if the description attribute will be set to an empty string
        when it is set to none
        """
        new_shot = Shot(**self.kwargs)
        new_shot.description = None
        self.assertEqual(new_shot.description, "")
    
    def test_description_argument_is_not_string(self):
        """testing if a TypeError will be raised when the description argument
        is not a string
        """
        self.kwargs["description"] = 10
        self.assertRaises(TypeError, Shot, **self.kwargs)
    
    def test_description_attribute_is_not_string(self):
        """testing if a TypeError will be raised when the description attribute
        is not a string
        """
        self.assertRaises(TypeError, setattr, self.test_shot, "description",
                          123123)

    def test_description_attribute_initialized_properly(self):
        """testing if the description attribute is initialized correctly with
        the given description argument
        """
        test_value = "test value"
        self.kwargs["description"] = test_value
        new_shot = Shot(**self.kwargs)
        self.assertEqual(new_shot.description, test_value)

    def test_description_attribute_is_working_properly(self):
        """testing if the description attribute is working properly
        """
        new_shot = Shot(**self.kwargs)
        test_value = "test value"
        new_shot.description = test_value
        self.assertEqual(new_shot.description, test_value)
    
    def test_duration_attribute_is_updated_correctly(self):
        """testing if the duration attribute is updated correctly with the
        changing values of start_frame and end_frame values
        """
        new_shot = Shot(**self.kwargs)
        self.assertEqual(new_shot.start_frame, 1)
        self.assertEqual(new_shot.end_frame, 100)
        new_shot.start_frame = 10
        self.assertEqual(new_shot.duration, 91)
        
        new_shot.end_frame = 110
        self.assertEqual(new_shot.duration, 101)
    
    def test_project_attribute_is_initialized_correctly(self):
        """testing if the project attribute is initialized correctly
        """
        self.assertIs(self.test_shot.project, self.kwargs["sequence"].project)


class ShotDBTester(unittest.TestCase):
    """tests the Shot class with a database
    """
    
    def setUp(self):
        """setup the test settings with environment variables
        """
        
        # -----------------------------------------------------------------
        # start of the setUp
        # create the environment variable and point it to a temp directory
        self.temp_settings_folder = tempfile.mktemp()
        self.temp_projects_folder = tempfile.mkdtemp()
        
        # copy the test settings
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
    
    def test_shot_is_created_properly_in_the_database(self):
        """testing if the shot instance is created properly in the database
        """
        self.fail("test is not implemented yet")
    
    def test_shot_is_read_properly_from_the_database(self):
        """testing if the shot instance is read properly from the database
        """
        self.fail("test is not implemented yet")
    
    def test_shot_is_updated_properly_in_the_database(self):
        """testing if the shot instance is updated properly in the database
        """
        self.fail("test is not implemented yet")
    
    def test_shot_is_deleted_properly_from_the_database(self):
        """testing if the shot instance is deleted properly from the database
        """
        self.fail("test is not implemented yet")
