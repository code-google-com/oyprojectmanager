#-*- coding: utf-8 -*-
import os
import shutil
import tempfile
import unittest
import logging


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
        
        self.config_fullpath = os.path.join(self.temp_config_folder, "config.py")
    
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
        config_file = open(self.config_fullpath, "w")
        config_file.writelines(["#-*- coding: utf-8 -*-\n",
                                'database_file_name = "' + test_value + '"\n'])
        config_file.close()

        # now import the config.py and see if it updates the
        # database_file_name variable
        from oyProjectManager import config
        conf = config.Config()

        self.assertEqual(test_value, conf.database_file_name)

    def test_config_variable_creates_new_variables_with_user_config(self):
        """testing if the database_file_name will be updated by the user
        config by adding new variables
        """
        # now create a config.py file and fill it with the desired values
        # like database_file_name = "test_value.db"
        test_value = ".test_value.db"
        config_file = open(self.config_fullpath, "w")
        config_file.writelines(["#-*- coding: utf-8 -*-\n",
                                'TEST_VALUE = "' + test_value + '"\n'])
        config_file.close()

        # now import the config.py and see if it updates the
        # database_file_name variable
        from oyProjectManager import config
        conf = config.Config()
        
        self.assertEqual(test_value, conf.TEST_VALUE)

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
        
        test_value = ".test_value.db"
        config_file = open(self.config_fullpath, "w")
        config_file.writelines(["#-*- coding: utf-8 -*-\n",
                                'database_file_name = "' + test_value + '"\n'])
        config_file.close()
        
        # now import the config.py and see if it updates the
        # database_file_name variable
        from oyProjectManager import config
        conf = config.Config()
        
        self.assertEqual(test_value, conf.database_file_name)
        
    def test_env_variable_with_deep_vars_module_import_with_shortcuts(self):
        """testing if the module path has multiple shortcuts like ~ and other env
        variables
        """
        splits = os.path.split(self.temp_config_folder)
        var1 = splits[0]
        var2 = os.path.sep.join(splits[1:])
        var3 = os.path.join("$var1", "$var2")
        
        os.environ["var1"] = var1
        os.environ["var2"] = var2
        os.environ["var3"] = var3
        os.environ["OYPROJECTMANAGER_PATH"] = "$var3"
        
        test_value = ".test_value.db"
        config_file = open(self.config_fullpath, "w")
        config_file.writelines(["#-*- coding: utf-8 -*-\n",
                                'database_file_name = "' + test_value + '"\n'])
        config_file.close()
        
        # now import the config.py and see if it updates the
        # database_file_name variable
        from oyProjectManager import config
        conf = config.Config()
        
        self.assertEqual(test_value, conf.database_file_name)
    
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
        config_file = open(self.config_fullpath, "w")
        config_file.writelines(["#-*- coding: utf-8 -*-\n",
                                'database_file_name = "' + test_value + '\n'])
        config_file.close()
        
        # now import the config.py and see if it updates the
        # database_file_name variable
        from oyProjectManager import config
        self.assertRaises(RuntimeError, config.Config)
    
