# -*- coding: utf-8 -*-
# Copyright (c) 2009-2012, Erkan Ozgur Yilmaz
# 
# This module is part of oyProjectManager and is released under the BSD 2
# License: http://www.opensource.org/licenses/BSD-2-Clause

import sys
import os
import shutil
import tempfile
import unittest

import sip
from oyProjectManager.models.asset import Asset
from oyProjectManager.models.auth import User
from oyProjectManager.models.entity import EnvironmentBase
from oyProjectManager.models.project import Project
from oyProjectManager.models.sequence import Sequence
from oyProjectManager.models.shot import Shot
from oyProjectManager.models.version import Version, VersionType

sip.setapi('QString', 2)
sip.setapi('QVariant', 2)
from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import Qt
from PyQt4.QtTest import QTest

from oyProjectManager import conf, db
from oyProjectManager.ui import version_creator

import logging
logger = logging.getLogger("oyProjectManager.ui.version_creator")
logger.setLevel(logging.DEBUG)

# exceptions for test purposes
class ExportAs(Exception):
    pass

class TestEnvironment(EnvironmentBase):
    """A test environment which just raises errors to check if the correct
    method has been called
    """
    
    name = "TestEnv"
    
    test_data = {
        "export_as": {"call count": 0, "data": None},
        "save_as": {"call count": 0, "data": None},
        "open_": {"call count": 0, "data": None},
        "reference": {"call count": 0, "data": None},
        "import_": {"call count": 0, "data": None},
    }
    
    def export_as(self, version):
        self.test_data["export_as"]["call count"] += 1
        self.test_data["export_as"]["data"] = version

    def save_as(self, version):
        self.test_data["save_as"]["call count"] += 1
        self.test_data["save_as"]["data"] = version
    
    def open_(self, version, force=False):
        self.test_data["open_"]["call count"] += 1
        self.test_data["open_"]["data"] = version
    
    def reference(self, version):
        self.test_data["reference"]["call count"] += 1
        self.test_data["reference"]["data"] = version
    
    def import_(self, version):
        self.test_data["import_"]["call count"] += 1
        self.test_data["import_"]["data"] = version
    
    def get_last_version(self):
        """mock version of the original this returns None all the time
        """
        return None

class VersionReplacerTester(unittest.TestCase):
    """tests the oyProjectManager.ui.version_replacer
    """
    
    def setUp(self):
        """setup the test
        """
        # -----------------------------------------------------------------
        # start of the setUp
        conf.database_url = "sqlite://"
        
        db.setup()
        
        # create the environment variable and point it to a temp directory
        self.temp_config_folder = tempfile.mkdtemp()
        self.temp_projects_folder = tempfile.mkdtemp()
        
        os.environ["OYPROJECTMANAGER_PATH"] = self.temp_config_folder
        os.environ[conf.repository_env_key] = self.temp_projects_folder
        
        # for PyQt4
        self.app = QtGui.QApplication(sys.argv)
    
    def tearDown(self):
        """clean up the test
        """
        # set the db.session to None
        db.session = None
        
        # delete the temp folders
        shutil.rmtree(self.temp_config_folder)
        shutil.rmtree(self.temp_projects_folder)
    
    def show_dialog(self, dialog):
        """show the given dialog
        """
        dialog.show()
        self.app.exec_()
        self.app.connect(
            self.app,
            QtCore.SIGNAL("lastWindowClosed()"),
            self.app,
            QtCore.SLOT("quit()")
        )
    
