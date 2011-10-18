# -*- coding: utf-8 -*-

import os
import shutil
import tempfile
from xml.dom import minidom
import mocker

from oyProjectManager.core.models import Repository, User


class RepositoryTester(mocker.MockerTestCase):
    """tests the repository with environment variables
    """
    
    def setUp(self):
        """testing the settings path from the environment variable
        """
        
        # -----------------------------------------------------------------
        # start of the setUp
        # create the environment variable and point it to a temp directory
        self.temp_settings_folder = tempfile.mktemp()
        self.temp_projects_folder = tempfile.mkdtemp()
        
        # copy the test settings
        import oyProjectManager
        
        self._test_settings_folder = os.path.join(
            os.path.dirname(
                os.path.dirname(
                    oyProjectManager.__file__
                )
            ),
            "tests", "test_settings"
        )
        
        os.environ["OYPROJECTMANAGER_PATH"] = self.temp_settings_folder
        os.environ["STALKER_REPOSITORY_PATH"] = self.temp_projects_folder
        
        # copy the default files to the folder
        shutil.copytree(
            self._test_settings_folder,
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
    
    def tearDown(self):
        """remove the temp folders
        """
        
        # delete the temp folder
        shutil.rmtree(self.temp_settings_folder)
        shutil.rmtree(self.temp_projects_folder)
    
    def test_create_project(self):
        """testing project creation
        """
        
        repo = Repository()
        
        project_name = 'TEST_PROJECT'
        
        newProject = repo.createProject(project_name)
        #newProject.create()
        
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
    
    def test_create_project_with_wrong_name_formating(self):
        """testing if the project name will be correctly formatted if the given
        project name is not in good format
        """
        
        test_values = [
            ("test project", "TEST_PROJECT")
        ]
        
        repo = Repository()
        
        for test_value in test_values:
            project_name = test_value[0]
            expected_project_name = test_value[1]
            
            new_project = repo.createProject(project_name)
            #new_project.create()
            
            # check if the project name is as expected
            self.assertEqual(new_project.name, expected_project_name)
            
            # also check if there is a folder created with the expected_name
            self.assertTrue(
                os.path.exists(
                    os.path.join(
                        repo.server_path,
                        expected_project_name
                        )
                    )
                )
    
    def test_without_environment_variable(self):
        """testing if a KeyError will be raised when there is no
        OYPROJECTMANAGER_PATH variable defined in the environment variables
        """
        
        # delete the environment variable
        if os.environ.has_key("OYPROJECTMANAGER_PATH"):
            os.environ.pop("OYPROJECTMANAGER_PATH")
        
        self.assertRaises(KeyError, repository.Repository)
    
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
        repo = Repository()
        
        self.assertEqual(repo.settings_dir_path, expanded_new_path)
        
        # now delete the tmp folder
        shutil.rmtree(expanded_new_path)
    
    def test_default_settings_file_full_path_property_is_working_properly(self):
        """testing if the default_settings_file_full_path porperty is working
        properly
        """
        
        repo = Repository()
        
        self.assertEqual(repo._default_settings_file_full_path,
                          repo.default_settings_file_full_path)
    
    def test_default_settings_file_full_path_property_is_read_only(self):
        """testing if the default_settings_file_full_path property is read only
        """
        
        repo = Repository()
        
        self.assertRaises(AttributeError,
                          setattr,
                          repo,
                          "default_settings_file_full_path",
                          "a value")
    
    def test_get_project_and_sequence_name_from_file_path_works_properly(self):
        """testing if get_project_and_sequence_name_from_file_path is working
        properly.
        """
        
        # create a fictional asset path
        repo = Repository()
        
        project_name = "Proj1"
        sequence_name = "Seq1"
        
        asset_path = os.path.join(repo.server_path, project_name,
                                  sequence_name, "Asset1")
        
        self.assertEqual(
            repo.get_project_and_sequence_name_from_file_path(asset_path),
            (project_name, sequence_name)
        )
    
    def test_get_project_and_sequence_name_from_file_path_returns_None(self):
        """testing if get_project_and_sequence_name_from_file_path returns
        (None, None) for irrelative paths.
        """
        
        repo = Repository()
        
        self.assertEqual(
            repo.get_project_and_sequence_name_from_file_path(
                "/an/irrelative/path/to/some/asset/or/something/else"),
            (None, None)
        )
    
    def test_get_project_and_sequence_name_from_file_path_returns_None_for_None(self):
        """testing if get_project_and_sequence_name_from_file_path returns
        (None, None) for None
        """
        
        repo = Repository()
        
        self.assertEqual(
            repo.get_project_and_sequence_name_from_file_path(None),
            (None, None)
        )
    
    def test_home_path_works_properly(self):
        """testing if get_home path works properly
        """
        
        repo = Repository()
        
        self.assertEqual(repo.home_path, os.environ["HOME"])
    
    def test_home_path_is_read_only(self):
        """testing if the home_path property is read only
        """
        
        repo = Repository()
        
        self.assertRaises(AttributeError,
                          setattr,
                          repo,
                          "home_path",
                          "/some/path/to/something")
    
    def test_last_user_property_working_properly(self):
        """testing if the last_user property is working properly
        """
        
        repo = Repository()
        
        # get the last user from the repo
        last_user = repo.last_user
        
        if last_user == "":
            # no saved user before
            # just create one
            repo.last_user = repo.user_initials[0]
            
            # re-read last_user
            last_user = repo.last_user
        
        # now check it if it is same with the last_user_file
        self.assertEqual(
            last_user,
            open(repo._last_user_file_full_path).readline().strip()
        )
    
    def test_last_user_property_sets_last_user_properly(self):
        """testing if the last_user property is properly setting the last user
        """
        
        repo = Repository()
        # store the current user
        current_last_user = repo.last_user
        
        # change last user by using the property
        # change it with the user first in the user list
        new_last_user = repo.user_initials[0]
        repo.last_user = new_last_user
        
        # check if it is set properly
        self.assertEqual(
            repo.last_user,
            new_last_user
        )
        
        # restore the previous user
        if current_last_user is not None:
            repo.last_user = current_last_user
    
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
        
        repo = Repository()
        
        repo.server_path = new_server_path
        
        self.assertEqual(repo.server_path, expanded_new_server_path)
        
        # clean up test
        shutil.rmtree(expanded_new_server_path)
    
    def test_server_path_working_properly(self):
        """testing if the server_path property is working properly
        """
        
        # for now just check if it is the same with the linux_path
        
        repo = Repository()
        
        self.assertEqual(repo.server_path, repo.linux_path)
    
    def test_server_path_setting_path_working_properly(self):
        """testing if the server_path property is working properly
        """
        
        # for now just test it for linux
        repo = Repository()
        
        new_server_path = tempfile.mkdtemp()
        
        repo.server_path = new_server_path
        
        # check if it is same with the server_path
        self.assertEqual(
            new_server_path,
            repo.server_path
        )
        
        # check if it is same with the linux path
        self.assertEqual(
            new_server_path,
            repo.linux_path
        )
        
        # now check if it is same with the linux path
        self.assertEqual(
            repo.server_path,
            repo.linux_path
        )
        
        # clean up
        os.rmdir(new_server_path)
    
    def test_linux_path_setting_the_server_path(self):
        """testing if changing the linux_path also changes the server_path
        under linux
        """
        
        new_server_path = tempfile.mkdtemp()
        
        # set this dir to the linux path and check if it is also changing the
        # server_path
        repo = Repository()
        
        repo.linux_path = new_server_path
        
        self.assertEqual(repo.server_path, new_server_path)
        
        # clean up
        os.rmdir(new_server_path)
    
    def test_settings_dir_path_property_works_properly(self):
        """testing if the settings_dir_path works properly
        """
        
        # check if the settings_dir path property is working properly
        # get the current settings_dir_path from the environment variable
        
        settings_dir_path_from_env = os.path.expanduser(
            os.path.expandvars(
                os.environ["OYPROJECTMANAGER_PATH"]
            )
        )
        
        repo = Repository()
        
        self.assertEqual(repo.settings_dir_path, settings_dir_path_from_env)
    
    def test_settings_dir_path_property_is_read_only(self):
        """testing if settings_dir_path property is read only
        """
        
        repo = Repository()
        self.assertRaises(AttributeError, setattr, repo, "settings_dir_path",
                          "")
    
    def test_projects_property_working_properly(self):
        """testing if the project property is working properly
        """
        
        # create a couple of projects
        project_names = ["PROJ1",
                         "PROJ2",
                         "PROJ3",
                         "TEST_PROJECT1",
                         ]
        
        repo = Repository()
        
        for project_name in project_names:
            proj = project.Project(project_name)
            proj.create()
        
        # now get the projects list and check
        # if it is same with the original projects list
        
        self.assertEqual(repo.projects, project_names)
    
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
                        "_TEST_PROJECT_",
                        "_PROJECT_SETUP_",
                        "FUL_3D",
                        ]
        
        expected_list = ["PROJ1",
                         "PROJ2",
                         "PROJ3",
                         "TEST_PROJECT",
                         "TEST_PROJECT1",
                         "_TEST_PROJECT_",
                         "_PROJECT_SETUP_",
                         "FUL_3D",
                         ]
        
        expected_list.sort()
        
        repo = Repository()
        
        # create a folder in the projects folder
        for folder_name in folder_names:
            os.mkdir(os.path.join(self.temp_projects_folder, folder_name))
        
        # now get the projects list and check
        # if it is same with the original projects list
        
        self.assertEqual(repo.projects, expected_list)
    
    def test_relative_path_working_properly(self):
        """testing if the relative_path is working properly
        """
        
        test_folder_name = "TEST_FOLDER"
        
        test_folder_full_path = os.path.join(
            self.temp_projects_folder,
            test_folder_name
        )
        
        repo = Repository()
        
        expected_path = os.path.join(
            "$" + repo.repository_path_env_key,
            test_folder_name
        )
        
        self.assertEqual(
            repo.relative_path(test_folder_full_path),
            expected_path
        )
    
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
        
        repo = Repository()
        
        # create the projects
        for project_name in project_names:
            proj = repo.createProject(project_name)
            #proj.create()
            
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
        self.assertEqual(
            project_names,
            repo.valid_projects
        )
    
    def test_repository_path_environment_variable_init_1(self):
        """testing if the repository path environment variable is initialized
        where there is no repository path key in the environment variables
        """
        
        # remove the environment variable if it exists
        key = "STALKER_REPOSITORY_PATH"
        value = ""
        
        has_key = os.environ.has_key(key)
        
        if has_key:
            value = os.environ[key]
            
            # remove the key
            os.environ.pop(key)
        
        # create another repo and check if it is going to create the key
        repo = Repository()
        self.assertTrue(os.environ.has_key(key))
        
        # restore the value
        if has_key:
            os.environ[key] = value
    
    def test_repository_path_environment_variable_init_2(self):
        """testing if the repository path environment variable is initialized
        correctly even there is a key in the environment with the same
        """
        
        # check if there is a key in the environment and create one if there
        # isn't any
        
        key = "STALKER_REPOSITORY_PATH"
        value = "/TEST_VALUE"
        
        if os.environ.has_key(key):
            # get the value
            value = os.environ[key]
        else:
            # set the value
            os.environ[key] = value
        
        # now create a Repository and check if it is going to get the value
        # for the repository_path
        
        repo = Repository()
        
        # the value should be still there intact
        self.assertEqual(os.environ[key], value)
    
    def _create_new_users_settings(self):
        """creates new users settings file for tests
        """
        # duplicate the current users.xml file and create a new one by hand
        # which has the correct formatting
        
        settings_path = os.path.expanduser(
            os.path.expandvars(
                os.environ["OYPROJECTMANAGER_PATH"]
            )
        )
        
        # check if there is a users.xml file
        orig_file_path = os.path.join(settings_path, "users.xml")
        backup_file_path = os.path.join(settings_path, "users.xml.orig")
        
        # rename it
        os.rename(orig_file_path, backup_file_path)
        
        new_users_file_content = \
            """<?xml version="1.0" ?>
            <root>
                <users>
                    <user initials="u1" name="user1"/>
                    <user initials="u2" name="user2"/>
                    <user initials="u3" name="user3"/>
                    <user initials="u4" name="user4"/>
                    <user initials="u5" name="user5"/>
                </users>
            </root>"""
        
        # write the date to the settings file
        new_file = open(orig_file_path, "w")
        new_file.write(new_users_file_content)
        new_file.close()
        
        return orig_file_path, backup_file_path
    
    def _restore_file(self, orig_file_path, backup_file_path):
        """restores the given file
        """
        
        # restore the original file
        os.remove(orig_file_path)
        os.rename(backup_file_path, orig_file_path)
    
    def test_users_property_is_returning_User_objects(self):
        """testing if the users property is just returning User objects
        """
        
        # create new users.xml with known values
        orig_file_path, backup_file_path = self._create_new_users_settings()
        
        # now do you magic
        repo = Repository()
        
        for userObj in repo.users:
            self.assertTrue(isinstance(userObj, User))
        
        # the users count should be 5 for our settings file
        self.assertEqual(len(repo.users), 5)
        
        # restore the file
        self._restore_file(orig_file_path, backup_file_path)
    
    def test_users_property_returning_correct_users(self):
        """testing if the users property is returning the correct users from
        the settings file
        """
        
        # create a new users.xml with known values
        orig_file_path, backup_file_path = self._create_new_users_settings()
        
        # now create a repository and check for the users
        repo = Repository()
        
        users = repo.users
        
        self.assertEqual(users[0].name, "user1")
        self.assertEqual(users[1].name, "user2")
        self.assertEqual(users[2].name, "user3")
        self.assertEqual(users[3].name, "user4")
        self.assertEqual(users[4].name, "user5")
        
        # restore the users.xml file
        self._restore_file(orig_file_path, backup_file_path)
    
    def test_users_property_is_read_only(self):
        """testing if the users property is read-only
        """
        
        repo = Repository()
        self.assertRaises(AttributeError, setattr, repo, "users", [])
    
    def test_user_names_property_is_working_correctly(self):
        """testing if the user_names property is working properly
        """
        
        # create a new users.xml with known values
        orig_file_path, backup_file_path = self._create_new_users_settings()
        
        # now create a repository and check for the users
        repo = Repository()
        
        user_names = repo.user_names
        
        self.assertEqual(user_names[0], "user1")
        self.assertEqual(user_names[1], "user2")
        self.assertEqual(user_names[2], "user3")
        self.assertEqual(user_names[3], "user4")
        self.assertEqual(user_names[4], "user5")
        
        # restore the users.xml file
        self._restore_file(orig_file_path, backup_file_path)
    
    def test_user_names_property_is_readonly(self):
        """testing if the user_names property is read only
        """
        
        repo = Repository()
        self.assertRaises(AttributeError, setattr, repo, "user_names", [])
    
    def test_users_settings_file_is_missing(self):
        """testing if an OSError will be raised when the users.xml file is
        missing
        """
        
        # rename the current users.xml file
        
        settings_path = os.path.expanduser(
            os.path.expandvars(
                os.environ["OYPROJECTMANAGER_PATH"]
            )
        )
        
        # check if there is a users.xml file
        orig_file_path = os.path.join(settings_path, "users.xml")
        backup_file_path = os.path.join(settings_path, "users.xml.orig")
        
        # rename it
        os.rename(orig_file_path, backup_file_path)
        
        # now create a Repository and expect an OSError
        self.assertRaises(OSError, repository.Repository)
        
        # rename back the settings file
        os.rename(backup_file_path, orig_file_path)
    
    def test_user_initials_property_is_read_only(self):
        """testing if the user_initials property is read only
        """
        
        repo = Repository()
        self.assertRaises(AttributeError, setattr, repo, "user_initials", [])
    
    def test_user_initials_working_properly(self):
        """testing if the user_initials property working properly
        """
        
        # it should return
        user_initials = ["u1", "u2", "u3", "u4", "u5"]
        repo = Repository()
        self.assertEqual(repo.user_initials, user_initials)
    
    def test_time_units_returns_a_dictionary(self):
        """testing if time_units returns a dictionary
        """
        
        repo = Repository()
        
        self.assertIsInstance(repo.time_units, dict)
    
    def test_time_units_is_a_read_only_property(self):
        """testing if time_units is read only
        """
        
        repo = Repository()
        self.assertRaises(AttributeError, setattr, repo, "time_units", None)
    
    def test_time_units_is_returning_the_correct_values(self):
        """testing if time_units is returning correct values
        """
        
        # the current test settings file should return the following dictionary
        time_units = {
            "game":15,
            "film":24,
            "pal":25,
            "ntsc":30,
            "show":48,
            "palf":50,
            "ntscf":60,
        }
        
        repo = Repository()
        self.assertEqual(repo.time_units, time_units)
    
    def test_defaultFiles_returning_a_list_of_tuples(self):
        """testing if the defaultFiles method returns a list of tuples
        """
        
        repo = Repository()
        
        for defaultFileInfo in repo.defaultFiles:
            self.assertIsInstance(defaultFileInfo, tuple)
    
    def test_defaultFiles_is_read_only(self):
        """testing if the defaultFiles property is read only
        """
        
        repo = Repository()
        self.assertRaises(AttributeError, setattr, repo, "defaultFiles", [])
    
    def test_defaultFiles_working_properly(self):
        """testing if the defaultFiles property is returning a tuple containing
        the default file locations
        """
        
        repo = Repository()
        defFiles_list = repo.defaultFiles
        
        # for the default setup it should return only one element and it is
        # the workspace.mel
        
        self.assertEqual(len(defFiles_list), 1)
        self.assertEqual(defFiles_list[0][0], "workspace.mel")
        self.assertEqual(defFiles_list[0][1], ".")
