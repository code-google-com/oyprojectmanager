# -*- coding: utf-8 -*-
# Copyright (c) 2009-2012, Erkan Ozgur Yilmaz
# 
# This module is part of oyProjectManager and is released under the BSD 2
# License: http://www.opensource.org/licenses/BSD-2-Clause

import os
import shutil
import tempfile
import unittest
from oyProjectManager import db, config
from oyProjectManager.core.models import Project, Sequence, Repository, Shot

import logging
logger = logging.getLogger("oyProjectManager.core.models")
logger.setLevel(logging.DEBUG)

conf = config.Config()

# TODO: update the tests of the Sequence class

class SequenceTester(unittest.TestCase):
    """tests the Sequence class
    """
    
    def setUp(self):
        """set up the test in class level
        """
        # -----------------------------------------------------------------
        # start of the setUp
        # create the environment variable and point it to a temp directory
        self.temp_config_folder = tempfile.mkdtemp()
        self.temp_projects_folder = tempfile.mkdtemp()
        
        os.environ["OYPROJECTMANAGER_PATH"] = self.temp_config_folder
        os.environ[conf.repository_env_key] = self.temp_projects_folder
        
        self.test_project = Project("Test Project")
        self.test_project.save()
        
        self.kwargs = {
            "project": self.test_project,
            "name": "Test Sequence",
            "code": "TEST_SEQUENCE"
        }
        
        self.test_sequence = Sequence(**self.kwargs)
        
        self._name_test_values = [
            # (input, name, code)
            ("test sequence", "test sequence", "TEST_SEQUENCE"),
            ("123 test sequence", "test sequence", "TEST_SEQUENCE"),
            ("£#$£#$test£#$£#$sequence", "testsequence", "TESTSEQUENCE"),
            ("_123test sequence", "test sequence", "TEST_SEQUENCE"),
            ("CamelCase", "CamelCase", "CAMEL_CASE"),
            ("234CamelCase", "CamelCase", "CAMEL_CASE"),
            ("camelCase", "camelCase", "CAMEL_CASE"),
            ("CamelCase", "CamelCase", "CAMEL_CASE"),
            ("minus-sign", "minus-sign", "MINUS_SIGN"),
            ("123432!+!'^+Test_SEquence323^+'^%&+%&324", "Test_SEquence323324",
             "TEST_SEQUENCE323324"),
            ("    ---test 9s_sequence", "test 9s_sequence", "TEST_9S_SEQUENCE"),
            ("    ---test 9s-sequence", "test 9s-sequence", "TEST_9S_SEQUENCE"),
            (" multiple     spaces are    converted to under     scores",
             "multiple     spaces are    converted to under     scores",
             "MULTIPLE_SPACES_ARE_CONVERTED_TO_UNDER_SCORES"),
            ("_Sequence_Setup_", "Sequence_Setup_", "SEQUENCE_SETUP_"),
            ("_SEQUENCE_SETUP_", "SEQUENCE_SETUP_", "SEQUENCE_SETUP_"),
            ("FUL_3D", "FUL_3D", "FUL_3D"),
        ]

    def tearDown(self):
        """cleanup the test
        """
        # set the db.session to None
        db.session = None
        
        # delete the temp folder
        shutil.rmtree(self.temp_config_folder)
        shutil.rmtree(self.temp_projects_folder)
    
    def test_setup_is_working_fine(self):
        """testing if test setup is working fine
        """

        # now create a repository and ask the server path and check if it
        # matches the test_settings
        repo = Repository()

        # BUG: works only under linux fix it later
        self.assertEqual(repo.server_path, self.temp_projects_folder)
    
    def test_project_argument_is_skipped(self):
        """testing if a TypeError will be raised when the project argument is
        skipped
        """
        self.kwargs.pop("project")
        self.assertRaises(TypeError, Sequence, **self.kwargs)
    
    def test_project_argument_is_None(self):
        """testing if a TypeError will be raised when a None passed with the
        project argument
        """
        self.kwargs["project"] = None
        self.assertRaises(TypeError, Sequence, **self.kwargs)
    
    def test_project_attribute_is_read_only(self):
        """testing if the project attribute is read-only
        """
        new_proj2 = Project("TEST_PROJECT2")
        new_proj2.save()
        self.assertRaises(AttributeError, setattr, self.test_sequence,
            "project", new_proj2)
    
    def test_project_argument_is_not_a_Project_instance(self):
        """testing if a TypeError will be raised when the project argument is
        not a oyProjectManager.core.models.Project instance
        """
        self.kwargs["project"] = "Test Project"
        self.assertRaises(TypeError, Sequence, **self.kwargs)
        
    def test___eq___operator(self):
        """testing the __eq__ (equal) operator
        """

        # create a new project and two sequence
        # then create three new sequence objects to compare each of them
        # with the other

        new_proj = Project("TEST_PROJECT_FOR_EQ_TEST")
        new_proj.create()
        
        seq1 = Sequence(new_proj, "SEQ1")
        seq2 = Sequence(new_proj, "SEQ1")
        seq3 = Sequence(new_proj, "SEQ2")

        new_proj2 = Project("TEST_PROJECT2")
        new_proj2.create()
        
        seq4 = Sequence(new_proj2, "SEQ3")
        
        self.assertTrue(seq1 == seq2)
        self.assertFalse(seq1 == seq3)
        self.assertFalse(seq1 == seq4)
        self.assertFalse(seq3 == seq4)

    def test___ne___operator(self):
        """testing the __ne__ (not equal) operator
        """

        # create a new project and two sequence
        # then create three new sequence objects to compare each of them
        # with the other

        new_proj = Project("TEST_PROJECT_FOR_NE_TEST")
        new_proj.create()
        
        seq1 = Sequence(new_proj, "SEQ1")
        seq2 = Sequence(new_proj, "SEQ1")
        seq3 = Sequence(new_proj, "SEQ2")

        new_proj2 = Project("TEST_PROJECT2")
        new_proj2.create()
        seq4 = Sequence(new_proj2, "SEQ3")

        self.assertFalse(seq1 != seq2)
        self.assertTrue(seq1 != seq3)
        self.assertTrue(seq1 != seq4)
        self.assertTrue(seq3 != seq4)
    
    def test_code_argument_is_skipped(self):
        """testing if the code attribute will equal to name argument if it is
        skipped
        """
        self.kwargs.pop("code")
        self.kwargs["name"] = "Test Sequence"
        expected_value = "TEST_SEQUENCE"
        new_seq1 = Sequence(**self.kwargs)
        self.assertEqual(new_seq1.code, expected_value)

    def test_code_argument_is_formatted_correctly(self):
        """testing if the code attribute is formatted correctly on Sequence
        instance creation
        """
        self.kwargs["name"] = "TEST_SEQ1"
        for test_value in self._name_test_values:
            self.kwargs["code"] = test_value[0]
            expected_value = test_value[2]
            
            new_sequence = Sequence(**self.kwargs)
            
            self.assertEqual(new_sequence.code, expected_value)
    
    def test_code_argument_is_None(self):
        """testing if the code argument is given as None the code attribute
        will be set to the same value with the name attribute
        """
        self.kwargs["code"] = None
        self.kwargs["name"] = "Test Sequence"
        expected_value = "TEST_SEQUENCE"
        new_seq1 = Sequence(**self.kwargs)
        self.assertEqual(new_seq1.code, expected_value)
    
    def test_code_argument_is_not_a_string_instance(self):
        """testing if a TypeError will be raised when the given code argument
        is not an instance of str or unicode
        """
        self.kwargs["code"] = 23123
        self.assertRaises(TypeError, Sequence, **self.kwargs)
    
    def test_description_attribute_is_working_properly(self):
        """testing if the description attribute is working properly
        """
        test_value = "test description"
        self.test_sequence.description = test_value
        self.assertEqual(self.test_sequence.description, test_value)
    
    def test_name_argument_is_skipped(self):
        """testing if a TypeError will be raised when the name argument is
        skipped
        """
        self.kwargs.pop("name")
        self.assertRaises(TypeError, Sequence, **self.kwargs)
    
    def test_name_argument_is_None(self):
        """testing if a TypeError will be raised when the name argument is None
        """
        self.kwargs["name"] = None
        self.assertRaises(TypeError, Sequence, **self.kwargs )
    
    def test_name_attribute_is_None(self):
        """testing if a TypeError will be raised when the name attribute is set
        to None
        """
        self.assertRaises(TypeError, setattr, self.test_sequence, "name", None)
    
    def test_name_argument_is_not_a_string_or_unicode_instance(self):
        """testing if a TypeError will be raised when the name argument is not
        an instance of string or unicode
        """
        self.kwargs["name"] = 23423
        self.assertRaises(TypeError, Sequence, **self.kwargs)
    
    def test_name_attribute_is_not_a_string_or_unicode_instance(self):
        """testing if a TypeError will be raised when the name attribute is not
        an instance of string or unicode
        """
        self.assertRaises(TypeError, setattr, self.test_sequence, "name", 2131)
    
    def test_name_argument_is_working_properly(self):
        """testing if the name attribute is set properly with the given value
        for the name argument
        """
        test_value = "Test Sequence With Name"
        self.kwargs["name"] = test_value
        new_seq = Sequence(**self.kwargs)
        self.assertEqual(new_seq.name, test_value)
    
    def test_name_attribute_is_working_properly(self):
        """testing if the name attribute is working properly
        """
        test_value = "Test Sequence New Name"
        self.test_sequence.name = test_value
        self.assertEqual(self.test_sequence.name, test_value)

    def test_name_argument_formatting(self):
        """testing if the name will be formatted correctly when creating a
        new project.
        """
        for test_value in self._name_test_values:
            self.kwargs["name"] = test_value[0]
            expected_name = test_value[1]
            new_sequence = Sequence(**self.kwargs)
            self.assertEqual(new_sequence.name, expected_name)

    def test_name_attribute_formatting(self):
        """testing if the name property will be formatted correctly.
        """
        for test_value in self._name_test_values:
            self.test_sequence.name = test_value[0]
            expected_name = test_value[1]
            self.assertEqual(self.test_sequence.name, expected_name)

class Sequence_DB_Tester(unittest.TestCase):
    """Tests the new type Sequence class with a database
    """
    
    def setUp(self):
        
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
        
        # delete the temp folder
        shutil.rmtree(self.temp_config_folder)
        shutil.rmtree(self.temp_projects_folder)
    
    def test_database_simple_data(self):
        """testing if the database file has the necessary information related to
        the Sequence
        """
        
        new_proj = Project(name="TEST_PROJECT")
        new_proj.create()
        
        test_seq_name = "TEST_SEQ1"
        new_seq = Sequence(new_proj, test_seq_name)
        new_seq.save()
        new_seq.create()
        
        # fill it with some non default values
        description = new_seq.description = "Test description"
        new_seq.save()
        
        # now check if the database is created correctly
        del new_seq
        
        # create the seq from scratch and let it read the database
        new_seq = db.session.query(Sequence).first()
        
        # now check if it was able to get these data
        self.assertEqual(description, new_seq.description)
    
    def test_database_recreation_of_sequence_object(self):
        """testing if the database file has the necessary information related to
        the Sequence
        """
        
        new_proj = Project(name="TEST_PROJECT")
        new_proj.create()
        
        test_seq_name = "TEST_SEQ1"
        new_seq = Sequence(new_proj, test_seq_name)
        new_seq.save()
        
        description = new_seq.description
        
        # now check if the database is created correctly
        del new_seq
        
        # create the seq from scratch and let it read the database
        new_seq = Sequence(new_proj, test_seq_name)
        
        # now check if it was able to get these data
        self.assertEqual(new_seq.description, description)
    
    def test_calling_create_multiple_times(self):
        """testing if no error will be raised when calling Sequence.create
        multiple times
        """
        
        new_proj = Project(name="TEST_PROJECT")
        new_proj.create()
        
        new_seq = Sequence(new_proj, "TEST_SEQ")
        new_seq.save()
        
        # now call create multiple times
        new_seq.create()
        new_seq.create()
        new_seq.create()
        new_seq.create()
        new_seq.create()
    
    def test_creating_two_different_sequences_and_calling_create(self):
        """testing if no error will be raised when creating two different
        Sequences for the same Project and calling the Sequences.create()
        in mixed order
        """
        
        new_proj = Project(name="TEST_PROJECT")
        new_proj.create()
        
        new_seq1 = Sequence(new_proj, "TEST_SEQ1")
        new_seq2 = Sequence(new_proj, "TEST_SEQ2")
        
        new_seq1.save()
        new_seq2.save()
        
#        print "calling new_seq1.create"
        new_seq1.create()
#        print "calling new_seq2.create"
        new_seq2.create()
    
    def test_add_shots_method_creates_shots_based_on_the_given_range_formulat(self):
        """testing if the add_shots will create shots based on the
        shot_range_formula argument
        """
        
        new_proj = Project(name="Test Project")
        new_proj.create()
        
        new_seq1 = Sequence(new_proj, "Test Sequence 1", "TEST_SEQ1")
        new_seq1.save()
        
        expected_shot_numbers = [
            '1', '2', '3', '4', '5', '6', '7', '8', '10', '12', '13', '14',
            '15'
        ]
        
        # assert there is no shots in the sequence
        self.assertTrue(len(new_seq1.shots)==0)
        
        # add a new shot
        new_seq1.add_shots("1")
        self.assertTrue(len(new_seq1.shots)==1)
        self.assertTrue(new_seq1.shots[0].number in expected_shot_numbers)
        
        # add a couple of shots
        new_seq1.add_shots("2-4")
        self.assertTrue(len(new_seq1.shots)==4)
        self.assertTrue(new_seq1.shots[1].number in expected_shot_numbers)
        self.assertTrue(new_seq1.shots[2].number in expected_shot_numbers)
        self.assertTrue(new_seq1.shots[3].number in expected_shot_numbers)
        
        # add a couple of more
        new_seq1.add_shots("5-8,10,12-15")
        self.assertTrue(len(new_seq1.shots)==13)
        self.assertTrue(new_seq1.shots[4].number in expected_shot_numbers)
        self.assertTrue(new_seq1.shots[5].number in expected_shot_numbers)
        self.assertTrue(new_seq1.shots[6].number in expected_shot_numbers)
        self.assertTrue(new_seq1.shots[7].number in expected_shot_numbers)
        self.assertTrue(new_seq1.shots[8].number in expected_shot_numbers)
        self.assertTrue(new_seq1.shots[9].number in expected_shot_numbers)
        self.assertTrue(new_seq1.shots[10].number in expected_shot_numbers)
        self.assertTrue(new_seq1.shots[11].number in expected_shot_numbers)
        self.assertTrue(new_seq1.shots[12].number in expected_shot_numbers)
    
    def test_add_alternative_shot_is_working_properly(self):
        """testing if the add_alternative_shot method is working properly
        """
        
        new_proj = Project("Test Project")
        new_proj.create()
        
        new_seq = Sequence(new_proj, "Test Sequence", "TEST_SEQ1")
        new_seq.save()
        
        new_shot = Shot(new_seq, 1)
        new_shot.save()
        
        # check if the sequence has only one shot
        self.assertEqual(len(new_seq.shots), 1)
        
        # now create an alternative to this shot
        new_seq.add_alternative_shot(1)
        
        # now check if the sequence has two shots
        self.assertEqual(len(new_seq.shots), 2)
        
        # and the second shots number is 1A
        self.assertEqual(new_seq.shots[1].number, "1A")
        
        # add a new alternative
        new_seq.add_alternative_shot("1")
        
        # check if there is three shots
        self.assertEqual(len(new_seq.shots), 3)
        
        # and the third shots number is 1B
        self.assertEqual(new_seq.shots[2].number, "1B")
