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
import logging
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
from oyProjectManager.ui import shot_editor

logger = logging.getLogger("oyProjectManager.ui.version_creator")
logger.setLevel(logging.DEBUG)

class ShotEditorTester(unittest.TestCase):
    """tests the oyProjectManager.ui.shot_editor class
    """
    
    def setUp(self):
        """setup the test
        """
        # -----------------------------------------------------------------
        # start of the setUp
        conf.database_url = "sqlite://"
        
        # create the environment variable and point it to a temp directory
        self.temp_config_folder = tempfile.mkdtemp()
        self.temp_projects_folder = tempfile.mkdtemp()
        
        os.environ["OYPROJECTMANAGER_PATH"] = self.temp_config_folder
        os.environ[conf.repository_env_key] = self.temp_projects_folder
        
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
    
    def test_shot_argument_is_a_shot_instance_will_fill_the_ui_with_shot_info(self):
        """testing if the ui is filled with correct info coming from the given
        shot
        """
        
        proj1 = Project('Test Project')
        proj1.save()
        
        seq1 = Sequence(proj1, 'Test Sequence')
        seq1.save()
        
        shot = Shot(seq1, 1, 2, 435)
        shot.handle_at_start = 23
        shot.handle_at_end = 12
        shot.save()
        
        dialog = shot_editor.MainDialog(shot=shot)
        
        # test if the "Editing Shot: SH001" is correctly updated
        self.assertEqual(
            shot.code,
            dialog.shot_name_label.text()
        )
        
        # test frame range info
        self.assertEqual(
            shot.start_frame,
            dialog.start_frame_spinBox.value()
        )
        
        self.assertEqual(
            shot.end_frame,
            dialog.end_frame_spinBox.value()
        )
        
        self.assertEqual(
            shot.handle_at_start,
            dialog.handle_at_start_spinBox.value()
        )
        
        self.assertEqual(
            shot.handle_at_end,
            dialog.handle_at_end_spinBox.value()
        )
    
    def test_shot_info_of_the_given_shot_is_updated_correctly(self):
        """testing if the shot info is updated when clicked to ok
        """
        
        proj1 = Project('Test Project')
        proj1.save()
        
        seq1 = Sequence(proj1, 'Test Sequence')
        seq1.save()
        
        shot = Shot(seq1, 1, 2, 435)
        shot.handle_at_start = 23
        shot.handle_at_end = 12
        shot.save()
        
        start_frame = 132
        end_frame = 250
        handle_at_start = 11
        handle_at_end = 32
        
        dialog = shot_editor.MainDialog(shot=shot)
#        self.show_dialog(dialog)
        
        # now update the values
        dialog.start_frame_spinBox.setValue(start_frame)
        dialog.end_frame_spinBox.setValue(end_frame)
        dialog.handle_at_start_spinBox.setValue(handle_at_start)
        dialog.handle_at_end_spinBox.setValue(handle_at_end)
        
        # hit ok
        QTest.mouseClick(
            dialog.buttonBox.buttons()[0],
            QtCore.Qt.LeftButton
        )
        
        # now check if the shot is updated
        self.assertEqual(start_frame, shot.start_frame)
        self.assertEqual(end_frame, shot.end_frame)
        self.assertEqual(handle_at_start, shot.handle_at_start)
        self.assertEqual(handle_at_end, shot.handle_at_end)
    
    def test_no_shot_is_given_will_set_the_text_label_to_NA(self):
        """testing if no shot instance is given will set the label to N/A
        """
        dialog = shot_editor.MainDialog()
        self.assertEqual("N/A", dialog.shot_name_label.text())
    
    def test_hit_cancel_will_close_the_dialog(self):
        """testing if hitting cancel will close the dialog
        """
        dialog = shot_editor.MainDialog()
        dialog.show()
        QTest.mouseClick(
            dialog.buttonBox.buttons()[1],
            QtCore.Qt.LeftButton
        )
        self.assertFalse(dialog.isVisible())
    
    def test_hit_ok_will_close_the_dialog(self):
        """testing if hitting ok will close the dialog
        """
        dialog = shot_editor.MainDialog()
        dialog.show()
        QTest.mouseClick(
            dialog.buttonBox.buttons()[0],
            QtCore.Qt.LeftButton
        )
        self.assertFalse(dialog.isVisible())
