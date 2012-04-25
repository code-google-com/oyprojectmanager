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
from oyProjectManager.core.models import (VersionType, Project)

conf = config.Config()

class VersionTypeTester(unittest.TestCase):
    """tests the VersionType class
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
        
        self.test_project = Project("TEST_PROJ1")
        self.test_project.create()
        self.test_project.save()
        
        self.kwargs = {
#            "project": self.test_project,
            "name":"Test VType",
            "code":"TVT",
            "path":"{{project.full_path}}/Sequences/{{sequence.code}}/SHOTS/{{version.base_name}}/{{type.code}}",
            "filename":"{{version.base_name}}_{{version.take_name}}_{{type.code}}_v{{'%03d'|format(version.version_number)}}_{{version.created_by.initials}}",
            "environments":["MAYA","HOUDINI"],
            "output_path":"SHOTS/{{version.base_name}}/{{type.code}}/OUTPUT/{{version.take_name}}",
            "extra_folders":"""{{version.path}}/exports
            {{version.path}}/cache
            """,
            "type_for": "Shot"
        }
        
        self.test_versionType = VersionType(**self.kwargs)
        self.test_versionType.save()
        
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
        """cleanup the test
        """
        # set the db.session to None
        db.session = None
        
        # delete the temp folder
        shutil.rmtree(self.temp_config_folder)
        shutil.rmtree(self.temp_projects_folder)
    
    def test_name_argument_is_None(self):
        """testing if a TypeError will be raised when the name argument is
        None
        """
        self.kwargs["name"] = None
        self.assertRaises(TypeError, VersionType, **self.kwargs)
    
    def test_name_attribute_is_None(self):
        """testing if a TypeError will be raised when the name attribute is
        set to None
        """
        self.assertRaises(TypeError, setattr, self.test_versionType, "name",
                          None)
    
    def test_name_argument_is_not_a_string(self):
        """testing if a TypeError will be raised when the name argument is not
        a string or unicode instance
        """
        self.kwargs["name"] = 123
        self.assertRaises(TypeError, VersionType, **self.kwargs)
    
    def test_name_attribute_is_not_a_string(self):
        """testing if a TypeError will be raised when the name argument is not
        a string or unicode instance
        """
        self.assertRaises(TypeError, setattr, self.test_versionType, "name", 8)
    
    def test_name_argument_is_working_properly(self):
        """testing if the name argument is working properly and sets the name
        attribute correctly
        """
        self.assertEqual(self.kwargs["name"], self.test_versionType.name)
    
    def test_name_attribute_is_working_properly(self):
        """testing if the name attribute is working properly
        """
        test_value = "New Name"
        self.test_versionType.name = test_value
        self.assertEqual(test_value, self.test_versionType.name)
    
    def test_name_attribute_is_not_unique(self):
        """testing if an IntegrityError error will be raised when the name
        argument is not unique
        """
        # creating a new VersionType should raise the ?? error
        new_vtype = VersionType(**self.kwargs)
        self.assertRaises(IntegrityError, new_vtype.save)
    
    def test_code_argument_is_skipped(self):
        """testing if a TypeError will be raised when the code argument is
        skipped
        """
        self.kwargs.pop("code")
        self.assertRaises(TypeError, VersionType, **self.kwargs)
    
    def test_code_argument_is_None(self):
        """testing if a TypeError will be raised when the code argument is
        None
        """
        self.kwargs["code"] = None
        self.assertRaises(TypeError, VersionType, **self.kwargs)
    
    def test_code_attribute_is_None(self):
        """testing if a TypeError will be raised when the code attribute is
        set to None
        """
        self.assertRaises(TypeError, setattr, self.test_versionType, "code",
                          None)
    
    def test_code_argument_is_not_a_string(self):
        """testing if a TypeError will be raised when the code argument is not
        a string or unicode instance
        """
        self.kwargs["code"] = 123
        self.assertRaises(TypeError, VersionType, **self.kwargs)
    
    def test_code_attribute_is_not_a_string(self):
        """testing if a TypeError will be raised when the code argument is not
        a string or unicode instance
        """
        self.assertRaises(TypeError, setattr, self.test_versionType, "code", 8)
    
    def test_code_argument_is_working_properly(self):
        """testing if the code argument is working properly and sets the code
        attribute correctly
        """
        self.assertEqual(self.kwargs["code"], self.test_versionType.code)
    
    def test_code_attribute_is_working_properly(self):
        """testing if the code attribute is working properly
        """
        test_value = "New Name"
        self.test_versionType.code = test_value
        self.assertEqual(test_value, self.test_versionType.code)
    
    def test_code_attribute_is_not_unique(self):
        """testing if an IntegrityError error will be raised when the code
        argument is not unique
        """
        # creating a new VersionType should raise the IntegrityError
        self.kwargs["name"] = "A Different Name"
        new_vtype = VersionType(**self.kwargs)
        self.assertRaises(IntegrityError, new_vtype.save)
    
    def test_filename_argument_is_skipped(self):
        """testing if a TypeError will be raised when the filename argument
        is skipped
        """
        self.kwargs.pop("filename")
        self.assertRaises(TypeError, VersionType, **self.kwargs)
    
    def test_filename_argument_is_empty_string(self):
        """testing if a ValueError will be raised when the filename argument
        is an empty string
        """
        self.kwargs["filename"] = ""
        self.assertRaises(ValueError, VersionType, **self.kwargs)
    
    def test_filename_attribute_is_empty_string(self):
        """testing if a ValueError will be raised when the filename attribute
        is set to an empty string
        """
        self.assertRaises(ValueError, setattr, self.test_versionType,
                          "filename", "")
    
    def test_filename_argument_is_not_a_string(self):
        """testing if a TypeError will be raised when the filename argument is
        not a string instance
        """
        self.kwargs["filename"] = 13245
        self.assertRaises(TypeError, VersionType, **self.kwargs)
    
    def test_filename_attribute_is_not_a_string(self):
        """testing if a TypeError will be raised when the filename attribute is
        not a string instance
        """
        self.assertRaises(TypeError, setattr, self.test_versionType,
                          "filename", 23412)
    
    def test_filename_argument_is_working_properly(self):
        """testing if the filename attribute is initialized correctly with the
        same value of the filename argument
        """
        self.assertEqual(self.test_versionType.filename,
                         self.kwargs["filename"])
    
    def test_filename_attribute_is_working_properly(self):
        """testing if the filename attribute is working properly
        """
        test_value = "test_filename"
        self.test_versionType.filename = test_value
        self.assertEqual(self.test_versionType.filename, test_value)
    
    def test_path_argument_is_skipped(self):
        """testing if a TypeError will be raised when the path argument
        is skipped
        """
        self.kwargs.pop("path")
        self.assertRaises(TypeError, VersionType, **self.kwargs)
    
    def test_path_argument_is_empty_string(self):
        """testing if a ValueError will be raised when the path argument
        is an empty string
        """
        self.kwargs["path"] = ""
        self.assertRaises(ValueError, VersionType, **self.kwargs)
    
    def test_path_attribute_is_empty_string(self):
        """testing if a ValueError will be raised when the path attribute
        is set to an empty string
        """
        self.assertRaises(ValueError, setattr, self.test_versionType, "path",
                          "")
    
    def test_path_argument_is_not_a_string(self):
        """testing if a TypeError will be raised when the path argument is
        not a string instance
        """
        self.kwargs["path"] = 13245
        self.assertRaises(TypeError, VersionType, **self.kwargs)
    
    def test_path_attribute_is_not_a_string(self):
        """testing if a TypeError will be raised when the path attribute is
        not a string instance
        """
        self.assertRaises(TypeError, setattr, self.test_versionType,
                          "path", 23412)
    
    def test_path_argument_is_working_properly(self):
        """testing if the path attribute is initialized correctly with the
        same value of the path argument
        """
        self.assertEqual(self.test_versionType.path,
                         self.kwargs["path"])
    
    def test_path_attribute_is_working_properly(self):
        """testing if the path attribute is working properly
        """
        test_value = "test_path"
        self.test_versionType.path = test_value
        self.assertEqual(self.test_versionType.path, test_value)
    
    def test_output_path_argument_is_skipped(self):
        """testing if a TypeError will be raised when the output_path
        argument is skipped
        """
        self.kwargs.pop("output_path")
        self.assertRaises(TypeError, VersionType, **self.kwargs)
    
    def test_output_path_argument_is_empty_string(self):
        """testing if a ValueError will be raised when the output_path
        argument is an empty string
        """
        self.kwargs["output_path"] = ""
        self.assertRaises(ValueError, VersionType, **self.kwargs)
    
    def test_output_path_attribute_is_empty_string(self):
        """testing if a ValueError will be raised when the output_path
        attribute is set to an empty string
        """
        self.assertRaises(ValueError, setattr, self.test_versionType,
                          "output_path", "")
    
    def test_output_path_argument_is_not_a_string(self):
        """testing if a TypeError will be raised when the output_path argument
        is not a string instance
        """
        self.kwargs["output_path"] = 13245
        self.assertRaises(TypeError, VersionType, **self.kwargs)
    
    def test_output_path_attribute_is_not_a_string(self):
        """testing if a TypeError will be raised when the output_path attribute
        is not a string instance
        """
        self.assertRaises(TypeError, setattr, self.test_versionType,
                          "output_path", 23412)
    
    def test_output_path_argument_is_working_properly(self):
        """testing if the output_path attribute is initialized correctly with
        the same value of the output_path argument
        """
        self.assertEqual(self.test_versionType.output_path,
                         self.kwargs["output_path"])
    
    def test_output_path_attribute_is_working_properly(self):
        """testing if the output_path attribute is working properly
        """
        test_value = "test_output_path"
        self.test_versionType.output_path = test_value
        self.assertEqual(self.test_versionType.output_path, test_value)
    
    def test_extra_folders_argument_is_skipped(self):
        """testing if the extra_folders argument is skipped the extra_folders
        attribute will be an empty string
        """
        self.kwargs.pop("extra_folders")
        new_version_type = VersionType(**self.kwargs)
        self.assertEqual(new_version_type.extra_folders, "")
    
    def test_extra_folders_argument_is_None(self):
        """testing if the extra_folders attribute is going to be an empty
        string when the extra folders argument is given as None
        """
        self.kwargs["extra_folders"] = None
        new_version_type = VersionType(**self.kwargs)
        self.assertEqual(new_version_type.extra_folders, "")
    
    def test_extra_folders_attribute_is_None(self):
        """testing if the extra_folders attribute will be an empty list when it
        is set to None
        """
        self.test_versionType.extra_folders = None
        self.assertEqual(self.test_versionType.extra_folders, "")
    
    def test_extra_folders_argument_is_not_a_string_instance(self):
        """testing if a TypeError will be raised when the extra_folders
        argument is not a string or unicode instance
        """
        self.kwargs["extra_folders"] = 123
        self.assertRaises(TypeError, VersionType, **self.kwargs)
    
    def test_extra_folders_attribute_is_not_a_string_instance(self):
        """testing if a TypeError will be raised when the extra_folders
        attribute is set to something other than a string or unicode instance
        """
        self.assertRaises(TypeError, setattr, self.test_versionType,
                          "extra_folders", 23423)
    
    def test_extra_folders_argument_is_working_properly(self):
        """testing if the extra_folders attribute will be set to the same value
        with the extra_folders argument while initialization
        """
        self.assertEqual(self.test_versionType.extra_folders,
                         self.kwargs["extra_folders"])
    
    def test_extra_folders_attribute_is_working_properly(self):
        """testing if the extra_folders attribute is working properly
        """
        test_value = "extra_folders"
        self.test_versionType.extra_folders = test_value
        self.assertEqual(self.test_versionType.extra_folders, test_value)
    
    def test_environments_argument_is_skipped(self):
        """testing if a TypeError will be raised when the environments
        argument is skipped
        """
        self.kwargs.pop("environments")
        self.assertRaises(TypeError, VersionType, **self.kwargs)
    
    def test_environments_argument_is_None(self):
        """testing if a TypeError will be raised when the environments
        argument is None
        """
        self.kwargs["environments"] = None
        self.assertRaises(TypeError, VersionType, **self.kwargs)
    
    def test_environments_attribute_is_None(self):
        """testing if a TypeError will be raised when the environments
        attribute is set to None
        """
        self.assertRaises(TypeError, setattr, self.test_versionType,
                          "environments", None)
    
    def test_environments_argument_is_not_a_list(self):
        """testing if a TypeError will be raised when the environments argument
        is not a list instance
        """
        self.kwargs["environments"] = 12354
        self.assertRaises(TypeError, VersionType, **self.kwargs)
    
    def test_environments_attribute_is_not_a_list(self):
        """testing if a TypeError will be raised when the environments
        attribute is set to something other than a list
        """
        self.assertRaises(TypeError, setattr, self.test_versionType,
                          "environments", 123)
    
    def test_environments_argument_is_not_a_list_of_strings(self):
        """testing if a TypeError will be raised when the environments argument
        is not a list of strings
        """
        self.kwargs["environments"] = [123, "MAYA"]
        self.assertRaises(TypeError, VersionType, **self.kwargs)
    
    def test_environments_attribute_is_not_a_list_of_strings(self):
        """testing if a TypeError will be raised when the environments
        attribute is not a list of strings
        """
        self.assertRaises(TypeError, setattr, self.test_versionType,
                          "environments", [123, "MAYA"])
    
    def test_environments_argument_works_properly(self):
        """testing if the environments attribute will be initialized correctly
        with the environments argument
        """
        test_value = ["MAYA", "HOUDINI"]
        self.kwargs["environments"] = test_value
        new_vtype = VersionType(**self.kwargs)
        
        for env in test_value:
            self.assertTrue(env in new_vtype.environments)
    
    def test_environments_attribute_works_properly(self):
        """testing if the environments attribute is working properly
        """
        test_value = ["MAYA", "HOUDINI", "NUKE", "3DEQUALIZER"]
        self.test_versionType.environments = test_value
        
        for env in test_value:
            self.assertTrue(env in self.test_versionType.environments)
    
    def test_type_for_argument_is_skipped(self):
        """testing if a TypeError will be raised when the type_for argument is
        skipped
        """
        self.kwargs.pop("type_for")
        self.assertRaises(TypeError, VersionType, **self.kwargs)
    
    def test_type_for_argument_is_None(self):
        """testing if a TypeError will be raised when the type_for argument
        is None
        """
        self.kwargs["type_for"] = None
        self.assertRaises(TypeError, VersionType, **self.kwargs)
    
    def test_type_for_argument_is_not_a_string_or_integer(self):
        """testing if a TypeError will be raised when the type_for argument is
        not a string or unicode or an integer
        """
        self.kwargs["type_for"] = [12]
        self.assertRaises(TypeError, VersionType, **self.kwargs)
    
    def test_type_for_argument_is_working_properly(self):
        """testing if the type_for argument is working properly
        """
        self.kwargs["name"] = "Test Animation"
        self.kwargs["code"] = "TA"
        self.kwargs["type_for"] = "Asset"
        new_vtype = VersionType(**self.kwargs)
        new_vtype.save()
        self.assertEqual(new_vtype.type_for, "Asset")
    
    def test_type_for_attribute_is_read_only(self):
        """testing if type_for attribute is read-only
        """
        self.assertRaises(AttributeError, setattr, self.test_versionType,
                          "type_for", "Asset")
    
    def test_save_method_saves_the_version_type_to_the_database(self):
        """testing if the save method saves the current VersionType to the
        database
        """
        self.kwargs["name"] = "Test Animation"
        self.kwargs["code"] = "TA"
        new_vtype = VersionType(**self.kwargs)
        new_vtype.save()
        
        code = new_vtype.code
        environments = new_vtype.environments
        filename = new_vtype.filename
        name = new_vtype.name
        output_path = new_vtype.output_path
        path = new_vtype.path
        type_for = new_vtype.type_for
        
#        del new_vtype
        
        new_vtypeDB = db.query(VersionType).\
            filter_by(name=self.kwargs["name"]).first()
        
        self.assertEqual(code, new_vtypeDB.code)
        self.assertEqual(filename, new_vtypeDB.filename)
        self.assertEqual(name, new_vtypeDB.name)
        self.assertEqual(output_path, new_vtypeDB.output_path)
        self.assertEqual(path, new_vtypeDB.path)
        self.assertEqual(type_for, new_vtypeDB.type_for)
        self.assertEqual(environments, new_vtypeDB.environments)
    
    def test__eq__(self):
        """testing the equality operator
        """
        
        verst1 = VersionType(
            name="Test Type",
            code="TT",
            path="path",
            filename="filename",
            output_path="output_path",
            environments=["MAYA", "NUKE"],
            type_for="Asset"
        )
        
        verst2 = VersionType(
            name="Test Type",
            code="TT",
            path="path",
            filename="filename",
            output_path="output_path",
            environments=["MAYA", "NUKE"],
            type_for="Asset"
        )
        
        verst3 = VersionType(
            name="Test Type 2",
            code="TT",
            path="path",
            filename="filename",
            output_path="output_path",
            environments=["MAYA", "NUKE"],
            type_for="Asset"
        )
        
        verst4 = VersionType(
            name="Test Type 3",
            code="TT3",
            path="path",
            filename="filename",
            output_path="output_path",
            environments=["MAYA", "NUKE"],
            type_for="Asset"
        )
        
        self.assertTrue(verst1==verst2)
        self.assertFalse(verst1==verst3)
        self.assertFalse(verst3==verst4)
    
    def test__ne__(self):
        """testing the equality operator
        """
        
        verst1 = VersionType(
            name="Test Type",
            code="TT",
            path="path",
            filename="filename",
            output_path="output_path",
            environments=["MAYA", "NUKE"],
            type_for="Asset"
        )
        
        verst2 = VersionType(
            name="Test Type",
            code="TT",
            path="path",
            filename="filename",
            output_path="output_path",
            environments=["MAYA", "NUKE"],
            type_for="Asset"
        )
        
        verst3 = VersionType(
            name="Test Type 2",
            code="TT",
            path="path",
            filename="filename",
            output_path="output_path",
            environments=["MAYA", "NUKE"],
            type_for="Asset"
        )
        
        verst4 = VersionType(
            name="Test Type 3",
            code="TT3",
            path="path",
            filename="filename",
            output_path="output_path",
            environments=["MAYA", "NUKE"],
            type_for="Asset"
        )
        
        self.assertFalse(verst1!=verst2)
        self.assertTrue(verst1!=verst3)
        self.assertTrue(verst3!=verst4)
