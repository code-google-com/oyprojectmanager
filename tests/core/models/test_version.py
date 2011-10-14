import os
import shutil
import tempfile
import unittest
from xml.dom import minidom
import oyProjectManager
from oyProjectManager.core.models import VersionableBase, Version, VersionType


class VersionTester(unittest.TestCase):
    """tests the Version class
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
        
        self.test_vbase = VersionableBase()
        
        self.test_type = VersionType(
            name="Animation",
            code="ANIM",
            path="SHOTS/{{assetBaseName}}/{{assetTypeName}}",
            filename="{{base_name}}_{{take_name}}_{{type_name}}_v{{version}}_{{created_by.initials}}",
            shotDependent=True,
            environments="MAYA,HOUDINI",
            output_path=\
             "SHOTS/{{assetBaseName}}/{{assetTypeName}}/OUTPUT/{{assetSubName}}"
        )
        
        self.kwargs = {
            "version_of": self.test_vbase,
            "filename": "random_name.ma",
            "path": "/server/projects/proj1",
            "base_name": "SH001",
            "take_name": "MAIN",
            "type": self.test_type,
            "revision_number": 0,
            "version_number": 1,
        }
        
        self.test_version = Version(**self.kwargs)
        
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
    
    def test_version_of_argument_is_skipped_raises_RuntimeError(self):
        """testing if a RuntimeError will be raised when the version_of
        argument is skipped
        """
        self.kwargs.pop("version_of")
        self.assertRaises(RuntimeError, Version, **self.kwargs)
    
    def test_version_of_argument_is_None(self):
        """testing if a RuntimeError will be raised when the version_of
        argument is None
        """
        self.kwargs["version_of"] = None
        self.assertRaises(RuntimeError, Version, **self.kwargs)
    
    def test_version_of_argument_is_not_a_VersionableBase_instance(self):
        """testing if a TypeError will be raised when the version_of argument
        is not a VersionableBase instance)
        """
        self.kwargs["version_of"] = "not a VersionableBase instance"
        self.assertRaises(TypeError, Version, **self.kwargs)
    
    def test_version_of_attribute_initialized_correctly(self):
        """testing if the version_of attribute initialized correctly
        """
        self.assertIs(self.test_version.version_of, self.kwargs["version_of"])
        
    
    def test_version_of_attribute_is_read_only(self):
        """testing if the version_of attribute is read-only
        """
        self.assertRaises(AttributeError, setattr, self.test_version,
                          "version_of", 123)
    
    def test_type_argument_skipped(self):
        """testing if a RuntimeError will be raised when the type argument is
        skipped
        """
        self.kwargs.pop("type")
        self.assertRaises(RuntimeError, Version, **self.kwargs)
    
    def test_type_argument_is_None(self):
        """testing if a RuntimeError will be raised when the type argument is
        None
        """
        self.kwargs["type"] = None
        self.assertRaises(RuntimeError, Version, **self.kwargs)
    
    def test_type_argument_is_not_VersionType_instance(self):
        """testing if a TypeError will be raised when the type argument is not
        a VersionType instance
        """
        self.kwargs["type"] = "not a VersionType instance"
        self.assertRaises(TypeError, Version, **self.kwargs)
    
    def test_type_attribute_initialized_properly(self):
        """testing if the type attribute is initialized correctly
        """
        self.assertIs(self.test_version.type, self.kwargs["type"])
    
    def test_type_attribute_is_read_only(self):
        """testing if the type attribute is read-only
        """
        new_type = VersionType(
            name="Model",
            code="MODEL",
            path="ASSETS/{{base_name}}/{{type_name}}",
            filename="{{base_name}}_{{take_name}}_{{type_name}}_v{{version}}_{{created_by.initials}}",
            shotDependent=True,
            environments="MAYA,HOUDINI",
            output_path="ASSETS/{{assetBaseName}}/{{assetTypeName}}/OUTPUT/{{assetSubName}}"
        )
        self.assertRaises(AttributeError, setattr, self.test_version, "type",
                          new_type)
    
    def test_filename_argument_is_None(self):
        """
        """
