# -*- coding: utf-8 -*-



import os
import sys
import shutil
import tempfile
from xml.dom import minidom
import mocker

from oyProjectManager.models import repository, project






########################################################################
class RepositoryTester(mocker.MockerTestCase):
    """tests the repository with environment variables
    """
    
    
    
    #----------------------------------------------------------------------
    def setUp(self):
        """testing the settings path from the environment variable
        """
        
        # -----------------------------------------------------------------
        # start of the setUp
        # create the environment variable and point it to a temp directory
        #self.temp_settings_folder = tempfile.mkdtemp()
        self.temp_settings_folder = tempfile.mktemp()
        self.temp_projects_folder = tempfile.mkdtemp()
        
        os.environ['OYPROJECTMANAGER_PATH'] = self.temp_settings_folder
        
        
        # copy the default files to the folder
        self.package_path = os.path.abspath(
            os.path.dirname(
                os.path.dirname(
                    os.path.dirname(__file__)
                )
            )
        )
        
        self.default_settings_dir_path = os.path.join(
            self.package_path, "oyProjectManager", "settings" )
        
        ## copy the setting files
        #files = ["defaultProjectSettings.xml",
                 #"environmentSettings.xml",
                 #"repositorySettings.xml",
                 #"users.xml",
                 #"_defaultFiles_",
                 #]
        
        #for file_ in files:
            #shutil.copy2(
                #os.path.join(
                    #self.default_settings_dir_path,
                    #file_)
                #,
                #os.path.join(
                    #self.temp_settings_folder,
                    #file_)
                #)
        
        shutil.copytree(
            self.default_settings_dir_path,
            self.temp_settings_folder,
        )
        
        # change the server path to a temp folder
        repository_settings_file_path = os.path.join(
            self.temp_settings_folder, 'repositorySettings.xml')
        
        # change the repositorySettings.xml by using the minidom
        xmlDoc = minidom.parse(repository_settings_file_path)
        
        serverNodes = xmlDoc.getElementsByTagName("server")
        for serverNode in serverNodes:
            serverNode.setAttribute("windows_path", self.temp_projects_folder)
            serverNode.setAttribute("linux_path", self.temp_projects_folder)
            serverNode.setAttribute("osx_path", self.temp_projects_folder)
        
        repository_settings_file = file(repository_settings_file_path,
                                        mode='w')
        xmlDoc.writexml(repository_settings_file, "\t", "\t", "\n")
    
    
    
    #----------------------------------------------------------------------
    def tearDown(self):
        """remove the temp folders
        """
        
        # delete the temp folder
        shutil.rmtree(self.temp_settings_folder)
        shutil.rmtree(self.temp_projects_folder)
    
    
    
    ##----------------------------------------------------------------------
    #def test_get_settings_path_with_environment_variable(self):
        #"""testing if the get_settings_path returns the correct path when the
        #environment variables is set
        #"""
        
        #repo = repository.Repository()
        
        ## this should return the same path with the environment
        #self.assertEqual(repo.get_settings_path(), self.temp_settings_folder)
    
    
    
    #----------------------------------------------------------------------
    def test_create_project(self):
        """testing project creation
        """
        
        repo = repository.Repository()
        
        project_name = 'TEST_PROJECT'
        
        newProject = repo.createProject(project_name)
        newProject.create()
        
        # lets check if there is a folder in the server path with the given
        # name
        self.assertTrue(
            os.path.exists(
                os.path.join(
                    repo.server_path,
                    project_name
                    )
                )
            )
    
    
    
    #----------------------------------------------------------------------
    def test_without_environment_variable(self):
        """testing if a KeyError will be raised when there is no
        OYPROJECTMANAGER_PATH variable defined in the environment variables
        """
        
        # delete the environment variable
        if os.environ.has_key("OYPROJECTMANAGER_PATH"):
            os.environ.pop("OYPROJECTMANAGER_PATH")
        
        self.assertRaises(KeyError, repository.Repository)
    
    
    
    #----------------------------------------------------------------------
    def test_environment_variable_is_expanded(self):
        """testing if user and environment values are expanded in
        OYPROJECTMANAGER_PATH environment variable
        """
        
        temp_folder_name = tempfile.mktemp().replace(tempfile.gettempdir(), "")
        
        other_env_key = "OTHERENVVAR1"
        other_env_value = "tmp"
        
        os.environ[other_env_key] = other_env_value
        
        new_path = os.path.join("~", "$" + other_env_key,
                                "tmp" + temp_folder_name)
        
        expanded_new_path = os.path.expanduser(os.path.expandvars(new_path))
        
        # copy the current settings to the target folder to not to raise any
        # other errors
        
        shutil.copytree(os.environ["OYPROJECTMANAGER_PATH"], expanded_new_path)
        
        os.environ["OYPROJECTMANAGER_PATH"] = new_path
        
        # now test if the path is expanded
        repo = repository.Repository()
        
        self.assertEquals(repo.settings_dir_path, expanded_new_path)
        
        # now delete the tmp folder
        shutil.rmtree(expanded_new_path)
    
    
    
    #----------------------------------------------------------------------
    def test_default_settings_file_full_path_property_is_working_properly(self):
        """testing if the default_settings_file_full_path porperty is working
        properly
        """
        
        repo = repository.Repository()
        
        self.assertEquals(repo._default_settings_file_full_path,
                          repo.default_settings_file_full_path)
    
    
    
    #----------------------------------------------------------------------
    def test_default_settings_file_full_path_property_is_read_only(self):
        """testing if the default_settings_file_full_path property is read only
        """
        
        repo = repository.Repository()
        
        self.assertRaises(AttributeError,
                          setattr,
                          repo,
                          "default_settings_file_full_path",
                          "a value")
    
    
    
    #----------------------------------------------------------------------
    def test_get_project_and_sequence_name_from_file_path_works_properly(self):
        """testing if get_project_and_sequence_name_from_file_path is working
        properly.
        """
        
        # create a fictional asset path
        repo = repository.Repository()
        
        project_name = "Proj1"
        sequence_name = "Seq1"
        
        asset_path = os.path.join(repo.server_path, project_name,
                                  sequence_name, "Asset1")
        
        self.assertEquals(
            repo.get_project_and_sequence_name_from_file_path(asset_path),
            (project_name, sequence_name)
        )
    
    
    
    #----------------------------------------------------------------------
    def test_get_project_and_sequence_name_from_file_path_returns_None(self):
        """testing if get_project_and_sequence_name_from_file_path returns
        (None, None) for irrelative paths.
        """
        
        repo = repository.Repository()
        
        self.assertEquals(
            repo.get_project_and_sequence_name_from_file_path(
                "/an/irrelative/path/to/some/asset/or/something/else"),
            (None, None)
        )
    
    
    
    #----------------------------------------------------------------------
    def test_home_path_works_properly(self):
        """testing if get_home path works properly
        """
        
        repo = repository.Repository()
        
        self.assertEquals(repo.home_path, os.environ["HOME"])
    
    
    
    #----------------------------------------------------------------------
    def test_home_path_is_read_only(self):
        """testing if the home_path property is read only
        """
        
        repo = repository.Repository()
        
        self.assertRaises(AttributeError,
                          setattr,
                          repo,
                          "home_path",
                          "/some/path/to/something")
    
    
    
    #----------------------------------------------------------------------
    def test_last_user_property_working_properly(self):
        """testing if the last_user property is working properly
        """
        
        repo = repository.Repository()
        
        # get the last user from the repo
        last_user = repo.last_user
        
        if last_user == "":
            # no saved user before
            # just create one
            repo.last_user = repo.userInitials[0]
            
            # re-read last_user
            last_user = repo.last_user
        
        # now check it if it is same with the last_user_file
        self.assertEquals(
            last_user,
            open(repo._last_user_file_full_path).readline().strip()
        )
    
    
    
    #----------------------------------------------------------------------
    def test_last_user_property_sets_last_user_properly(self):
        """testing if the last_user property is properly setting the last user
        """
        
        repo = repository.Repository()
        # store the current user
        current_last_user = repo.last_user
        
        # change last user by using the property
        # change it with the user first in the user list
        new_last_user = repo.userInitials[0]
        repo.last_user = new_last_user
        
        # check if it is set properly
        self.assertEquals(
            repo.last_user,
            new_last_user
        )
        
        # restore the previous user
        if current_last_user is not None:
            repo.last_user = current_last_user
    
    
    
    #----------------------------------------------------------------------
    def test_server_path_expands_variables(self):
        """teting if the server_path property is expanding environment
        variables properly.
        """
        
        # set the new server path to a user relative and environment relative
        # path
        os.environ["ENVVAR1"] = "tmp"
        new_server_path = os.path.join("~", "tmp", "$ENVVAR1")
        expanded_new_server_path = os.path.expanduser(
            os.path.expandvars(new_server_path)
        )
        
        # create the folder
        try:
            os.makedirs(expanded_new_server_path)
        except OSError:
            # the path exists
            pass
        
        repo = repository.Repository()
        
        repo.server_path = new_server_path
        
        self.assertEquals(repo.server_path, expanded_new_server_path)
        
        # clean up test
        shutil.rmtree(expanded_new_server_path)
    
    
    
    #----------------------------------------------------------------------
    def test_server_path_working_properly(self):
        """testing if the server_path property is working properly
        """
        
        # for now just check if it is the same with the linux_path
        
        repo = repository.Repository()
        
        self.assertEquals(repo.server_path, repo.linux_path)
    
    
    
    #----------------------------------------------------------------------
    def test_server_path_setting_path_working_properly(self):
        """testing if the server_path property is working properly
        """
        
        # for now just test it for linux
        repo = repository.Repository()
        
        new_server_path = tempfile.mkdtemp()
        
        repo.server_path = new_server_path
        
        # check if it is same with the server_path
        self.assertEquals(
            new_server_path,
            repo.server_path
        )
        
        # check if it is same with the linux path
        self.assertEquals(
            new_server_path,
            repo.linux_path
        )
        
        # now check if it is same with the linux path
        self.assertEquals(
            repo.server_path,
            repo.linux_path
        )
        
        # clean up
        os.rmdir(new_server_path)
    
    
    
    #----------------------------------------------------------------------
    def test_linux_path_setting_the_server_path(self):
        """testing if changing the linux_path also changes the server_path
        under linux
        """
        
        new_server_path = tempfile.mkdtemp()
        
        # set this dir to the linux path and check if it is also changing the
        # server_path
        repo = repository.Repository()
        
        repo.linux_path = new_server_path
        
        self.assertEquals(repo.server_path, new_server_path)
        
        # clean up
        os.rmdir(new_server_path)
    
    
    
    #----------------------------------------------------------------------
    def test_settings_dir_path_works_properly(self):
        """testing if the settings_dir_path works properly
        """
        
        # check if the settings_dir path property is working properly
        # get the current settings_dir_path from the environment variable
        
        settings_dir_path_from_env = os.path.expanduser(
            os.path.expandvars(
                os.environ["OYPROJECTMANAGER_PATH"]
            )
        )
        
        repo = repository.Repository()
        
        self.assertEquals(repo.settings_dir_path, settings_dir_path_from_env)
    
    
    
    #----------------------------------------------------------------------
    def test_projects_property_working_properly(self):
        """testing if the project property is working properly
        """
        
        # create a couple of projects
        project_names = ["PROJ1",
                         "PROJ2",
                         "PROJ3",
                         "TEST_PROJECT1",
                         ]
        
        repo = repository.Repository()
        
        for project_name in project_names:
            #proj = repo.createProject(project_name)
            proj = project.Project(project_name)
            proj.create()
        
        # now get the projects list and check
        # if it is same with the original projects list
        
        self.assertEquals(repo.projects, project_names)
    
    
    
    #----------------------------------------------------------------------
    def test_update_project_list_working_properly(self):
        """testing if the update_project_list is filtering folders correctly
        """
        
        # create a couple of projects
        folder_names = ["PROJ1",
                        "PROJ2",
                        "PROJ3",
                        "TEST_PROJECT",
                        "TEST_PROJECT1",
                        "1test project2",
                        ".DS_Store",
                        ]
        
        expected_list = ["PROJ1",
                         "PROJ2",
                         "PROJ3",
                         "TEST_PROJECT",
                         "TEST_PROJECT1",
                         ]
        
        repo = repository.Repository()
        
        # create a folder in the projects folder
        for folder_name in folder_names:
            os.mkdir(os.path.join(self.temp_projects_folder, folder_name))
        
        # now get the projects list and check
        # if it is same with the original projects list
        
        self.assertEquals(repo.projects, expected_list)
    
    
    
    #----------------------------------------------------------------------
    def test_relative_path_working_properly(self):
        """testing if the relative_path is working properly
        """
        
        test_folder_name = "TEST_FOLDER"
        
        test_folder_full_path = os.path.join(
            self.temp_projects_folder,
            test_folder_name
        )
        
        repo = repository.Repository()
        
        expected_path = os.path.join(
            "$" + repo.repository_path_env_key,
            test_folder_name
        )
        
        self.assertEquals(
            repo.relative_path(test_folder_full_path),
            expected_path
        )
    
    
    
    #----------------------------------------------------------------------
    def test_valid_projects_returns_valid_projects(self):
        """testing if valid_projects property returns valid projects
        """
        
        # create a couple of projects with sequences
        # then create a couple of extra folders
        # and check if we get only the projects
        
        project_names = ["PROJ1", "PROJ2", "PROJ3"]
        seq_name = "SEQ1"
        shots = "1"
        extra_folders = ["PROJ4", "PROJ5", "PROJ6"]
        
        repo = repository.Repository()
        
        # create the projects
        for project_name in project_names:
            proj = repo.createProject(project_name)
            proj.create()
            
            # create a sequence for them
            proj.createSequence(seq_name, shots)
        
        # create folders
        for folder in extra_folders:
            os.mkdir(
                os.path.join(
                    repo.server_path,
                    folder
                )
            )
        
        # now check if we only get the valid projects
        self.assertEquals(
            project_names,
            repo.valid_projects
        )