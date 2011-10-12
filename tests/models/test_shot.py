import os
import shutil
import tempfile
import unittest
from xml.dom import minidom
import oyProjectManager


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
        self.fail("test is not implemented yet")
    
    def test_name_argument_is_None(self):
        """testing if a TypeError will be raised when the name argument is None
        """
        self.fail("test is not implemented yet")

    def test_name_attribute_is_None(self):
        """testing if a TypeError will be raised when the name attribute is set
        to None
        """
        self.fail("test is not implemented yet")
    
    def test_name_argument_is_not_a_string(self):
        """testing if a TypeError will be raised when the name argument is not
        a string
        """
        self.fail("test is not implemented yet")
    
    def test_name_attribute_is_not_a_string(self):
        """testing if a TypeError will be raised when the name attribute is not
        a string
        """
        self.fail("test is not implemented yet")
    
    
    def test_name_argument_formatted_correctly(self):
        """testing if the name attribute is formatted correctly when the class
        is initialized
        """
        self.fail("test is not implemented yet")
    
    def test_name_attribute_formatted_correctly(self):
        """testing if the name attribute is formatted correctly
        """
        self.fail("test is not implemented yet")
    
    def test_sequence_argument_is_skipped(self):
        """testing if a RuntimeError will be raised when the sequence argument
        is skipped
        """
        self.fail("test is not implemented yet")
    
    def test_sequence_argument_is_None(self):
        """testing if a RuntimeError will be raised when the sequence argument
        is None
        """
        self.fail("test is not implemented yet")
    
    def test_sequence_argument_is_not_a_Sequence_instance(self):
        """testing if a TypeError will be raised when the sequence argument is
        not a Sequence instance
        """
        self.fail("test is not implemented yet")
    
    def test_sequence_argument_is_working_properly(self):
        """testing if the sequence argument is working correctly
        """
        self.fail("test is not implemented yet")
    
    def test_sequence_attribute_is_read_only(self):
        """testing if the sequence attribute is read-only
        """
        
        self.fail("test is not implemented yet")
        
    
    
    
        
    
        
