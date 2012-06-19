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
from oyProjectManager.models.link import FileLink

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
        
        self.kwargs = {
            "filename": "test_file_name.txt",
            "path": "/some/path/to/an/unknown/place",
            "type": "Text"
        }
        
        self.test_file_link = FileLink(**self.kwargs)
    
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
        self.kwargs.pop("filename")
        self.assertRaises(TypeError, FileLink, **self.kwargs)
    
    def test_filename_argument_is_None(self):
        """testing if a TypeError will be raised when the filename argument is
        given as None
        """
        self.kwargs["filename"] = None
        self.assertRaises(TypeError, FileLink, **self.kwargs)
    
    def test_filename_attribute_is_None(self):
        """testing if a TypeError will be raised when the filename attribute is
        set to None
        """
        self.assertRaises(TypeError, setattr, self.test_file_link, 'filename',
            None)
    
    def test_filename_argument_is_not_a_string(self):
        """testing if a TypeError will be raised when the filename attribute is
        not a string
        """
        self.kwargs['filename'] = 2342
        self.assertRaises(TypeError, FileLink, **self.kwargs)
    
    def test_filename_attribute_is_not_a_string(self):
        """testing if a TypeError will be raised when the filename attribute is
        set to a value with type other then a string
        """
        self.assertRaises(TypeError, setattr, self.test_file_link, 'filename',
            2342)
    
    def test_filename_argument_is_working_properly(self):
        """testing if the filename argument is setting the filename attribute
        properly
        """
        self.assertEqual(self.kwargs['filename'], self.test_file_link.filename)
    
    def test_filename_attribute_is_working_properly(self):
        """testing if the filename attribute is working properly
        """
        test_value = "new_file_name"
        self.test_file_link.filename = test_value
        self.assertEqual(test_value, self.test_file_link.filename)
    
    def test_path_argument_is_skipped(self):
        """testing if a TypeError will be raised when the path argument is
        skipped.
        """
        self.kwargs.pop("path")
        self.assertRaises(TypeError, FileLink, **self.kwargs)
    
    def test_path_argument_is_None(self):
        """testing if a TypeError will be raised when the path argument is
        given as None
        """
        self.kwargs["path"] = None
        self.assertRaises(TypeError, FileLink, **self.kwargs)
    
    def test_path_attribute_is_None(self):
        """testing if a TypeError will be raised when the path attribute is
        set to None
        """
        self.assertRaises(TypeError, setattr, self.test_file_link, 'path',
            None)
    
    def test_path_argument_is_not_a_string(self):
        """testing if a TypeError will be raised when the path attribute is
        not a string
        """
        self.kwargs['path'] = 2342
        self.assertRaises(TypeError, FileLink, **self.kwargs)
    
    def test_path_attribute_is_not_a_string(self):
        """testing if a TypeError will be raised when the path attribute is
        set to a value with type other then a string
        """
        self.assertRaises(TypeError, setattr, self.test_file_link, 'path',
            2342)
    
    def test_path_argument_is_working_properly(self):
        """testing if the path argument is setting the path attribute
        properly
        """
        self.assertEqual(self.kwargs['path'], self.test_file_link.path)
    
    def test_path_attribute_is_working_properly(self):
        """testing if the path attribute is working properly
        """
        test_value = "new_path_name"
        self.test_file_link.path = test_value
        self.assertEqual(test_value, self.test_file_link.path)
    
    def test_type_argument_is_skipped(self):
        """testing if the type argument is skipped will set the type to an
        empty string
        """
        self.kwargs.pop('type')
        new_file_link = FileLink(**self.kwargs)
        self.assertIs("", new_file_link.type)
    
    def test_type_argument_is_None(self):
        """testing if the type argument is None will set the type to an empty
        string
        """
        self.kwargs['type'] = None
        new_file_link = FileLink(**self.kwargs)
        self.assertIs("", new_file_link.type)
    
    def test_type_attribute_is_None(self):
        """testing if the type attribute is set to None will set it to empty
        string
        """
        self.test_file_link.type = None
        self.assertEqual("", self.test_file_link.type)
    
    def test_type_argument_is_not_a_string(self):
        """testing if the type argument is not a string will raise a TypeError
        """
        self.kwargs['type'] = 2342
        self.assertRaises(TypeError, FileLink, **self.kwargs)
    
    def test_type_attribute_is_not_a_string(self):
        """testing if the type attribute is not a string will raise a TypeError
        """
        self.assertRaises(TypeError, setattr, self.test_file_link, 'type', 24)
    
    def test_type_argument_is_working_properly(self):
        """testing if the type argument value is correctly passed to the type
        attribute
        """
        test_value = "Image Sequence"
        self.kwargs['type'] = test_value
        new_file_link = FileLink(**self.kwargs)
        self.assertEqual(test_value, new_file_link.type)
    
    def test_type_attribute_is_working_properly(self):
        """testing if the type attribute is working properly
        """
        test_value = "Video"
        self.kwargs['type'] = test_value
        self.test_file_link.type = test_value
        self.assertEqual(test_value, self.test_file_link.type)
    
