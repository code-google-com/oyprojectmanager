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
from oyProjectManager import db, conf
from oyProjectManager.models.project import Project
from oyProjectManager.models.repository import Repository
from oyProjectManager.models.sequence import Sequence
from oyProjectManager.models.shot import Shot

import logging
logger = logging.getLogger('oyProjectManager.models.sequence')
logger.setLevel(logging.DEBUG)

class SequenceTester(unittest.TestCase):
    """tests the Sequence class
    """
    
    def setUp(self):
        """set up the test in class level
        """
        # -----------------------------------------------------------------
        # start of the setUp
        conf.database_url = "sqlite://"
        
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
            ("test sequence", "test sequence", "test_sequence"),
            ("123 test sequence", "123 test sequence", "123_test_sequence"),
            ("£#$£#$test£#$£#$sequence", "testsequence", "testsequence"),
            ("_123test sequence", "_123test sequence", "_123test_sequence"),
            ("CamelCase", "CamelCase", "CamelCase"),
            ("234CamelCase", "234CamelCase", "234CamelCase"),
            ("camelCase", "camelCase", "camelCase"),
            ("CamelCase", "CamelCase", "CamelCase"),
            ("minus-sign", "minus-sign", "minus-sign"),
            ("123432!+!'^+Test_SEquence323^+'^%&+%&324", "123432Test_SEquence323324",
             "123432Test_SEquence323324"),
            ("    ---test 9s_sequence", "test 9s_sequence", "test_9s_sequence"),
            ("    ---test 9s-sequence", "test 9s-sequence", "test_9s-sequence"),
            (" multiple     spaces are    converted to under     scores",
             "multiple     spaces are    converted to under     scores",
             "multiple_spaces_are_converted_to_under_scores"),
            ("_Sequence_Setup_", "_Sequence_Setup_", "_Sequence_Setup_"),
            ("_SEQUENCE_SETUP_", "_SEQUENCE_SETUP_", "_SEQUENCE_SETUP_"),
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
        not a oyProjectManager.models.project.Project instance
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
        expected_value = "Test_Sequence"
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
        expected_value = "Test_Sequence"
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
        """set up tests
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
            '15', '304_SB_0403_0040'
        ]
        
        # assert there is no shots in the sequence
        self.assertTrue(len(new_seq1.shots)==0)
        
        # add a new shot
        new_seq1.add_shots("1")
        self.assertTrue(len(new_seq1.shots)==1)
        self.assertTrue(new_seq1.shots[0].number in expected_shot_numbers)
        
        # add a couple of shots
        new_seq1.add_shots("2,3,4")
        self.assertTrue(len(new_seq1.shots)==4)
        self.assertTrue(new_seq1.shots[1].number in expected_shot_numbers)
        self.assertTrue(new_seq1.shots[2].number in expected_shot_numbers)
        self.assertTrue(new_seq1.shots[3].number in expected_shot_numbers)
        
        # add a couple of more
        #new_seq1.add_shots("5-8,10,12-15")
        new_seq1.add_shots("5,6,7,8,10,12,13,14,15,304_sb_0403_0040")
        
        self.assertTrue(len(new_seq1.shots)==14)
        self.assertIn(new_seq1.shots[4].number, expected_shot_numbers)
        self.assertIn(new_seq1.shots[5].number, expected_shot_numbers)
        self.assertIn(new_seq1.shots[6].number, expected_shot_numbers)
        self.assertIn(new_seq1.shots[7].number, expected_shot_numbers)
        self.assertIn(new_seq1.shots[8].number, expected_shot_numbers)
        self.assertIn(new_seq1.shots[9].number, expected_shot_numbers)
        self.assertIn(new_seq1.shots[10].number, expected_shot_numbers)
        self.assertIn(new_seq1.shots[11].number, expected_shot_numbers)
        self.assertIn(new_seq1.shots[12].number, expected_shot_numbers)
        self.assertIn(new_seq1.shots[13].number, expected_shot_numbers)
    
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

    def test_name_argument_is_not_unique_for_same_project(self):
        """testing if the name argument is not unique raises IntegrityError
        """

        test_project = Project("Test Project for Name Uniqueness")
        test_project.save()
        
        test_seq1 = Sequence(test_project, "Seq1")
        test_seq1.save()
        
        test_seq2 = Sequence(test_project, "Seq1")
        self.assertRaises(IntegrityError, test_seq2.save)
    
    def test_name_argument_is_not_unique_for_different_projects(self):
        """testing if no name argument is unique for different projects will
        not raise IntegrityError
        """

        test_project1 = Project("Test Project for Name Uniqueness 1")
        test_project1.save()
        
        test_project2 = Project("Test Project for Name Uniqueness 2")
        test_project2.save()
        
        test_seq1 = Sequence(test_project1, "Seq1")
        test_seq1.save()

        test_seq2 = Sequence(test_project2, "Seq1")
        test_seq2.save() # no Integrity Error

    def test_code_argument_is_not_unique_for_same_project(self):
        """testing if the code argument is not unique raises IntegrityError
        """

        test_project = Project("Test Project for Name Uniqueness")
        test_project.save()

        test_seq1 = Sequence(test_project, "Seq1A", "SEQ1")
        test_seq1.save()

        test_seq2 = Sequence(test_project, "Seq1B", "SEQ1")
        self.assertRaises(IntegrityError, test_seq2.save)

    def test_code_argument_is_not_unique_for_different_projects(self):
        """testing if no code argument is unique for different projects will
        not raise IntegrityError
        """

        test_project1 = Project("Test Project for Name Uniqueness 1")
        test_project1.save()

        test_project2 = Project("Test Project for Name Uniqueness 2")
        test_project2.save()

        test_seq1 = Sequence(test_project1, "SEQ1A", "SEQ1A")
        test_seq1.save()
        
        test_seq2 = Sequence(test_project2, "SEQ1B", "SEQ1A")
        test_seq2.save() # no Integrity Error
    
    def test_code_argument_is_not_unique_for_different_projects_2(self):
        """testing if no code argument is unique for different projects will
        not raise IntegrityError
        """
        
        p1 = Project("Migros Kanguru", "MIGROS_KANGURU")
        p1.save()
        
        p2 = Project("Migros M-Label", "MIGROS_M_LABEL")
        p2.save()
        
        s1 = Sequence(p2, "TVC", "TVC")
        s1.save()
        
        p3 = Project("Fairy Obelix Booster", "FAIRY_OBELIX_BOOSTER")
        p3.save()
        
        s2 = Sequence(p3, "TVC", "TVC")
        s2.save()
    
    def test_add_shots_method_will_remove_the_shot_prefix_if_the_given_shot_starts_with_it(self):
        """testing if the add_shots method will remove the shot prefix in the
        given shot code if it starts with the shot prefix of the project
        """
        proj1 = Project('Test Proj1')
        proj1.save()
        
        seq1 = Sequence(proj1, 'Test Seq1')
        seq1.save()
        
        # now try to add a shot with the name SH001
        seq1.add_shots(proj1.shot_number_prefix + "001")
        
        # now check the first shot of the seq1 has a shot number of 1 and the
        # code is SH001
        self.assertEqual("1", seq1.shots[0].number)
        self.assertEqual('SH001', seq1.shots[0].code)
    
    def test_add_shots_is_working_properly_for_projects_with_no_shot_number_prefix(self):
        """testing if the add_shots method working properly for projects with
        no or empty shot_number_prefix
        """
        proj1 = Project('proj1', 'proj1')
        proj1.shot_number_prefix = ""
        proj1.shot_number_padding = 0
        proj1.save()
        
        seq1 = Sequence(proj1, 'seq91')
        seq1.save()

        shot_code = 'VFX91-3'
        seq1.add_shots(shot_code)
        # should complete without any error
        
        shot = seq1.shots[0]
        self.assertEqual(shot.code, shot_code)
    
    def test_deleting_a_sequence_will_not_delete_the_related_project(self):
        """testing if deleting a sequence will not delete the related project
        """
        proj1 = Project('Test Project 1')
        proj1.save()
        
        seq1 = Sequence(proj1, 'Test Sequence 1')
        seq1.save()
        
        seq2 = Sequence(proj1, 'Test Sequence 2')
        seq2.save()
        
        # check if they are in the session
        self.assertIn(proj1, db.session)
        self.assertIn(seq1, db.session)
        self.assertIn(seq2, db.session)
        
        db.session.delete(seq1)
        db.session.commit()
        
        self.assertIn(proj1, db.session)
        self.assertNotIn(seq1, db.session)
        self.assertIn(seq2, db.session)
    
    def test_deleting_a_sequence_will_also_delete_the_related_shots(self):
        """testing if deleting a sequence will also delete the related shots
        """
        proj1 = Project('Test Project 1')
        proj1.save()
        
        seq1 = Sequence(proj1, 'Seq1')
        seq1.save()
        
        seq2 = Sequence(proj1, 'Seq2')
        seq2.save()
        
        shot1 = Shot(seq1, 1)
        shot1.save()
        
        shot2 = Shot(seq1, 2)
        shot2.save()
        
        shot3 = Shot(seq2, 1)
        shot3.save()
        
        shot4 = Shot(seq2, 2)
        shot4.save()
        
        # check if they are in session
        self.assertIn(proj1, db.session)
        self.assertIn(seq1, db.session)
        self.assertIn(seq2, db.session)
        self.assertIn(shot1, db.session)
        self.assertIn(shot2, db.session)
        self.assertIn(shot3, db.session)
        self.assertIn(shot4, db.session)
        
        # delete seq1
        db.session.delete(seq1)
        db.session.commit()
        
        # check if all the objects which must be deleted are really deleted
        self.assertNotIn(seq1, db.session)
        self.assertNotIn(shot1, db.session)
        self.assertNotIn(shot2, db.session)
        
        # and others are in
        self.assertIn(proj1, db.session)
        self.assertIn(seq2, db.session)
        self.assertIn(shot3, db.session)
        self.assertIn(shot4, db.session)
    
