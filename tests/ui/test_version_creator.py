#-*- coding: utf-8 -*-
import os
import shutil
import tempfile
import unittest
#import thread

#from PyQt4 import QtCore, QtGui
#from PyQt4.QtCore import Qt
#from PyQt4.QtGui import QApplication
#from PyQt4.QtTest import QTest

from PySide import QtCore, QtGui
from PySide.QtCore import Qt
from PySide.QtGui import QApplication
from PySide.QtTest import QTest

import sys
#from oyProjectManager import conf
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
        
        self.app = QApplication(sys.argv)
    
    def tearDown(self):
        """clean up the test
        """
        self.app.quit()
        
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
        self.assertEqual(len(dialog.projects_comboBox), 2)
    
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
            unicode(dialog.projects_comboBox.currentText()),
            dialog.projects_comboBox.project_obj.name
        )
    
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
        item_texts = [unicode(listWidget.item(i).text()) for i in range(listWidget.count())]
        
        self.assertIn(asset1.name, item_texts)
        self.assertIn(asset2.name, item_texts)
        self.assertNotIn(asset3.name, item_texts)
        self.assertNotIn(asset4.name, item_texts)
        
        # now update the project to the second one
        dialog.projects_comboBox.setCurrentIndex(1)
        
        # now check if their names are in the asset names listWidget
        listWidget = dialog.assets_listWidget
        item_texts = [unicode(listWidget.item(i).text()) for i in range(listWidget.count())]
        
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
            unicode(dialog.asset_description_textEdit.toPlainText()),
            asset1.description
        )
        
        # select the second asset
        list_item = dialog.assets_listWidget.item(1)
        list_item.setSelected(True)
        dialog.assets_listWidget.setCurrentItem(list_item)
        
        self.assertEqual(
            unicode(dialog.asset_description_textEdit.toPlainText()),
            asset2.description
        )
        
        # change project
        dialog.projects_comboBox.setCurrentIndex(1)
        self.assertEqual(
            unicode(dialog.asset_description_textEdit.toPlainText()),
            asset3.description
        )
        
        # select the second asset
        list_item = dialog.assets_listWidget.item(1)
        list_item.setSelected(True)
        dialog.assets_listWidget.setCurrentItem(list_item)
        
        self.assertEqual(
            unicode(dialog.asset_description_textEdit.toPlainText()),
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
            unicode(dialog.asset_description_edit_pushButton.text()),
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
            unicode(dialog.asset_description_edit_pushButton.text()),
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
            unicode(dialog.asset_description_edit_pushButton.text()),
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
        
        # check if the create_asset_pushButton becomes enabled again
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
        
        # check if the create_asset_pushButton becomes disabled
        self.assertFalse(
            dialog.shots_tab.isEnabled()
        )
        
        # push the edit pushButton again
        QTest.mouseClick(
            dialog.asset_description_edit_pushButton,
            QtCore.Qt.LeftButton
        )
        
        # check if the create_asset_pushButton becomes enabled again
        self.assertTrue(
            dialog.shots_tab.isEnabled()
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
            unicode(dialog.asset_description_textEdit.toPlainText())
        )
        
        # change the asset back to the first one
        list_item = dialog.assets_listWidget.item(0)
        list_item.setSelected(True)
        dialog.assets_listWidget.setCurrentItem(list_item)
        
        # check if the description has updated to the asset1's edited
        # description
        self.assertEqual(
            test_value,
            unicode(dialog.asset_description_textEdit.toPlainText())
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
        asset_vtypes = \
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
                unicode(dialog.takes_comboBox.currentText())
            )
        
        self.assertItemsEqual(
            ["Main", "Test"],
            ui_take_names
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
        asset_vtypes = \
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
                unicode(dialog.version_types_comboBox.currentText())
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
        asset_vtypes = \
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
            unicode(dialog.previous_versions_tableWidget.item(0, 1).text()),
            vers1.created_by.name
        )
        
        self.assertEqual(
            unicode(dialog.previous_versions_tableWidget.item(0, 2).text()),
            vers1.note
        )
        
        self.assertEqual(
            unicode(dialog.previous_versions_tableWidget.item(0, 4).text()),
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
        asset_vtypes = \
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
        dialog.show()
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
                unicode(dialog.previous_versions_tableWidget.item(i,1).text()),
                versions[i].created_by.name
            )
        
            self.assertEqual(
                unicode(dialog.previous_versions_tableWidget.item(i,2).text()),
                versions[i].note
            )
            
            # TODO: add test for file size column
            
            self.assertEqual(
                unicode(dialog.previous_versions_tableWidget.item(i,4).text()),
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

    def test_create_asset_pushButton_pops_up_a_QInputDialog(self):
        """testing if the create_asset_pushButton pops up a QInputDialog
        """
        
        proj = Project("TEST_PROJ1")
#        proj.create()
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
        
        # push the create asset button
        #thread.start_new_thread(function, args[, kwargs])
        #QTest.mouseClick(dialog.create_asset_pushButton, Qt.LeftButton)
        
        # spawn a new thread to click the button
#        thread_1_id = thread.start_new_thread(
#            QTest.mouseClick,
#            (dialog.create_asset_pushButton, Qt.LeftButton)
#        )
        
        # and another to enter the text
#        thread_2_id
        
#        for child in dialog.children():
#            if isinstance(child, QtGui.QInputDialog):
#                print "found child"
#            print child
        
#        QTest.keyClicks(None, "test name")
#        QTest.keyClick(None, Qt.Key_Enter)
        
        self.fail("test is not implemented yet")
    
    def test_tab_changed_updates_types_comboBox(self):
        """testing if the the types_comboBox is updated according to the
        selected tab
        """
        #        dialog.show()
        # project
        proj1 = Project("TEST_PROJECT")
        proj1.create()
        
        # sequence
        seq1 = Sequence(proj1, "TEST_SEQ")
        seq1.create()
        
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
            unicode(dialog.version_types_comboBox.currentText()),
            asset_vtypes[0].name
        )
        
        # set the tab to Shots
        dialog.tabWidget.setCurrentIndex(1)
        
        # check if the type comboBox lists the asset type of the first shot
        self.assertEqual(
            unicode(dialog.version_types_comboBox.currentText()),
            shot_vtypes[0]
        )
        

