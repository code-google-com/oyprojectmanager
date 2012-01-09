# -*- coding: utf-8 -*-
# Copyright (c) 2009-2012, Erkan Ozgur Yilmaz
# 
# This module is part of oyProjectManager and is released under the BSD 2
# License: http://www.opensource.org/licenses/BSD-2-Clause
#
#import os
#import shutil
#import tempfile
#import subprocess
#import unittest
#from xml.dom import minidom
#import jinja2
#import pyseq
#from oyProjectManager import config
#from oyProjectManager.core.models import Asset, Repository, Sequence, Shot
#
#from oyProjectManager.core.models import Project
#from oyProjectManager.utils.backup import BackUp
#
#conf = config.Config()
#
#class BackUpCreationTester(unittest.TestCase):
#    """tests :mod:`~oyProjectManager.utils.backup` module
#    """
#    
#    @classmethod
#    def setUpClass(cls):
#        """set up the test at class level
#        """
#        os.environ[conf.repository_env_key] = tempfile.mkdtemp()
#        
#        # create a new project called BACKUP_TEST_PROJECT
#        cls.test_project = Project(name="BACKUP_TEST_PROJECT")
#        cls.test_project.create()
#    
#    @classmethod
#    def tearDownClass(cls):
#        """tear down the test at class level
#        """
#        # remove the project dir
#        try:
#            shutil.rmtree(cls.test_project.full_path)
#        except IOError:
#            pass
#    
#    def setUp(self):
#        """sets up the test
#        """
#        # create a BackUp node
#        self.kwargs = {
#            "project": "BACKUP_TEST_PROJECT",
#            "output": "/tmp/oyProjectManager_Backup/BackUp",
#            "number_of_versions": 1,
#            "extra_filter_rules": 
#                "/tmp/oyProjectManager_BackUp/extra_filter_rules",
#        }
#        
#        self.test_backUp_obj = BackUp(**self.kwargs)
#    
#    def test_project_argument_skipped(self):
#        """testing if a TypeError will be raised when the project argument is
#        skipped
#        """
#        self.kwargs.pop("project")
#        self.assertRaises(TypeError, BackUp, **self.kwargs)
#    
#    def test_project_argument_is_empty_string(self):
#        """testing if a ValueError will be raised when the project argument 
#        is an empty string
#        """
#        self.kwargs["project"] = ""
#        self.assertRaises(ValueError, BackUp, **self.kwargs)
#    
#    def test_project_attribute_is_empty_string(self):
#        """testing if a ValueError will be raised when the project attribute 
#        is empty string
#        """
#        self.assertRaises(ValueError, setattr, self.test_backUp_obj, 
#                          "project", "")
#    
#    def test_project_argument_is_not_a_Project_instance_or_string(self):
#        """testing if a TypeError will be raised when the project argument is
#        not a :class:`~oyProjectManager.core.models.Project` instance or string
#        """
#        self.kwargs["project"] = 123123
#        self.assertRaises(TypeError, BackUp, **self.kwargs)
#    
#    def test_project_attribute_is_not_a_Project_instance_or_string(self):
#        """testing if a TypeError will be raised when the project attribute is
#        not a :class:`~oyProjectManager.core.models.Project` instance or a
#        valid project name
#        """
#        test_value = 123123
#        self.assertRaises(TypeError, setattr, self.test_backUp_obj, 
#                          "project", test_value)
#    
#    def test_project_argument_works_properly(self):
#        """testing if the project argument is working properly, means it fills
#        the project attribute with the appropriate value
#        """
#        
#        self.kwargs["project"] = "BACKUP_TEST_PROJECT"
#        new_backup = BackUp(**self.kwargs)
#        self.assertEqual(new_backup.project,
#                         Project(name=self.kwargs["project"]))
#    
#    
#    def test_project_attribute_works_properly(self):
#        """testing if the project attribute is working properly
#        """
#        repo = Repository()
#        project_name = repo.project_names[0]
#        
#        self.assertNotEqual(project_name, "")
#        project = Project(name=project_name)
#        
#        self.test_backUp_obj.project = project
#        
#        self.assertEqual(self.test_backUp_obj.project, project)
#    
#    def test_project_argument_is_not_an_existing_Project(self):
#        """testing if a RuntimeError will be raised when the given Project
#        with the project argument is not an existing project instance
#        """
#        self.kwargs["project"] = "there is no project with this name"
#        self.assertRaises(RuntimeError, BackUp, **self.kwargs)
#    
#    def test_project_attribute_is_not_an_existing_Project(self):
#        """testing if a RuntimeError will be raised when the given Project with
#        the project attribute is not an existing project
#        """
#        self.assertRaises(RuntimeError, setattr, self.test_backUp_obj,
#                          "project", "there is no project with this name")
#    
#    def test_extra_filter_rules_argument_is_skipped(self):
#        """testing if extra_filter_rules attribute will be an empty string if
#        the extra_filter_rules argument is an empty string
#        """
#        self.kwargs.pop("extra_filter_rules")
#        new_BackUp_obj = BackUp(**self.kwargs)
#        self.assertEqual(new_BackUp_obj.extra_filter_rules, "")
#
#    def test_extra_filter_rules_argument_is_empty_string(self):
#        """testing if extra_filter_rules attribute will be an empty string when
#        the extra_filter_rules argument is an empty string
#        """
#        self.kwargs["extra_filter_rules"] = ""
#        new_BackUp_obj = BackUp(**self.kwargs)
#        self.assertEqual(new_BackUp_obj.extra_filter_rules, "")
#
#    def test_extra_filter_rules_argument_is_not_a_string(self):
#        """testing if a TypeError will be raised when the extra_filter_rules 
#        argument is not a string instance
#        """
#        self.kwargs["extra_filter_rules"] = 213132
#        self.assertRaises(TypeError, BackUp, **self.kwargs)
#
#    def test_extra_filter_rules_attribute_is_not_a_string(self):
#        """testing if a TypeError will be raised when the extra_filter_rules 
#        attribute is not a string instance
#        """
#        self.assertRaises(TypeError, setattr, self.test_backUp_obj, 
#                          "extra_filter_rules", 1234)
#    
#    def test_extra_filter_rules_argument_is_working_properly(self):
#        """testing if extra_filter_rules attribute is set according to the 
#        value of extra_filter_rules argument
#        """
#        test_value = "test_value"
#        self.kwargs["extra_filter_rules"] = test_value
#        new_BackUp_obj = BackUp(**self.kwargs)
#        self.assertEqual(new_BackUp_obj.extra_filter_rules, test_value)
#    
#    def test_extra_filter_rules_attribute_is_working_properly(self):
#        """testing if the extra_filter_rules attribute is working properly
#        """
#        test_value = "test_value"
#        self.test_backUp_obj.extra_filter_rules = test_value
#        self.assertEqual(self.test_backUp_obj.extra_filter_rules, test_value)
#    
#    def test_output_argument_is_skipped(self):
#        """testing if a TypeError will be raised when the output argument is 
#        skipped
#        """
#        self.kwargs.pop("output")
#        self.assertRaises(TypeError, BackUp, **self.kwargs)
#    
#    def test_output_argument_is_empty_string(self):
#        """testing if a ValueError will be raised when the output argument is
#        an empty string
#        """
#        self.kwargs["output"] = ""
#        self.assertRaises(ValueError, BackUp, **self.kwargs)
#        
#    
#    def test_output_attribute_is_empty_string(self):
#        """testing if a ValueError will be raised when the output attribute 
#        is set to an empty string
#        """
#        self.assertRaises(ValueError, setattr, self.test_backUp_obj, 
#                          "output", "")
#    
#    def test_output_argument_is_not_a_string(self):
#        """testing if a TypeError will be raised when the output argument is 
#        not a string instance
#        """
#        self.kwargs["output"] = 2134234
#        self.assertRaises(TypeError, BackUp, **self.kwargs)
#    
#    def test_output_attribute_is_not_a_string(self):
#        """testing if a TypeError will be raised when the output attribute is
#         not a string instance
#        """
#        self.assertRaises(TypeError, setattr, self.test_backUp_obj, "output",
#                          1231)
#    
#    def test_number_of_versions_argument_is_skipped(self):
#        """testing if the value of the number_of_versions attribute will be 
#        the default value when the number_of_versions argument is skipped
#        """
#        self.kwargs.pop("number_of_versions")
#        new_backup = BackUp(**self.kwargs)
#        self.assertEqual(new_backup.num_of_versions, 1)
#    
#    def test_number_of_versions_argument_is_None(self):
#        """testing if the value of the number_of_versions attribute will be 
#        the default value when the number_of_versions argument is None
#        """
#        self.kwargs["number_of_versions"] = None
#        new_backup = BackUp(**self.kwargs)
#        self.assertEqual(new_backup.num_of_versions, 1)
#    
#    def test_number_of_versions_attribute_is_None(self):
#        """testing if the number_of_versions attribute will be set to the 
#        default value when it is set to None
#        """
#        self.test_backUp_obj.num_of_versions = None
#        self.assertEqual(self.test_backUp_obj.num_of_versions, 1)
#    
#    def test_number_of_versions_argument_is_not_integer(self):
#        """testing if a TypeError will be raised when the number_of_versions 
#        argument is not an integer
#        """
#        self.kwargs["number_of_versions"] = "not integer"
#        self.assertRaises(TypeError, BackUp, **self.kwargs)
#        
#    def test_number_of_versions_attribute_is_not_integer(self):
#        """testing if a TypeError will be raised when the number_of_versions 
#        attribute is set to a value which is not an integer
#        """
#        self.assertRaises(TypeError, setattr, self.test_backUp_obj,
#                          "num_of_v")
#    
#    def test_number_of_versions_argument_accepts_negative_values(self):
#        """testing if the number_of_version argument accepts negative values
#        """
#        test_value = -1
#        self.kwargs["number_of_versions"] = test_value
#        new_backup = BackUp(**self.kwargs)
#        self.assertEqual(new_backup.num_of_versions, test_value)
#
#
##class BackUp_DoBackup_Tester(unittest.TestCase):
##    """tests the backup process
##    """
##    
##    def setUp(self):
##        """setup the test
##        """
##        
##        # -----------------------------------------------------------------
##        # start of the setUp
##        # create the environment variable and point it to a temp directory
##        self.temp_config_folder = tempfile.mkdtemp()
##        self.temp_projects_folder = tempfile.mkdtemp()
##        
##        os.environ["OYPROJECTMANAGER_PATH"] = self.temp_config_folder
##        os.environ["REPO"] = self.temp_projects_folder
##        
##        # create a project
##        self.test_project = Project(name="BACKUP_TEST_PROJECT")
##        self.test_project.create()
##        
##        # create a couple of sequences
##        self.test_seq1 = Sequence(self.test_project, "BACKUP_TEST_SEQ1")
##        self.test_seq1.shots.append(Shot(self.test_seq1, 1))
##        self.test_seq1.create()
##        
##        self.test_seq2 = Sequence(self.test_project, "BACKUP_TEST_SEQ2")
##        self.test_seq2.shots.append(Shot(self.test_seq2, 1))
##        self.test_seq2.create()
##        
##        # create an FX asset
##        self.fx_asset = Asset(
##            self.test_project,
##            self.test_seq1,
##            "SH001_MAIN_FX_r00_v001_oy.ma"
##        )
##        
##        self.lighting_asset = Asset(
##            self.test_project,
##            self.test_seq1,
##            "SH001_MAIN_LIGHTING_r00_v002_oy.ma"
##        )
##        
##        self.compositing_asset1 = Asset(
##            self.test_project,
##            self.test_seq1,
##            "SH001_MAIN_COMP_r00_v001_oy.nk"
##        )
##        
##        self.compositing_asset2 = Asset(
##            self.test_project,
##            self.test_seq1,
##            "SH001_MAIN_COMP_r00_v002_oy.nk"
##        )
##        
##        # create the render image sequence
##        self.imageSeq1 = pyseq.uncompress(
##            os.path.join(
##                self.test_seq1.full_path,
##                self.fx_asset.output_path,
##                "test_image_seq1.%03d.jpg 1-100",
##            ),
##            format="%h%p%t %r"
##        )
##        
##        try:
##            os.makedirs(
##                os.path.dirname(
##                    self.imageSeq1.path()
##                )
##            )
##        except OSError:
##            pass
##    
##        
##        self.imageSeq2 = pyseq.uncompress(
##            os.path.join(
##                self.test_seq1.full_path,
##                self.fx_asset.output_path,
##                "test_image_seq2.%03d.jpg 1-100",
##            ),
##            format="%h%p%t %r"
##        )
##        
##        try:
##            os.makedirs(
##                os.path.dirname(
##                    self.imageSeq2.path()
##                )
##            )
##        except OSError:
##            pass
##        
##        
##        
##        self.imageSeq3 = pyseq.uncompress(
##            os.path.join(
##                self.test_seq1.full_path,
##                self.fx_asset.output_path,
##                "test_image_seq3.%03d.jpg 1-100",
##            ),
##            format="%h%p%t %r"
##        )
##        
##        try:
##            os.makedirs(
##                os.path.dirname(
##                    self.imageSeq3.path()
##                )
##            )
##        except OSError:
##            pass
##        
##        
##        self.imageSeq4 = pyseq.uncompress(
##            os.path.join(
##                self.test_seq1.full_path,
##                self.compositing_asset2.output_path,
##                os.path.splitext(self.compositing_asset2.fileName)[0] + \
##                    ".%03d.jpg 1-100",
##            ),
##            format="%h%p%t %r"
##        )
##        
##        try:
##            os.makedirs(
##                os.path.dirname(
##                    self.imageSeq4.path()
##                )
##            )
##        except OSError:
##            pass
##        
##        
##        for image in self.imageSeq1:
##            subprocess.call(["touch", image.path], shell=False)
##        
##        for image in self.imageSeq2:
##            subprocess.call(["touch", image.path], shell=False)
##        
##        for image in self.imageSeq3:
##            subprocess.call(["touch", image.path], shell=False)
##        
##        for image in self.imageSeq4:
##            subprocess.call(["touch", image.path], shell=False)
##        
##        # create a nuke file with several read and write nodes
##        # open the nuke file
##        self.nuke_file = open(
##            os.path.join(
##                self._test_files_folder,
##                "nuke_file_template.nk"
##            ),
##            "r"
##        )
##        
##        # render it as a jinja2 template
##        nuke_template = jinja2.Template(self.nuke_file.read())
##        self.nuke_file.close()
##        
##        
##        # write it to the new path
##        nuke_output_file = open(
##            self.compositing_asset2.full_path,
##            "w"
##        )
##        
##        print self.compositing_asset2.full_path
##        
##        
##        nuke_output_file.write(
##            nuke_template.render(
##                project_dir=self.test_seq1.full_path,
##                comp_file_path=self.compositing_asset2.full_path
##            )
##        )
##        
##        nuke_output_file.close()
##        # test the backup process
##        
##        # create a place to backup the files
##        self.backup_path = tempfile.mkdtemp()
##    
##    
##    def tearDown(self):
##        """tear down the test
##        """
##        shutil.rmtree(self.temp_config_folder)
##        shutil.rmtree(self.temp_projects_folder)
##    
##    
##    def test_doBackUp_(self):
##        """
##        """
##        
##        # now back up the project
##        backup_obj = BackUp(self.test_project.name, self.backup_path)
##        backup_obj.doBackup()
##        
##        # now test if the project is created with all the paths in the backup
##        # path
##        
##        # there should be three sequences in the backup path
##        # read1 --> self.imageSeq2
##        # read2 --> self.imageSeq3
##        # write --> self.imageSeq4
##        
##        
##        self.assertTrue(
##            all(
##                [os.path.exists(
##                    item.path.replace(
##                        self.test_project.full_path, self.backup_path
##                    )
##                ) for item in self.imageSeq2]
##            )
##        )
##        
##        self.assertTrue(
##            all(
##                [os.path.exists(
##                    item.path.replace(
##                        self.test_project.full_path, self.backup_path
##                    )
##                ) for item in self.imageSeq3]
##            )
##        )
##        
##        self.assertTrue(
##            all(
##                [os.path.exists(
##                    item.path.replace(
##                        self.test_project.full_path, self.backup_path
##                    )
##                ) for item in self.imageSeq4]
##            )
##        )
#        
#        
#
