# -*- coding: utf-8 -*-
# Copyright (c) 2009-2012, Erkan Ozgur Yilmaz
# 
# This module is part of oyProjectManager and is released under the BSD 2
# License: http://www.opensource.org/licenses/BSD-2-Clause

import os
import shutil
import tempfile
import unittest
import logging
from oyProjectManager.core.models import User


class ConfigTester(unittest.TestCase):
    """test the system configuration
    """
    
    def setUp(self):
        """setup the test
        """
        logger = logging.getLogger("oyProjectManager")
        logger.setLevel(logging.DEBUG)
        
        # so we need a temp directory to be specified as our config folder
        self.temp_config_folder = tempfile.mkdtemp()
        
        # we should set the environment variable
        os.environ["OYPROJECTMANAGER_PATH"] = self.temp_config_folder
        
        self.config_full_path = os.path.join(self.temp_config_folder, "config.py")
    
    def tearDown(self):
        """clean up the test
        """
        # and remove the temp directory
        shutil.rmtree(self.temp_config_folder)

    def test_config_variable_updates_with_user_config(self):
        """testing if the database_file_name will be updated by the user
        config
        """
        # now create a config.py file and fill it with the desired values
        # like database_file_name = "test_value.db"
        test_value = ".test_value.db"
        config_file = open(self.config_full_path, "w")
        config_file.writelines(["#-*- coding: utf-8 -*-\n",
                                'database_url = "' + test_value + '"\n'])
        config_file.close()

        # now import the config.py and see if it updates the
        # database_file_name variable
        from oyProjectManager import config
        conf = config.Config()

        self.assertEqual(test_value, conf.database_url)

    def test_config_variable_doesnt_create_new_variables_with_user_config(self):
        """testing if the config will not be updated by the user config by
        adding new variables
        """
        # now create a config.py file and fill it with the desired values
        # like database_file_name = "test_value.db"
        test_value = ".test_value.db"
        config_file = open(self.config_full_path, "w")
        config_file.writelines(["#-*- coding: utf-8 -*-\n",
                                'test_value = "' + test_value + '"\n'])
        config_file.close()
        
        # now import the config.py and see if it updates the
        # database_file_name variable
        from oyProjectManager import config
        conf = config.Config()
        
        self.assertRaises(KeyError, getattr, conf, "test_value")
    
    def test_env_variable_with_vars_module_import_with_shortcuts(self):
        """testing if the module path has shortcuts like ~ and other env
        variables
        """
        splits = os.path.split(self.temp_config_folder)
        var1 = splits[0]
        var2 = os.path.sep.join(splits[1:])
        
        os.environ["var1"] = var1
        os.environ["var2"] = var2
        os.environ["OYPROJECTMANAGER_PATH"] = "$var1/$var2"
        
        test_value = "sqlite3:///.test_value.db"
        config_file = open(self.config_full_path, "w")
        config_file.writelines(["#-*- coding: utf-8 -*-\n",
                                'database_url = "' + test_value + '"\n'])
        config_file.close()
        
        # now import the config.py and see if it updates the
        # database_file_name variable
        from oyProjectManager import config
        conf = config.Config()
        
        self.assertEqual(test_value, conf.database_url)
        
    def test_env_variable_with_deep_vars_module_import_with_shortcuts(self):
        """testing if the module path has multiple shortcuts like ~ and other
        env variables
        """
        splits = os.path.split(self.temp_config_folder)
        var1 = splits[0]
        var2 = os.path.sep.join(splits[1:])
        var3 = os.path.join("$var1", "$var2")
        
        os.environ["var1"] = var1
        os.environ["var2"] = var2
        os.environ["var3"] = var3
        os.environ["OYPROJECTMANAGER_PATH"] = "$var3"
        
        test_value = "sqlite:///.test_value.db"
        config_file = open(self.config_full_path, "w")
        config_file.writelines(["#-*- coding: utf-8 -*-\n",
                                'database_url = "' + test_value + '"\n'])
        config_file.close()
        
        # now import the config.py and see if it updates the
        # database_file_name variable
        from oyProjectManager import config
        conf = config.Config()
        
        self.assertEqual(test_value, conf.database_url)
    
    def test_non_existing_path_in_environment_variable(self):
        """testing if the non existing path situation will be handled
        gracefully by warning the user
        """
        os.environ["OYPROJECTMANAGER_PATH"] = "/tmp/non_existing_path"
        from oyProjectManager import config
        config.Config()
    
    def test_syntax_error_in_settings_file(self):
        """testing if a RuntimeError will be raised when there are syntax
        errors in the config.py file
        """
        # now create a config.py file and fill it with the desired values
        # like database_file_name = "test_value.db"
        # but do a syntax error on purpose, like forgetting the last quato sign
        test_value = ".test_value.db"
        config_file = open(self.config_full_path, "w")
        config_file.writelines(["#-*- coding: utf-8 -*-\n",
                                'database_file_name = "' + test_value + '\n'])
        config_file.close()
        
        # now import the config.py and see if it updates the
        # database_file_name variable
        from oyProjectManager import config
        self.assertRaises(RuntimeError, config.Config)
    
#    def test_users_attribute_will_return_a_list_of_User_instances(self):
#        """testing if the config.users will return a list of
#        oyProjectManager.core.models.User instances defined in the config.py
#        file with the users_data variable
#        """
#        
#        config_file = open(self.config_full_path, "w")
#        config_file.writelines(["#-*- coding: utf-8 -*-\n",
#                                'users_data = [\n'
#                                '    {"name":"Test User 1",\n',
#                                '     "initials":"tu1",\n'
#                                '     "email": "testuser1@user.com"},\n'
#                                '    {"name":"Test User 2",\n',
#                                '     "initials":"tu2",\n'
#                                '     "email": "testuser2@user.com"},\n'
#                                ']\n'])
#        config_file.close()
#        
#        # now import the config.py and see if it updates the
#        # database_file_name variable
#        from oyProjectManager import config
#        conf = config.Config()
#        
#        self.assertIsInstance(conf.users, list)
#        user1 = conf.users[0]
#        user2 = conf.users[1]
#        self.assertIsInstance(user1, User)
#        self.assertIsInstance(user2, User)
#        
#        self.assertEqual(user1.name, "Test User 1")
#        self.assertEqual(user1.initials, "tu1")
#        self.assertEqual(user1.email, "testuser1@user.com")
#        
#        self.assertEqual(user2.name, "Test User 2")
#        self.assertEqual(user2.initials, "tu2")
#        self.assertEqual(user2.email, "testuser2@user.com")
