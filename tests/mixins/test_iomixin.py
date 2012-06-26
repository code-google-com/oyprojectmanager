# -*- coding: utf-8 -*-
# Copyright (c) 2009-2012, Erkan Ozgur Yilmaz
# 
# This module is part of oyProjectManager and is released under the BSD 2
# License: http://www.opensource.org/licenses/BSD-2-Clause
import os
import shutil
import tempfile

import unittest
from sqlalchemy import Column, Integer
from oyProjectManager import conf, db
from oyProjectManager.db.declarative import Base
from oyProjectManager.models.link import FileLink
from oyProjectManager.models.mixins import IOMixin

class IOMixClass(Base, IOMixin):
    """A class which is mixed with IOMixin for testing purposes
    """
    __tablename__ = "IOMixClasses"
    IOMixClass_id = Column("id", Integer, primary_key=True)

    def __init__(self, **kwargs):
        super(IOMixClass, self).__init__(**kwargs)
        IOMixin.__init__(self, **kwargs)

class IOMixinTester(unittest.TestCase):
    """tests the oyProjectManager.models.mixins.IOMixin class
    """
    
    def setUp(self):
        """set up the test
        """
        conf.database_url = "sqlite://"
        
        # create the environment variable and point it to a temp directory
        self.temp_config_folder = tempfile.mkdtemp()
        self.temp_projects_folder = tempfile.mkdtemp()
        
        os.environ["OYPROJECTMANAGER_PATH"] = self.temp_config_folder
        os.environ[conf.repository_env_key] = self.temp_projects_folder
        
        self.inputs = [
            FileLink(filename="a.%03d.tga 5-100 13")
        ]
        
        
        self.kwargs = {
            "inputs": "test_file_name.txt",
            "outputs": "/some/path/to/an/unknown/place",
        }
    
    def tearDown(self):
        """clean up the test
        """
        
        # set the db.session to None
        db.session = None
        
        # delete the temp folders
        shutil.rmtree(self.temp_config_folder)
        shutil.rmtree(self.temp_projects_folder)
    
    
