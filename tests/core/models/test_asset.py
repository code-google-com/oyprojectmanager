# -*- coding: utf-8 -*-
# Copyright (c) 2009-2012, Erkan Ozgur Yilmaz
# 
# This module is part of oyProjectManager and is released under the BSD 2
# License: http://www.opensource.org/licenses/BSD-2-Clause

import os
import shutil
import tempfile
import unittest
from sqlalchemy.exc import IntegrityError
from oyProjectManager import config, db
from oyProjectManager.core.models import Project, Asset

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
        
        os.environ["OYPROJECTMANAGER_PATH"] = self.temp_config_folder
        os.environ[conf.repository_env_key] = self.temp_projects_folder
        
        self.test_proj = Project("TEST_PROJ1")
        self.test_proj.create()
        
        self.kwargs = {
            "project": self.test_proj,
            "name": "Test Asset",
            "code": "TEST_ASSET"
        }
        
        self.test_asset = Asset(**self.kwargs)
        self.test_asset.save()
        
        self._name_test_values = [
            ("Test Asset", "Test Asset"),
            ("23Test_Asset", "Test_Asset"),
            ("TEST_ASSET", "TEST_ASSET"),
            ("£#$£#$AB", "AB"),
            ("'^+'^%^+%&&AB3£#$£½'^+'3'^+'4", "AB334"),
            ("afasfas fasf asdf67", "Afasfas fasf asdf67"),
            ("45a", "A"),
            ("45acafs","Acafs"),
            ("45'^+'^+a 234", "A 234"),
            ("45asf78wr", "Asf78wr"),
            ("'^+'afsd2342'^+'asdFGH", "Afsd2342asdFGH"),
        ]
        
        self._code_test_values = [
            ("Test Asset", "Test_Asset"),
            ("23Test_Asset", "Test_Asset"),
            ("TEST_ASSET", "TEST_ASSET"),
            ("£#$£#$AB", "AB"),
            ("'^+'^%^+%&&AB3£#$£½'^+'3'^+'4", "AB334"),
            ("afasfas fasf asdf67", "Afasfas_fasf_asdf67"),
            ("45a", "A"),
            ("45acafs","Acafs"),
            ("45'^+'^+a 234", "A_234"),
            ("45asf78wr", "Asf78wr"),
            ("'^+'afsd2342'^+'asdFGH", "Afsd2342asdFGH"),
        ]
    
    def tearDown(self):
        """cleanup the test
        """
        
        # set the db.session to None
        db.session = None
        
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
        self.kwargs["name"] = None
        self.assertRaises(TypeError, Asset, **self.kwargs)
    
    def test_name_attribute_is_None(self):
        """testing if a TypeError will be raised when the name attribute is set
        to None
        """
        self.assertRaises(TypeError, setattr, self.test_asset, "name", None)
    
    def test_name_argument_is_not_a_string(self):
        """testing if a TypeError will be raised when the name argument is not
        a string
        """
        self.kwargs["name"] = 123445
        self.assertRaises(TypeError, Asset, **self.kwargs)
    
    def test_name_attribute_is_not_a_string(self):
        """testing if a TypeError will be raised when the name attribute is not
        a string
        """
        self.assertRaises(TypeError, setattr, self.test_asset, "name", 123456)
    
    def test_name_argument_is_working_properly(self):
        """test if the name attribute initialized correctly with the value of
        the name argument
        """
        test_value = "Test Value"
        self.kwargs["name"] = test_value
        new_asset = Asset(**self.kwargs)
        self.assertEqual(new_asset.name, test_value)
    
    def test_name_attribute_is_working_properly(self):
        """testing if the name attribute is working properly
        """
        test_value = "Test Value"
        self.test_asset.name = test_value
        self.assertEqual(self.test_asset.name, test_value)
    
    def test_name_argument_formatting(self):
        """testing if the name argument will be formatted correctly
        """
        for test_value in self._name_test_values:
            self.kwargs["name"] = test_value[0]
            new_asset = Asset(**self.kwargs)
            self.assertEqual(new_asset.name, test_value[1])
    
    def test_name_attribute_formatting(self):
        """testing if the name attribute will be formatted correctly
        """
        for test_value in self._name_test_values:
            self.test_asset.name = test_value[0]
            self.assertEqual(self.test_asset.name, test_value[1])
    
    def test_name_argument_is_empty_string_after_formatting(self):
        """testing if a ValueError will be raised when the name argument is an
        empty string after formatting
        """
        self.kwargs["name"] = "£#$£'^+'324"
        self.assertRaises(ValueError, Asset, **self.kwargs)
        
        self.kwargs["name"] = u"546324"
        self.assertRaises(ValueError, Asset, **self.kwargs)
    
    def test_name_attribute_is_empty_string_after_formatting(self):
        """testing if a ValueError will be raised when the name attribugte is
        an empty string after formatting
        """
        self.assertRaises(ValueError, setattr, self.test_asset, "name",
                          "£#$£'^+'324")

        self.assertRaises(ValueError, setattr, self.test_asset, "name",
                          "2324234")
    
    def test_name_argument_is_not_unique(self):
        """testing if a IntegrityError will be raised when the name is unique
        """
        # create an asset with the same name
        new_asset = Asset(**self.kwargs)
        self.assertRaises(IntegrityError, new_asset.save)
    
    def test_code_argument_is_skipped(self):
        """testing if the code attribute will be get from the name attribute if
        the code argument is skipped
        """
        self.kwargs["name"] = "Test Value"
        self.kwargs.pop("code")
        expected_value = "Test_Value"
        new_asset = Asset(**self.kwargs)
        self.assertEqual(new_asset.code, expected_value)
    
    def test_code_argument_is_None(self):
        """testing if the code attribute will be get from the name attribute if
        the code argument is None
        """
        self.kwargs["name"] = "Test Value"
        self.kwargs["code"] = None
        expected_value = "Test_Value"
        new_asset = Asset(**self.kwargs)
        self.assertEqual(new_asset.code, expected_value)
    
    def test_code_attribute_is_None(self):
        """testing if the code attribute will be get from the name attribute if
        it is set to None
        """
        self.test_asset.name = "Test Value"
        self.test_asset.code = None
        expected_value = "Test_Value"
        self.assertEqual(self.test_asset.code, expected_value)
    
    def test_code_argument_is_not_a_string_instance(self):
        """testing if a TypeError will be raised when the code argument is not
        an instance of string or unicode
        """
        self.kwargs["code"] = 2134
        self.assertRaises(TypeError, Asset, **self.kwargs)
    
    def test_code_attribute_is_not_a_string_instance(self):
        """testing if a TypeError will be raised when the code attribute is set
        to a value which is not a string or unicode
        """
        self.assertRaises(TypeError, setattr, self.test_asset, "code", 2342)
    
    def test_code_argument_is_working_properly(self):
        """testing if the code attribute is set from the code argument
        """
        self.kwargs["code"] = "TEST_VALUE"
        new_asset = Asset(**self.kwargs)
        self.assertEqual(new_asset.code, self.kwargs["code"])
    
    def test_code_attribute_is_working_properly(self):
        """testing if the code attribute is working properly
        """
        test_value = "TEST_VALUE"
        self.test_asset.code = test_value
        self.assertEqual(self.test_asset.code, test_value)
    
    def test_code_argument_formatting(self):
        """testing if the code argument is formatted correctly
        """
        for test_value in self._code_test_values:
            self.kwargs["code"] = test_value[0]
            new_asset = Asset(**self.kwargs)
            self.assertEqual(new_asset.code, test_value[1])
    
    def test_code_attribute_formatting(self):
        """testing if the code attribute is formatted correctly
        """
        for test_value in self._code_test_values:
            self.test_asset.code = test_value[0]
            self.assertEqual(self.test_asset.code, test_value[1])
    
    def test_code_argument_is_empty_string_after_formatting(self):
        """testing if a ValueError will be raised when the code argument is an
        empty string after formatting
        """
        self.kwargs["code"] = "'^+'%+%1231"
        self.assertRaises(ValueError, Asset, **self.kwargs)
    
    def test_code_attribute_is_empty_string_after_formatting(self):
        """testing if a ValueError will be raised when the code attribugte is
        an empty string after formatting
        """
        self.assertRaises(ValueError, setattr, self.test_asset, "code",
                          "'^+'%+%1231")
    
    def test_code_argument_is_not_unique(self):
        """testing if an IntegrityError will be raised when the code argument
        is not unique
        """
        self.kwargs["name"] = "Another_Asset_Name"
        new_asset = Asset(**self.kwargs)
        self.assertRaises(IntegrityError, new_asset.save)
    
    def test_save_method_saves_the_asset_to_the_database(self):
        """testing if the save method saves the asset to the database
        """
        self.test_asset.save()
        self.assertTrue(self.test_asset in db.session)
    
    def test_equality_of_assets(self):
        """testing if two assets are equal if their names and projects are also
        equal
        """
        
        proj1 = Project("EQUALITY_TEST_PROJECT_1")
        proj1.create()
        
        proj2 = Project("EQUALITY_TEST_PROJECT_2")
        proj2.create()
        
        asset1 = Asset(proj1, "TEST_ASSET1")
        asset2 = Asset(proj1, "TEST_ASSET1")
        
        asset3 = Asset(proj1, "TEST_ASSET3")
        asset4 = Asset(proj2, "TEST_ASSET3")
        
        self.assertTrue(asset1==asset2)
        self.assertFalse(asset1==asset3)
        self.assertFalse(asset3==asset4)
    
    def test_inequality_of_assets(self):
        """testing if two assets are inequal if their names are different and
        or their projects are different
        """
        
        proj1 = Project("EQUALITY_TEST_PROJECT_1")
        proj1.create()
        
        proj2 = Project("EQUALITY_TEST_PROJECT_2")
        proj2.create()
        
        asset1 = Asset(proj1, "TEST_ASSET1")
        asset2 = Asset(proj1, "TEST_ASSET1")
        
        asset3 = Asset(proj1, "TEST_ASSET3")
        asset4 = Asset(proj2, "TEST_ASSET3")
        
        self.assertFalse(asset1!=asset2)
        self.assertTrue(asset1!=asset3)
        self.assertTrue(asset3!=asset4)
