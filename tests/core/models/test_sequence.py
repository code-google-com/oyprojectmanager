# -*- coding: utf-8 -*-

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
        self.assertRaises(TypeError, Sequence, name="test_seq")
    
    def test_project_argument_is_None(self):
        """testing if a TypeError will be raised when a None passed with the
        project argument
        """
        self.assertRaises(TypeError, Sequence, project=None)
    
    def test_project_attribute_is_read_only(self):
        """testing if the project attribute is read-only
        """
        new_proj = Project("TEST_PROJECT1")
        new_proj.create()
        new_seq = Sequence(new_proj, "TEST_SEQ")
        new_seq.save()
        
        new_proj2 = Project("TEST_PROJECT2")
        new_proj2.create()
        self.assertRaises(AttributeError, setattr, new_seq, "project",
                          new_proj2)
    
    def test_project_argument_is_not_a_Project_instance(self):
        """testing if a TypeError will be raised when the project argument is
        not a oyProjectManager.core.models.Project instance
        """
        
        self.assertRaises(TypeError, Sequence, 1231, "TEST_SEQ1")
    
    def test_project_argument_is_a_string(self):
        """testing if a sequence can be created by passing the name of the
        project as a string
        """
        new_proj = Project("TEST_PROJECT")
        new_proj.create()
        
        # it should be possible to create a sequence
        # with a string in the project argument
        new_seq = Sequence("TEST_PROJECT", "TEST_SEQUENCE1")
        new_seq.save()
        
        # now check if the sequence.project is a Project instance
        self.assertTrue(isinstance(new_seq.project, Project))
    
    def test_project_argument_is_a_string_and_the_project_is_not_created(self):
        """testing if a RuntimeError will be generated when the project argument
        is string and the project is not created yet
        """
        
        self.assertRaises(RuntimeError, Sequence, "TEST_PROJ", "TEST_SEQ")
    
    def test___eq___operator(self):
        """testing the __eq__ (equal) operator
        """

        # create a new project and two sequence
        # then create three new sequence objects to compare each of them
        # with the other

        new_proj = Project("TEST_PROJECT")
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

        new_proj = Project("TEST_PROJECT")
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
        new_proj1 = Project("TEST_PROJ1")
        new_proj1.create()
        
        new_seq1 = Sequence(new_proj1, "TEST_SEQ1")
        self.assertEqual(new_seq1.code, new_seq1.name)
    
    def test_code_argument_is_None(self):
        """testing if the code argument is given as None the code attribute
        will be set to the same value with the name attribute
        """
        new_proj1 = Project("TEST_PROJ1")
        new_proj1.create()
        
        new_seq1 = Sequence(project=new_proj1, name="TEST_SEQ1", code=None)
        self.assertEqual(new_seq1.code, new_seq1.name)
    
    def test_create_method_will_not_create_the_sequence_structure_if_save_is_not_called_before(self):
        """testing if the sequence structure is not created if the save method
        is not called previously
        """
        
        # create a config file which has a known placement for sequences
        config_content = \
        "project_structure = \"\"\"{% for sequence in project.sequences %}\n" + \
        "    {% set seq_path = 'Sequences/' + sequence.code %}\n" + \
        "    {{seq_path}}/Edit/Offline\n" + \
        "    {{seq_path}}/Edit/Sound\n" + \
        "    {{seq_path}}/References/Artworks\n" + \
        "    {{seq_path}}/References/Text/Scenario\n" + \
        "    {{seq_path}}/References/Photos_Images\n" + \
        "    {{seq_path}}/References/Videos\n" + \
        "    {{seq_path}}/References/Others\n" + \
        "    {{seq_path}}/Others\n" + \
        "    {{seq_path}}/Others/assets\n" + \
        "    {{seq_path}}/Others/clips\n" + \
        "    {{seq_path}}/Others/data\n" + \
        "    {{seq_path}}/Others/fur\n" + \
        "    {{seq_path}}/Others/fur/furAttrMap\n" + \
        "    {{seq_path}}/Others/fur/furEqualMap\n" + \
        "    {{seq_path}}/Others/fur/furFiles\n" + \
        "    {{seq_path}}/Others/fur/furImages\n" + \
        "    {{seq_path}}/Others/fur/furShadowMap\n" + \
        "    {{seq_path}}/Others/mel\n" + \
        "    {{seq_path}}/Others/particles\n" + \
        "{% endfor %}\n" + \
        "\"\"\"\n"
        
        # write it to a file called config.py in the OYPROJECTMANAGER_PATH
        config_file = open(
            os.path.join(self.temp_config_folder, "config.py"), "w"
        )
        
        config_file.writelines([config_content])
        config_file.close()
        
        new_proj1 = Project("TEST_PROJ1")
        new_proj1.create()
        
        # check if there is no sequence folder
        dir_content = os.listdir(new_proj1.fullpath)
        
        self.assertTrue("Sequences" not in dir_content)
        
        new_seq = Sequence(new_proj1, "TEST_SEQ1")
        #new_seq.save()
        new_seq.create()
        
        # check if a sequence folder with the name of the sequence is not
        # created
        dir_content = os.listdir(new_proj1.fullpath)
        
        self.assertTrue("Sequences" in dir_content)
    
    def test_create_method_creates_the_sequence_structure(self):
        """testing if calling the create method creates the sequence structure
        by calling Project.create
        """
        
        # create a config file which has a known placement for sequences
        config_content = \
        "project_structure = \"\"\"{% for sequence in project.sequences %}\n" + \
        "    {% set seq_path = 'Sequences/' + sequence.code %}\n" + \
        "    {{seq_path}}/Edit/Offline\n" + \
        "    {{seq_path}}/Edit/Sound\n" + \
        "    {{seq_path}}/References/Artworks\n" + \
        "    {{seq_path}}/References/Text/Scenario\n" + \
        "    {{seq_path}}/References/Photos_Images\n" + \
        "    {{seq_path}}/References/Videos\n" + \
        "    {{seq_path}}/References/Others\n" + \
        "    {{seq_path}}/Others\n" + \
        "    {{seq_path}}/Others/assets\n" + \
        "    {{seq_path}}/Others/clips\n" + \
        "    {{seq_path}}/Others/data\n" + \
        "    {{seq_path}}/Others/fur\n" + \
        "    {{seq_path}}/Others/fur/furAttrMap\n" + \
        "    {{seq_path}}/Others/fur/furEqualMap\n" + \
        "    {{seq_path}}/Others/fur/furFiles\n" + \
        "    {{seq_path}}/Others/fur/furImages\n" + \
        "    {{seq_path}}/Others/fur/furShadowMap\n" + \
        "    {{seq_path}}/Others/mel\n" + \
        "    {{seq_path}}/Others/particles\n" + \
        "{% endfor %}\n" + \
        "\"\"\"\n"
        
        # write it to a file called config.py in the OYPROJECTMANAGER_PATH
        config_file = open(
            os.path.join(self.temp_config_folder, "config.py"), "w"
        )
        
        config_file.writelines([config_content])
        config_file.close()
        
        new_proj1 = Project("TEST_PROJ1")
        new_proj1.create()
        
        # check if there is no sequence folder
        dir_content = os.listdir(new_proj1.fullpath)
        
        self.assertTrue("Sequences" not in dir_content)
        
        new_seq = Sequence(new_proj1, "TEST_SEQ1")
        new_seq.save()
        new_seq.create()
        
        # check if a sequence folder with the name of the sequence is created
        dir_content = os.listdir(
            os.path.join(new_proj1.fullpath, "Sequences")
        )
        
        self.assertTrue("TEST_SEQ1" in dir_content)
    
    def test_description_attribute_is_working_properly(self):
        """testing if the description attribute is working properly
        """
        new_proj = Project("TEST_PROJ1")
        new_proj.create()
        
        new_seq = Sequence(new_proj, "TEST_SEQ1")
        test_value = "test description"
        new_seq.description = test_value
        self.assertEqual(new_seq.description, test_value)
    
    def test_name_argument_is_skipped(self):
        """testing if a TypeError will be raised when the name argument is
        skipped
        """
        self.fail("test is not implemented yet")
    
    def test_name_argument_is_None(self):
        """testing if a TypeError will be raised when the name argument is None
        """
        self.fail("test is not implemented yet")
    
    def test_name_attribute_is_None(self):
        """testing if a TypeError will be raised when the name attribute is set
        to None
        """
        self.fail("test is not implemented yet")
    
    def test_name_argument_is_not_a_string_or_unicode_instance(self):
        """testing if a TypeError will be raised when the name argument is not
        an instance of string or unicode
        """
        self.fail("test is not implemented yet")
    
    def test_name_attribute_is_not_a_string_or_unicode_instance(self):
        """testing if a TypeError will be raised when the name attribute is not
        an instance of string or unicode
        """
        self.fail("test is not implemented yet")
    
    def test_name_argument_is_working_properly(self):
        """testing if the name attribute is set properly with the given value
        for the name argument
        """
        self.fail("test is not implemented yet")
    
    def test_name_attribute_is_working_properly(self):
        """testing if the name attribute is working properly
        """
        self.fail("test is not implemented yet")
    
    def test_name_argument_formatting(self):
        """testing if the name attribute is formatted correctly with the given
        value to the name argument
        """
        self.fail("test is not implemented yet")
    
    def test_name_attribute_formatting(self):
        """testing if the name attribute is formatted correctly
        """
        self.fail("test is not implemented yet")

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
    
    def test_sequence_raises_error_when_the_given_project_is_not_created_yet(self):
        """testing if the sequence raises an error when the project is not
        created yet
        """
        
        new_proj = Project(name="TEST_PROJECT")
        self.assertRaises(RuntimeError, Sequence, new_proj, name="TEST_SEQ")
    
#    def test_sequence_session_is_project_session(self):
#        """testing if the session instance is passed correctly to the sequence
#        instance
#        """
#        
#        new_proj = Project(name="TEST_PROJECT")
#        new_proj.create()
#        
#        new_seq = Sequence(new_proj, name="TEST_SEQ")
#        new_seq.create()
#        
#        self.assertIs(db.session, new_seq.session)
    
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
