# -*- coding: utf-8 -*-

import os
import shutil
import tempfile
import unittest

from oyProjectManager import config
from oyProjectManager.core.models import VersionableBase

conf = config.Config()

class VersionableBaseTester(unittest.TestCase):
    """tests the VersionableBase class
    """
    
    def setUp(self):
        """setup the test settings with environment variables
        """
        
        # -----------------------------------------------------------------
        # start of the setUp
        # create the environment variable and point it to a temp directory
        self.temp_config_folder = tempfile.mkdtemp()
        self.temp_projects_folder = tempfile.mkdtemp()
        
        os.environ["OYPROJECTMANAGER_PATH"] = self.temp_config_folder
        os.environ[conf.repository_env_key] = self.temp_projects_folder
    
    def tearDown(self):
        """remove the temp folders
        """
        
        # delete the temp folder
        shutil.rmtree(self.temp_config_folder)
        shutil.rmtree(self.temp_projects_folder)
    
    def test_versions_attribute_is_read_only(self):
        """testing if the versions attribute is read-only
        """
        new_vbase = VersionableBase()
        self.assertRaises(AttributeError, setattr, new_vbase, "versions",
                          12312)
    
    def test_project_attribute_is_read_only(self):
        """testing if the project attribute is read-only
        """
        
        new_vbase = VersionableBase()
        self.assertRaises(AttributeError, setattr, new_vbase, "project",
                          123124)
