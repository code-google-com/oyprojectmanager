# -*- coding: utf-8 -*-
# Copyright (c) 2009-2012, Erkan Ozgur Yilmaz
# 
# This module is part of oyProjectManager and is released under the BSD 2
# License: http://www.opensource.org/licenses/BSD-2-Clause
import os
import shutil
import tempfile

import unittest
from sqlalchemy import Column, Integer
from oyProjectManager import conf, db
from oyProjectManager.db.declarative import Base
from oyProjectManager.models.link import FileLink
from oyProjectManager.models.mixins import IOMixin

class IOMixedInClass(Base, IOMixin):
    """A class which is mixed with IOMixin for testing purposes
    """
    __tablename__ = "IOMixClasses"
    IOMixClass_id = Column("id", Integer, primary_key=True)

    def __init__(self, **kwargs):
        super(IOMixedInClass, self).__init__(**kwargs)
        IOMixin.__init__(self, **kwargs)


class IOMixedInClass2(Base, IOMixin):
    """A class which is mixed with IOMixin for testing purposes
    """
    __tablename__ = "IOMixClasses2"
    IOMixClass_id = Column("id", Integer, primary_key=True)

    def __init__(self, **kwargs):
        super(IOMixedInClass2, self).__init__(**kwargs)
        IOMixin.__init__(self, **kwargs)

class IOMixinTester(unittest.TestCase):
    """tests the oyProjectManager.models.mixins.IOMixin class
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
        
        self.inputs = [
            FileLink(
                filename="a.%03d.tga 5-14 100",
                path="/tmp"
            ),
            FileLink(
                filename='b.%03d.tga 1-100',
                path="/tmp"
            )
        ]
        
        self.outputs = [
            FileLink(
                filename='Test_Proj_Test_Seq_SH001_MAIN_Lighting_beauty_MasterBeauty.%03d.exr 1-100',
                path='/tmp'
            ),
             FileLink(
                filename='Test_Proj_Test_Seq_SH001_MAIN_Lighting_shadow_MasterBeauty.%03d.exr 1-100',
                path='/tmp'
            ),
        ]
        
        self.kwargs = {
            "inputs": self.inputs,
            "outputs": self.outputs,
        }
        
        self.test_io_mixed_in_obj = IOMixedInClass(**self.kwargs)
    
    def tearDown(self):
        """clean up the test
        """
        
        # set the db.session to None
        db.session = None
        
        # delete the temp folders
        shutil.rmtree(self.temp_config_folder)
        shutil.rmtree(self.temp_projects_folder)
    
    def test_inputs_argument_is_skipped(self):
        """testing if skipping the inputs argument will set the inputs to an
        empty list
        """
        self.kwargs.pop('inputs')
        new_obj = IOMixedInClass(**self.kwargs)
        self.assertEqual(new_obj.inputs, [])
    
    def test_inputs_argument_is_None(self):
        """testing if a TypeError will be raised when the inputs argument is
        set to None
        """
        self.kwargs['inputs'] = None
        self.assertRaises(TypeError, IOMixedInClass, **self.kwargs)
    
    def test_inputs_attribute_is_None(self):
        """testing if a TypeError will be raised when the inputs attribute is
        set to None
        """
        self.assertRaises(
            TypeError,
            setattr,
            self.test_io_mixed_in_obj.inputs,
            None
        )
    
    def test_inputs_argument_is_not_a_list_instance(self):
        """testing if a TypeError will be raised when the inputs argument is
        not a list
        """
        self.kwargs['inputs'] = 'not a list instance'
        self.assertRaises(TypeError, IOMixedInClass, **self.kwargs)
    
    def test_inputs_attribute_is_not_a_list_instance(self):
        """testing if a TypeError will be raised when the inputs attribute is
        set to something other than a list
        """
        self.assertRaises(TypeError, setattr, self.test_io_mixed_in_obj,
            'inputs', 'not a list instance')
    
    def test_inputs_argument_is_not_a_list_of_FileLink_instances(self):
        """testing if a TypeError will be raised when the inputs argument is
        not a list of all FileLink instances
        """
        self.kwargs['inputs'] = ['these', 'are', 'not', 'a', 'FileLink',
                                 'instances']
        self.assertRaises(TypeError, IOMixedInClass, **self.kwargs)
    
    def test_inputs_attribute_is_not_a_list_of_FileLink_instances(self):
        """testing if a TypeError will be raised when the inputs attribute is
        not set to a list of all FileLink instances
        """
        self.assertRaises(
            TypeError,
            setattr,
            self.test_io_mixed_in_obj, 'inputs',
            ['these', 'are', 'not', 'a', 'FileLink', 'instances']
        )
        
    def test_inputs_argument_is_working_properly(self):
        """testing if the inputs argument value is passed to inputs attribute
        correctly
        """
        self.assertEqual(
            self.test_io_mixed_in_obj.inputs,
            self.kwargs['inputs']
        )
    
    def test_inputs_attribute_is_working_properly(self):
        """testing if the inputs attribute is working properly
        """
        new_FileLinks = [
            FileLink('test.tga', '/tmp')
        ]
        self.test_io_mixed_in_obj.inputs = new_FileLinks
        self.assertEqual(
            self.test_io_mixed_in_obj.inputs,
            new_FileLinks
        )
    
    def test_outputs_argument_is_skipped(self):
        """testing if skipping the outputs argument will set the outputs to an
        empty list
        """
        self.kwargs.pop('outputs')
        new_obj = IOMixedInClass(**self.kwargs)
        self.assertEqual(new_obj.outputs, [])
    
    def test_outputs_argument_is_None(self):
        """testing if a TypeError will be raised when the outputs argument is
        set to None
        """
        self.kwargs['outputs'] = None
        self.assertRaises(TypeError, IOMixedInClass, **self.kwargs)
    
    def test_outputs_attribute_is_None(self):
        """testing if a TypeError will be raised when the outputs attribute is
        set to None
        """
        self.assertRaises(
            TypeError,
            setattr,
            self.test_io_mixed_in_obj.outputs,
            None
        )
    
    def test_outputs_argument_is_not_a_list_instance(self):
        """testing if a TypeError will be raised when the outputs argument is
        not a list
        """
        self.kwargs['outputs'] = 'not a list instance'
        self.assertRaises(TypeError, IOMixedInClass, **self.kwargs)
    
    def test_outputs_attribute_is_not_a_list_instance(self):
        """testing if a TypeError will be raised when the outputs attribute is
        set to something other than a list
        """
        self.assertRaises(TypeError, setattr, self.test_io_mixed_in_obj,
            'outputs', 'not a list instance')
    
    def test_outputs_argument_is_not_a_list_of_FileLink_instances(self):
        """testing if a TypeError will be raised when the outputs argument is
        not a list of all FileLink instances
        """
        self.kwargs['outputs'] = ['these', 'are', 'not', 'a', 'FileLink',
                                 'instances']
        self.assertRaises(TypeError, IOMixedInClass, **self.kwargs)
    
    def test_outputs_attribute_is_not_a_list_of_FileLink_instances(self):
        """testing if a TypeError will be raised when the outputs attribute is
        not set to a list of all FileLink instances
        """
        self.assertRaises(
            TypeError,
            setattr,
            self.test_io_mixed_in_obj, 'outputs',
            ['these', 'are', 'not', 'a', 'FileLink', 'instances']
        )
        
    def test_outputs_argument_is_working_properly(self):
        """testing if the outputs argument value is passed to outputs attribute
        correctly
        """
        self.assertEqual(
            self.test_io_mixed_in_obj.outputs,
            self.kwargs['outputs']
        )
    
    def test_outputs_attribute_is_working_properly(self):
        """testing if the outputs attribute is working properly
        """
        new_FileLinks = [
            FileLink('test.tga', '/tmp')
        ]
        self.test_io_mixed_in_obj.outputs = new_FileLinks
        self.assertEqual(
            self.test_io_mixed_in_obj.outputs,
            new_FileLinks
        )

class IOMixin_DB_Tester(unittest.TestCase):
    """tests IOMixin in a persistent environment
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
        
        self.inputs = [
            FileLink(
                filename="a.%03d.tga 5-14 100",
                path="/tmp"
            ),
            FileLink(
                filename='b.%03d.tga 1-100',
                path="/tmp"
            )
        ]
        
        self.outputs = [
            FileLink(
                filename='Test_Proj_Test_Seq_SH001_MAIN_Lighting_beauty_MasterBeauty.%03d.exr 1-100',
                path='/tmp'
            ),
             FileLink(
                filename='Test_Proj_Test_Seq_SH001_MAIN_Lighting_shadow_MasterBeauty.%03d.exr 1-100',
                path='/tmp'
            ),
        ]
        
        self.kwargs = {
            "inputs": self.inputs,
            "outputs": self.outputs,
        }
        
        self.test_io_mixed_in_obj = IOMixedInClass(**self.kwargs)
    
    def tearDown(self):
        """clean up the test
        """
        
        # set the db.session to None
        db.session = None
        
        # delete the temp folders
        shutil.rmtree(self.temp_config_folder)
        shutil.rmtree(self.temp_projects_folder)
 
    def test_persistence_of_IOMixin(self):
        """testing the persistence of IOMixedInClass
        """
        db.setup()
        db.session.add(self.test_io_mixed_in_obj)
        db.session.commit()
        
        # now delete the object and try to retrieve it back
        del self.test_io_mixed_in_obj
        
        io_mixed_in_obj_DB = db.session.query(IOMixedInClass).first()
        
        # check the attributes
        self.assertEqual(
            io_mixed_in_obj_DB.inputs, self.kwargs['inputs']
        )
        self.assertEqual(
            io_mixed_in_obj_DB.outputs, self.kwargs['outputs']
        )
    
    def test_another_class_mixed_in_with_IOMixin(self):
        """testing if everything works properly if more than one class is mixed
        in with the IOMixin
        """
        db.setup()
        new_io_mixed_in_obj2 = IOMixedInClass2(**self.kwargs)
        db.session.add(self.test_io_mixed_in_obj)
        db.session.add(new_io_mixed_in_obj2)
        db.session.commit()
        
        # delete them and retrieve back from DB
        del new_io_mixed_in_obj2
        del self.test_io_mixed_in_obj
        
        a = db.query(IOMixedInClass).first()
        b = db.query(IOMixedInClass2).first()
        
        self.assertEqual(a.inputs, self.kwargs['inputs'])
        self.assertEqual(a.outputs, self.kwargs['outputs'])
        
        self.assertEqual(b.inputs, self.kwargs['inputs'])
        self.assertEqual(b.outputs, self.kwargs['outputs'])
