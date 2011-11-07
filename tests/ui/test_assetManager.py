#-*- coding: utf-8 -*-
from PyQt4 import QtCore
import os
import shutil
import tempfile
import unittest
from PyQt4.QtCore import Qt
from PyQt4.QtGui import QApplication
from PyQt4.QtTest import QTest
import sys
from oyProjectManager import config
from oyProjectManager.core.models import Project, Asset
from oyProjectManager.ui import assetManager

conf = config.Config()



class AssetManagerTester(unittest.TestCase):
    """tests the oyProjectManager.ui.assetManager class
    """
    
    def setUp(self):
        """setup the test
        """
        
        # -----------------------------------------------------------------
        # start of the setUp
        # create the environment variable and point it to a temp directory
        self.temp_config_folder = tempfile.mkdtemp()
        self.temp_projects_folder = tempfile.mkdtemp()
        
        os.environ[conf.repository_env_key] = self.temp_projects_folder
        
        self.app = QApplication(sys.argv)
        
        os.environ[conf.repository_env_key] = self.temp_projects_folder
    
    def tearDown(self):
        """clean up the test
        """
        # delete the temp folders
        shutil.rmtree(self.temp_config_folder)
        shutil.rmtree(self.temp_projects_folder)
    
    def test_close_button_closes_ui(self):
        """testing if the close button is closing the ui
        """
        dialog = assetManager.MainDialog_New()
        
        # now run the UI
        QTest.mouseClick(dialog.close_pushButton, Qt.LeftButton)
        self.assertEqual(dialog.isVisible(), False)
        
    def test_projects_combobox_is_filled_with_projects(self):
        """testing if the projects_combobox is filled with projects
        """
        # create a couple of test projects
        proj1 = Project("Test Project1")
        proj2 = Project("Test Project2")
        
        proj1.create()
        proj2.create()
        
        dialog = assetManager.MainDialog_New()
        
        # see if the projects filled with projects
        self.assertEqual(len(dialog.projects_comboBox), 2)
    
    def test_projects_combobox_first_project_is_selected(self):
        """testing if the first project is selected in the project combo box
        """
        # create a couple of test projects
        proj1 = Project("Test Project1")
        proj2 = Project("Test Project2")
        
        proj1.create()
        proj2.create()
        
        dialog = assetManager.MainDialog_New()
        # see if the projects filled with projects
        self.assertEqual(dialog.projects_comboBox.currentIndex(), 0)
        
        
    
    def test_users_combobox_is_filled_with_users_from_the_config(self):
        """testing if the users combobox is filled with the user names
        """
        
        # get the users from the config
        users = conf.users
        
        dialog = assetManager.MainDialog_New()
        
        # check if all the names in the users are in the combobox
        
        
        content = [dialog.user_comboBox.itemText(i)
                   for i in range(dialog.user_comboBox.count())]
        
        for user in users:
            self.assertIn(user.name, content)
    
    def test_asset_names_list_filled(self):
        """testing if the asset names listWidget is filled with asset names
        """
        
        # create a new project
        proj1 = Project("TEST_PROJECT1")
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
        
        dialog = assetManager.MainDialog_New()
#        dialog.show()
#        self.app.exec_()
#        self.app.connect(
#            self.app,
#            QtCore.SIGNAL("lastWindowClosed()"),
#            self.app,
#            QtCore.SLOT("quit()")
#        )
        
        # now check if their names are in the asset names listWidget
        listWidget = dialog.asset_names_listWidget
        item_texts = [unicode(listWidget.item(i).text()) for i in range(listWidget.count())]
        
        self.assertIn(asset1.name, item_texts)
        self.assertIn(asset2.name, item_texts)
        self.assertNotIn(asset3.name, item_texts)
        self.assertNotIn(asset4.name, item_texts)
        
        # now update the project to the second one
        dialog.projects_comboBox.setCurrentIndex(1)
        
        # now check if their names are in the asset names listWidget
        listWidget = dialog.asset_names_listWidget
        item_texts = [unicode(listWidget.item(i).text()) for i in range(listWidget.count())]
        
        self.assertNotIn(asset1.name, item_texts)
        self.assertNotIn(asset2.name, item_texts)
        self.assertIn(asset3.name, item_texts)
        self.assertIn(asset4.name, item_texts)
    
    def test_description_text_edit_field_updated(self):
        """testing if the description field is updated with the selected asset
        """
        
        proj1 = Project("TEST_PROJECT1")
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
        
        dialog = assetManager.MainDialog_New()
        dialog.show()
        self.app.exec_()
        self.app.connect(
            self.app,
            QtCore.SIGNAL("lastWindowClosed()"),
            self.app,
            QtCore.SLOT("quit()")
        )
        
        # check if the first assets description is shown in the asset
        # description window
        self.assertEqual(
            unicode(dialog.asset_description_textEdit.toPlainText()),
            asset1.description
        )
        
        # select the second asset
        list_item = dialog.asset_names_listWidget.item(1)
        list_item.setSelected(True)
        dialog.asset_names_listWidget.setCurrentItem(list_item)
        
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
        list_item = dialog.asset_names_listWidget.item(1)
        list_item.setSelected(True)
        dialog.asset_names_listWidget.setCurrentItem(list_item)
        
        self.assertEqual(
            unicode(dialog.asset_description_textEdit.toPlainText()),
            asset4.description
        )
    
    def test_asset_description_edit_button_is_checked(self):
        """testing if the edit button changes to done   
        """
        
        # create the dialog
        dialog = assetManager.MainDialog_New()
        dialog.show()
        self.app.exec_()
        self.app.connect(
            self.app,
            QtCore.SIGNAL("lastWindowClosed()"),
            self.app,
            QtCore.SLOT("quit()")
        )
        
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
        
    
    def test_asset_description_updated_with_edit_button(self):
        """testing if the asset description update will be persistent when the
        edit button is checked and done is selected afterwards
        """
        
        proj1 = Project("TEST_PROJECT1")
        proj1.create()
        
        asset1 = Asset(proj1, "TEST_ASSET1")
        asset1.description = "Description for TEST_ASSET1 before change"
        
        asset2 = Asset(proj1, "TEST_ASSET2")
        asset2.description = "Description for TEST_ASSET2 before change"
        
        asset1.save()
        asset2.save()
        
        # now create the dialog
        dialog = assetManager.MainDialog_New()
#        dialog.show()
#        self.app.exec_()
#        self.app.connect(
#            self.app,
#            QtCore.SIGNAL("lastWindowClosed()"),
#            self.app,
#            QtCore.SLOT("quit()")
#        )
        
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
        
        test_value = "Description for TEST_ASSET1 after change"
        
        # change the description of asset1
        dialog.asset_description_textEdit.setText(test_value)
        
        # hit done pushButton
        QTest.mouseClick(
            dialog.asset_description_edit_pushButton,
            QtCore.Qt.LeftButton
        )
        
        # change the asset to the next one
        list_item = dialog.asset_names_listWidget.item(1)
        list_item.setSelected(True)
        dialog.asset_names_listWidget.setCurrentItem(list_item)
        
        # check if the description is changed to the asset2's description
        self.assertEqual(
            asset2.description,
            unicode(dialog.asset_description_textEdit.toPlainText())
        )
        
        # change the asset back to the first one
        list_item = dialog.asset_names_listWidget.item(0)
        list_item.setSelected(True)
        dialog.asset_names_listWidget.setCurrentItem(list_item)
        
        # check if the description has updated to the asset1's edited
        # description
        self.assertEqual(
            test_value,
            unicode(dialog.asset_description_textEdit.toPlainText())
        )
