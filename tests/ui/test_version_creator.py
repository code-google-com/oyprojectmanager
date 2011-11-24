#-*- coding: utf-8 -*-

import sys
import os
import shutil
import tempfile
import unittest

from PySide import QtCore, QtGui
from PySide.QtCore import Qt
from PySide.QtTest import QTest

from oyProjectManager import config
from oyProjectManager.core.models import (Project, Asset, Version, User,
                                          VersionType, Sequence, Shot)
from oyProjectManager.ui import version_creator

conf = config.Config()

class VersionCreatorTester(unittest.TestCase):
    """tests the oyProjectManager.ui.version_creator class
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
        
        if QtGui.qApp is None:
            self.app = QtGui.QApplication(sys.argv)
        else:
            self.app = QtGui.qApp
    
    def tearDown(self):
        """clean up the test
        """
        self.app.quit()
        del self.app
        
        # delete the temp folders
        shutil.rmtree(self.temp_config_folder)
        shutil.rmtree(self.temp_projects_folder)
    
    def test_close_button_closes_ui(self):
        """testing if the close button is closing the ui
        """
        dialog = version_creator.MainDialog_New()
        
        # now run the UI
        QTest.mouseClick(dialog.close_pushButton, Qt.LeftButton)
        self.assertEqual(dialog.isVisible(), False)
    
    def test_projects_comboBox_no_problem_when_there_is_no_project(self):
        """testing if there will be no problem when there is no project created
        yet
        """
        dialog = version_creator.MainDialog_New()
    
    def test_projects_comboBox_is_filled_with_projects(self):
        """testing if the projects_combobox is filled with projects
        """
        # create a couple of test projects
        proj1 = Project("Test Project1")
        proj2 = Project("Test Project2")
        
        proj1.create()
        proj2.create()
        
        dialog = version_creator.MainDialog_New()
        
        # see if the projects filled with projects
        self.assertEqual(dialog.projects_comboBox.count(), 2)
    
    def test_projects_comboBox_first_project_is_selected(self):
        """testing if the first project is selected in the project combo box
        """
        # create a couple of test projects
        proj1 = Project("Test Project1")
        proj2 = Project("Test Project2")
        
        proj1.create()
        proj2.create()
        
        dialog = version_creator.MainDialog_New()
        # see if the projects filled with projects
        self.assertEqual(dialog.projects_comboBox.currentIndex(), 0)
    
    def test_projects_comboBox_has_project_obj_attribute(self):
        """testing if there is a project_obj object holding the current Project
        instance
        """
        # create a couple of test projects
        proj1 = Project("TEST_PROJ1")
        proj2 = Project("TEST_PROJ2")
        proj3 = Project("TEST_PROJ3")
        
        proj1.create()
        proj2.create()
        proj3.create()
        
        dialog = version_creator.MainDialog_New()
        
        # check if the projects_comboBox has an attribute called project_obj
        self.assertTrue(hasattr(dialog.projects_comboBox, "project_obj"))
    
    def test_projects_comboBox_project_obj_attribute_is_Project_instance(self):
        """testing if the project_obj attribute in the projects_comboBox is a
        Project instance
        """
        # create a couple of test projects
        proj1 = Project("TEST_PROJ1")
        proj2 = Project("TEST_PROJ2")
        proj3 = Project("TEST_PROJ3")
        
        proj1.create()
        proj2.create()
        proj3.create()
        
        dialog = version_creator.MainDialog_New()
        
        # check if the project_obj is a Project instance
        self.assertIsInstance(dialog.projects_comboBox.project_obj, Project)
    
    def test_projects_comboBox_project_obj_attributes_name_is_same_with_comboBox_text(self):
        """testing if the Project instance which is held in the project_obj
        attribute in the projects_comboBox has the same name with the 
        """
        
        # create a couple of test projects
        proj1 = Project("TEST_PROJ1")
        proj2 = Project("TEST_PROJ2")
        proj3 = Project("TEST_PROJ3")
        
        proj1.create()
        proj2.create()
        proj3.create()
        
        dialog = version_creator.MainDialog_New()
        
        # check if the name of the project is the same with the currently
        # selected project
        self.assertEqual(
            dialog.projects_comboBox.currentText(),
            dialog.projects_comboBox.project_obj.name
        )
    
    def test_project_comboBox_with_no_sequences_and_shots(self):
        """testing if no error will be raised when there are couple of projects
        but no sequences
        """
        
        proj1 = Project("TEST_PROJ1")
        proj1.create()
        
        proj2 = Project("TEST_PROJ2")
        proj2.create()
        
        dialog = version_creator.MainDialog_New()
#        dialog.show()
#        self.app.exec_()
#        self.app.connect(
#            self.app,
#            QtCore.SIGNAL("lastWindowClosed()"),
#            self.app,
#            QtCore.SLOT("quit()")
#        )
        pass
    
    def test_project_comboBox_updates_the_sequences_if_and_only_if_the_tab_is_in_shots(self):
        """testing if the project_comboBox updates the sequences_comboBox if
        and only if the tab is in the "Shots"
        """
        
        proj1 = Project("TEST_PROJECT1")
        proj1.create()
        
        proj2 = Project("TEST_PROJECT2")
        proj2.create()
        
        seq1 = Sequence(proj1, "TEST_SEQ1")
        seq2 = Sequence(proj1, "TEST_SEQ2")
        seq3 = Sequence(proj1, "TEST_SEQ3")
        
        # create the dialog
        dialog = version_creator.MainDialog_New()
        
        # the default tab should be asset
        self.assertEqual(dialog.tabWidget.currentIndex(), 0)
        
        # the sequences_comboBox should be empty
        self.assertEqual(dialog.sequences_comboBox.count(), 0)
        
        # changing the tabWidget to the Shots should fill the
        # sequences_comboBox
        
        dialog.tabWidget.setCurrentIndex(1)
        
        # check if the sequences_comboBox is filled with sequences
        self.assertEqual(dialog.sequences_comboBox.count(), 3)
    
    def test_users_comboBox_is_filled_with_users_from_the_config(self):
        """testing if the users combobox is filled with the user names
        """
        
        # get the users from the config
        users = conf.users
        
        dialog = version_creator.MainDialog_New()
        
        # check if all the names in the users are in the combobox
        
        
        content = [dialog.user_comboBox.itemText(i)
                   for i in range(dialog.user_comboBox.count())]
        
        for user in users:
            self.assertIn(user.name, content)
    
    def test_asset_names_list_filled(self):
        """testing if the asset names listWidget is filled with asset names
        """
        
        # create a new project
        proj1 = Project("TEST_PROJECT1a")
        proj2 = Project("TEST_PROJECT2")
        proj1.create()
        proj2.create()
        
        # create a couple of assets
        asset1 = Asset(proj1, "Test Asset 1")
        asset2 = Asset(proj1, "Test Asset 2")
        asset3 = Asset(proj2, "Test Asset 3")
        asset4 = Asset(proj2, "Test Asset 4")
        asset1.save()
        asset2.save()
        asset3.save()
        asset4.save()
        
        dialog = version_creator.MainDialog_New()
#        dialog.show()
#        self.app.exec_()
#        self.app.connect(
#            self.app,
#            QtCore.SIGNAL("lastWindowClosed()"),
#            self.app,
#            QtCore.SLOT("quit()")
#        )
        
        # now check if their names are in the asset names listWidget
        listWidget = dialog.assets_listWidget
        item_texts = [listWidget.item(i).text() for i in range(listWidget.count())]
        
        self.assertIn(asset1.name, item_texts)
        self.assertIn(asset2.name, item_texts)
        self.assertNotIn(asset3.name, item_texts)
        self.assertNotIn(asset4.name, item_texts)
        
        # now update the project to the second one
        dialog.projects_comboBox.setCurrentIndex(1)
        
        # now check if their names are in the asset names listWidget
        listWidget = dialog.assets_listWidget
        item_texts = [listWidget.item(i).text() for i in range(listWidget.count())]
        
        self.assertNotIn(asset1.name, item_texts)
        self.assertNotIn(asset2.name, item_texts)
        self.assertIn(asset3.name, item_texts)
        self.assertIn(asset4.name, item_texts)
    
    def test_description_text_edit_field_updated(self):
        """testing if the description field is updated with the selected asset
        """
        
        proj1 = Project("TEST_PROJECT1b")
        proj2 = Project("TEST_PROJECT2")
        proj1.create()
        proj2.create()
        
        asset1 = Asset(proj1, "TEST_ASSET1")
        asset2 = Asset(proj1, "TEST_ASSET2")
        asset3 = Asset(proj2, "TEST_ASSET3")
        asset4 = Asset(proj2, "TEST_ASSET4")
        
        asset1.description = "Test description for asset 1"
        asset2.description = "Test description for asset 2"
        asset3.description = "Test description for asset 3"
        asset4.description = "Test description for asset 4"
        
        asset1.save()
        asset2.save()
        asset3.save()
        asset4.save()
        
        dialog = version_creator.MainDialog_New()
#        dialog.show()
#        self.app.exec_()
#        self.app.connect(
#            self.app,
#            QtCore.SIGNAL("lastWindowClosed()"),
#            self.app,
#            QtCore.SLOT("quit()")
#        )
        
        # check if the first assets description is shown in the asset
        # description window
        self.assertEqual(
            dialog.asset_description_textEdit.toPlainText(),
            asset1.description
        )
        
        # select the second asset
        list_item = dialog.assets_listWidget.item(1)
        list_item.setSelected(True)
        dialog.assets_listWidget.setCurrentItem(list_item)
        
        self.assertEqual(
            dialog.asset_description_textEdit.toPlainText(),
            asset2.description
        )
        
        # change project
        dialog.projects_comboBox.setCurrentIndex(1)
        self.assertEqual(
            dialog.asset_description_textEdit.toPlainText(),
            asset3.description
        )
        
        # select the second asset
        list_item = dialog.assets_listWidget.item(1)
        list_item.setSelected(True)
        dialog.assets_listWidget.setCurrentItem(list_item)
        
        self.assertEqual(
            dialog.asset_description_textEdit.toPlainText(),
            asset4.description
        )
    
    def test_asset_description_edit_pushButton_is_disabled_when_there_is_no_asset(self):
        """testing if the asset_description_edit_pushButton is disabled when
        there is no asset
        """
        
        proj = Project("TEST_PROJECT")
        proj.create()
        
        # create the dialog
        dialog = version_creator.MainDialog_New()
#        dialog.show()
#        self.app.exec_()
#        self.app.connect(
#            self.app,
#            QtCore.SIGNAL("lastWindowClosed()"),
#            self.app,
#            QtCore.SLOT("quit()")
#        )
        
        # check if it is unchecked by default
        self.assertFalse(dialog.asset_description_edit_pushButton.isEnabled())
    
    def test_asset_description_edit_pushButton_is_checked_when_there_is_an_asset(self):
        """testing if the edit button changes to done   
        """
        proj = Project("TEST_PROJECT")
        proj.create()
        
        asset1 = Asset(proj, "TEST_ASSET")
        asset1.save()
        
        # create the dialog
        dialog = version_creator.MainDialog_New()
#        dialog.show()
#        self.app.exec_()
#        self.app.connect(
#            self.app,
#            QtCore.SIGNAL("lastWindowClosed()"),
#            self.app,
#            QtCore.SLOT("quit()")
#        )
        
        # check if it is unchecked by default
        self.assertFalse(dialog.asset_description_edit_pushButton.isChecked())
        
        # check if the asset_description_edit button text is edit
        self.assertEqual(
            dialog.asset_description_edit_pushButton.text(),
            "Edit"
        )
        
        # check if the dialog.asset_description_textEdit is read only
        self.assertTrue(dialog.asset_description_textEdit.isReadOnly())
        
        # click in the edit button
        QTest.mouseClick(
            dialog.asset_description_edit_pushButton,
            QtCore.Qt.LeftButton
        )
        
        # check check state
        self.assertTrue(dialog.asset_description_edit_pushButton.isChecked())
        
        # check if the text changed to Done
        self.assertEqual(
            dialog.asset_description_edit_pushButton.text(),
            "Done"
        )
        
        # check if the asset_description_textEdit becomes read-write
        self.assertFalse(dialog.asset_description_textEdit.isReadOnly())
        
        # re click it
        # click in the edit button
        QTest.mouseClick(
            dialog.asset_description_edit_pushButton,
            QtCore.Qt.LeftButton
        )
        
        # check the checked state
        self.assertFalse(dialog.asset_description_edit_pushButton.isChecked())
        
        # check the text
        self.assertEqual(
            dialog.asset_description_edit_pushButton.text(),
            "Edit"
        )
    
    def test_asset_description_edit_pushButton_enables_asset_description_textEdit(self):
        """testing if pushing the edit pushButton for the first time enables
        the asset_description_textEdit and disables it when pushed for a second
        time
        """
        
        proj1 = Project("TEST_PROJECT1c")
        proj1.create()
        
        asset1 = Asset(proj1, "TEST_ASSET1")
        asset1.description = "Description for TEST_ASSET1 before change"
        
        asset2 = Asset(proj1, "TEST_ASSET2")
        asset2.description = "Description for TEST_ASSET2 before change"
        
        asset1.save()
        asset2.save()
        
        # now create the dialog
        dialog = version_creator.MainDialog_New()
        
        # check if the description textEdit field is read-only
        self.assertTrue(
            dialog.asset_description_textEdit.isReadOnly()
        )
        
        # push the edit pushButton
        QTest.mouseClick(
            dialog.asset_description_edit_pushButton,
            QtCore.Qt.LeftButton
        )
        
        # check if the description textEdit field become writable
        self.assertFalse(
            dialog.asset_description_textEdit.isReadOnly()
        )
        
        # hit done pushButton
        QTest.mouseClick(
            dialog.asset_description_edit_pushButton,
            QtCore.Qt.LeftButton
        )
        
        self.assertTrue(
            dialog.asset_description_textEdit.isReadOnly()
        )
    
    def test_asset_description_edit_pushButton_disables_assets_listWidget(self):
        """testing if pushing the edit pushButton for the first time disables
        the assets_listWidget and enables it when pushed for a second
        time
        """
        
        proj1 = Project("TEST_PROJECT1d")
        proj1.create()
        
        asset1 = Asset(proj1, "TEST_ASSET1")
        asset1.description = "Description for TEST_ASSET1 before change"
        
        asset2 = Asset(proj1, "TEST_ASSET2")
        asset2.description = "Description for TEST_ASSET2 before change"
        
        asset1.save()
        asset2.save()
        
        # now create the dialog
        dialog = version_creator.MainDialog_New()
        
        # check if it is already enabled
        self.assertTrue(
            dialog.assets_listWidget.isEnabled()
        )
        
        # push the edit pushButton
        QTest.mouseClick(
            dialog.asset_description_edit_pushButton,
            QtCore.Qt.LeftButton
        )
        
        # check if the assets_listWidget becomes disabled
        self.assertFalse(
            dialog.assets_listWidget.isEnabled()
        )
        
        # hit done pushButton
        QTest.mouseClick(
            dialog.asset_description_edit_pushButton,
            QtCore.Qt.LeftButton
        )
        
        # check if it becomes enabled again
        self.assertTrue(
            dialog.assets_listWidget.isEnabled()
        )
        
        dialog.close()
        del dialog
    
    def test_asset_description_edit_pushButton_disables_create_asset_pushButton(self):
        """testing if pushing the edit pushButton for the first time disables
        the create_asset_pushButton and enables it when pushed for a second
        time
        """
        
        proj1 = Project("TEST_PROJECT1f")
        proj1.create()
        
        asset1 = Asset(proj1, "TEST_ASSET1")
        asset1.description = "Description for TEST_ASSET1 before change"
        
        asset2 = Asset(proj1, "TEST_ASSET2")
        asset2.description = "Description for TEST_ASSET2 before change"
        
        asset1.save()
        asset2.save()
        
        # now create the dialog
        dialog = version_creator.MainDialog_New()
        
        # check if it is already enabled
        self.assertTrue(
            dialog.create_asset_pushButton.isEnabled()
        )
        
        # push the edit pushButton
        QTest.mouseClick(
            dialog.asset_description_edit_pushButton,
            QtCore.Qt.LeftButton
        )
        
        # check if the create_asset_pushButton becomes disabled
        self.assertFalse(
            dialog.create_asset_pushButton.isEnabled()
        )
        
        # push the edit pushButton again
        QTest.mouseClick(
            dialog.asset_description_edit_pushButton,
            QtCore.Qt.LeftButton
        )
        
        # check if it becomes enabled again
        self.assertTrue(
            dialog.create_asset_pushButton.isEnabled()
        )
    
    def test_asset_description_edit_pushButton_disables_shots_tab(self):
        """testing if pushing the edit pushButton for the first time disables
        the shots_tab and enables it when pushed for a second
        time
        """
        
        proj1 = Project("TEST_PROJECT1g")
        proj1.create()
        
        asset1 = Asset(proj1, "TEST_ASSET1")
        asset1.description = "Description for TEST_ASSET1 before change"
        
        asset2 = Asset(proj1, "TEST_ASSET2")
        asset2.description = "Description for TEST_ASSET2 before change"
        
        asset1.save()
        asset2.save()
        
        # now create the dialog
        dialog = version_creator.MainDialog_New()
        
        # check if it is already enabled
        self.assertTrue(
            dialog.shots_tab.isEnabled()
        )
        
        # push the edit pushButton
        QTest.mouseClick(
            dialog.asset_description_edit_pushButton,
            QtCore.Qt.LeftButton
        )
        
        # check if it becomes disabled
        self.assertFalse(
            dialog.shots_tab.isEnabled()
        )
        
        # push the edit pushButton again
        QTest.mouseClick(
            dialog.asset_description_edit_pushButton,
            QtCore.Qt.LeftButton
        )
        
        # check if it becomes enabled again
        self.assertTrue(
            dialog.shots_tab.isEnabled()
        )
    
    def test_asset_description_edit_pushButton_disables_new_version_groupBox(self):
        """testing if pushing the edit pushButton for the first time disables
        the new_version_groupBox and enables it when pushed for a second
        time
        """
        
        proj1 = Project("TEST_PROJECT1g")
        proj1.create()
        
        asset1 = Asset(proj1, "TEST_ASSET1")
        asset1.description = "Description for TEST_ASSET1 before change"
        
        asset2 = Asset(proj1, "TEST_ASSET2")
        asset2.description = "Description for TEST_ASSET2 before change"
        
        asset1.save()
        asset2.save()
        
        # now create the dialog
        dialog = version_creator.MainDialog_New()
        
        # check if it is already enabled
        self.assertTrue(
            dialog.new_version_groupBox.isEnabled()
        )
        
        # push the edit pushButton
        QTest.mouseClick(
            dialog.asset_description_edit_pushButton,
            QtCore.Qt.LeftButton
        )
        
        # check if it becomes disabled
        self.assertFalse(
            dialog.new_version_groupBox.isEnabled()
        )
        
        # push the edit pushButton again
        QTest.mouseClick(
            dialog.asset_description_edit_pushButton,
            QtCore.Qt.LeftButton
        )
        
        # check if it becomes enabled again
        self.assertTrue(
            dialog.new_version_groupBox.isEnabled()
        )
    
    def test_asset_description_edit_pushButton_updates_asset_description(self):
        """testing if the asset description update will be persistent when the
        edit button is checked and done is selected afterwards
        """
        
        proj1 = Project("TEST_PROJECT1h")
        proj1.create()
        
        asset1 = Asset(proj1, "TEST_ASSET1")
        asset1.description = "Description for TEST_ASSET1 before change"
        
        asset2 = Asset(proj1, "TEST_ASSET2")
        asset2.description = "Description for TEST_ASSET2 before change"
        
        asset1.save()
        asset2.save()
        
        # now create the dialog
        dialog = version_creator.MainDialog_New()
#        dialog.show()
#        self.app.exec_()
#        self.app.connect(
#            self.app,
#            QtCore.SIGNAL("lastWindowClosed()"),
#            self.app,
#            QtCore.SLOT("quit()")
#        )
        
        # push the edit pushButton
        QTest.mouseClick(
            dialog.asset_description_edit_pushButton,
            QtCore.Qt.LeftButton
        )
        
        test_value = "Description for TEST_ASSET1 after change"
        
        # change the description of asset1
        dialog.asset_description_textEdit.setText(test_value)
        
        # hit done pushButton
        QTest.mouseClick(
            dialog.asset_description_edit_pushButton,
            QtCore.Qt.LeftButton
        )
        
        # change the asset to the next one
        list_item = dialog.assets_listWidget.item(1)
        list_item.setSelected(True)
        dialog.assets_listWidget.setCurrentItem(list_item)
        
        # check if the description is changed to the asset2's description
        self.assertEqual(
            asset2.description,
            dialog.asset_description_textEdit.toPlainText()
        )
        
        # change the asset back to the first one
        list_item = dialog.assets_listWidget.item(0)
        list_item.setSelected(True)
        dialog.assets_listWidget.setCurrentItem(list_item)
        
        # check if the description has updated to the asset1's edited
        # description
        self.assertEqual(
            test_value,
            dialog.asset_description_textEdit.toPlainText()
        )
    
    def test_asset_description_edit_pushButton_disables_previous_versions_groupBox(self):
        """testing if pushing the edit pushButton for the first time disables
        the previous_versions_groupBox and enables it when pushed for a second
        time
        """

        proj1 = Project("TEST_PROJECT1h")
        proj1.create()
        
        asset1 = Asset(proj1, "TEST_ASSET1")
        asset1.description = "Description for TEST_ASSET1 before change"
        
        asset2 = Asset(proj1, "TEST_ASSET2")
        asset2.description = "Description for TEST_ASSET2 before change"
        
        asset1.save()
        asset2.save()
        
        # now create the dialog
        dialog = version_creator.MainDialog_New()

        # check if it is already enabled
        self.assertTrue(
            dialog.previous_versions_groupBox.isEnabled()
        )
        
        # push the edit pushButton
        QTest.mouseClick(
            dialog.asset_description_edit_pushButton,
            QtCore.Qt.LeftButton
        )
        
        # check if it becomes disabled
        self.assertFalse(
            dialog.previous_versions_groupBox.isEnabled()
        )
        
        # push the edit pushButton again
        QTest.mouseClick(
            dialog.asset_description_edit_pushButton,
            QtCore.Qt.LeftButton
        )

        # check if it becomes enabled again
        self.assertTrue(
            dialog.previous_versions_groupBox.isEnabled()
        )

    def test_shot_description_edit_pushButton_is_disabled_when_there_is_no_shot(self):
        """testing if the shot_description_edit_pushButton is disabled when
        there is no shot
        """

        proj = Project("TEST_PROJECT")
        proj.create()

        seq1 = Sequence(proj, "TEST_SEQ")

        # create the dialog
        dialog = version_creator.MainDialog_New()
        #        dialog.show()
        #        self.app.exec_()
        #        self.app.connect(
        #            self.app,
        #            QtCore.SIGNAL("lastWindowClosed()"),
        #            self.app,
        #            QtCore.SLOT("quit()")
        #        )

        # switch to the Shots tab
        dialog.tabWidget.setCurrentIndex(1)

        # check if it is unchecked by default
        self.assertFalse(dialog.shot_description_edit_pushButton.isEnabled())
    
    def test_shot_description_edit_pushButton_is_checked_when_there_is_a_shot(self):
        """testing if the edit button changes to done   
        """
        proj = Project("TEST_PROJECT")
        proj.create()

        seq1 = Sequence(proj, "TEST_SEQ1")

        shot = Shot(seq1, 1)
        shot.save()

        # create the dialog
        dialog = version_creator.MainDialog_New()
        #        dialog.show()
        #        self.app.exec_()
        #        self.app.connect(
        #            self.app,
        #            QtCore.SIGNAL("lastWindowClosed()"),
        #            self.app,
        #            QtCore.SLOT("quit()")
        #        )

        # set to shots tab
        dialog.tabWidget.setCurrentIndex(1)

        # check if it is unchecked by default
        self.assertFalse(dialog.shot_description_edit_pushButton.isChecked())

        # check if the shot_description_edit button text is edit
        self.assertEqual(
            dialog.shot_description_edit_pushButton.text(),
            "Edit"
        )

        # check if the dialog.shot_description_textEdit is read only
        self.assertTrue(dialog.shot_description_textEdit.isReadOnly())

        # click in the edit button
        QTest.mouseClick(
            dialog.shot_description_edit_pushButton,
            QtCore.Qt.LeftButton
        )

        # check check state
        self.assertTrue(dialog.shot_description_edit_pushButton.isChecked())

        # check if the text changed to Done
        self.assertEqual(
            dialog.shot_description_edit_pushButton.text(),
            "Done"
        )

        # check if the shot_description_textEdit becomes writable
        self.assertFalse(dialog.shot_description_textEdit.isReadOnly())

        # re click it
        # click in the edit button
        QTest.mouseClick(
            dialog.shot_description_edit_pushButton,
            QtCore.Qt.LeftButton
        )

        # check the checked state
        self.assertFalse(dialog.shot_description_edit_pushButton.isChecked())

        # check the text
        self.assertEqual(
            dialog.shot_description_edit_pushButton.text(),
            "Edit"
        )
    
    def test_shot_description_edit_pushButton_enables_shot_description_textEdit(self):
        """testing if pushing the edit pushButton for the first time enables
        the shot_description_textEdit and disables it when pushed for a second
        time
        """

        proj1 = Project("TEST_PROJECT1c")
        proj1.create()

        seq1 = Sequence(proj1, "TEST_SEQ1")

        shot1 = Shot(seq1, 1)
        shot2 = Shot(seq1, 2)
        shot3 = Shot(seq1, 3)

        shot1.save()
        shot2.save()
        shot3.save()

        # now create the dialog
        dialog = version_creator.MainDialog_New()

        # set the tab to Shots
        dialog.tabWidget.setCurrentIndex(1)

        # check if the description textEdit field is read-only
        self.assertTrue(
            dialog.shot_description_textEdit.isReadOnly()
        )

        # push the edit pushButton
        QTest.mouseClick(
            dialog.shot_description_edit_pushButton,
            QtCore.Qt.LeftButton
        )

        # check if the description textEdit field become writable
        self.assertFalse(
            dialog.shot_description_textEdit.isReadOnly()
        )

        # hit done pushButton
        QTest.mouseClick(
            dialog.shot_description_edit_pushButton,
            QtCore.Qt.LeftButton
        )

        self.assertTrue(
            dialog.shot_description_textEdit.isReadOnly()
        )
    
    def test_shot_description_edit_pushButton_disables_shots_listWidget(self):
        """testing if pushing the edit pushButton for the first time disables
        the shots_listWidget and enables it when pushed for a second time
        """
        
        proj1 = Project("TEST_PROJECT1d")
        proj1.create()
        
        seq1 = Sequence(proj1, "TEST_SEQ1")
        
        shot1 = Shot(seq1, 1)
        shot2 = Shot(seq1, 2)
        shot3 = Shot(seq1, 3)
        
        shot1.save()
        shot2.save()
        shot3.save()
        
        # now create the dialog
        dialog = version_creator.MainDialog_New()
        
        # set the tab to Shots
        dialog.tabWidget.setCurrentIndex(1)
        
        # check if it is already enabled
        self.assertTrue(
            dialog.shots_listWidget.isEnabled()
        )
        
        # push the edit pushButton
        QTest.mouseClick(
            dialog.shot_description_edit_pushButton,
            QtCore.Qt.LeftButton
        )
        
        # check if the shots_listWidget becomes disabled
        self.assertFalse(
            dialog.shots_listWidget.isEnabled()
        )
        
        # hit done pushButton
        QTest.mouseClick(
            dialog.shot_description_edit_pushButton,
            QtCore.Qt.LeftButton
        )
        
        # check if it becomes enabled again
        self.assertTrue(
            dialog.shots_listWidget.isEnabled()
        )
        
        dialog.close()
        del dialog
    
    def test_shot_description_edit_pushButton_disables_projects_comboBox(self):
        """testing if pushing the edit pushButton for the first time disables
        the projects_comboBox and enables it when pushed for a second time
        """
        
        proj1 = Project("TEST_PROJECT1d")
        proj1.create()
        
        seq1 = Sequence(proj1, "TEST_SEQ1")
        
        shot1 = Shot(seq1, 1)
        shot2 = Shot(seq1, 2)
        shot3 = Shot(seq1, 3)
        
        shot1.save()
        shot2.save()
        shot3.save()
        
        # now create the dialog
        dialog = version_creator.MainDialog_New()
        
        # set the tab to Shots
        dialog.tabWidget.setCurrentIndex(1)
        
        # check if it is already enabled
        self.assertTrue(
            dialog.projects_comboBox.isEnabled()
        )
        
        # push the edit pushButton
        QTest.mouseClick(
            dialog.shot_description_edit_pushButton,
            QtCore.Qt.LeftButton
        )
        
        # check if the projects_comboBox becomes disabled
        self.assertFalse(
            dialog.projects_comboBox.isEnabled()
        )
        
        # hit done pushButton
        QTest.mouseClick(
            dialog.shot_description_edit_pushButton,
            QtCore.Qt.LeftButton
        )
        
        # check if it becomes enabled again
        self.assertTrue(
            dialog.projects_comboBox.isEnabled()
        )
        
        dialog.close()
        del dialog
    
    def test_shot_description_edit_pushButton_disables_sequences_comboBox(self):
        """testing if pushing the edit pushButton for the first time disables
        the sequences_comboBox and enables it when pushed for a second time
        """
        
        proj1 = Project("TEST_PROJECT1d")
        proj1.create()
        
        seq1 = Sequence(proj1, "TEST_SEQ1")
        
        shot1 = Shot(seq1, 1)
        shot2 = Shot(seq1, 2)
        shot3 = Shot(seq1, 3)
        
        shot1.save()
        shot2.save()
        shot3.save()
        
        # now create the dialog
        dialog = version_creator.MainDialog_New()
        
        # set the tab to Shots
        dialog.tabWidget.setCurrentIndex(1)
        
        # check if it is already enabled
        self.assertTrue(
            dialog.sequences_comboBox.isEnabled()
        )
        
        # push the edit pushButton
        QTest.mouseClick(
            dialog.shot_description_edit_pushButton,
            QtCore.Qt.LeftButton
        )
        
        # check if the sequences_comboBox becomes disabled
        self.assertFalse(
            dialog.sequences_comboBox.isEnabled()
        )
        
        # hit done pushButton
        QTest.mouseClick(
            dialog.shot_description_edit_pushButton,
            QtCore.Qt.LeftButton
        )
        
        # check if it becomes enabled again
        self.assertTrue(
            dialog.sequences_comboBox.isEnabled()
        )
        
        dialog.close()
        del dialog
    
    def test_shot_description_edit_pushButton_disables_create_shot_pushButton(self):
        """testing if pushing the edit pushButton for the first time disables
        the create_shot_pushButton and enables it when pushed for a second time
        """
        
        proj1 = Project("TEST_PROJECT1f")
        proj1.create()
        
        seq1 = Sequence(proj1, "TEST_SEQ1")
        
        shot1 = Shot(seq1, 1)
        shot2 = Shot(seq1, 2)
        shot3 = Shot(seq1, 3)
        
        shot1.save()
        shot2.save()
        shot3.save()
        
        # now create the dialog
        dialog = version_creator.MainDialog_New()
        
        # set the tab to Shots
        dialog.tabWidget.setCurrentIndex(1)
        
        # check if it is already enabled
        self.assertTrue(
            dialog.create_shot_pushButton.isEnabled()
        )
        
        # push the edit pushButton
        QTest.mouseClick(
            dialog.shot_description_edit_pushButton,
            QtCore.Qt.LeftButton
        )
        
        # check if the create_shot_pushButton becomes disabled
        self.assertFalse(
            dialog.create_shot_pushButton.isEnabled()
        )
        
        # push the edit pushButton again
        QTest.mouseClick(
            dialog.shot_description_edit_pushButton,
            QtCore.Qt.LeftButton
        )
        
        # check if the create_shot_pushButton becomes enabled again
        self.assertTrue(
            dialog.create_shot_pushButton.isEnabled()
        )
    
    def test_shot_description_edit_pushButton_disables_assets_tab(self):
        """testing if pushing the edit pushButton for the first time disables
        the assets_tab and enables it when pushed for a second time
        """
        
        proj1 = Project("TEST_PROJECT1g")
        proj1.create()
        
        asset1 = Asset(proj1, "TEST_ASSET1")
        asset1.description = "Description for TEST_ASSET1 before change"
        
        asset2 = Asset(proj1, "TEST_ASSET2")
        asset2.description = "Description for TEST_ASSET2 before change"
        
        asset1.save()
        asset2.save()
        
        seq1 = Sequence(proj1, "TEST_SEQ1")
        
        shot1 = Shot(seq1, 1)
        shot2 = Shot(seq1, 2)
        shot3 = Shot(seq1, 3)
        shot4 = Shot(seq1, 4)
        shot5 = Shot(seq1, 5)
        
        shot1.save()
        shot2.save()
        shot3.save()
        shot4.save()
        shot5.save()
        
        # now create the dialog
        dialog = version_creator.MainDialog_New()
        
        # switch the tab to Shots
        dialog.tabWidget.setCurrentIndex(1)
        
        # check if it is already enabled
        self.assertTrue(
            dialog.assets_tab.isEnabled()
        )
        
        # push the edit pushButton
        QTest.mouseClick(
            dialog.shot_description_edit_pushButton,
            QtCore.Qt.LeftButton
        )
        
        # check if the create_asset_pushButton becomes disabled
        self.assertFalse(
            dialog.assets_tab.isEnabled()
        )
        
        # push the edit pushButton again
        QTest.mouseClick(
            dialog.shot_description_edit_pushButton,
            QtCore.Qt.LeftButton
        )
        
        # check if the create_asset_pushButton becomes enabled again
        self.assertTrue(
            dialog.assets_tab.isEnabled()
        )
    
    def test_shot_description_textEdit_updated_with_the_selected_shot(self):
        """testing if the shot_description_textEdit is updated with the
        selected shot
        """
        
        proj1 = Project("TEST_PROJECT1")
        proj1.create()
        
        seq1 = Sequence(proj1, "TEST_SEQUENCE")
        
        shot1 = Shot(seq1, 1)
        shot2 = Shot(seq1, 2)
        shot3 = Shot(seq1, 3)
        shot4 = Shot(seq1, 4)
        
        shot1.description = "SH001 description"
        shot2.description = "SH002 description"
        shot3.description = "SH003 description"
        shot4.description = "SH004 description"
        
        shot1.save()
        shot2.save()
        shot3.save()
        shot4.save()
        
        dialog = version_creator.MainDialog_New()
        
        # set the shots tab
        dialog.tabWidget.setCurrentIndex(1)
        
        # select first sequence
        dialog.sequences_comboBox.setCurrentIndex(0)
        
        # select first shot
        item = dialog.shots_listWidget.item(0)
        dialog.shots_listWidget.setCurrentItem(item)
        
        # check if the shot_description equals to the shot1.description
        text = dialog.shot_description_textEdit.toPlainText()
        self.assertEqual(text, shot1.description)
        
        # change to the second shot
        item = dialog.shots_listWidget.item(1)
        dialog.shots_listWidget.setCurrentItem(item)
        
        # check if the shot_description equals to the shot2.description
        text = dialog.shot_description_textEdit.toPlainText()
        self.assertEqual(text, shot2.description)
    
    def test_shot_description_edit_pushButton_updates_shot_description(self):
        """testing if the shot description update will be persistent when the
        edit button is checked and done is selected afterwards
        """
        
        proj1 = Project("TEST_PROJECT1h")
        proj1.create()
        
        seq1 = Sequence(proj1, "TEST_SEQ1")
        
        shot1 = Shot(seq1, 1)
        shot2 = Shot(seq1, 2)
        shot3 = Shot(seq1, 3)
        shot4 = Shot(seq1, 4)
        
        shot1.description = "Description for SH001 before change"
        shot2.description = "Description for SH002 before change"
        shot3.description = "Description for SH003 before change"
        shot4.description = "Description for SH004 before change"
        
        shot1.save()
        shot2.save()
        shot3.save()
        shot4.save()
        
        # now create the dialog
        dialog = version_creator.MainDialog_New()
        
        # set the tab to Shots
        dialog.tabWidget.setCurrentIndex(1)
        
#        dialog.show()
#        self.app.exec_()
#        self.app.connect(
#            self.app,
#            QtCore.SIGNAL("lastWindowClosed()"),
#            self.app,
#            QtCore.SLOT("quit()")
#        )
        
        # push the edit pushButton
        QTest.mouseClick(
            dialog.shot_description_edit_pushButton,
            QtCore.Qt.LeftButton
        )
        
        test_value = "Description for SH001 after change"
        
        # change the description of asset1
        dialog.shot_description_textEdit.setText(test_value)
        
        # hit done pushButton
        QTest.mouseClick(
            dialog.shot_description_edit_pushButton,
            QtCore.Qt.LeftButton
        )
        
        # change the shot to the next one
        list_item = dialog.shots_listWidget.item(1)
        list_item.setSelected(True)
        dialog.shots_listWidget.setCurrentItem(list_item)
        
        # check if the description is changed to the shot2's description
        self.assertEqual(
            shot2.description,
            dialog.shot_description_textEdit.toPlainText()
        )
        
        # change the shot back to the first one
        list_item = dialog.shots_listWidget.item(0)
        list_item.setSelected(True)
        dialog.shots_listWidget.setCurrentItem(list_item)
        
        # check if the description has updated to the shot1's edited
        # description
        self.assertEqual(
            test_value,
            dialog.shot_description_textEdit.toPlainText()
        )
    
    def test_shot_description_edit_pushButton_disables_new_version_groupBox(self):
        """testing if pushing the edit pushButton for the first time disables
        the new_version_groupBox and enables it when pushed for a second
        time
        """

        proj1 = Project("TEST_PROJECT1h")
        proj1.create()

        seq1 = Sequence(proj1, "TEST_SEQ1")

        shot1 = Shot(seq1, 1)
        shot2 = Shot(seq1, 2)
        shot3 = Shot(seq1, 3)
        shot4 = Shot(seq1, 4)

        shot1.description = "Description for SH001 before change"
        shot2.description = "Description for SH002 before change"
        shot3.description = "Description for SH003 before change"
        shot4.description = "Description for SH004 before change"

        shot1.save()
        shot2.save()
        shot3.save()
        shot4.save()

        # now create the dialog
        dialog = version_creator.MainDialog_New()

        # set to the shots tab
        dialog.tabWidget.setCurrentIndex(1)

        # check if it is already enabled
        self.assertTrue(
            dialog.new_version_groupBox.isEnabled()
        )

        # push the edit pushButton
        QTest.mouseClick(
            dialog.shot_description_edit_pushButton,
            QtCore.Qt.LeftButton
        )

        # check if it becomes disabled
        self.assertFalse(
            dialog.new_version_groupBox.isEnabled()
        )

        # push the edit pushButton again
        QTest.mouseClick(
            dialog.shot_description_edit_pushButton,
            QtCore.Qt.LeftButton
        )

        # check if it becomes enabled again
        self.assertTrue(
            dialog.new_version_groupBox.isEnabled()
        )

    def test_shot_description_edit_pushButton_disables_previous_versions_groupBox(self):
        """testing if pushing the edit pushButton for the first time disables
        the previous_versions_groupBox and enables it when pushed for a second
        time
        """

        proj1 = Project("TEST_PROJECT1h")
        proj1.create()

        seq1 = Sequence(proj1, "TEST_SEQ1")

        shot1 = Shot(seq1, 1)
        shot2 = Shot(seq1, 2)
        shot3 = Shot(seq1, 3)
        shot4 = Shot(seq1, 4)

        shot1.description = "Description for SH001 before change"
        shot2.description = "Description for SH002 before change"
        shot3.description = "Description for SH003 before change"
        shot4.description = "Description for SH004 before change"

        shot1.save()
        shot2.save()
        shot3.save()
        shot4.save()

        # now create the dialog
        dialog = version_creator.MainDialog_New()

        # set to the shots tab
        dialog.tabWidget.setCurrentIndex(1)

        # check if it is already enabled
        self.assertTrue(
            dialog.previous_versions_groupBox.isEnabled()
        )
        
        # push the edit pushButton
        QTest.mouseClick(
            dialog.shot_description_edit_pushButton,
            QtCore.Qt.LeftButton
        )
        
        # check if it becomes disabled
        self.assertFalse(
            dialog.previous_versions_groupBox.isEnabled()
        )
        
        # push the edit pushButton again
        QTest.mouseClick(
            dialog.shot_description_edit_pushButton,
            QtCore.Qt.LeftButton
        )

        # check if it becomes enabled again
        self.assertTrue(
            dialog.previous_versions_groupBox.isEnabled()
        )
    
    def test_takes_comboBox_lists_all_the_takes_of_current_asset_versions(self):
        """testing if the takes_comboBox lists all the takes of the current
        asset and current version_type
        """
        # TODO: test this when there is no asset in the project

        proj1 = Project("TEST_PROJECT1i")
        proj1.create()

        asset1 = Asset(proj1, "TEST_ASSET1")
        asset1.save()

        asset2 = Asset(proj1, "TEST_ASSET2")
        asset2.save()

        # new user
        user1 = User(name="User1", initials="u1",
                     email="user1@test.com")

        # create a couple of versions
        asset_vtypes =\
        proj1.query(VersionType).filter_by(type_for="Asset").all()

        vers1 = Version(asset1, asset1.name, asset_vtypes[0], user1,
                        take_name="Main")
        vers1.save()

        vers2 = Version(asset1, asset1.name, asset_vtypes[0], user1,
                        take_name="Main")
        vers2.save()

        vers3 = Version(asset1, asset1.name, asset_vtypes[0], user1,
                        take_name="Test")
        vers3.save()

        vers4 = Version(asset1, asset1.name, asset_vtypes[0], user1,
                        take_name="Test")
        vers4.save()

        # a couple of versions for asset2 to see if they are going to be mixed
        vers5 = Version(asset2, asset2.name, asset_vtypes[1], user1,
                        take_name="Test2")
        vers5.save()

        vers6 = Version(asset2, asset2.name, asset_vtypes[2], user1,
                        take_name="Test3")
        vers6.save()

        dialog = version_creator.MainDialog_New()
        #        dialog.show()
        #        self.app.exec_()
        #        self.app.connect(
        #            self.app,
        #            QtCore.SIGNAL("lastWindowClosed()"),
        #            self.app,
        #            QtCore.SLOT("quit()")
        #        )

        # check if Main and Test are in the takes_comboBox
        ui_take_names = []
        for i in range(dialog.takes_comboBox.count()):
            dialog.takes_comboBox.setCurrentIndex(i)
            ui_take_names.append(
                dialog.takes_comboBox.currentText()
            )

        self.assertItemsEqual(
            ["Main", "Test"],
                            ui_take_names
        )

    def test_takes_comboBox_lists_all_the_takes_of_current_shot_versions(self):
        """testing if the takes_comboBox lists all the takes of the current
        shot and current version_type
        """
        # TODO: test this when there is no shot in the project

        proj1 = Project("TEST_PROJECT1i")
        proj1.create()

        seq1 = Sequence(proj1, "TEST_SEQ1")

        asset1 = Asset(proj1, "TEST_ASSET1")
        asset1.save()

        asset2 = Asset(proj1, "TEST_ASSET2")
        asset2.save()

        shot1 = Shot(seq1, 1)
        shot2 = Shot(seq1, 2)
        shot3 = Shot(seq1, 3)

        shot1.save()
        shot2.save()
        shot3.save()

        # new user
        user1 = User(name="User1", initials="u1",
                     email="user1@test.com")

        # create a couple of versions
        asset_vtypes =\
        proj1.query(VersionType).filter_by(type_for="Asset").all()

        shot_vtypes =\
        proj1.query(VersionType).filter_by(type_for="Shot").all()

        vers1 = Version(asset1, asset1.name, asset_vtypes[0], user1,
                        take_name="Main")
        vers1.save()

        vers2 = Version(asset1, asset1.name, asset_vtypes[0], user1,
                        take_name="Main")
        vers2.save()

        vers3 = Version(asset1, asset1.name, asset_vtypes[0], user1,
                        take_name="Test")
        vers3.save()

        vers4 = Version(asset1, asset1.name, asset_vtypes[0], user1,
                        take_name="Test")
        vers4.save()

        # a couple of versions for asset2 to see if they are going to be mixed
        vers5 = Version(asset2, asset2.name, asset_vtypes[1], user1,
                        take_name="Test2")
        vers5.save()

        vers6 = Version(asset2, asset2.name, asset_vtypes[2], user1,
                        take_name="Test3")
        vers6.save()

        # versions for shots
        vers7 = Version(shot1, shot1.code, shot_vtypes[0], user1,
                        take_name="Main")
        vers7.save()

        vers8 = Version(shot1, shot1.code, shot_vtypes[0], user1,
                        take_name="Main")
        vers8.save()

        vers9 = Version(shot1, shot1.code, shot_vtypes[0], user1,
                        take_name="TestForShot")
        vers9.save()

        vers10 = Version(shot2, shot2.code, shot_vtypes[1], user1,
                         take_name="TestForShot2")
        vers10.save()

        vers11 = Version(shot3, shot2.code, shot_vtypes[2], user1,
                         take_name="TestForShot3")
        vers11.save()

        dialog = version_creator.MainDialog_New()
        #        dialog.show()
        #        self.app.exec_()
        #        self.app.connect(
        #            self.app,
        #            QtCore.SIGNAL("lastWindowClosed()"),
        #            self.app,
        #            QtCore.SLOT("quit()")
        #        )

        # set to the shot tab
        dialog.tabWidget.setCurrentIndex(1)

        # select shot1
        item = dialog.shots_listWidget.item(0)
        dialog.shots_listWidget.setCurrentItem(item)

        # check if Main and TestForShot are in the takes_comboBox
        ui_take_names = []
        for i in range(dialog.takes_comboBox.count()):
            dialog.takes_comboBox.setCurrentIndex(i)
            ui_take_names.append(
                dialog.takes_comboBox.currentText()
            )

        self.assertItemsEqual(
            ["Main", "TestForShot"],
                                   ui_take_names
        )

        # check if shot2 has correct takes
        item = dialog.shots_listWidget.item(1)
        dialog.shots_listWidget.setCurrentItem(item)

        # check if Main and TestForShot are in the takes_comboBox
        ui_take_names = []
        for i in range(dialog.takes_comboBox.count()):
            dialog.takes_comboBox.setCurrentIndex(i)
            ui_take_names.append(
                dialog.takes_comboBox.currentText()
            )

        self.assertItemsEqual(
            ["TestForShot2"],
                            ui_take_names
        )
    
    def test_takes_comboBox_lists_Main_by_default(self):
        """testing if the takes_comboBox lists "Main" by default
        """
        
        dialog = version_creator.MainDialog_New()
        self.assertEqual(
            conf.default_take_name,
            dialog.takes_comboBox.currentText()
        )
    
    def test_takes_comboBox_lists_Main_by_default_for_asset_with_no_versions(self):
        """testing if the takes_comboBox lists "Main" by default for an asset
        with no version
        """
        
        proj = Project("TEST_PROJECT1")
        proj.create()
        
        asset1 = Asset(proj, "TEST_ASSET")
        asset1.save()
        
        dialog = version_creator.MainDialog_New()
        self.assertEqual(
            conf.default_take_name,
            dialog.takes_comboBox.currentText()
        )
        
#        dialog.show()
#        self.app.exec_()
#        self.app.connect(
#            self.app,
#            QtCore.SIGNAL("lastWindowClosed()"),
#            self.app,
#            QtCore.SLOT("quit()")
#        )
    
    def test_takes_comboBox_lists_Main_by_default_for_new_asset_version_types(self):
        """testing if the takes_comboBox lists "Main" by default for an asset
        with a new version added to the version_types comboBox
        """
        
        proj = Project("TEST_PROJECT")
        proj.create()
        
        asset1 = Asset(proj, "TEST_ASSET")
        asset1.save()
        
        # create the dialog
        dialog = version_creator.MainDialog_New()
        
        # get all the asset version types for project
        asset_vtypes = proj.query(VersionType).\
            filter(VersionType.type_for=="Asset").all()
        
        type_name = asset_vtypes[0].name
        
        # add new version type by hand
        dialog.version_types_comboBox.addItem(type_name)
        dialog.version_types_comboBox.setCurrentIndex(
            dialog.version_types_comboBox.count() - 1
        )
        
        # now check if the takes_comboBox lists Main by default
        self.assertEqual(
            dialog.takes_comboBox.currentText(),
            conf.default_take_name
        )
    
    def test_version_types_comboBox_lists_all_the_types_of_the_current_asset_versions(self):
        """testing if the version_types_comboBox lists all the types of
        the current asset
        """

        proj1 = Project("TEST_PROJECT1j")
        proj1.create()

        asset1 = Asset(proj1, "TEST_ASSET1")
        asset1.save()

        asset2 = Asset(proj1, "TEST_ASSET2")
        asset2.save()

        # new user
        user1 = User(name="User1", initials="u1",
                     email="user1@test.com")

        # create a couple of versions
        asset_vtypes =\
        proj1.query(VersionType).filter_by(type_for="Asset").all()

        vers1 = Version(asset1, asset1.name, asset_vtypes[0], user1,
                        take_name="Main")
        vers1.save()

        vers2 = Version(asset1, asset1.name, asset_vtypes[0], user1,
                        take_name="Main")
        vers2.save()

        vers3 = Version(asset1, asset1.name, asset_vtypes[1], user1,
                        take_name="Test")
        vers3.save()

        vers4 = Version(asset1, asset1.name, asset_vtypes[2], user1,
                        take_name="Test")
        vers4.save()

        # a couple of versions for asset2 to see if they are going to be mixed
        vers5 = Version(asset2, asset2.name, asset_vtypes[3], user1,
                        take_name="Test2")
        vers5.save()

        vers6 = Version(asset2, asset2.name, asset_vtypes[4], user1,
                        take_name="Test3")
        vers6.save()

        dialog = version_creator.MainDialog_New()
        #        dialog.show()
        #        self.app.exec_()
        #        self.app.connect(
        #            self.app,
        #            QtCore.SIGNAL("lastWindowClosed()"),
        #            self.app,
        #            QtCore.SLOT("quit()")
        #        )

        # check if Main and Test are in the takes_comboBox
        ui_type_names = []
        for i in range(dialog.version_types_comboBox.count()):
            dialog.version_types_comboBox.setCurrentIndex(i)
            ui_type_names.append(
                dialog.version_types_comboBox.currentText()
            )

        self.assertItemsEqual(
            [asset_vtypes[0].name, asset_vtypes[1].name, asset_vtypes[2].name],
                                                                              ui_type_names
        )

    def test_previous_versions_tableWidget_is_updated_properly(self):
        """testing if the previous_versions_tableWidget is updated properly
        when the version_type is changed to a type with the same take_name
        """

        proj1 = Project("TEST_PROJECT1k")
        proj1.create()

        asset1 = Asset(proj1, "TEST_ASSET1")
        asset1.save()

        asset2 = Asset(proj1, "TEST_ASSET2")
        asset2.save()

        # new user
        user1 = User(name="User1", initials="u1",
                     email="user1@test.com")

        # create a couple of versions
        asset_vtypes =\
        proj1.query(VersionType).filter_by(type_for="Asset").all()

        vers1 = Version(
            asset1,
            asset1.name,
            asset_vtypes[0],
            user1,
            take_name="Main",
            note="test note"
        )
        vers1.save()

        vers2 = Version(
            asset1,
            asset1.name,
            asset_vtypes[1],
            user1,
            take_name="Main",
            note="test note 2"
        )
        vers2.save()

        dialog = version_creator.MainDialog_New()
        #        dialog.show()
        #        self.app.exec_()
        #        self.app.connect(
        #            self.app,
        #            QtCore.SIGNAL("lastWindowClosed()"),
        #            self.app,
        #            QtCore.SLOT("quit()")
        #        )

        # select the first asset
        list_item = dialog.assets_listWidget.item(0)
        dialog.assets_listWidget.setCurrentItem(list_item)

        # select the first type
        dialog.version_types_comboBox.setCurrentIndex(0)

        # select the first take
        dialog.takes_comboBox.setCurrentIndex(0)

        # which should list vers1

        # the row count should be 1
        self.assertEqual(
            dialog.previous_versions_tableWidget.rowCount(),
            1
        )

        # now check if the previous versions tableWidget has the info
        self.assertEqual(
            int(dialog.previous_versions_tableWidget.item(0, 0).text()),
            vers1.version_number
        )

        self.assertEqual(
            dialog.previous_versions_tableWidget.item(0, 1).text(),
            vers1.created_by.name
        )

        self.assertEqual(
            dialog.previous_versions_tableWidget.item(0, 2).text(),
            vers1.note
        )

        self.assertEqual(
            dialog.previous_versions_tableWidget.item(0, 4).text(),
            vers1.fullpath
        )

    def test_previous_versions_tableWidget_is_filled_with_proper_info(self):
        """testing if the previous_versions_tableWidget is filled with proper
        information
        """

        proj1 = Project("TEST_PROJECT1l")
        proj1.create()

        asset1 = Asset(proj1, "TEST_ASSET1")
        asset1.save()

        asset2 = Asset(proj1, "TEST_ASSET2")
        asset2.save()

        # new user
        user1 = User(name="User1", initials="u1",
                     email="user1@test.com")

        # create a couple of versions
        asset_vtypes =\
            proj1.query(VersionType).filter_by(type_for="Asset").all()
        
        vers1 = Version(
            asset1,
            asset1.name,
            asset_vtypes[0],
            user1,
            take_name="Main",
            note="test note"
        )
        vers1.save()
        
        vers2 = Version(
            asset1,
            asset1.name,
            asset_vtypes[0],
            user1,
            take_name="Main",
            note="test note 2"
        )
        vers2.save()

        vers3 = Version(
            asset1,
            asset1.name,
            asset_vtypes[1],
            user1,
            take_name="Main",
            note="test note 3"
        )
        vers3.save()

        vers4 = Version(
            asset1,
            asset1.name,
            asset_vtypes[2],
            user1,
            take_name="Main",
            note="test note 4"
        )
        vers4.save()

        vers4a = Version(
            asset1,
            asset1.name,
            asset_vtypes[2],
            user1,
            take_name="NewTake",
            note="test note 4a"
        )
        vers4a.save()

        # a couple of versions for asset2 to see if they are going to be mixed
        vers5 = Version(
            asset2,
            asset2.name,
            asset_vtypes[3],
            user1,
            take_name="Test2",
            note="test note 5"
        )
        vers5.save()

        vers6 = Version(
            asset2,
            asset2.name,
            asset_vtypes[4],
            user1,
            take_name="Test3",
            note="test note 6"
        )
        vers6.save()

        dialog = version_creator.MainDialog_New()
        #        dialog.show()
        #        self.app.exec_()
        #        self.app.connect(
        #            self.app,
        #            QtCore.SIGNAL("lastWindowClosed()"),
        #            self.app,
        #            QtCore.SLOT("quit()")
        #        )

        # select the first asset
        list_item = dialog.assets_listWidget.item(0)
        dialog.assets_listWidget.setCurrentItem(list_item)

        # select the first type
        dialog.version_types_comboBox.setCurrentIndex(0)

        # select the first take
        dialog.takes_comboBox.setCurrentIndex(0)

        # which should list vers1 and vers2

        # the row count should be 2
        self.assertEqual(
            dialog.previous_versions_tableWidget.rowCount(),
            2
        )

        # now check if the previous versions tableWidget has the info

        versions = [vers1, vers2]
        for i in range(2):

            self.assertEqual(
                int(dialog.previous_versions_tableWidget.item(i,0).text()),
                versions[i].version_number
            )

            self.assertEqual(
                dialog.previous_versions_tableWidget.item(i,1).text(),
                versions[i].created_by.name
            )

            self.assertEqual(
                dialog.previous_versions_tableWidget.item(i,2).text(),
                versions[i].note
            )

            # TODO: add test for file size column

            self.assertEqual(
                dialog.previous_versions_tableWidget.item(i,4).text(),
                versions[i].fullpath
            )

#    def test_speed_test(self):
#        """test the speed of the interface
#        """
#        
#        import logging
#        logger = logging.getLogger("oyProjectManager")
#        logger.setLevel(logging.FATAL)
#        
#        projects = []
#        for i in range(10):
#            # create projects
#            proj = Project("TEST_PROJ%03d" % i)
#            proj.create()
#            
##            data = []
#            
#            user = User("Test User 1", "tu1")
#            
#            for j in range(10):
#                # create assets
#                asset = Asset(proj, "TEST_ASSET%03d" % j)
##                asset.save()
#                proj.session.add(asset)
#                
#                asset_types = \
#                    proj.query(VersionType).filter_by(type_for="Asset").all()
#                
##                data.append(asset)
#                
#                for asset_type in asset_types:
#                    
#                    take_list = ["Take1", "Take2", "Take3", "Take4"]
#                    
#                    for take in take_list:
#                        
#                        for k in range(10):
#                            # create versions
#                            vers = Version(asset, asset.name, asset_type, user,take)
##                            vers.save()
#                            proj.session.add(vers)
#                            
##                            data.append(vers)
#            
##            proj.session.add_all(data)
#            proj.session.commit()
#        
#        dialog = version_creator.MainDialog_New()
#        dialog.show()
#        self.app.exec_()
#        self.app.connect(
#            self.app,
#            QtCore.SIGNAL("lastWindowClosed()"),
#            self.app,
#            QtCore.SLOT("quit()")
#        )

    def test_tab_changed_updates_types_comboBox(self):
        """testing if the the types_comboBox is updated according to the
        selected tab
        """

        # project
        proj1 = Project("TEST_PROJECT")
        proj1.create()

        # sequence
        seq1 = Sequence(proj1, "TEST_SEQ1")
        seq2 = Sequence(proj1, "TEST_SEQ2")
        seq3 = Sequence(proj1, "TEST_SEQ3")
        seq4 = Sequence(proj1, "TEST_SEQ4")

        # user
        user1 = User("Test User", "tu")

        # assets
        asset1 = Asset(proj1, "TEST_ASSET1")
        asset2 = Asset(proj1, "TEST_ASSET2")
        asset1.save()
        asset2.save()

        # shots
        shot1 = Shot(seq1, 1)
        shot1.save()
        shot2 = Shot(seq1, 2)
        shot2.save()
        shot3 = Shot(seq1, 3)
        shot3.save()

        asset_vtypes = proj1.query(VersionType).\
        filter_by(type_for="Asset").all()

        shot_vtypes = proj1.query(VersionType).\
        filter_by(type_for="Shot").all()

        # versions
        vers1 = Version(asset1, asset1.code, asset_vtypes[0], user1)
        vers1.save()
        vers2 = Version(asset2, asset2.code, asset_vtypes[1], user1)
        vers2.save()
        vers3 = Version(shot1, shot1.code, shot_vtypes[0], user1)
        vers3.save()
        vers4 = Version(shot2, shot2.code, shot_vtypes[1], user1)
        vers4.save()

        dialog = version_creator.MainDialog_New()
        #        dialog.show()
        #        self.app.exec_()
        #        self.app.connect(
        #            self.app,
        #            QtCore.SIGNAL("lastWindowClosed()"),
        #            self.app,
        #            QtCore.SLOT("quit()")
        #        )

        # set the tab to Asset
        dialog.tabWidget.setCurrentIndex(0)

        # check if the type comboBox lists the asset type of the first asset
        self.assertEqual(
            dialog.version_types_comboBox.currentText(),
            asset_vtypes[0].name
        )

        # set the tab to Shots
        dialog.tabWidget.setCurrentIndex(1)

        # check if the type comboBox lists the asset type of the first shot
        self.assertEqual(
            dialog.version_types_comboBox.currentText(),
            shot_vtypes[0].name
        )

    def test_sequence_comboBox_changed_fills_shots_listWidget(self):
        """testing if the shots_listWidget is filled with proper shot codes
        when the sequences_comboBox is changed
        """

        proj1 = Project("TEST_PROJECT1")
        proj2 = Project("TEST_PROJECT2")

        proj1.create()
        proj2.create()

        seq1 = Sequence(proj1, "TEST_SEQ1")
        seq2 = Sequence(proj1, "TEST_SEQ2")

        # for seq1
        shot1_1 = Shot(seq1, 1)
        shot1_2 = Shot(seq1, 2)
        shot1_3 = Shot(seq1, "1A")
        shot1_4 = Shot(seq1, "2A")
        shot1_5 = Shot(seq1, "3")

        shot1_1.save()
        shot1_2.save()
        shot1_3.save()
        shot1_4.save()
        shot1_5.save()

        # for seq2
        shot2_1 = Shot(seq2, 1)
        shot2_2 = Shot(seq2, 2)
        shot2_3 = Shot(seq2, 3)
        shot2_4 = Shot(seq2, 4)
        shot2_5 = Shot(seq2, 5)

        shot2_1.save()
        shot2_2.save()
        shot2_3.save()
        shot2_4.save()
        shot2_5.save()

        # create the dialog
        dialog = version_creator.MainDialog_New()
        #        dialog.show()
        #        self.app.exec_()
        #        self.app.connect(
        #            self.app,
        #            QtCore.SIGNAL("lastWindowClosed()"),
        #            self.app,
        #            QtCore.SLOT("quit()")
        #        )

        # change the tabWidget to Shots
        dialog.tabWidget.setCurrentIndex(1)

        # set the sequences_comboBox to index 0
        dialog.sequences_comboBox.setCurrentIndex(0)

        # check if the shots_listWidget has the correct items
        listWidget = dialog.shots_listWidget
        item_texts = [listWidget.item(i).text() for i in range(listWidget.count())]

        self.assertItemsEqual(
            item_texts,
            ["SH001", "SH002", "SH001A", "SH002A", "SH003"]
        )

        # change the sequence to sequence 2
        dialog.sequences_comboBox.setCurrentIndex(1)

        # check if the shots_listWidget has the correct items
        item_texts = [listWidget.item(i).text() for i in range(listWidget.count())]

        self.assertItemsEqual(
            item_texts,
            ["SH001", "SH002", "SH003", "SH004", "SH005"]
        )
    
    def test_shots_listWidget_has_shots_attribute(self):
        """testing if the shot_listWidget has an attribute called shots
        """
        dialog = version_creator.MainDialog_New()
        self.assertTrue(hasattr(dialog.shots_listWidget, "shots"))
    
    def test_shots_listWidget_shots_attribute_is_filled_with_shots_instances(self):
        """testing if the shots_listWidget's shots attribute is filled with the
        current Shot instances of the current Sequence
        """
        
        proj1 = Project("TEST_PROJECT1")
        proj1.create()
        
        seq1 = Sequence(proj1, "TEST_SEQ1")
        seq2 = Sequence(proj1, "TEST_SEQ2")
        
        # for seq1
        shot1 = Shot(seq1, 1)
        shot2 = Shot(seq1, 2)
        shot3 = Shot(seq1, 3)
        shot4 = Shot(seq1, 4)
        shot5 = Shot(seq1, 5)
        
        # for seq2
        shot6 = Shot(seq2, 1)
        shot7 = Shot(seq2, 2)
        shot8 = Shot(seq2, 3)
        shot9 = Shot(seq2, 4)
        shot10 = Shot(seq2, 5)
        
        shot1.save()
        shot2.save()
        shot3.save()
        shot4.save()
        shot5.save()
        shot6.save()
        shot7.save()
        shot8.save()
        shot9.save()
        shot10.save()
        
        dialog = version_creator.MainDialog_New()
        
        # switch to the shots tab
        dialog.tabWidget.setCurrentIndex(1)
        
        # select the first sequence
        dialog.sequences_comboBox.setCurrentIndex(0)
        
        # check if the shots_listWidget's shot attribute is a list and has the
        # shots
        
        expected_list = [shot1, shot2, shot3, shot4, shot5]
        
        self.assertEqual(len(dialog.shots_listWidget.shots), 5)
        
        self.assertTrue(all([isinstance(shot, Shot) for shot in dialog.shots_listWidget.shots]))
        
        self.assertListEqual(
            expected_list,
            dialog.shots_listWidget.shots
        )
    
    def test_create_asset_pushButton_pops_up_a_QInputDialog(self):
        """testing if the create_asset_pushButton pops up a QInputDialog
        """

        proj = Project("TEST_PROJ1")
        proj.create()
        
        dialog = version_creator.MainDialog_New()
#        dialog.show()
#        self.app.exec_()
#        self.app.connect(
#            self.app,
#            QtCore.SIGNAL("lastWindowClosed()"),
#            self.app,
#            QtCore.SLOT("quit()")
#        )
        
        # push the create asset button
        # spawn a new thread to click the button
#        class Thread1(QtCore.QThread):
#            def run(self):
#                """overridden run method
#                """
#                QTest.mouseClick(dialog.create_asset_pushButton, Qt.LeftButton)
#                self.exec_()
#        
#        thread1 = Thread1()
##        thread1.run()
#        thread1.start()
#        
#        print dialog.input_dialog
#        thread1.wait()
        
#        print "something"
#        
#        thread2 = threading.Thread(
#            target=QTest.keyClicks,
#            args=(dialog.input_dialog, "test name"),
#        )
#        thread2.start()
#        thread2.join()
#        
#        thread3 = threading.Thread(
#            target=QTest.keyClick,
#            args=(dialog.input_dialog, Qt.Key_Enter)
#        )
#        thread3.start()
#        thread3.join()
#        
#        self.assertTrue(dialog.input_dialog.isShown())
        
        self.fail("test is not implemented yet")

    def test_add_type_toolButton_pops_up_a_QInputDialog_for_asset(self):
        """testing if hitting the add_type_toolButton pops up a QInputDialog
        with a comboBox filled with all the suitable version types for the
        current asset
        """
        
        proj1 = Project("TEST_PROJECT")
        proj1.create()
        
        # create assets
        asset1 = Asset(proj1, "Test Asset 1")
        asset1.save()
        
        asset2 = Asset(proj1, "Test Asset 2")
        asset2.save()
        
        # sequences
        seq1 = Sequence(proj1, "Test Sequence 1")
        seq2 = Sequence(proj1, "Test Sequence 2")
        
        # shots
        shot1 = Shot(seq1, 1)
        shot2 = Shot(seq1, 2)
        shot3 = Shot(seq1, 3)
        
        shot4 = Shot(seq2, 4)
        shot5 = Shot(seq2, 5)
        shot6 = Shot(seq2, 6)
        
        shot1.save()
        shot2.save()
        shot3.save()
        shot4.save()
        shot5.save()
        shot6.save()
        
        # new user
        user1 = User(
            name="User1",
            initials="u1",
            email="user1@test.com"
        )
        
        # create a couple of versions
        asset_vtypes =\
            proj1.query(VersionType).filter_by(type_for="Asset").all()
        
        vers1 = Version(
            asset1,
            asset1.name,
            asset_vtypes[0],
            user1,
            take_name="Main",
            note="test note"
        )
        vers1.save()
        
        dialog = version_creator.MainDialog_New()
        dialog.show()
        self.app.exec_()
        self.app.connect(
            self.app,
            QtCore.SIGNAL("lastWindowClosed()"),
            self.app,
            QtCore.SLOT("quit()")
        )
    
    def test_get_versionable_returns_the_correct_versionable_instance(self):
        """testing if the get_versionable method is returning the correct
        versionable from the UI
        """
        
        proj1 = Project("TEST_PROJECT1")
        proj1.create()
        
        # Assets
        asset1 = Asset(proj1, "Test Asset1")
        asset1.save()
        
        asset2 = Asset(proj1, "Test Asset2")
        asset2.save()
        
        asset3 = Asset(proj1, "Test Asset3")
        asset3.save()
        
        # sequences
        seq1 = Sequence(proj1, "TEST_SEQ1")
        seq2 = Sequence(proj1, "TEST_SEQ2")
        
        # Shots
        shot1 = Shot(seq1, 1)
        shot2 = Shot(seq1, 2)
        shot3 = Shot(seq1, 3)
        shot4 = Shot(seq1, 4)
        
        shot1.save()
        shot2.save()
        shot3.save()
        shot4.save()
        
        dialog = version_creator.MainDialog_New()
        
        # set the tabWidget to 0
        dialog.tabWidget.setCurrentIndex(0)
        
        # set to the first asset
        dialog.assets_listWidget.setCurrentRow(0)
        
        # get the current versionable and expect it to be the asset1
        versionable = dialog.get_versionable()
        
        self.assertEqual(versionable, asset1)
        
        # set to the second asset
        dialog.assets_listWidget.setCurrentRow(1)
        
        # get the current versionable and expect it to be the asset2
        versionable = dialog.get_versionable()
        
        self.assertEqual(versionable, asset2)
        
        # switch to shot tab
        dialog.tabWidget.setCurrentIndex(1)
        
        # set to the first sequence
        dialog.sequences_comboBox.setCurrentIndex(0)
        
        # set to the first shot
        dialog.shots_listWidget.setCurrentRow(0)
        
        # get the versionable and expect it to be shot1
        versionable = dialog.get_versionable()
        
        self.assertEqual(versionable, shot1)
        
        # set it to the second shot
        dialog.shots_listWidget.setCurrentRow(1)
        
        # get the versionable and expect it to be shot2
        versionable = dialog.get_versionable()
        
        self.assertEqual(versionable, shot2)
    
    def test_add_take_toolButton_pops_up_a_QInputDialog_with_input_field(self):
        """testing if the add_take_toolButton pops up a QInputDialog with an
        input text field
        """
        self.fail("test is not implemented yet")
    
