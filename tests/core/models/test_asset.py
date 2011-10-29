# -*- coding: utf-8 -*-

import os
import shutil
import tempfile
import unittest
from oyProjectManager import config
from oyProjectManager.core.models import Project, Sequence, Shot, Asset

conf = config.Config()

class AssetTester(unittest.TestCase):
    """tests the Asset class
    """
    
    def setUp(self):
        """setup the test settings with environment variables
        """
        
        # -----------------------------------------------------------------
        # start of the setUp
        # create the environment variable and point it to a temp directory
        self.temp_config_folder = tempfile.mkdtemp()
        self.temp_projects_folder = tempfile.mkdtemp()
        
        os.environ[conf.repository_env_key] = self.temp_projects_folder
        
        self.test_proj = Project("TEST_PROJ1")
        self.test_proj.create()
        
        self.kwargs = {
            "project": self.test_proj,
            "name": "Test Asset",
            "code": "TEST_ASSET"
        }
        
        self.test_asset = Asset(**self.kwargs)
        
        self._name_test_values = [
            ("Test Asset", "Test Asset"),
            ("23Test_Asset", "Test_Asset"),
            ("TEST_ASSET", "TEST_ASSET"),
            ("£#$£#$AB", "AB"),
            ("'^+'^%^+%&&AB3£#$£½'^+'3'^+'4", "AB34"),
            ("afasfas fasf asdf67", "Afasfas fas_asdf67"),
            ("45a", "A"),
            ("45acafs","Acacfs"),
            ("45'^+'^+a 234", "A 234"),
            ("45asf78wr", "45Asf78wr"),
            ("'^+'afsd2342'^+'asdFGH", "AsdFGH2342asdFGH"),
        ]
        
        self._code_test_values = [
            ("Test Asset", "Test_Asset"),
            ("23Test_Asset", "Test_Asset"),
            ("TEST_ASSET", "TEST_ASSET"),
            ("£#$£#$AB", "AB"),
            ("'^+'^%^+%&&AB3£#$£½'^+'3'^+'4", "AB34"),
            ("afasfas fasf asdf67", "Afasfas_fas_asdf67"),
            ("45a", "A"),
            ("45acafs","Acacfs"),
            ("45'^+'^+a 234", "A_234"),
            ("45asf78wr", "Asf78wr"),
            ("'^+'afsd2342'^+'asdFGH", "AsdFGH2342asdFGH"),
        ]
        
    
    def tearDown(self):
        """remove the temp folders
        """
        
        # delete the temp folder
        shutil.rmtree(self.temp_config_folder)
        shutil.rmtree(self.temp_projects_folder)
    
    def test_name_argument_is_skipped(self):
        """testing if a TypeError will be raised when the name argument is
        skipped
        """
        self.kwargs.pop("name")
        self.assertRaises(TypeError, Asset, **self.kwargs)
    
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
    
    def test_name_argument_is_working_properly(self):
        """test if the name attribute initialized correctly with the value of
        the name argument
        """
        self.fail("test is not implemented yet")
    
    def test_name_attribute_is_working_properly(self):
        """testing if the name attribute is working properly
        """
        self.fail("test is not implemented yet")
    
    def test_name_argument_formatting(self):
        """testing if the name argument will be formatted correctly
        """
        self.fail("test is not implemented yet")
    
    def test_name_attribute_formatting(self):
        """testing if the name attribute will be formatted correctly
        """
        self.fail("test is not implemented yet")
    
    def test_code_argument_is_skipped(self):
        """testing if the code attribute will be get from the name attribute if
        the code argument is skipped
        """
        self.fail("test is not implemented yet")
    
    def test_code_argument_is_None(self):
        """testing if the code attribute will be get from the name attribute if
        the code argument is None
        """
        self.fail("test is not implemented yet")
    
    def test_code_attribute_is_None(self):
        """testing if the code attribute will be get from the name attribute if
        it is set to None
        """
        self.fail("test is not implemented yet")
    
    def test_code_argument_is_not_a_string_instance(self):
        """testing if a TypeError will be raised when the code argument is not
        an instance of string or unicode
        """
        self.fail("test is not implemented yet")
    
    def test_code_attribute_is_not_a_string_instance(self):
        """testing if a TypeError will be raised when the code attribute is set
        to a value which is not a string or unicode
        """
        self.fail("test is not implemented yet")
    
    def test_code_argument_is_working_properly(self):
        """testing if the code attribute is set from the code argument
        """
        self.fail("test is not implemented yet")
    
    def test_code_attribute_is_working_properly(self):
        """testing if the code attribute is working properly
        """
        self.fail("test is not implemented yet")
    
    def test_code_argument_formatting(self):
        """testing if the code argument is formatted correctly
        """
        self.fail("test is not implemented yet")
    
    def test_code_attribute_formatting(self):
        """testing if the code attribute is formatted correctly
        """
        self.fail("test is not implemented yet")
    
