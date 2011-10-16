#-*- coding: utf-8 -*-

import os
import shutil
import tempfile
import unittest
from xml.dom import minidom
import oyProjectManager
from oyProjectManager import conf
from oyProjectManager.core.models import (VersionableBase, Version,
                                          VersionType, User, Project)


class VersionTypeTester(unittest.TestCase):
    """tests the VersionType class
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
        
#        print self.temp_projects_folder
        
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
        
        self.test_project = Project("TEST_PROJ1")
        self.test_project.create()
        self.test_project.save()
        
        # set it just for testing purposes
        self.test_vbase = VersionableBase()
        self.test_vbase._project = self.test_project
        
        self.test_versionType = VersionType(
            name="Animation",
            code="ANIM",
            path="SHOTS/{{version.base_name}}/{{type.code}}",
            filename="{{version.base_name}}_{{version.take_name}}_{{type.code}}_v{{'%03d'|format(version.version_number)}}_{{version.created_by.initials}}",
            environments="MAYA,HOUDINI",
            output_path="SHOTS/{{version.base_name}}/{{type.code}}/OUTPUT/{{version.take_name}}"
        )
        
        self.test_user = User(
            name="Test User",
            initials="tu",
            email="testuser@test.com"
        )
        
        self.kwargs = {
            "version_of": self.test_vbase,
            "type": self.test_versionType,
            "base_name": "SH001",
            "take_name": "MAIN",
            "version_number": 1,
            "note": "this is the note for this version",
            "created_by": self.test_user
        }
        
        self.test_version = Version(**self.kwargs)
        
        self._name_test_values = [
            ("base name", "Base_Name"),
            ("123123 base_name", "Base_Name"),
            ("123432!+!'^+Base_NAme323^+'^%&+%&324", "Base_NAme323324"),
            ("    ---base 9s_name", "Base_9s_Name"),
            ("    ---base 9s-name", "Base_9s_Name"),
            (" multiple     spaces are    converted to under     scores",
             "Multiple_Spaces_Are_Converted_To_Under_Scores"),
            ("camelCase", "CamelCase"),
            ("CamelCase", "CamelCase"),
            ("_Project_Setup_", "Project_Setup"),
            ("_PROJECT_SETUP_", "PROJECT_SETUP"),
            ("FUL_3D", "FUL_3D"),
            ("BaseName", "BaseName"),
            ("baseName", "BaseName"),
            (" baseName", "BaseName"),
            (" base name", "Base_Name"),
            (" 12base name", "Base_Name"),
            (" 12 base name", "Base_Name"),
            (" 12 base name 13", "Base_Name_13"),
            (">£#>$#£½$ 12 base £#$£#$£½¾{½{ name 13", "Base_Name_13"),
            ("_base_name_", "Base_Name"),
        ]
    
    def tearDown(self):
        """remove the temp folders
        """
        
        # delete the temp folder
        shutil.rmtree(self.temp_settings_folder)
        shutil.rmtree(self.temp_projects_folder)
    
    
