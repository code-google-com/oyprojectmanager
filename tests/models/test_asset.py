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
from oyProjectManager import conf, db, Asset, Project, VersionType, User, Version

class AssetTester(unittest.TestCase):
    """tests the Asset class
    """
    
    def setUp(self):
        """setup the test settings with environment variables
        """
        # -----------------------------------------------------------------
        # start of the setUp
        # create the environment variable and point it to a temp directory
        conf.database_url = "sqlite://"
        
        self.temp_config_folder = tempfile.mkdtemp()
        self.temp_projects_folder = tempfile.mkdtemp()
        
        os.environ["OYPROJECTMANAGER_PATH"] = self.temp_config_folder
        os.environ[conf.repository_env_key] = self.temp_projects_folder
        
        self.test_proj = Project("TEST_PROJ1")
        self.test_proj.create()
        
        self.kwargs = {
            "project": self.test_proj,
            "name": "Test Asset",
            "code": "TEST_ASSET",
            'type': 'Prop',
        }
        
        self.test_asset = Asset(**self.kwargs)
        self.test_asset.save()
        
        self._name_test_values = [
            ("Test Asset", "Test Asset"),
            ("23Test_Asset", "23Test_Asset"),
            ("TEST_ASSET", "TEST_ASSET"),
            ("£#$£#$AB", "AB"),
            ("'^+'^%^+%&&AB3£#$£½'^+'3'^+'4", "AB334"),
            ("afasfas fasf asdf67", "Afasfas fasf asdf67"),
            ("45a", "45a"),
            ("45acafs","45acafs"),
            ("45'^+'^+a 234", "45a 234"),
            ("45asf78wr", "45asf78wr"),
            ("'^+'afsd2342'^+'asdFGH", "Afsd2342asdFGH"),
        ]
        
        self._code_test_values = [
            ("Test Asset", "Test_Asset"),
            ("23Test_Asset", "23Test_Asset"),
            ("TEST_ASSET", "TEST_ASSET"),
            ("£#$£#$AB", "AB"),
            ("'^+'^%^+%&&AB3£#$£½'^+'3'^+'4", "AB334"),
            ("afasfas fasf asdf67", "Afasfas_fasf_asdf67"),
            ("45a", "45a"),
            ("45acafs","45acafs"),
            ("45'^+'^+a 234", "45a_234"),
            ("45asf78wr", "45asf78wr"),
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
        self.kwargs["name"] = "£#$£'^+'"
        self.assertRaises(ValueError, Asset, **self.kwargs)
    
    def test_name_attribute_is_empty_string_after_formatting(self):
        """testing if a ValueError will be raised when the name attribugte is
        an empty string after formatting
        """
        self.assertRaises(ValueError, setattr, self.test_asset, "name",
                          "£#$£'^+'")
    
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
        self.kwargs["code"] = "'^+'%+%"
        self.assertRaises(ValueError, Asset, **self.kwargs)
    
    def test_code_attribute_is_empty_string_after_formatting(self):
        """testing if a ValueError will be raised when the code attribugte is
        an empty string after formatting
        """
        self.assertRaises(ValueError, setattr, self.test_asset, "code",
                          "'^+'%+%")
    
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
    
    def test_type_argument_is_skipped(self):
        """testing if skipping the type argument the type attribute will be set
        to conf.default_asset_type_name
        """
        self.kwargs.pop('type')
        new_asset = Asset(**self.kwargs)
        self.assertEqual(new_asset.type, conf.default_asset_type_name)
    
    def test_type_argument_is_None(self):
        """testing if setting the type argument to None will set the type
        attribute to conf.default_asset_type_name
        """
        self.kwargs['type'] = None
        new_asset = Asset(**self.kwargs)
        self.assertEqual(new_asset.type, conf.default_asset_type_name)
    
    def test_type_attribute_is_set_to_None(self):
        """testing if setting the type attribute to None will set the type to
        conf.default_asset_type_name
        """
        self.test_asset.type = None
        self.assertEqual(self.test_asset.type, conf.default_asset_type_name)
    
    def test_type_argument_accepts_string_or_unicode_only(self):
        """testing if a TypeError will be raised when the type argument is set
        to a value other than string or unicode value
        """
        self.kwargs['type'] = 12312
        self.assertRaises(TypeError, Asset, **self.kwargs)
    
    def test_type_attribute_accepts_string_or_unicode_only(self):
        """testing if a TypeError will be raised when the type attribute is set
        to a value other than string or unicode
        """
        self.assertRaises(TypeError, setattr, self.test_asset, 'type', 2342)
    
    def test_type_argument_is_working_properly(self):
        """testing if the type attribute is set with the type argument
        """
        self.kwargs['type'] = "Test_Type_1"
        new_asset = Asset(**self.kwargs)
        self.assertEqual(self.kwargs['type'], new_asset.type)
    
    def test_type_attribute_is_working_properly(self):
        """testing if the type attribute is working properly
        """
        test_value = "Test_Type_1"
        self.test_asset.type = test_value
        self.assertEqual(self.test_asset.type, test_value)
    
    def test_type_argument_formatting(self):
        """testing if the type argument is formatted correctly
        """
        for test_values in self._code_test_values:
            input_value = test_values[0]
            expected_value = test_values[1]
            self.kwargs['type'] = input_value
            new_asset = Asset(**self.kwargs)
            self.assertEqual(new_asset.type, expected_value)
    
    def test_type_argument_is_invalid_after_formatting(self):
        """testing if a ValueError will be raised when the type argument is
        invalid after formatting
        """
        self.kwargs['type'] = '@#$@#$'
        self.assertRaises(ValueError, Asset, **self.kwargs)
    
    def test_type_attribute_is_invalid_after_formatting(self):
        """testing if a ValueError will be raised when the type attribute is
        invalid after formatting
        """
        self.assertRaises(ValueError, setattr, self.test_asset, 'type', '#@$#')
    
    def test_type_attribute_formatting(self):
        """testing if the type attribute is formatted correctly
        """
        for test_values in self._code_test_values:
            input_value = test_values[0]
            expected_value = test_values[1]
            self.test_asset.type = input_value
            self.assertEqual(self.test_asset.type, expected_value)
    
    def test_deleting_an_asset_will_not_delete_the_related_project(self):
        """testing if deleting an asset will not delete the related project
        """
        proj1 = Project('test project 1')
        proj1.save()
        
        asset = Asset(proj1, 'Test asset')
        asset.save()
        
        # check if they are in the session
        self.assertIn(proj1, db.session)
        self.assertIn(asset, db.session)
        
        # delete the asset
        db.session.delete(asset)
        db.session.commit()
        
        # check if it is removed from the session
        self.assertNotIn(asset, db.session)
        
        # and the project is there
        self.assertIn(proj1, db.session)
    
    def test_deleting_an_asset_will_not_delete_the_other_assets_in_the_related_project(self):
        """testing if deleting an asset will not delete the other assets in the
        related project
        """
        proj1 = Project('test project 1')
        proj1.save()
        
        asset1 = Asset(proj1, 'test asset 1')
        asset1.save()
        
        asset2 = Asset(proj1, 'test asset 2')
        asset2.save()
        
        asset3 = Asset(proj1, 'test asset 3')
        asset3.save()
        
        # check if they are properly in the db.session
        self.assertIn(proj1, db.session)
        self.assertIn(asset1, db.session)
        self.assertIn(asset2, db.session)
        self.assertIn(asset3, db.session)
        
        # delete asset1
        db.session.delete(asset1)
        db.session.commit()
        
        # check if the asset1 is deleted
        self.assertNotIn(asset1, db.session)
        
        # and the others are in place
        self.assertIn(proj1, db.session)
        self.assertIn(asset2, db.session)
        self.assertIn(asset3, db.session)
    
    def test_deleting_an_asset_will_delete_all_the_related_versions(self):
        """testing if deleting an asset will also delete the related versions
        """
        proj1 = Project('test project 1')
        proj1.save()
        
        asset1 = Asset(proj1, 'test asset 1')
        asset1.save()
        
        asset2 = Asset(proj1, 'test asset 2')
        asset2.save()
        
        asset_vtypes = VersionType.query().filter_by(type_for="Asset").all()
        
        user = User.query().first()
        
        vers1 = Version(
            version_of=asset1,
            base_name=asset1.code,
            type=asset_vtypes[0],
            created_by=user
        )
        vers1.save()
        
        vers2 = Version(
            version_of=asset1,
            base_name=asset1.code,
            type=asset_vtypes[0],
            created_by=user
        )
        vers2.save()
        
        vers3 = Version(
            version_of=asset1,
            base_name=asset1.code,
            type=asset_vtypes[0],
            created_by=user
        )
        vers3.save()
    
        vers4 = Version(
            version_of=asset2,
            base_name=asset2.code,
            type=asset_vtypes[0],
            created_by=user
        )
        vers4.save()
        
        vers5 = Version(
            version_of=asset2,
            base_name=asset2.code,
            type=asset_vtypes[0],
            created_by=user
        )
        vers5.save()
        
        vers6 = Version(
            version_of=asset2,
            base_name=asset2.code,
            type=asset_vtypes[0],
            created_by=user
        )
        vers6.save()    
        
        # check if all are in the session
        self.assertIn(proj1, db.session)
        self.assertIn(asset1, db.session)
        self.assertIn(asset2, db.session)
        self.assertIn(vers1, db.session)
        self.assertIn(vers2, db.session)
        self.assertIn(vers3, db.session)
        self.assertIn(vers4, db.session)
        self.assertIn(vers5, db.session)
        self.assertIn(vers6, db.session)
        
        # delete the asset
        db.session.delete(asset1)
        db.session.commit()
        
        # check if it is not in the session anymore
        self.assertNotIn(asset1, db.session)
        
        # check if the versions are also deleted
        self.assertNotIn(vers1, db.session)
        self.assertNotIn(vers2, db.session)
        self.assertNotIn(vers3, db.session)
        
        # check if the others are still there
        self.assertIn(proj1, db.session)
        self.assertIn(asset2, db.session)
        self.assertIn(vers4, db.session)
        self.assertIn(vers5, db.session)
        self.assertIn(vers6, db.session)
    
    def test_deleting_an_asset_will_delete_all_the_related_versions_but_keep_references(self):
        """testing if deleting an asset will only delete the version of that
        asset and will keep the referenced versions.
        """
        proj1 = Project('test project 1')
        proj1.save()
        
        asset1 = Asset(proj1, 'test asset 1')
        asset1.save()
        
        asset2 = Asset(proj1, 'test asset 2')
        asset2.save()
        
        asset_vtypes = VersionType.query().filter_by(type_for="Asset").all()
        
        user = User.query().first()
        
        vers1 = Version(
            version_of=asset1,
            base_name=asset1.code,
            type=asset_vtypes[0],
            created_by=user
        )
        vers1.save()
        
        vers2 = Version(
            version_of=asset1,
            base_name=asset1.code,
            type=asset_vtypes[0],
            created_by=user
        )
        vers2.save()
        
        vers3 = Version(
            version_of=asset1,
            base_name=asset1.code,
            type=asset_vtypes[0],
            created_by=user
        )
        vers3.save()
    
        vers4 = Version(
            version_of=asset2,
            base_name=asset2.code,
            type=asset_vtypes[0],
            created_by=user
        )
        vers4.save()
        
        vers5 = Version(
            version_of=asset2,
            base_name=asset2.code,
            type=asset_vtypes[0],
            created_by=user
        )
        vers5.save()
        
        vers6 = Version(
            version_of=asset2,
            base_name=asset2.code,
            type=asset_vtypes[0],
            created_by=user
        )
        vers6.save()
        
        # reference vers4, vers5 and vers6 to vers1, vers2 and vers3
        vers1.references.append(vers4)
        vers1.references.append(vers5)
        vers1.references.append(vers6)
        
        vers2.references.append(vers4)
        vers2.references.append(vers5)
        vers2.references.append(vers6)
        
        vers3.references.append(vers4)
        vers3.references.append(vers5)
        vers3.references.append(vers6)
        
        # check if all are in the session
        self.assertIn(proj1, db.session)
        self.assertIn(asset1, db.session)
        self.assertIn(asset2, db.session)
        self.assertIn(vers1, db.session)
        self.assertIn(vers2, db.session)
        self.assertIn(vers3, db.session)
        self.assertIn(vers4, db.session)
        self.assertIn(vers5, db.session)
        self.assertIn(vers6, db.session)
        
        # there should be 9 entries in the secondary table
        result = db.session\
            .query('referencer_id', 'reference_id')\
            .from_statement("SELECT referencer_id, reference_id "
                            "FROM Version_References").all()
        self.assertEqual(len(result), 9)
        
        # delete the asset
        db.session.delete(asset1)
        db.session.commit()
        
        # check if it is not in the session anymore
        self.assertNotIn(asset1, db.session)
        
        # check if the versions are also deleted
        self.assertNotIn(vers1, db.session)
        self.assertNotIn(vers2, db.session)
        self.assertNotIn(vers3, db.session)
        
        # check if the others are still there
        self.assertIn(proj1, db.session)
        self.assertIn(asset2, db.session)
        self.assertIn(vers4, db.session)
        self.assertIn(vers5, db.session)
        self.assertIn(vers6, db.session)
        
        # to be sure check the secondary table
        result = db.session\
            .query('referencer_id', 'reference_id')\
            .from_statement("SELECT referencer_id, reference_id "
                            "FROM Version_References").all()
        self.assertEqual(len(result), 0)
