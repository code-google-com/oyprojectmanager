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

#from PySide import QtCore, QtGui
#from PySide.QtCore import Qt
#from PySide.QtTest import QTest
import sip
sip.setapi('QString', 2)
sip.setapi('QVariant', 2)
from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import Qt
from PyQt4.QtTest import QTest

from oyProjectManager import config, db
from oyProjectManager.core.models import (Project, Sequence, Shot)
from oyProjectManager.ui import project_manager

conf = config.Config()

class ProjectManager_Tester(unittest.TestCase):
    """tests the oyProjectManager.ui.project_manager
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
        #        os.environ["OYPROJECTMANAGER_PATH"] = ""
        os.environ[conf.repository_env_key] = self.temp_projects_folder
        
        # re-parse the settings
        #        conf._parse_settings()
        
        # for PySide
#        if QtGui.qApp is None:
#            print "qApp is None"
#            self.app = QtGui.QApplication(sys.argv)
#        else:
#            print "qApp is OK"
#            self.app = QtGui.qApp
        
        # for PyQt4
        self.app = QtGui.QApplication(sys.argv)
    
    def tearDown(self):
        """clean up the test
        """
        # for PySide
#        self.app.quit()
#        del self.app
        
        # set the db.session to None
        db.session = None

        # delete the temp folders
        shutil.rmtree(self.temp_config_folder)
        shutil.rmtree(self.temp_projects_folder)
    
    def test_projects_comboBox_is_filled_with_projects_on_the_database(self):
        """testing if the projects_comboBox is filled with Project instances
        from the database
        """
        
        # create a couple of projects
        project1 = Project("Test Project 1")
        project2 = Project("Test Project 2")
        project3 = Project("Test Project 3")
        
        project1.save()
        project2.save()
        project3.save()
        
        # open UI
        dialog = project_manager.MainDialog()
#        dialog.show()
#        self.app.exec_()
#        self.app.connect(
#            self.app,
#            QtCore.SIGNAL("lastWindowClosed()"),
#            self.app,
#            QtCore.SLOT("quit()")
#        )
        
        # check if the projects are listed there
        self.assertEqual(dialog.projects_comboBox.count(), 3)

        item_texts = []
        for i in range(3):
            dialog.projects_comboBox.setCurrentIndex(i)
            item_texts.append(dialog.projects_comboBox.currentText())
        
        self.assertTrue(project1.name in item_texts)
        self.assertTrue(project2.name in item_texts)
        self.assertTrue(project3.name in item_texts)

    def test_close_pushButton_closes_ui(self):
        """testing if the close_pushButton is closing the ui
        """
        dialog = project_manager.MainDialog()
        dialog.show()
        
        self.assertEqual(dialog.isVisible(), True)
        
        # now run the UI
        QTest.mouseClick(dialog.close_pushButton, Qt.LeftButton)
        self.assertEqual(dialog.isVisible(), False)        

    
    def test_projects_comboBox_index_is_0_on_init(self):
        """testing if the projects_comboBox is set to the first project on the
        list when __init__
        """

        project1 = Project("Test Project 1")
        project2 = Project("Test Project 2")
        project3 = Project("Test Project 3")
        
        project1.save()
        project2.save()
        project3.save()
        
        dialog = project_manager.MainDialog()
        
        self.assertEqual(dialog.projects_comboBox.currentIndex(), 0)

    def test_projects_comboBox_caches_Project_instances_in_projects_attribute(self):
        """testing if the projects_comboBox caches the Project instances in an
        attribute called projects
        """
        
        project1 = Project("Test Project 1")
        project2 = Project("Test Project 2")
        project3 = Project("Test Project 3")

        project1.save()
        project2.save()
        project3.save()

        dialog = project_manager.MainDialog()
        
        self.assertTrue(hasattr(dialog.projects_comboBox, "projects"))

        self.assertTrue(project1 in dialog.projects_comboBox.projects)
        self.assertTrue(project2 in dialog.projects_comboBox.projects)
        self.assertTrue(project3 in dialog.projects_comboBox.projects)
        
        
    
    def test_sequences_comboBox_is_filled_with_sequences_from_the_current_project(self):
        """testing if the sequences_comboBox is filled with the correct
        sequences from the currently chosen Project instance
        """
        
        project1 = Project("Test Project 1")
        project2 = Project("Test Project 2")
        
        project1.create()
        project2.create()
        
        project1.save()
        project2.save()
        
        seq1 = Sequence(project1, "Test Sequence 1")
        seq1.save()
        seq2 = Sequence(project1, "Test Sequence 2")
        seq2.save()
        seq3 = Sequence(project2, "Test Sequence 3")
        seq3.save()
        seq4 = Sequence(project2, "Test Sequence 4")
        seq4.save()
        
        # create dialog
        dialog = project_manager.MainDialog()
#        dialog.show()
#        self.app.exec_()
#        self.app.connect(
#            self.app,
#            QtCore.SIGNAL("lastWindowClosed()"),
#            self.app,
#            QtCore.SLOT("quit()")
#        )
        
        # set the project to project2
        index = dialog.projects_comboBox.findText(project2.name)
        dialog.projects_comboBox.setCurrentIndex(index)
        
        # check if the sequences_comboBox is filled with correct data
        self.assertEqual(dialog.sequences_comboBox.count(), 2)

        item_texts = []
        for i in range(2):
            dialog.sequences_comboBox.setCurrentIndex(i)
            item_texts.append(dialog.sequences_comboBox.currentText())
        
        self.assertTrue(seq3.name in item_texts)
        self.assertTrue(seq4.name in item_texts)
        
        # set the project to project1
        index = dialog.projects_comboBox.findText(project1.name)
        dialog.projects_comboBox.setCurrentIndex(index)

        # check if the sequences_comboBox is filled with correct data
        self.assertEqual(dialog.sequences_comboBox.count(), 2)

        item_texts = []
        for i in range(2):
            dialog.sequences_comboBox.setCurrentIndex(i)
            item_texts.append(dialog.sequences_comboBox.currentText())

        self.assertTrue(seq1.name in item_texts)
        self.assertTrue(seq2.name in item_texts)


    def test_sequences_comboBox_caches_Sequence_instances_in_sequences_attribute(self):
        """testing if the sequence_comboBox caches the Sequence instances in
        an attribute called Sequence
        """

        project1 = Project("Test Project 1")
        project1.create()

        project2 = Project("Test Project 2")
        project2.create()

        seq1 = Sequence(project1, "Test Sequence 1")
        seq1.save()
        
        seq2 = Sequence(project1, "Test Sequence 2")
        seq2.save()

        seq3 = Sequence(project2, "Test Sequence 3")
        seq3.save()

        seq4 = Sequence(project2, "Test Sequence 4")
        seq4.save()

        seq5 = Sequence(project2, "Test Sequence 5")
        seq5.save()

        dialog = project_manager.MainDialog()
        
        self.assertTrue(hasattr(dialog.sequences_comboBox, "sequences"))

        # set it to project1
        index = dialog.projects_comboBox.findText(project1.name)
        dialog.projects_comboBox.setCurrentIndex(index)

        # check if sequences_comboBox.sequences has 3 elements
        self.assertEqual(len(dialog.sequences_comboBox.sequences), 2)

        # check if all the sequences are there
        self.assertTrue(seq1 in dialog.sequences_comboBox.sequences)
        self.assertTrue(seq2 in dialog.sequences_comboBox.sequences)

        # set it to project2
        index = dialog.projects_comboBox.findText(project2.name)
        dialog.projects_comboBox.setCurrentIndex(index)

        # check if sequences_comboBox.sequences has 3 elements
        self.assertEqual(len(dialog.sequences_comboBox.sequences), 3)

        # check if all the sequences are there
        self.assertTrue(seq3 in dialog.sequences_comboBox.sequences)
        self.assertTrue(seq4 in dialog.sequences_comboBox.sequences)
        self.assertTrue(seq5 in dialog.sequences_comboBox.sequences)

    def test_shots_comboBox_is_filled_with_the_shots_from_the_current_sequence(self):
        """testing if the shots_comboBox is filled with the shots from the
        currently selected Sequence instance
        """
        
        # projects
        project1 = Project("Test Project 1")
        project1.create()

        project2 = Project("Test Project 2")
        project2.create()
        
        # sequences
        seq1 = Sequence(project1, "Test Sequence 1")
        seq1.save()
        
        seq2 = Sequence(project1, "Test Sequence 2")
        seq2.save()

        seq3 = Sequence(project2, "Test Sequence 3")
        seq3.save()
        
        seq4 = Sequence(project2, "Test Sequence 4")
        seq4.save()
        
        # shots
        shot1 = Shot(seq1, 1)
        shot2 = Shot(seq1, 2)
        shot3 = Shot(seq1, 3)

        shot4 = Shot(seq2, 4)
        shot5 = Shot(seq2, 5)
        shot6 = Shot(seq2, 6)

        shot7 = Shot(seq3, 7)
        shot8 = Shot(seq3, 8)
        shot9 = Shot(seq3, 9)

        shot10 = Shot(seq4, 10)
        shot11 = Shot(seq4, 11)
        shot12 = Shot(seq4, 12)
        
        db.session.add_all(
            [shot1, shot2, shot3, shot4, shot5, shot6, shot7, shot8, shot9,
             shot10, shot11, shot12]
        )
        db.session.commit()
        
        dialog = project_manager.MainDialog()
#        dialog.show()
#        self.app.exec_()
#        self.app.connect(
#            self.app,
#            QtCore.SIGNAL("lastWindowClosed()"),
#            self.app,
#            QtCore.SLOT("quit()")
#        )
        
        # set to project1
        index = dialog.projects_comboBox.findText(project1.name)
        dialog.projects_comboBox.setCurrentIndex(index)
        
        # set to seq1
        index = dialog.sequences_comboBox.findText(seq1.name)
        dialog.sequences_comboBox.setCurrentIndex(index)
        
        # check if shots_comboBox has 3 entries
        self.assertEqual(dialog.shots_comboBox.count(), 3)
        
        # check if shot1, shot2, shot3 are in the comboBox
        item_texts = []
        for i in range(3):
            dialog.shots_comboBox.setCurrentIndex(i)
            item_texts.append(dialog.shots_comboBox.currentText())
        
        self.assertTrue(shot1.code in item_texts)
        self.assertTrue(shot2.code in item_texts)
        self.assertTrue(shot3.code in item_texts)

        # set to project2
        index = dialog.projects_comboBox.findText(project2.name)
        dialog.projects_comboBox.setCurrentIndex(index)

        # set to seq4
        index = dialog.sequences_comboBox.findText(seq4.name)
        dialog.sequences_comboBox.setCurrentIndex(index)

        # check if shots_comboBox has 3 entries
        self.assertEqual(dialog.shots_comboBox.count(), 3)

        # check if shot10, shot11, shot12 are in the comboBox
        item_texts = []
        for i in range(3):
            dialog.shots_comboBox.setCurrentIndex(i)
            item_texts.append(dialog.shots_comboBox.currentText())

        self.assertTrue(shot10.code in item_texts)
        self.assertTrue(shot11.code in item_texts)
        self.assertTrue(shot12.code in item_texts)
    
    def test_addProject_toolButton_pops_a_QInputDialog(self):
        """testing if the addProject_toolButton pops a QInputDialog and asks
        for a project name
        """
        self.fail("test is not implemented yet")
