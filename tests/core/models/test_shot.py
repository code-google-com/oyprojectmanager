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
from oyProjectManager.core.models import Project, Sequence, Shot

conf = config.Config()

class ShotTester(unittest.TestCase):
    """tests the Shot class
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
        
        self.test_seq = Sequence(self.test_proj, "TEST_SEQ")
        self.test_seq.save()
        self.test_seq.create()
        
        self.kwargs = {
            "sequence": self.test_seq,
            "number": 1,
            "start_frame": 1,
            "end_frame": 100,
            "description": "Test shot"
        }
        
        self.test_shot = Shot(**self.kwargs)
        
        self._number_test_values = [
            (23, "23"),
            ("23", "23"),
            ("324ASF", "324A"),
            ("AD43", "43"),
            ("AS43A", "43A"),
            ("afasfas fasf asdf67", "67"),
            ("45a", "45A"),
            ("45acafs","45A"),
            ("45'^+'^+a", "45A"),
            ("45asf78wr", "45A"),
            ("'^+'afsd2342'^+'asdFGH", "2342A"),
        ]
    
    def tearDown(self):
        """cleanup the test
        """
        # set the db.session to None
        db.session = None
        
        # delete the temp folder
        shutil.rmtree(self.temp_config_folder)
        shutil.rmtree(self.temp_projects_folder)
    
    def test_number_argument_is_skipped(self):
        """testing if a TypeError will be raised when the number argument is
        skipped
        """
        self.kwargs.pop("number")
        self.assertRaises(TypeError, Shot, **self.kwargs)
    
    def test_number_argument_is_None(self):
        """testing if a TypeError will be raised when the number argument is
        None
        """
        self.kwargs["number"] = None
        self.assertRaises(TypeError, Shot, **self.kwargs)

    def test_number_attribute_is_None(self):
        """testing if a TypeError will be raised when the number attribute is
        set to None
        """
        self.assertRaises(TypeError, setattr, self.test_shot, "number", None)
    
    def test_number_argument_is_empty_string(self):
        """testing if a ValueError will be raised when the number argument is
        an empty string
        """
        self.kwargs["number"] = ""
        self.assertRaises(ValueError, Shot, **self.kwargs)
    
    def test_number_attribute_is_set_to_empty_string(self):
        """testing if a ValueError will be raised when the number attribute is
        set to an empty string
        """
        self.assertRaises(ValueError, setattr, self.test_shot, "number", "")
    
    def test_number_argument_is_not_a_string_or_integer(self):
        """testing if a TypeError will be raised when the number argument is
        not a string or integer
        """
        self.kwargs["number"] = [123]
        self.assertRaises(TypeError, Shot, **self.kwargs)
    
    def test_number_attribute_is_not_a_string_integer(self):
        """testing if a TypeError will be raised when the number attribute is
        not a string or integer
        """
        self.assertRaises(TypeError, setattr, self.test_shot, "number", [])
    
    def test_number_argument_formatted_correctly(self):
        """testing if the number attribute is formatted correctly when the class
        is initialized
        """
        for test_value in self._number_test_values:
            self.kwargs["number"] = test_value[0]
            new_shot = Shot(**self.kwargs)
            self.assertEqual(test_value[1], new_shot.number)
            
    
#    def test_number_attribute_formatted_correctly(self):
#        """testing if the number attribute is formatted correctly
#        """
#        for test_value in self._number_test_values:
#            self.kwargs["number"] = test_value[0]
#            new_shot = Shot(**self.kwargs)
#            self.assertEqual(test_value[1], new_shot.number)
    
    def test_number_is_already_defined_in_the_sequence(self):
        """testing if an IntegrityError will be raised when the shot number is
        already defined in the given Sequence
        """
        self.kwargs["number"] = 101
        new_shot1 = Shot(**self.kwargs)
        new_shot2 = Shot(**self.kwargs)
        db.session.add_all([new_shot1, new_shot2])
        self.assertRaises(IntegrityError, db.session.commit)
    
    def test_number_is_already_defined_in_the_sequence_for_an_already_created_one(self):
        """testing if a ValueError will be raised when the number is already
        defined for a Shot in the same Sequence instance
        """
        self.kwargs["number"] = 101
        new_shot1 = Shot(**self.kwargs)
        new_shot1.save()
        
        self.assertRaises(ValueError, Shot, **self.kwargs)
    
    def test_number_argument_is_string_or_integer(self):
        """testing if both strings and integers are ok to pass to the number
        argument
        """
        self.kwargs["number"] = 10
        new_shot1 = Shot(**self.kwargs)
        self.assertEqual(new_shot1.number, "10")
        
        self.kwargs["number"] = "11A"
        new_shot2 = Shot(**self.kwargs)
        self.assertEqual(new_shot2.number, "11A")
    
    def test_code_attribute_is_calculated_from_the_number_argument(self):
        """testing if the code attribute is calculated from the number
        argument
        """
        
        self.kwargs["number"] = 10
        new_shot1 = Shot(**self.kwargs)
        self.assertEqual(new_shot1.code, "SH010")
        
        
        self.kwargs["number"] = "10A"
        new_shot1 = Shot(**self.kwargs)
        self.assertEqual(new_shot1.code, "SH010A")
    
    def test_code_attribute_is_calculated_from_the_number_attribute(self):
        """testing if the code attribute is calculated from the number
        attribute
        """
        
        self.test_shot.number = 10
        self.assertEqual(self.test_shot.code, "SH010")
        
        self.test_shot.number = "10A"
        self.assertEqual(self.test_shot.code, "SH010A")
    
    def test_code_attribute_is_read_only(self):
        """testing if the code attribute is read_only
        """
        self.assertRaises(AttributeError, setattr, self.test_shot, "code",
                          "SH010A")
    
#    def test_code_argument_is_not_in_good_format(self):
#        """testing if a ValueError will be raised when the code argument format
#        is not correct
#        """
#        self.kwargs["code"] = "wrong format"
#        self.assertRaises(ValueError, Shot, **self.kwargs)
#    
#    def test_code_attribute_is_not_in_good_format(self):
#        """testing if a ValueError will be raised when the code attribute
#        format is not correct
#        """
#        self.assertRaises(ValueError, setattr, self.test_shot, "code",
#                          "wrong format")
#    
#    def test_code_argument_is_formatted_correctly(self):
#        """testing if the code argument is formatted correctly
#        """
#        for test_value in self._code_test_values:
#            self.kwargs["code"] = test_value[0]
#            new_shot = Shot(**self.kwargs)
#            self.assertEqual(new_shot.code, test_value[1])
#    
#    def test_code_attribute_is_formatted_correctly(self):
#        """testing if the code attribute is formatted correctly
#        """
#        for test_value in self._code_test_values:
#            self.test_shot.code = test_value[0]
#            self.assertEqual(self.test_shot.code, test_value[1])
    
    def test_sequence_argument_is_skipped(self):
        """testing if a TypeError will be raised when the sequence argument
        is skipped
        """
        self.kwargs.pop("sequence")
        self.assertRaises(TypeError, Shot, **self.kwargs)
    
    def test_sequence_argument_is_None(self):
        """testing if a TypeError will be raised when the sequence argument
        is None
        """
        self.kwargs["sequence"] = None
        self.assertRaises(TypeError, Shot, **self.kwargs)
    
    def test_sequence_argument_is_not_a_Sequence_instance(self):
        """testing if a TypeError will be raised when the sequence argument is
        not a Sequence instance
        """
        self.kwargs["sequence"] = "not a sequence instance"
        self.assertRaises(TypeError, Shot, **self.kwargs)
    
    def test_sequence_argument_is_working_properly(self):
        """testing if the sequence argument is working correctly
        """
        self.assertTrue(self.test_shot.sequence is self.test_seq)
    
    def test_sequence_attribute_is_read_only(self):
        """testing if the sequence attribute is read-only
        """
        new_seq = Sequence(self.test_proj, "TEST_SEQ2")
        new_seq.save()
        self.assertRaises(AttributeError, setattr, self.test_shot, "sequence",
                          new_seq)
    
    def test_start_frame_argument_is_skipped(self):
        """testing if the start_frame attribute will be set to the default
        value when the start_frame argument is skipped
        """
        self.kwargs.pop("start_frame")
        new_shot = Shot(**self.kwargs)
        self.assertEqual(new_shot.start_frame, 1)
    
    def test_start_frame_argument_is_None(self):
        """testing if the start_frame attribute will be set to the default
        value when the start_frame argument is skipped
        """
        self.kwargs["start_frame"] = None
        new_shot = Shot(**self.kwargs)
        self.assertEqual(new_shot.start_frame, 1)
    
    def test_start_frame_attribute_is_None(self):
        """testing if the start_frame attribute will be set to the default
        value when it is set to None
        """
        self.test_shot.start_frame = None
        self.assertEqual(self.test_shot.start_frame, 1)
    
    def test_start_frame_argument_is_not_integer(self):
        """testing if a TypeError will be raised when the start_frame argument
        is not an integer
        """
        self.kwargs["start_frame"] = "asdfa"
        self.assertRaises(TypeError, Shot, **self.kwargs)
    
    def test_start_frame_attribute_is_not_integer(self):
        """testing if a TypeError will be raised when the start_frame attribute
        is not set to an integer value
        """
        self.assertRaises(TypeError, setattr, self.test_shot, "start_frame",
                          "asdfs")
    
    def test_start_frame_attribute_is_working_properly(self):
        """testing if the start_frame attribute is working properly
        """
        test_value = 10
        self.test_shot.start_frame = test_value
        self.assertEqual(self.test_shot.start_frame, test_value)
    
    def test_start_frame_attribute_updates_the_duration_attribute(self):
        """testing if the start_frame attribute updates the duration attribute
        value
        """
        self.test_shot.start_frame = 10
        self.assertEqual(self.test_shot.end_frame, 100)
        self.assertEqual(self.test_shot.duration, 91)
    
    def test_end_frame_argument_is_skipped(self):
        """testing if the end_frame attribute will be set to the default
        value when the end_frame argument is skipped
        """
        self.kwargs.pop("end_frame")
        new_shot = Shot(**self.kwargs)
        self.assertEqual(new_shot.end_frame, 1)
    
    def test_end_frame_argument_is_None(self):
        """testing if the end_frame attribute will be set to the default
        value when the end_frame argument is skipped
        """
        self.kwargs["end_frame"] = None
        new_shot = Shot(**self.kwargs)
        self.assertEqual(new_shot.end_frame, 1)
    
    def test_end_frame_attribute_is_Non(self):
        """testing if the end_frame attribute will be set to the default
        value when it is set to None
        """
        self.test_shot.end_frame = None
        self.assertEqual(self.test_shot.end_frame, 1)
    
    def test_end_frame_argument_is_not_integer(self):
        """testing if a TypeError will be raised when the end_frame argument
        is not an integer
        """
        self.kwargs["end_frame"] = "asdfa"
        self.assertRaises(TypeError, Shot, **self.kwargs)
    
    def test_end_frame_attribute_is_not_integer(self):
        """testing if a TypeError will be raised when the end_frame attribute
        is not set to an integer value
        """
        self.assertRaises(TypeError, setattr, self.test_shot, "end_frame",
                          "asdfs")
    
    def test_end_frame_attribute_is_working_properly(self):
        """testing if the end_frame attribute is working properly
        """
        test_value = 10
        self.test_shot.end_frame = test_value
        self.assertEqual(self.test_shot.end_frame, test_value)
    
    def test_end_frame_attribute_updates_the_duration_attribute(self):
        """testing if the end_frame attribute updates the duration attribute
        value
        """
        self.test_shot.end_frame = 200
        self.assertEqual(self.test_shot.start_frame, 1)
        self.assertEqual(self.test_shot.duration, 200)
    
    def test_duration_attribute_is_updated_correctly(self):
        """testing if the duration attribute is updated correctly with the
        changing values of start_frame and end_frame values
        """
        new_shot = Shot(**self.kwargs)
        self.assertEqual(new_shot.start_frame, 1)
        self.assertEqual(new_shot.end_frame, 100)
        new_shot.start_frame = 10
        self.assertEqual(new_shot.duration, 91)
        
        new_shot.end_frame = 110
        self.assertEqual(new_shot.duration, 101)
    
    def test_project_attribute_is_initialized_correctly(self):
        """testing if the project attribute is initialized correctly
        """
        self.assertTrue(self.test_shot.project is
                        self.kwargs["sequence"].project)

    def test_shot_is_CRUD_properly_in_the_database(self):
        """testing if the shot instance is created properly in the database
        """
        new_proj = Project("TEST_PROJ_FOR_CRUD")
        new_proj.create()
        
        new_seq = Sequence(new_proj, "TEST_SEQ1")
        new_seq.save()
        
        new_shot = Shot(new_seq, 1)
        new_shot.save()
        
        # now query the database if it is created and read correctly
        self.assertEqual(new_shot, db.query(Shot).first())
        
        # now update it
        new_shot.start_frame = 100
        new_shot.end_frame = 200
        new_shot.save()

        self.assertEqual(
            new_shot.start_frame,
            db.query(Shot).first().start_frame
        )
        self.assertEqual(
            new_shot.end_frame,
            db.query(Shot).first().end_frame
        )
        
        # now delete it
        db.session.delete(new_shot)
        db.session.commit()
        
        self.assertEqual(db.query(Shot).all(), [])
    
    def test_equality_of_shots(self):
        """testing if the equality operator is working properly
        """
        proj1 = Project("TEST_EQ_PROJ")
        proj1.create()
        
        seq1 = Sequence(proj1, "TEST_SEQ1")
        seq2 = Sequence(proj1, "TEST_SEQ2")
        
        shot1 = Shot(seq1, 1)
        shot2 = Shot(seq1, 2)
        shot3 = Shot(seq2, 1)
        
        shot1a = Shot(seq1, 1)
        
        self.assertTrue(shot1==shot1a)
        self.assertFalse(shot1==shot2)
        self.assertFalse(shot1a==shot3)
    
    def test_inequality_of_shots(self):
        """testing if the equality operator is working properly
        """
        proj1 = Project("TEST_EQ_PROJ")
        proj1.create()
        
        seq1 = Sequence(proj1, "TEST_SEQ1")
        seq2 = Sequence(proj1, "TEST_SEQ2")
        
        shot1 = Shot(seq1, 1)
        shot2 = Shot(seq1, 2)
        shot3 = Shot(seq2, 1)
        
        shot1a = Shot(seq1, 1)
        
        self.assertFalse(shot1!=shot1a)
        self.assertTrue(shot1!=shot2)
        self.assertTrue(shot1a!=shot3)
