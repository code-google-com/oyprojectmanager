# -*- coding: utf-8 -*-
# Copyright (c) 2009-2012, Erkan Ozgur Yilmaz
# 
# This module is part of oyProjectManager and is released under the BSD 2
# License: http://www.opensource.org/licenses/BSD-2-Clause

import os

import shutil
import tempfile
import unittest
from oyProjectManager import config, db
from oyProjectManager.core.errors import CircularDependencyError
from oyProjectManager.core.models import (Asset, Shot, Version, VersionType,
                                          User, Project, Sequence)

conf = config.Config()

class VersionTester(unittest.TestCase):
    """tests the Version class
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
        
        self.test_sequence = Sequence(self.test_project, "TEST_SEQ1")
        self.test_sequence.save()
        self.test_sequence.create()
        
        # set it just for testing purposes
        self.test_shot = Shot(self.test_sequence, 1)
        
        self.test_versionType = VersionType(
            name="Test Animation",
            code="TANIM",
            path="{{project.code}}/Sequences/{{sequence.code}}/Shots/{{version.base_name}}/{{type.code}}",
            filename="{{version.base_name}}_{{version.take_name}}_{{type.code}}_v{{'%03d'|format(version.version_number)}}_{{version.created_by.initials}}{{version.extension}}",
            output_path="{{version.path}}/OUTPUT/{{version.take_name}}",
            environments=["MAYA", "HOUDINI"],
            type_for="Shot"
        )
        
        self.test_user = User(
            name="Test User",
            initials="tu",
            email="testuser@test.com"
        )
        
        self.kwargs = {
            "version_of": self.test_shot,
            "type": self.test_versionType,
            "base_name": "SH001",
            "take_name": "MAIN",
            "version_number": 1,
            "note": "this is the note for this version",
            "created_by": self.test_user,
            "extension": ".ma"
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
        """cleanup the test
        """
        # set the db.session to None
        db.session = None
        
        # delete the temp folder
        shutil.rmtree(self.temp_config_folder)
        shutil.rmtree(self.temp_projects_folder)
    
    def test_version_of_argument_is_skipped_raises_TypeError(self):
        """testing if a TypeError will be raised when the version_of
        argument is skipped
        """
        self.kwargs.pop("version_of")
        self.assertRaises(TypeError, Version, **self.kwargs)
    
    def test_version_of_argument_is_None(self):
        """testing if a TypeError will be raised when the version_of
        argument is None
        """
        self.kwargs["version_of"] = None
        self.assertRaises(TypeError, Version, **self.kwargs)
    
    def test_version_of_argument_is_not_a_VersionableBase_instance(self):
        """testing if a TypeError will be raised when the version_of argument
        is not a VersionableBase instance)
        """
        self.kwargs["version_of"] = "not a VersionableBase instance"
        self.assertRaises(TypeError, Version, **self.kwargs)
    
    def test_version_of_attribute_initialized_correctly(self):
        """testing if the version_of attribute initialized correctly
        """
        self.assertEqual(self.test_version.version_of, self.kwargs["version_of"])
    
    def test_version_of_attribute_is_read_only(self):
        """testing if the version_of attribute is read-only
        """
        self.assertRaises(AttributeError, setattr, self.test_version,
                          "version_of", 123)
    
    def test_type_argument_skipped(self):
        """testing if a TypeError will be raised when the type argument is
        skipped
        """
        self.kwargs.pop("type")
        self.assertRaises(TypeError, Version, **self.kwargs)
    
    def test_type_argument_is_None(self):
        """testing if a TypeError will be raised when the type argument is
        None
        """
        self.kwargs["type"] = None
        self.assertRaises(TypeError, Version, **self.kwargs)
    
    def test_type_argument_is_not_VersionType_instance(self):
        """testing if a TypeError will be raised when the type argument is not
        a VersionType instance
        """
        self.kwargs["type"] = "not a VersionType instance"
        self.assertRaises(TypeError, Version, **self.kwargs)
    
    def test_type_attribute_initialized_properly(self):
        """testing if the type attribute is initialized correctly
        """
        self.assertEqual(self.test_version.type, self.kwargs["type"])
    
    def test_type_attribute_is_read_only(self):
        """testing if the type attribute is read-only
        """
        new_type = VersionType(
            name="Test Model",
            code="TMODEL",
            path="ASSETS/{{base_name}}/{{type_name}}",
            filename="{{base_name}}_{{take_name}}_{{type_name}}_v{{version}}_{{created_by.initials}}",
            environments=["MAYA", "HOUDINI"],
            output_path="ASSETS/{{assetBaseName}}/{{assetTypeName}}/OUTPUT/{{assetSubName}}",
            type_for="Asset"
        )
        self.assertRaises(AttributeError, setattr, self.test_version, "type",
                          new_type)
    
    def test_type_argument_is_not_proper_for_the_version_of_type(self):
        """testing if a TypeError will be raised when the given VersionType
        instance's type_for attribute doesn't match the class which is given by
        version_of argument
        """
        
        # create an Asset
        new_asset = Asset(self.test_project, "TEST_ASSET1")
        new_asset.save()
        
        # create a new VersionType which is suitable for Shots
        new_vtype = VersionType(
            "Test Type", code="TType",
            path="{{project.code}}/Sequences/{{sequence.code}}/SHOTS/{{version.base_name}}/{{type.code}}",
            filename="{{version.base_name}}_{{version.take_name}}_\
            {{type.code}}_v{{'%03d'|format(version.version_number)}}_\
            {{version.created_by.initials}}",
            output_path="SHOTS/{{version.base_name}}/{{type.code}}/OUTPUT/\
            {{version.take_name}}",
            environments=["MAYA", "HOUDINI"],
            type_for="Shot"
        )
        
        # try to create a new Version with it
        # and expect a TypeError to be raised
        self.assertRaises(
            TypeError,
            Version, new_asset, new_asset.name, new_vtype, self.test_user
        )
    
    def test_base_name_argument_is_skipped(self):
        """testing if a TypeError will be raised when the base_name argument
        is skipped
        """
        self.kwargs.pop("base_name")
        self.assertRaises(TypeError, Version, **self.kwargs)
    
    def test_base_name_argument_is_None(self):
        """testing if a TypeError will be raised when the base_name argument
        is None
        """
        self.kwargs["base_name"] = None
        self.assertRaises(TypeError, Version, **self.kwargs)
    
    def test_base_name_attribute_is_None(self):
        """testing if a TypeError will be raised when the base_name
        attribute is set to None
        """
        self.assertRaises(TypeError, setattr, self.test_version,
                          "base_name", None)
    
    def test_base_name_argument_is_not_a_string(self):
        """testing if a TypeError will be raised when the base_name argument is
        not a string or unicode instance
        """
        self.kwargs["base_name"] = 12
        self.assertRaises(TypeError, Version, **self.kwargs)
    
    def test_base_name_attribute_is_not_a_string(self):
        """testing if a TypeError will be raised when the base_name argument is
        not a string or unicode instance
        """
        self.assertRaises(TypeError, setattr, self.test_version, "base_name",
                          12)
    
    def test_base_name_attribute_is_initialized_correctly(self):
        """testing if the base_name attribute is initialized correctly
        """
        self.assertEqual(self.test_version.base_name, self.kwargs["base_name"])
    
    def test_base_name_attribute_is_working_properly(self):
        """testing if the base_name attribute is working properly
        """
        test_value = "NewBaseName"
        self.test_version.base_name = test_value
        self.assertEqual(self.test_version.base_name, test_value)
    
    def test_base_name_attribute_is_formatted_correctly_on_new_Version(self):
        """testing if the base_name attribute is formatted correctly when it is
        initialized
        """
        
        for test_value in self._name_test_values:
            self.kwargs["base_name"] = test_value[0]
            new_version = Version(**self.kwargs)
            self.assertEqual(new_version.base_name, test_value[1])
    
    def test_base_name_attribute_is_formatted_correctly(self):
        """testing if the base_name attribute is formatted correctly when it is
        set to a value
        """
        for test_value in self._name_test_values:
            self.test_version.base_name = test_value[0]
            self.assertEqual(self.test_version.base_name, test_value[1])
    
    def test_base_name_argument_is_empty_string_after_formatting(self):
        """testing if a ValueError will be raised when the base_name argument
        is an empty string after it is formatted
        """
        self.kwargs["base_name"] = "'^+'^23423"
        self.assertRaises(ValueError, Version, **self.kwargs)
    
    def test_base_name_attribute_is_empty_string_after_formatting(self):
        """testing if a ValueError will be raised when the base_name attribute
        is an empty string after it is formatted
        """
        self.assertRaises(ValueError, setattr, self.test_version, "base_name",
                          "'^+'^23423")

    def test_take_name_argument_is_skipped(self):
        """testing if the default value MAIN is used when the take_name
        argument is skipped
        """
        self.kwargs.pop("take_name")
        new_version = Version(**self.kwargs)
        self.assertEqual(new_version.take_name, conf.default_take_name)
    
    def test_take_name_argument_is_None(self):
        """testing if the default value MAIN is used when the take_name
        argument is None
        """
        self.kwargs["take_name"] = None
        new_version = Version(**self.kwargs)
        self.assertEqual(new_version.take_name, conf.default_take_name)
    
    def test_take_name_attribute_is_None(self):
        """testing if the default take name value will be used when the
        take_name attribute is set to None
        """
        self.test_version.take_name = None
        self.assertEqual(self.test_version.take_name, conf.default_take_name)
    
    def test_take_name_argument_is_not_a_string(self):
        """testing if a TypeError will be raised when the take_name argument is
        not a string or unicode instance
        """
        self.kwargs["take_name"] = 12
        self.assertRaises(TypeError, Version, **self.kwargs)
    
    def test_take_name_attribute_is_not_a_string(self):
        """testing if a TypeError will be raised when the take_name argument is
        not a string or unicode instance
        """
        self.assertRaises(TypeError, setattr, self.test_version, "take_name",
                          12)
    
    def test_take_name_attribute_is_initialized_correctly(self):
        """testing if the take_name attribute is initialized correctly
        """
        self.assertEqual(self.test_version.take_name, self.kwargs["take_name"])
    
    def test_take_name_attribute_is_working_properly(self):
        """testing if the take_name attribute is working properly
        """
        test_value = "NewBaseName"
        self.test_version.take_name = test_value
        self.assertEqual(self.test_version.take_name, test_value)
    
    def test_take_name_attribute_is_formatted_correctly_on_new_Version(self):
        """testing if the take_name attribute is formatted correctly when it is
        initialized
        """
        
        for test_value in self._name_test_values:
            self.kwargs["take_name"] = test_value[0]
            new_version = Version(**self.kwargs)
            self.assertEqual(new_version.take_name, test_value[1])
    
    def test_take_name_attribute_is_formatted_correctly(self):
        """testing if the take_name attribute is formatted correctly when it is
        set to a value
        """
        for test_value in self._name_test_values:
            self.test_version.take_name = test_value[0]
            self.assertEqual(self.test_version.take_name, test_value[1])
    
    def test_take_name_argument_is_empty_string_after_formatting(self):
        """testing if a ValueError will be raised when the take_name argument
        is an empty string after it is formatted
        """
        self.kwargs["take_name"] = "'^+'^23423"
        self.assertRaises(ValueError, Version, **self.kwargs)
    
    def test_take_name_attribute_is_empty_string_after_formatting(self):
        """testing if a ValueError will be raised when the take_name attribute
        is an empty string after it is formatted
        """
        self.assertRaises(ValueError, setattr, self.test_version, "take_name",
                          "'^+'^23423")
    
    def test_version_number_argument_is_skipped_for_new_Version(self):
        """testing if the default value is used for the version attribute if
        the version argument is skipped for a new Version
        """
        self.kwargs.pop("version_number")
        new_version = Version(**self.kwargs)
        self.assertEqual(new_version.version_number, 1)
    
    def test_version_number_argument_is_skipped_for_non_new_Version(self):
        """testing if the smallest possible integer is used for the version
        attribute if the version argument is skipped for a non new Version
        """
        self.kwargs.pop("version_number")
        new_version1 = Version(**self.kwargs)
        new_version1.save()
        
        new_version2 = Version(**self.kwargs)
        new_version2.save()

        new_version3 = Version(**self.kwargs)
        new_version3.save()
        
        new_version4 = Version(**self.kwargs)
        new_version4.save()
        
        self.assertEqual(new_version1.version_number, 1)
        self.assertEqual(new_version2.version_number, 2)
        self.assertEqual(new_version3.version_number, 3)
        self.assertEqual(new_version4.version_number, 4)
    
    def test_version_is_given_smaller_than_the_max_in_db(self):
        """testing if the version is updated with the smallest available number
        if it is smaller than the maximum version number in the database
        """
        
        # lets create two Versions with same version and expect to see the last
        # one has a bigger version_number
        self.kwargs["base_name"] = "A"
        self.kwargs["version_number"] = 100
        new_version1 = Version(**self.kwargs)
        new_version1.save()
        
        self.assertEqual(new_version1.version_number, 100)
        
        new_version2 = Version(**self.kwargs)
        self.assertEqual(new_version2.version_number, 101)
    
    def test_version_number_is_zero(self):
        """testing if the version number will be updated with the smallest
        possible version_number value from the db if it is zero
        """
        self.kwargs["base_name"] = "Azero"
        self.kwargs["version_number"] = 0
        versA1 = Version(**self.kwargs)
        versA1.save()
        self.assertEqual(versA1.version_number, 1)
        
        versA2 = Version(**self.kwargs)
        versA2.save()
        self.assertEqual(versA2.version_number, 2)
    
    def test_version_number_is_negative(self):
        """testing if the version number will be updated with the smallest
        possible positive version_number value from the db if it is negative
        """
        self.kwargs["base_name"] = "Aneg"
        self.kwargs["version_number"] = -100
        versA1 = Version(**self.kwargs)
        versA1.save()
        self.assertEqual(versA1.version_number, 1)
        
        versA2 = Version(**self.kwargs)
        versA2.save()
        self.assertEqual(versA2.version_number, 2)
    
    def test_version_number_for_two_assets(self):
        """testing if the version number is calculated correctly for two assets
        with different versions_types but with same take_names
        """
        
        shot1 = Shot(self.test_sequence, "1A")
        shot1.save()
        
        # now create two versions with the same version_type
        new_vers1 = Version(
            shot1, shot1.code, self.test_versionType, self.test_user,
            take_name="Take1"
        )
        new_vers1.save()
        
        new_vers2 = Version(
            shot1, shot1.code, self.test_versionType, self.test_user,
            take_name="Take2"
        )
        new_vers2.save()
        
        self.assertEqual(new_vers1.version_number, 1)
        self.assertEqual(new_vers1.version_number, 1)

    def test_max_version_returns_the_maximum_version_number_from_the_database_for_changing_types(self):
        """testing if the max_version is returning the maximum version number
        for the current Version from the database for changing type values
        """
        self.fail("test is not implemented yet")
    
    def test_max_version_returns_the_maximum_version_number_from_the_database_for_changing_version_ofs(self):
        """testing if the max_version is returning the maximum version number
        for the current Version from the database for changing version_of
        values
        """
        self.fail("test is not implemented yet")
    
    def test_max_version_returns_the_maximum_version_number_from_the_database_for_changing_take_names(self):
        """testing if the max_version is returning the maximum version number
        for the current Version from the database for changing take_name values
        """
        
        self.kwargs.pop("version_number")
        
        self.kwargs["take_name"] = "A"
        for i in range(50):
            new_A = Version(**self.kwargs)
            new_A.save()
        
        self.kwargs["take_name"] = "B"
        for i in range(100):
            new_B = Version(**self.kwargs)
            new_B.save()
        
        # now try to create a new A and expect the version number to be 51
        self.kwargs["take_name"] = "A"
        A_new = Version(**self.kwargs)
        A_new.save()
        self.assertEqual(A_new.version_number, 51)
        
        # and B should be 101
        self.kwargs["take_name"] = "B"
        B_new = Version(**self.kwargs)
        B_new.save()
        self.assertEqual(B_new.version_number, 101)

    def test_max_version_will_not_be_effected_by_base_name(self):
        """testing if the max_version is not effected by changing base_names
        """

        self.kwargs.pop("version_number")

        self.kwargs["base_name"] = "A"
        for i in range(50):
            new_A = Version(**self.kwargs)
            new_A.save()

        self.kwargs["base_name"] = "B"
        for i in range(100):
            new_B = Version(**self.kwargs)
            new_B.save()

        # now try to create a new A and expect the version number to be 151
        self.kwargs["base_name"] = "A"
        A_new = Version(**self.kwargs)
        A_new.save()
        self.assertEqual(A_new.version_number, 151)

        # and B should be 152
        self.kwargs["base_name"] = "B"
        B_new = Version(**self.kwargs)
        B_new.save()
        self.assertEqual(B_new.version_number, 152)
    
    def test_version_number_continues_correctly_even_if_the_Versionable_name_has_changed(self):
        """testing if the version_number continues correctly even if the
        Versionable's name has changed
        """
        
        new_asset = Asset(self.test_project, "Asset 1")
        new_asset.save()
        
        self.kwargs["version_of"] = new_asset
        
        new_type = VersionType(
            name="TModel2",
            code="TModel2",
            path="{{project.code}}/Assets/{{version.base_name}}/{{type.code}}",
            filename="{{version.base_name}}_{{version.take_name}}_{{type.code}}_v{{'%03d'|format(version.version_number)}}_{{version.created_by.initials}}{{version.extension}}",
            output_path="{{version._path}}/Output/{{version.take_name}}",
            extra_folders="",
            environments=["Maya", "Houdini"],
            type_for="Asset"
        )
        
        self.kwargs["type"] = new_type
        
        # create a couple of versions
        version1 = Version(**self.kwargs)
        version1.save()
        
        self.assertEqual(version1.version_number, 1)
        
        version2 = Version(**self.kwargs)
        version2.save()
        
        self.assertEqual(version2.version_number, 2)
        
        # rename the asset
        new_asset.name = "Asset 2"
        new_asset.code = "Asset 2"
        new_asset.save()
        self.kwargs["base_name"] = new_asset.code
        
        version3 = Version(**self.kwargs)
        version3.save()
        
        self.assertEqual(version3.version_number, 3)
    
    def test_note_argument_skipped(self):
        """testing if the note attribute will be an empty string if the note
        attribute is skipped
        """
        self.kwargs.pop("note")
        new_version = Version(**self.kwargs)
        self.assertEqual(new_version.note, "")
    
    def test_note_argument_is_set_to_None(self):
        """testing if the note attribute will be an empty string if the note
        argument is set to None
        """
        self.kwargs["note"] = None
        new_version = Version(**self.kwargs)
        self.assertEqual(new_version.note, "")
    
    def test_note_attribute_is_set_to_None(self):
        """testing if the note attribute will be an empty string if it is set
        to None
        """
        self.test_version.note = None
        self.assertEqual(self.test_version.note, "")
    
    def test_note_argument_is_not_a_string(self):
        """testing if a TypeError will be raised when the note argument is not
        a string or unicode instance
        """
        self.kwargs["note"] = 123123
        self.assertRaises(TypeError, Version, **self.kwargs)
    
    def test_note_attribute_is_set_to_a_non_string(self):
        """testing if a TypeError will be raised when the note attribute is set
        to a value which is neither string or unicode
        """
        self.assertRaises(TypeError, setattr, self.test_version, "note", 123)
    
    def test_note_argument_is_working_properly(self):
        """testing if the note attribute is initialized correctly with the
        given note argument value
        """
        self.assertEqual(self.test_version.note, self.kwargs["note"])
    
    def test_note_attribute_is_working_properly(self):
        """testing if the note attribute is working properly
        """
        test_value = "test value goes here"
        self.test_version.note = test_value
        self.assertEqual(self.test_version.note, test_value)
    
    def test_created_by_argument_is_skipped(self):
        """testing if a TypeError will be raised when the created_by
        argument is skipped
        """
        self.kwargs.pop("created_by")
        self.assertRaises(TypeError, Version, **self.kwargs)
    
    def test_created_by_argument_is_None(self):
        """testing if a TypeError will be raised when the created_by
        argument is set to None
        """
        self.kwargs["created_by"] = None
        self.assertRaises(TypeError, Version, **self.kwargs)
    
    def test_created_by_attribute_is_set_to_None(self):
        """testing if a TypeError will be raised when the created_by
        attribute is set to None
        """
        self.assertRaises(TypeError, setattr, self.test_version,
                          "created_by", None)
    
    def test_created_by_argument_is_not_a_User_instance(self):
        """testing if a TypeError will be raised when the created_by argument
        is not a oyProjectManager.core.models.User instance
        """
        self.kwargs["created_by"] = 1231
        self.assertRaises(TypeError, Version, **self.kwargs)
    
    def test_created_by_attribute_is_not_a_User_instance(self):
        """testing if a TypeError will be raised when the created_by attribute
        is set to a value other than a oyProjectManager.core.models.User
        instance
        """
        self.assertRaises(TypeError, setattr, self.test_version, "created_by",
                          12314)
    
    def test_created_by_argument_is_working_properly(self):
        """testing if the created_by attribute is initialized correctly with
        the correct value given to created_by argument
        """
        self.assertEqual(self.test_version.created_by,
                         self.kwargs["created_by"])
    
    def test_created_by_attribute_is_working_properly(self):
        """testing if the created_by attribute is working properly
        """
        new_user = User(name="Test User 2", initials="tu2",
                        email="test_user2@test.com")
        self.test_version.created_by = new_user
        self.assertEqual(self.test_version.created_by, new_user)
    
    def test_filename_attribute_is_rendered_properly(self):
        """testing if the filename attribute is rendered properly with the
        given VersionType's filename template
        """
        self.assertEqual(
            self.test_version.filename,
            self.kwargs["base_name"] + "_" + \
            self.kwargs["take_name"] + "_" + \
            self.kwargs["type"].code + "_" + \
            "v" + str(self.kwargs["version_number"]).zfill(3) + "_" + \
            self.kwargs["created_by"].initials + self.kwargs["extension"]
        )
    
    def test_filename_attribute_is_read_only(self):
        """testing if the filename attribute is read-only
        """
        self.assertRaises(AttributeError, setattr, self.test_version,
                          "filename", "test_file_name")
    
    def test_filename_attribute_doesnt_change_with_the_VersionType(self):
        """testing if the filename stays the same when the VersionType
        attributes change
        """
        prev_filename = self.test_version.filename
        # now change the associated VersionType.filename
        self.kwargs["type"].filename = "A"
        
        self.assertEqual(prev_filename, self.test_version.filename)
    
#    def test_abs_path_attribute_is_rendered_properly(self):
#        """testing if the abs_path attribute is rendered properly with the
#        given VersionType's path template
#        """
#        # path = "SHOTS/{{version.base_name}}/{{version.type.code}}"
#        self.assertEqual(
#            self.test_version.abs_path,
#            self.test_version.project.full_path +
#            "/Sequences/TEST_SEQ1/Shots/" + self.kwargs["base_name"] + "/" +
#            self.kwargs["type"].code
#        )
#    
#    def test_abs_path_returns_a_proper_absolute_path_when_path_is_absolute(self):
#        """testing if the abs_path returns a proper absolute path even though
#        the path it self is an absolute path
#        """
#
#        new_versionType = VersionType(
#            name="Test Animation New",
#            code="TANIMNEW",
#            path="{{project.full_path}}/Sequences/{{sequence.code}}/Shots/{{version.base_name}}/{{type.code}}",
#            filename="{{version.base_name}}_{{version.take_name}}_{{type.code}}_v{{'%03d'|format(version.version_number)}}_{{version.created_by.initials}}{{version.extension}}",
#            output_path="{{version.path}}/OUTPUT/{{version.take_name}}",
#            environments=["MAYA", "HOUDINI"],
#            type_for="Shot"
#        )
#        
#        self.kwargs["type"] = new_versionType
#        new_version = Version(**self.kwargs)
#        
#        expected_path = self.test_project.full_path + "/Sequences/" + \
#                        self.test_sequence.code + "/Shots/" + \
#                        new_version.base_name + "/" + new_version.type.code
#        
#        self.assertTrue(new_version.abs_path == expected_path)
    
    def test_path_attribute_is_rendered_properly(self):
        """testing if the path attribute is rendered properly with the given
        VersionType's path template
        """
        # path = "SHOTS/{{version.base_name}}/{{version.type.code}}"
        self.assertEqual(
            self.test_version.path,
            os.path.join(
                self.test_project.full_path,
                "Sequences/TEST_SEQ1/Shots/" + self.kwargs["base_name"] + "/" +
                self.kwargs["type"].code
            )
        )
    
    def test_path_attribute_is_read_only(self):
        """testing if the path attribute is read-only
        """
        self.assertRaises(AttributeError, setattr, self.test_version, "path",
                          "test_file_name")
    
    def test_path_attribute_doesnt_change_with_the_VersionType(self):
        """testing if the path stays the same when the VersionType attributes
        change
        """
        prev_path = self.test_version.path
        # now change the associated VersionType.path
        self.kwargs["type"].path = "A"
        
        self.assertEqual(prev_path, self.test_version.path)
    
    def test_path_attribute_is_absolute(self):
        """testing if the rendered path attribute is absolute
        """
        self.assertTrue(os.path.isabs(self.test_version.path))
    
    def test_output_path_attribute_is_rendered_properly(self):
        """testing if the output_path attribute is rendered properly with the
        given VersionType's output_path template
        """
        # output_path = "SHOTS/{{version.base_name}}/{{version.type.code}}/
        #                    OUTPUT/{{version.take_name}}"
        self.assertEqual(
            self.test_version.output_path,
            self.test_version.path + "/OUTPUT/" + self.kwargs["take_name"]
        )
    
    def test_output_path_attribute_is_read_only(self):
        """testing if the output_path attribute is read-only
        """
        self.assertRaises(AttributeError, setattr, self.test_version,
                          "output_path", "test_file_name")
    
    def test_output_path_attribute_doesnt_change_with_the_VersionType(self):
        """testing if the output_path stays the same when the VersionType
        attributes change
        """
        prev_output_path = self.test_version.output_path
        # now change the associated VersionType.output_path
        self.kwargs["type"].output_path = "A"
        
        self.assertEqual(prev_output_path, self.test_version.output_path)
    
    def test_output_path_attribute_is_absolute(self):
        """testing if the output_path attribute is absolute
        """
        self.assertTrue(os.path.isabs(self.test_version.output_path))
        
    def test_full_path_attribute_is_rendered_properly(self):
        """testing if the full_path attribute is rendered properly
        """
        
        self.assertEqual(
            self.test_version.full_path,
            os.path.join(
                self.test_project.full_path,
                "Sequences/TEST_SEQ1/Shots/SH001/TANIM/SH001_MAIN_TANIM_v001_tu.ma"
            ).replace("\\", "/")
        )

    def test_full_path_attribute_is_read_only(self):
        """testing if the full_path attribute is read-only
        """
        self.assertRaises(AttributeError, setattr, self.test_version,
                          "full_path", "test/full/name")
    
    def test_full_path_attribute_doesnt_change_with_the_VersionType(self):
        """testing if the full_path stays the same when the VersionType
        attributes change
        """
        prev_full_path = self.test_version.full_path
        # now change the associated VersionType.path
        self.kwargs["type"].filename = "A"
        self.kwargs["type"].path = "A"
        
        self.assertEqual(prev_full_path, self.test_version.full_path)
    
    def test_full_path_attribute_is_absolute(self):
        """testing if the full_path attribute value is absolute
        """
        self.assertTrue(os.path.isabs(self.test_version.full_path))
    
    def test_references_attribute_accepts_Version_instances_only(self):
        """testing if a TypeError will be raised when the value passed to the
        references attribute is not a Version instance
        """
        self.assertRaises(TypeError, setattr, self.test_version, "references",
                          12314)
    
    def test_references_attribute_accepts_Version_instances_other_than_itself(self):
        """testing if a ValueError will be raised when the value passed to the
        references attribute is self
        """
        self.assertRaises(ValueError,
                          self.test_version.references.append,
                          self.test_version )
    
    def test_references_attribute_doesnt_allow_circular_references(self):
        """testing if a CyclicDependencyError will be raised when the reference
        passed with the references value also references this Version instance
        """
        
        self.kwargs["base_name"] = "Test Version 1"
        vers1 = Version(**self.kwargs)
        vers1.save()
        
        self.kwargs["base_name"] = "Test Version 2"
        vers2 = Version(**self.kwargs)
        vers2.references.append(vers1)
        vers2.save()
        
        self.assertRaises(CircularDependencyError,
            vers1.references.append, vers2
        )
    
    def test_references_attribute_doesnt_allow_deep_circular_references(self):
        """testing if a CyclicDependencyError will be raised when the reference
        passed with the references value has another reference which references
        this Version instance
        """
        self.kwargs["base_name"] = "Test Version 1"
        vers1 = Version(**self.kwargs)
        vers1.save()
        
        self.kwargs["base_name"] = "Test Version 2"
        vers2 = Version(**self.kwargs)
        vers2.save()
        
        self.kwargs["base_name"] = "Test Version 3"
        vers3 = Version(**self.kwargs)
        vers3.references.append(vers1)
        vers3.save()
        
        vers2.references.append(vers3)
        vers2.save()
        
        self.assertRaises(CircularDependencyError,
            vers1.references.append, vers2
        )
    
    def test__eq__operator(self):
        """testing the equality operator
        """
        
        vers1 = Version(**self.kwargs)
        vers2 = Version(**self.kwargs)
        
        # different version_of
        self.kwargs["version_of"] = Shot(self.test_sequence, 2)
        vers3 = Version(**self.kwargs)
        
        # different base_name
        self.kwargs["base_name"] = "AnotherBaseName"
        vers4 = Version(**self.kwargs)
        
        # different version_type
        
        new_versionType = VersionType(
            name="Shot Type 1",
            code="ShotType1",
            path="{{project.code}}/Shots/{{version.base_name}}/{{type.code}}",
            filename="{{version.base_name}}_{{version.take_name}}_{{type.code}}_v{{'%03d'|format(version.version_number)}}_{{version.created_by.initials}}{{version.extension}}",
            output_path="{{version._path}}/Output/{{version.take_name}}",
            extra_folders="",
            environments=["Maya", "Houdini"],
            type_for="Shot"
        )
        
        self.kwargs["type"] = new_versionType
        vers5 = Version(**self.kwargs)
        
        self.assertTrue(vers1==vers2)
        self.assertFalse(vers1==vers3)
        self.assertFalse(vers3==vers4)
        self.assertFalse(vers4==vers5)
    
    def test__ne__operator(self):
        """testing the not equal operator
        """
        
        vers1 = Version(**self.kwargs)
        vers2 = Version(**self.kwargs)
        
        # different version_of
        self.kwargs["version_of"] = Shot(self.test_sequence, 2)
        vers3 = Version(**self.kwargs)
        
        # different base_name
        self.kwargs["base_name"] = "AnotherBaseName"
        vers4 = Version(**self.kwargs)
        
        # different version_type
        
        new_versionType = VersionType(
            name="Test Model 3",
            code="TMODEL3",
            path="SHOTS/{{version.base_name}}/{{type.code}}",
            filename="{{version.base_name}}_{{version.take_name}}_\
{{type.code}}_v{{'%03d'|format(version.version_number)}}_\
{{version.created_by.initials}}",
            output_path="SHOTS/{{version.base_name}}/{{type.code}}/OUTPUT/\
{{version.take_name}}",
            environments=["MAYA", "HOUDINI"],
            type_for="Shot"
        )
        
        self.kwargs["type"] = new_versionType
        vers5 = Version(**self.kwargs)
        
        self.assertFalse(vers1!=vers2)
        self.assertTrue(vers1!=vers3)
        self.assertTrue(vers3!=vers4)
        self.assertTrue(vers4!=vers5)
    
    def test_extension_argument_is_skipped(self):
        """testing if the extension will be an empty string if the extension
        argument is skipped
        """
        self.kwargs.pop("extension")
        new_version = Version(**self.kwargs)
        self.assertEqual(new_version.extension, "")
    
    def test_extension_argument_is_not_a_string_instance(self):
        """testing if a TypeError will be raised when the extension is not an
        instance of string of unicode
        """
        self.kwargs["extension"] = 123123
        self.assertRaises(TypeError, Version, **self.kwargs)
    
    def test_extension_attribute_is_not_a_string_instance(self):
        """testing if a TypeError will be raised when the extension attribute
        is not a string or unicode instance
        """
        self.assertRaises(TypeError, setattr, self.test_version, "extension",
                          1231)
    
    def test_extension_argument_without_dot_sign(self):
        """testing if the extension attribute will include a dot even when the
        given extension arguments first character is not a dot
        """
        self.kwargs["extension"] = "ma"
        new_version = Version(**self.kwargs)
        self.assertEqual(new_version.extension, ".ma")
    
    def test_extension_attribute_without_a_dot_sign(self):
        """testing if the extension attribute will include a dot even when the
        given values first character is not a dot sign
        """
        self.test_version.extension = "psd"
        self.assertEqual(self.test_version.extension, ".psd")
    
    def test_extension_argument_is_working_properly(self):
        """testing if the extension attribute will be properly set to the given
        value with the extension argument
        """
        test_value = ".mov"
        self.kwargs["extension"] = test_value
        new_version = Version(**self.kwargs)
        self.assertEqual(new_version.extension, test_value)
    
    def test_extension_attribute_is_working_properly(self):
        """testing if the extension attribute is working properly
        """
        self.test_version.extension = ".ma"
        self.assertEqual(self.test_version.extension, ".ma")
    
    def test_extension_attribute_updates_the_filename_attribute(self):
        """testing if changing the extension attribute also updates the
        filename attribute
        """
        self.kwargs["extension"] = "ma"
        new_vers = Version(**self.kwargs)
        
        self.assertEqual(new_vers.filename, "SH001_MAIN_TANIM_v001_tu.ma")
        
        # change the extension
        new_vers.extension = "mb"
        
        # check if the filename is also updated
        self.assertEqual(new_vers.filename, "SH001_MAIN_TANIM_v001_tu.mb")
    
    def test_project_attribute_is_read_only(self):
        """testing if the project attribute is read only
        """
        self.assertRaises(AttributeError, setattr, self.test_version,
                          "project", self.test_project)
    
    def test_project_attribute_is_working_properly(self):
        """testing if the project attribute is returning the correct project
        instance
        """
        self.assertEqual(self.test_version.project,
                         self.test_version.version_of.project)
    
    def test_is_latest_version_method_is_working_properly(self):
        """testing if the is_latest_version method returns True if the current
        Version is the last among the others
        """
        
        version1 = Version(**self.kwargs)
        version1.save()
        version2 = Version(**self.kwargs)
        version2.save()
        version3 = Version(**self.kwargs)
        version3.save()
        
        self.assertFalse(version1.is_latest_version())
        self.assertFalse(version2.is_latest_version())
        self.assertTrue(version3.is_latest_version())
    
    def test_is_latest_version_method_for_different_takes(self):
        """testing if the is_latest_version method returns True if the current
        Version is the last among the others even there are Versions with
        different takes
        """

        version1 = Version(**self.kwargs)
        version1.save()
        version2 = Version(**self.kwargs)
        version2.save()
        
        self.kwargs["take_name"] = "NewTake"
        version3 = Version(**self.kwargs)
        version3.save()
        version4 = Version(**self.kwargs)
        version4.save()

        self.assertFalse(version1.is_latest_version())
        self.assertTrue(version2.is_latest_version())
        self.assertFalse(version3.is_latest_version())
        self.assertTrue(version4.is_latest_version())
    
    def test_is_latest_version_method_for_different_types(self):
        """testing if the is_latest_version method returns True if the current
        Version is the last among the others even there are Versions with
        different types
        """

        vType1 = VersionType(
            name="VersionType1",
            code="VT1",
            path="{{project.code}}/Sequences/{{sequence.code}}/Shots/{{version.base_name}}/{{type.code}}",
            filename="{{version.base_name}}_{{version.take_name}}_{{type.code}}_v{{'%03d'|format(version.version_number)}}_{{version.created_by.initials}}{{version.extension}}",
            output_path="{{version.path}}/OUTPUT/{{version.take_name}}",
            environments=["MAYA", "HOUDINI"],
            type_for="Shot"
        )
        
        vType2 = VersionType(
            name="VersionType2",
            code="VT2",
            path="{{project.code}}/Sequences/{{sequence.code}}/Shots/{{version.base_name}}/{{type.code}}",
            filename="{{version.base_name}}_{{version.take_name}}_{{type.code}}_v{{'%03d'|format(version.version_number)}}_{{version.created_by.initials}}{{version.extension}}",
            output_path="{{version.path}}/OUTPUT/{{version.take_name}}",
            environments=["MAYA", "HOUDINI"],
            type_for="Shot"
        )

        vType3 = VersionType(
            name="VersionType3",
            code="VT3",
            path="{{project.code}}/Sequences/{{sequence.code}}/Shots/{{version.base_name}}/{{type.code}}",
            filename="{{version.base_name}}_{{version.take_name}}_{{type.code}}_v{{'%03d'|format(version.version_number)}}_{{version.created_by.initials}}{{version.extension}}",
            output_path="{{version.path}}/OUTPUT/{{version.take_name}}",
            environments=["MAYA", "HOUDINI"],
            type_for="Shot"
        )
        
        vType1.save()
        vType2.save()
        vType3.save()
        
        self.kwargs["type"] = vType1
        vers1 = Version(**self.kwargs)
        vers1.save()
        vers2 = Version(**self.kwargs)
        vers2.save()
        vers3 = Version(**self.kwargs)
        vers3.save()
        
        self.kwargs["type"] = vType2
        vers4 = Version(**self.kwargs)
        vers4.save()
        vers5 = Version(**self.kwargs)
        vers5.save()
        vers6 = Version(**self.kwargs)
        vers6.save()

        self.kwargs["type"] = vType3
        vers7 = Version(**self.kwargs)
        vers7.save()
        vers8 = Version(**self.kwargs)
        vers8.save()
        vers9 = Version(**self.kwargs)
        vers9.save()

        self.assertFalse(vers1.is_latest_version())
        self.assertFalse(vers2.is_latest_version())
        self.assertTrue(vers3.is_latest_version())
        
        self.assertFalse(vers4.is_latest_version())
        self.assertFalse(vers5.is_latest_version())
        self.assertTrue(vers6.is_latest_version())

        self.assertFalse(vers7.is_latest_version())
        self.assertFalse(vers8.is_latest_version())
        self.assertTrue(vers9.is_latest_version())



    def test_latest_version_method_returns_the_latest_versions_instance(self):
        """testing if the latest_version instance returns the latest Version
        instance in this series
        """
        
        version1 = Version(**self.kwargs)
        version1.save()
        version2 = Version(**self.kwargs)
        version2.save()
        version3 = Version(**self.kwargs)
        version3.save()
        
        self.assertTrue(version1.latest_version()==version3)
        self.assertTrue(version2.latest_version()==version3)
        self.assertTrue(version3.latest_version()==version3)
    
    def test_dependency_update_list_method_returns_a_list_of_Versions_that_needs_update(self):
        """testing if the dependency_update_list returns a list of Version
        instances which are referenced by this Version instance but have newer
        versions available
        """
        
        # create a couple of Versions
        
        # Group 1
        self.kwargs["take_name"] = "Take1"
        versionRef_A1 = Version(**self.kwargs)
        versionRef_A1.save()
        versionRef_A2 = Version(**self.kwargs)
        versionRef_A2.save()
        versionRef_A3 = Version(**self.kwargs)
        versionRef_A3.save()
        
        # Group 2
        # just change the take
        self.kwargs["take_name"] = "Take2"
        versionRef_B1 = Version(**self.kwargs)
        versionRef_B1.save()
        versionRef_B2 = Version(**self.kwargs)
        versionRef_B2.save()
        versionRef_B3 = Version(**self.kwargs)
        versionRef_B3.save()

        # Group 3
        # just change the take
        self.kwargs["take_name"] = "Take3"
        versionRef_C1 = Version(**self.kwargs)
        versionRef_C1.save()
        versionRef_C2 = Version(**self.kwargs)
        versionRef_C2.save()
        versionRef_C3 = Version(**self.kwargs)
        versionRef_C3.save()
        
        # Main Version
        self.kwargs["take_name"] = "Take4"
        versionMain = Version(**self.kwargs)
        versionMain.save()

        # and reference them to each other
        versionMain.references.append(versionRef_A1)
        versionMain.references.append(versionRef_B1)
        versionMain.references.append(versionRef_C3)
        versionMain.save()
        
        # check if the dependency_update_list has only two elements
        self.assertEqual(len(versionMain.dependency_update_list), 2)
        
        # and versionRef_A1 and versionRef_B1 are the ones in the list
        self.assertTrue(versionRef_A1 in versionMain.dependency_update_list)
        self.assertTrue(versionRef_B1 in versionMain.dependency_update_list)

    def test_dependency_update_list_method_returns_a_list_of_Versions_that_needs_update_for_deeper_references(self):
        """testing if the dependency_update_list returns a list of Version
        instances which are referenced by this Version instance but have newer
        versions available and also return their references if they also have
        newer versions
        """

        # create a couple of Versions

        # Group 1
        self.kwargs["take_name"] = "Take1"
        versionRef_A1 = Version(**self.kwargs)
        versionRef_A1.save()
        versionRef_A2 = Version(**self.kwargs)
        versionRef_A2.save()
        versionRef_A3 = Version(**self.kwargs)
        versionRef_A3.save()

        # Group 2
        # just change the take
        self.kwargs["take_name"] = "Take2"
        versionRef_B1 = Version(**self.kwargs)
        versionRef_B1.save()
        versionRef_B2 = Version(**self.kwargs)
        versionRef_B2.save()
        versionRef_B3 = Version(**self.kwargs)
        versionRef_B3.save()

        # Group 3
        # just change the take
        self.kwargs["take_name"] = "Take3"
        versionRef_C1 = Version(**self.kwargs)
        versionRef_C1.save()
        versionRef_C2 = Version(**self.kwargs)
        versionRef_C2.save()
        versionRef_C3 = Version(**self.kwargs)
        versionRef_C3.save()

        # Main Version
        self.kwargs["take_name"] = "Take4"
        versionMain = Version(**self.kwargs)
        versionMain.save()

        # and reference them to each other
        versionMain.references.append(versionRef_A1)
        versionRef_A1.references.append(versionRef_B1)
        versionRef_B1.references.append(versionRef_C1)
        versionMain.save()
        versionRef_A1.save()
        versionRef_B1.save()

        # check if the dependency_update_list has only two elements
        self.assertEqual(len(versionMain.dependency_update_list), 3)

        # and versionRef_A1 and versionRef_B1 are the ones in the list
        self.assertTrue(versionRef_A1 in versionMain.dependency_update_list)
        self.assertTrue(versionRef_B1 in versionMain.dependency_update_list)
        self.assertTrue(versionRef_C1 in versionMain.dependency_update_list)

