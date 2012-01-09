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
from oyProjectManager.core.models import VersionableBase, Project

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
        """cleanup the test
        """
        # set the db.session to None
        db.session = None
        
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

    def test__code_is_not_unique_for_the_same_project(self):
        """testing if a IntegrityError will be raised when the _code attribute
        is not unique for the same project
        """

        project = Project("CODE_TEST_PROJECT")
        project.save()
        
        vbase1 = VersionableBase()
        vbase1._code = "Test"
        vbase1._project = project

        db.session.add(vbase1)
        db.session.commit()

        vbase2 = VersionableBase()
        vbase2._code = "Test"
        vbase2._project = project

        db.session.add(vbase2)

        # now expect an IntegrityError
        self.assertRaises(IntegrityError, db.session.commit)

    def test__code_is_not_unique_for_the_different_project(self):
        """testing if no IntegrityError will be raised when the _code attribute
        is not unique for to different projects
        """
        
        project1 = Project("CODE_TEST_PROJECT_1")
        project1.save()
        
        project2 = Project("CODE_TEST_PROJECT_2")
        project2.save()
        
        vbase1 = VersionableBase()
        vbase1._code = "Test"
        vbase1._project = project1
        
        db.session.add(vbase1)
        db.session.commit()
        
        vbase2 = VersionableBase()
        vbase2._code = "Test"
        vbase2._project = project2
        
        db.session.add(vbase2)
        
        # do not expect any IntegrityError
        db.session.commit()

    def test__name_is_not_unique_for_the_same_project(self):
        """testing if a IntegrityError will be raised when the _name attribute
        is not unique for the same project
        """

        project = Project("CODE_TEST_PROJECT")
        project.save()
        
        vbase1 = VersionableBase()
        vbase1._name = "Test"
        vbase1._project = project

        db.session.add(vbase1)
        db.session.commit()

        vbase2 = VersionableBase()
        vbase2._name = "Test"
        vbase2._project = project
        
        db.session.add(vbase2)
        
        # now expect an IntegrityError
        self.assertRaises(IntegrityError, db.session.commit)

    def test__name_is_not_unique_for_the_different_project(self):
        """testing if no IntegrityError will be raised when the _name attribute
        is not unique for to different projects
        """

        project1 = Project("CODE_TEST_PROJECT_1")
        project1.save()

        project2 = Project("CODE_TEST_PROJECT_2")
        project2.save()

        vbase1 = VersionableBase()
        vbase1._name = "Test"
        vbase1._project = project1

        db.session.add(vbase1)
        db.session.commit()

        vbase2 = VersionableBase()
        vbase2._name = "Test"
        vbase2._project = project2

        db.session.add(vbase2)

        # do not expect any IntegrityError
        db.session.commit()

    def test_description_attribute_is_set_to_None(self):
        """testing if a TypeError will be raised when the description attribute
        is set to None
        """
        vbase = VersionableBase()
        self.assertRaises(TypeError, setattr, vbase, "description", None)

    def test_description_attribute_is_not_a_string(self):
        """testing if a TypeError will be raised when the description attribute
        is not set to a string or unicode
        """
        vbase = VersionableBase()
        self.assertRaises(TypeError, setattr, vbase, "description", 234235)

    def test_description_attribute_is_working_properly(self):
        """testing if the description attribute is working properly
        """
        vbase = VersionableBase()
        test_value = "this is the description"
        vbase.description = test_value
        self.assertEqual(vbase.description, test_value)
    
    def test_project_can_not_be_None(self):
        """testing if a IntegrityError will be raised when the project
        attribute is None
        """
        vbase = VersionableBase()
        vbase._name = "Test"
        vbase._project = None
        
        db.setup()
        db.session.add(vbase)
        
        self.assertRaises(IntegrityError, db.session.commit)
        
