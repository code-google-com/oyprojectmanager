# -*- coding: utf-8 -*-
import os

import shutil
import tempfile
import unittest
from oyProjectManager import config
from oyProjectManager.core.models import (VersionableBase, Version,
                                          VersionType, User, Project)

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
        
        os.environ[conf.repository_env_key] = self.temp_projects_folder
        
        self.test_project = Project("TEST_PROJ1")
        self.test_project.create()
        self.test_project.save()
        
        # set it just for testing purposes
        self.test_vbase = VersionableBase()
        self.test_vbase._project = self.test_project
        
        self.test_versionType = VersionType(
            project=self.test_project,
            name="Test Animation",
            code="TANIM",
            path="SHOTS/{{version.base_name}}/{{type.code}}",
            filename="{{version.base_name}}_{{version.take_name}}_{{type.code}}_v{{'%03d'|format(version.version_number)}}_{{version.created_by.initials}}",
            output_path="SHOTS/{{version.base_name}}/{{type.code}}/OUTPUT/{{version.take_name}}",
            environments=["MAYA", "HOUDINI"],
            type_for="Shot"
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
        self.assertIs(self.test_version.version_of, self.kwargs["version_of"])
    
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
        self.assertIs(self.test_version.type, self.kwargs["type"])
    
    def test_type_attribute_is_read_only(self):
        """testing if the type attribute is read-only
        """
        new_type = VersionType(
            project=self.test_project,
            name="Test Model",
            code="TMODEL",
            path="ASSETS/{{base_name}}/{{type_name}}",
            filename="{{base_name}}_{{take_name}}_{{type_name}}_v{{version}}_{{created_by.initials}}",
            environments="MAYA,HOUDINI",
            output_path="ASSETS/{{assetBaseName}}/{{assetTypeName}}/OUTPUT/{{assetSubName}}",
            type_for="Asset"
        )
        self.assertRaises(AttributeError, setattr, self.test_version, "type",
                          new_type)
    
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
        self.assertEqual(new_version.take_name, conf.take_name)
    
    def test_take_name_argument_is_None(self):
        """testing if the default value MAIN is used when the take_name
        argument is None
        """
        self.kwargs["take_name"] = None
        new_version = Version(**self.kwargs)
        self.assertEqual(new_version.take_name, conf.take_name)
    
    def test_take_name_attribute_is_None(self):
        """testing if the default take name value will be used when the
        take_name attribute is set to None
        """
        self.test_version.take_name = None
        self.assertEqual(self.test_version.take_name, conf.take_name)
    
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
    
    def test_max_version_returns_the_maximum_version_number_from_the_database(self):
        """testing if the max_version is returning the maximum version number
        for the current Version from the database
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
        
        # now try to create a new A and expect the version number to be 51
        self.kwargs["base_name"] = "A"
        A_new = Version(**self.kwargs)
        A_new.save()
        self.assertEqual(A_new.version_number, 51)
        
        # and B should be 101
        self.kwargs["base_name"] = "B"
        B_new = Version(**self.kwargs)
        B_new.save()
        self.assertEqual(B_new.version_number, 101)
    
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
            self.kwargs["created_by"].initials
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
    
    def test_path_attribute_is_rendered_properly(self):
        """testing if the path attribute is rendered properly with the given
        VersionType's path template
        """
        # path = "SHOTS/{{version.base_name}}/{{version.type.code}}"
        self.assertEqual(
            self.test_version.path,
            "SHOTS/" + self.kwargs["base_name"] + "/" + self.kwargs["type"].code
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
    
    def test_fullpath_attribute_is_rendered_properly(self):
        """testing if the fullpath attribute is rendered properly
        """
        self.assertEqual(
            self.test_version.fullpath,
            "SHOTS/SH001/TANIM/SH001_MAIN_TANIM_v001_tu"
        )

    def test_fullpath_attribute_is_read_only(self):
        """testing if the fullpath attribute is read-only
        """
        self.assertRaises(AttributeError, setattr, self.test_version,
                          "fullpath", "test/full/name")
    
    def test_fullpath_attribute_doesnt_change_with_the_VersionType(self):
        """testing if the fullpath stays the same when the VersionType
        attributes change
        """
        prev_fullpath = self.test_version.fullpath
        # now change the associated VersionType.path
        self.kwargs["type"].filename = "A"
        self.kwargs["type"].path = "A"
        
        self.assertEqual(prev_fullpath, self.test_version.fullpath)
    
    def test_references_attribute_accepts_Version_instances_only(self):
        """testing if a TypeError will be raised when the value passed to the
        references attribute is not a Version instance
        """
        self.fail("test is not implemented yet")
    
    def test_references_attribute_accepts_Version_instances_other_than_itself(self):
        """testing if a ValueError will be raised when the value passed to the
        references attribute is self
        """
        self.fail("test is not implemented yet")
    
    def test_references_attribute_doesnt_allow_circular_references(self):
        """testing if a CyclicDependencyError will be raised when the reference
        passed with the references value also references this Version instance
        """
        self.fail("test is not implemented yet")
    
    def test_references_attribute_doesnt_allow_deep_circular_references(self):
        """testing if a CyclicDependencyError will be raised when the reference
        passed with the references value has another reference which references
        this Version instance
        """
        self.fail("test is not implemented yet")
