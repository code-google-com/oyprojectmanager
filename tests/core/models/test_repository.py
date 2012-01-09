# -*- coding: utf-8 -*-
# Copyright (c) 2009-2012, Erkan Ozgur Yilmaz
# 
# This module is part of oyProjectManager and is released under the BSD 2
# License: http://www.opensource.org/licenses/BSD-2-Clause

import os
import shutil
import tempfile
import unittest

from oyProjectManager import config, db
from oyProjectManager.core.models import Repository, Project

conf = config.Config()

class RepositoryTester(unittest.TestCase):
    """tests the oyProjectManager.core.models.Repository class
    """
    
    def setUp(self):
        """setup the test
        """
        # -----------------------------------------------------------------
        # start of the setUp
        # create the environment variable and point it to a temp directory
        self.temp_config_folder = tempfile.mkdtemp()
        self.temp_projects_folder = tempfile.mkdtemp()
        
        os.environ["OYPROJECTMANAGER_PATH"] = self.temp_config_folder
        os.environ[conf.repository_env_key] = self.temp_projects_folder
        
        self.config_full_path = os.path.join(
            self.temp_config_folder, "config.py"
        )
    
    def tearDown(self):
        """cleanup the test
        """
        
        # set the db.session to None
        db.session = None
        
        # delete the temp folder
        shutil.rmtree(self.temp_config_folder)
        shutil.rmtree(self.temp_projects_folder)
    
    def test_no_REPO_env_variable_will_raise_a_RuntimeError(self):
        """testing if a RuntimeError will be raised when there is no REPO
        env variable is defined.
        """
        os.environ.pop("REPO")
        self.assertRaises(RuntimeError, Repository)
    
    def test_REPO_is_empty_string(self):
        """testing if a ValueError will be raised when the REPO is an empty
        string
        """
        os.environ["REPO"] = ""
        self.assertRaises(ValueError, Repository)
    
    def test_REPO_path_doesnt_exists(self):
        """testing if a IOError
        """
    
    def test_REPO_has_home_shortcut(self):
        """testing if the $REPO path is expanded correctly if it has "~" kind
        of shortcuts
        """
        test_value = "~/Project"
        os.environ[conf.repository_env_key] = test_value
        repo = Repository()
        self.assertEqual(repo.server_path, os.path.expanduser(test_value))
    
#    def test_project_names_is_working_properly(self):
#        """testing if the project_names attribute gives the valid project names
#        correctly
#        """
#        
#        # create a couple of projects
#        real_projects = ["TEST1", "TEST2", "TEST3"]
#        for real_project in real_projects:
#            proj = Project(name=real_project)
#            proj.create()
#        
#        # and a couple of fake folders
#        fake_projects = ["FAKE_PROJ1", "FAKE_PROJ2", "FAKE_PROJ3"]
#        for fake_project in fake_projects:
#            os.mkdir(
#                os.path.join(
#                    self.temp_projects_folder,
#                    fake_project
#                )
#            )
#        
#        
#        
#        # check if all the folders are created
#        folders = []
#        folders.extend(real_projects)
#        folders.extend(fake_projects)
#        for proj_name in folders:
#            self.assertTrue(
#                os.path.exists(
#                    os.path.join(
#                        self.temp_projects_folder,
#                        proj_name
#                    )
#                )
#            )
#        
#        # now check if repository only returns real_project names
#        repo = Repository()
#        self.assertItemsEqual(real_projects, repo.project_names)
    
    def test_get_project_name_is_working_properly(self):
        """testing if the get_project_name method is working properly
        """
        test_values = [
            (os.path.join(self.temp_projects_folder, "TEST/Seqs/Seq1/Edit"),
             "TEST"),
            (self.temp_projects_folder + "/../"  + 
             os.path.normpath(self.temp_projects_folder)
                .split(os.path.sep)[-1] + "/TEST/Seqs/Seq1/Edit", "TEST"),
            (None, None),
            (self.temp_projects_folder, None),
        ]
        
        repo = Repository()
        
        print "self.repo.server_path", repo.server_path
        
        for test_value in test_values:
            self.assertEqual(repo.get_project_name(test_value[0]),
                             test_value[1])
    
    def test_relative_path_returns_a_path_with_env_var(self):
        """testing if the relative_path returns a path starting with $REPO
        """
        
        test_value = "TEST/Seqs/Seq1/Shots/SH001/FX/SH001_Main_FX_v001_oy.hip"
        test_path = os.path.join(self.temp_projects_folder, test_value)
        
        expected = "$" + conf.repository_env_key + "/" + test_value
        
        repo = Repository()
        self.assertEqual(repo.relative_path(test_path), expected)
    
    def test_server_path_returns_the_correct_value_for_the_current_os(self):
        """testing if server_path returns the correct value for the operating
        system
        """
        repo = Repository()
        self.assertEqual(self.temp_projects_folder,
                    os.environ[conf.repository_env_key])
        self.assertEqual(repo.server_path, self.temp_projects_folder)
    
    def test_server_path_attribute_is_read_only(self):
        """testing if the server_path is read only
        """
        repo = Repository()
        self.assertRaises(AttributeError, setattr, repo, "server_path",
                          "some value")
    
    def test_windows_path_attribute_is_read_only(self):
        """testing if the windows_path is read only
        """
        repo = Repository()
        self.assertRaises(AttributeError, setattr, repo, "windows_path",
                          "some value")
    
    def test_linux_path_attribute_is_read_only(self):
        """testing if the linux_path is read only
        """
        repo = Repository()
        self.assertRaises(AttributeError, setattr, repo, "linux_path",
                          "some value")
    
    def test_osx_path_attribute_is_read_only(self):
        """testing if the osx_path is read only
        """
        repo = Repository()
        self.assertRaises(AttributeError, setattr, repo, "osx_path",
                          "some value")
    
