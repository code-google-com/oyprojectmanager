# -*- coding: utf-8 -*-
# Copyright (c) 2009-2012, Erkan Ozgur Yilmaz
# 
# This module is part of oyProjectManager and is released under the BSD 2
# License: http://www.opensource.org/licenses/BSD-2-Clause
import os
import shutil
import tempfile
import unittest

from oyProjectManager import db, conf

class FileLinkTester(unittest.TestCase):
    """tests the oyProjectManager.models.link.FileLink class
    """
    
    def setUp(self):
        """set up the test
        """
        conf.database_url = "sqlite://"
        
        # create the environment variable and point it to a temp directory
        self.temp_config_folder = tempfile.mkdtemp()
        self.temp_projects_folder = tempfile.mkdtemp()
        
        os.environ["OYPROJECTMANAGER_PATH"] = self.temp_config_folder
        os.environ[conf.repository_env_key] = self.temp_projects_folder
    
    def tearDown(self):
        """clean up the test
        """
        
        # set the db.session to None
        db.session = None
        
        # delete the temp folders
        shutil.rmtree(self.temp_config_folder)
        shutil.rmtree(self.temp_projects_folder)
    
    def test_filename_argument_is_skipped(self):
        """testing if a TypeError will be raised when the filename argument is
        skipped.
        """
        self.fail('test is not implemented')
    
    def test_filename_argument_is_None(self):
        """testing if a TypeError will be raised when the filename argument is
        given as None
        """
        self.fail('test is not implemented yet')
    
    def test_filename_attribute_is_None(self):
        """testing if a TypeError will be raised when the filename attribute is
        set to None
        """
        self.fail('test is not implemented yet')
    
    def test_filename_argument_is_not_a_string(self):
        """testing if a TypeError will be raised when the filename attribute is
        not a string
        """
        self.fail('test is not implemented yet')
    
    def test_filename_attribute_is_not_a_string(self):
        """testing if a TypeError will be raised when the filename attribute is
        set to a value with type other then a string
        """
        self.fail('test is not implemented yet')
    
    def test_filename_argument_is_working_properly(self):
        """testing if the filename argument is setting the filename attribute
        properly
        """
        self.fail('test is not implemented yet')
    
    def test_filename_attribute_is_working_properly(self):
        """testing if the filename attribute is working properly
        """
        self.fail('test is not implemented yet')
    
    def test_path_argument_is_skipped(self):
        """testing if a TypeError will be raised when the path argument is
        skipped.
        """
        self.fail('test is not implemented')
    
    def test_path_argument_is_None(self):
        """testing if a TypeError will be raised when the path argument is
        given as None
        """
        self.fail('test is not implemented yet')
    
    def test_path_attribute_is_None(self):
        """testing if a TypeError will be raised when the path attribute is
        set to None
        """
        self.fail('test is not implemented yet')
    
    def test_path_argument_is_not_a_string(self):
        """testing if a TypeError will be raised when the path attribute is
        not a string
        """
        self.fail('test is not implemented yet')
    
    def test_path_attribute_is_not_a_string(self):
        """testing if a TypeError will be raised when the path attribute is
        set to a value with type other then a string
        """
        self.fail('test is not implemented yet')
    
    def test_path_argument_is_working_properly(self):
        """testing if the path argument is setting the path attribute
        properly
        """
        self.fail('test is not implemented yet')
    
    def test_path_attribute_is_working_properly(self):
        """testing if the path attribute is working properly
        """
        self.fail('test is not implemented yet')
    
    def test_type_argument_is_skipped(self):
        """testing if the type argument is skipped will set the type to None
        """
        self.fail('test is not implemented yet')
    
    def test_type_argument_is_None(self):
        """testing if the type argument is None will now raise any errors
        """
        self.fail('test is not implemented yet')
    
    def test_type_attribute_is_None(self):
        """testing if the type attribute is set to None will not raise any
        errors
        """
        self.fail('test is not implemented yet')
    
    def test_type_argument_is_not_a_string(self):
        """testing if the type argument is not a string will raise a TypeError
        """
        self.fail('test is not implemented yet')
    
    def test_type_attribute_is_not_a_string(self):
        """testing if the type attribute is not a string will raise a TypeError
        """
        self.fail('test is not implemented yet')
    
    def test_type_argument_is_working_properly(self):
        """testing if the type argument value is correctly passed to the type
        attribute
        """
        self.fail('test is not implemented yet')
    
    def test_type_attribute_is_working_properly(self):
        """testing if the type attribute is working properly
        """
        self.fail('test is not implemented yet')
