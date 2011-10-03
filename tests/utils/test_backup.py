

import unittest
from oyProjectManager.models.project import Project
from oyProjectManager.models.repository import Repository
from oyProjectManager.utils.backup import BackUp


class BackUpCreationTester(unittest.TestCase):
    """tests :mod:`~oyProjectManager.utils.backup` module
    """
    
    def setUp(self):
        """sets up the test
        """
        
        # create a BackUp node
        
        self.kwargs = {
            "project": "BACKUP_TEST_PROJECT",
#            "sequences": ["BACKUP_TEST_SEQUENCE1", "BACKUP_TEST_SEQUENCE2"],
            "output": "/tmp/oyProjectManager_Backup/BackUp",
            "number_of_versions": 1,
            "extra_filter_rules": 
                "/tmp/oyProjectManager_BackUp/extra_filter_rules",
        }
        
        self.test_backUp_obj = BackUp(**self.kwargs)
    
    def test_project_argument_skipped(self):
        """testing if a TypeError will be raised when the project argument is
        skipped
        """
        self.kwargs.pop("project")
        self.assertRaises(TypeError, BackUp, **self.kwargs)
    
    def test_project_argument_is_empty_string(self):
        """testing if a ValueError will be raised when the project argument 
        is an empty string
        """
        self.kwargs["project"] = ""
        self.assertRaises(ValueError, BackUp, **self.kwargs)
    
    def test_project_attribute_is_empty_string(self):
        """testing if a ValueError will be raised when the project attribute 
        is empty string
        """
        
        self.assertRaises(ValueError, setattr, self.test_backUp_obj, 
                          "project", "")
    
    def test_project_attribute_is_not_a_Project_instance_or_string(self):
        """testing if a TypeError will be raised when the project attribute 
        is not a :class:`~oyProjectManager.models.project.Project` instance 
        or a valid project name
        """
        
        test_value = 123123
        self.assertRaises(TypeError, setattr, self.test_backUp_obj, 
                          "project", test_value)
    
    def test_project_attribute_works_properly(self):
        """testing if the project attribute is working properly
        """
        
        repo = Repository()
        project_name = repo.projects[0]
        
        self.assertNotEqual(project_name, "")
        project = Project(name=project_name)
        
        self.test_backUp_obj.project = project
        
        self.assertEqual(self.test_backUp_obj.project, project)
    
#    def test_sequences_argument_is_skipped(self):
#        """testing if the sequence attribute is an empty list if the sequence
#         argument is skipped
#        """
#        
#        self.fail("test is not implemented yet")
#    
#    def test_sequences_argument_is_not_a_list(self):
#        """testing if a TypeError will be raised when the sequences argument 
#        is not a list
#        """
#        
#        self.fail("test is not implemented yet")
#    
#    def test_sequences_attribute_is_not_a_list(self):
#        """testing if a TypeError will be raised when the sequences attribute
#         is not a list
#        """
#        
#        self.fail("test is not implemented yet")
#    
#    def test_sequences_argument_elements_are_not_Sequence_instances_or_string(self):
#        """testing if a TypeError will be raised when the sequences argument 
#        elements are not a list of
#        :class:`~oyProjectManager.models.project.Sequence` instances
#        """
#        
#        self.fail("test is not implemented yet")
#    
#    def test_sequences_attribute_elements_are_not_Sequence_instances_or_string(self):
#        """testing if a TypeError will be raised when the sequences attribute
#         elements are not all
#         :class:`~oyProjectManager.models.project.Sequence` instances.
#        """
#        
#        self.fail("test is not implemented yet")
#    
#    def test_sequences_argument_dont_belong_to_project_instance(self):
#        """testing if a ValueError will be raised when the given sequences
#        do not belong to the given Project instance
#        """
#        
#        self.fail("test is not implemented yet")
#    
#    def test_sequences_attribute_dont_belong_to_project_instance(self):
#        """testing if a ValueError will be raised when the given sequences 
#        with the sequence attribute do not belong to the given Project instance
#        """
#        
#        self.fail("test is not implemented yet")
    
    def test_extra_filter_rules_argument_is_skipped(self):
        """testing if extra_filter_rules attribute will be an empty string if
        the extra_filter_rules argument is an empty string
        """
        
        self.fail("test is not implemented yet")

    def test_extra_filter_rules_argument_is_empty_string(self):
        """testing if extra_filter_rules attribute will be an empty string when
        the extra_filter_rules argument is an empty string
        """
        
        self.fail("test is not implemented yet")

    def test_extra_filter_rules_argument_is_not_a_string(self):
        """testing if a TypeError will be raised when the extra_filter_rules 
        argument is not a string instance
        """

        self.fail("test is not implemented yet")

    def test_extra_filter_rules_attribute_is_not_a_string(self):
        """testing if a TypeError will be raised when the extra_filter_rules 
        attribute is not a string instance
        """

        self.fail("test is not implemented yet")
    
    def test_output_argument_is_skipped(self):
        """testing if a TypeError will be raised when the output argument is 
        skipped
        """
        
        self.fail("test is not implemented yet")
    
    def test_output_argument_is_empty_string(self):
        """testing if a ValueError will be raised when the output argument is
        an empty string
        """
        
        self.fail("test is not implemented yet")
    
    def test_output_attribute_is_empty_string(self):
        """testing if a ValueError will be raised when the output attribugte 
        is set to an empty string
        """
        
        self.fail("test is not implemented yet")
    
    def test_output_argument_is_not_a_string(self):
        """testing if a TypeError will be raised when the output argument is 
        not a string instance
        """
        
        self.fail("test is not implemented yet")
    
    def test_output_attribute_is_not_a_string(self):
        """testing if a TypeError will be raised when the output attribute is
         not a string instance
        """
        
        self.fail("test is not implemented yet")
    
    def test_number_of_versions_argument_is_skipped(self):
        """testing if the value of the number_of_versions attribute will be 
        the default value when the number_of_versions argument is skipped
        """
        
        self.fail("test is not implemented yet")
    
    def test_number_of_versions_argument_is_None(self):
        """testing if the value of the number_of_versions attribute will be 
        the default value when the number_of_versions argument is None
        """
        
        self.fail("test is not implemented yet")
    
    def test_number_of_versions_attribute_is_None(self):
        """testing if the number_of_versions attribute will be set to the 
        default value when it is set to None
        """
        
        self.fail("test is not implemented yet")
    
    def test_number_of_versions_argument_is_not_integer(self):
        """testing if a TypeError will be raised when the number_of_versions 
        argument is not an integer
        """
        
        self.fail("test is not implemented yet")
        
        
        
    def test_number_of_versions_attribute_is_not_integer(self):
        """testing if a TypeError will be raised when the number_of_versions 
        attribute is set to a value which is not an integer
        """
        
        self.fail("test is not implemented yet")
    
    
    
    def test_number_of_versions_argument_accepts_negative_values(self):
        """testing if the number_of_version argument accepts negative values
        """
        
        self.fail("test is not implemented yet")


class BackUp_DoBackup_Tester(unittest.TestCase):
    """tests the backup process
    """
    
    def setUp(self):
        """setup the test
        """
        
        # create a project
        # create a couple of sequences
        # create a nuke file with several read and write nodes
        
        # create a list of dummy file sequences and set the reads file 
        # attribute to this file sequences
        
        # test the backup process
        
        self.fail("test is not implemented yet")
    
    
    
    def test_doBackUp_(self):
        """
        """
        
        self.fail("test is not implemented yet")
        
        
