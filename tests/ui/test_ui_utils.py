# -*- coding: utf-8 -*-
# Copyright (c) 2009-2012, Erkan Ozgur Yilmaz
# 
# This module is part of oyProjectManager and is released under the BSD 2
# License: http://www.opensource.org/licenses/BSD-2-Clause
import os
import shutil
import tempfile
import unittest
import sys
from oyProjectManager import conf, db
from oyProjectManager.core.models import Project, Asset
from oyProjectManager.ui import ui_utils

import sip
sip.setapi('QString', 2)
sip.setapi('QVariant', 2)
from PyQt4 import QtGui

class UIUtilsTester(unittest.TestCase):
    """tests the ui_utils functions
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
    
    
    def create_test_image(self, pixmap_full_path):
        """Creates a test image at the given path
        """
        
        # first create a thumbnail
        pixmap = QtGui.QPixmap(
            [
                "16 16 2 1",
                "  c None",
                ". c white",
                " . . . . . . . .",
                ". . . . . . . . ",
                " . . . . . . . .",
                ". . . . . . . . ",
                " . . . . . . . .",
                ". . . . . . . . ",
                " . . . . . . . .",
                ". . . . . . . . ",
                " . . . . . . . .",
                ". . . . . . . . ",
                " . . . . . . . .",
                ". . . . . . . . ",
                " . . . . . . . .",
                ". . . . . . . . ",
                " . . . . . . . .",
                ". . . . . . . . "
            ]
        )
        
       
        # write the image
        pixmap.save(pixmap_full_path)
        
        # assert the image is saved to the path
        self.assertTrue(os.path.exists(pixmap_full_path))
        
        return pixmap
 
    def test_upload_thumbnail_updates_the_thumbnail_path_for_the_given_versionable(self):
        """testing if the upload_thumbnail updates the thumbnail field of the
        given Versionable instance
        """
        
        proj = Project("Test Project")
        proj.create()
        
        asset = Asset(proj, "Test Asset")
        asset.save()
        
        # save the image to the temp directory
        pixmap_full_path = os.path.join(
            self.temp_config_folder,
            "test.jpg"
        )
        
        self.create_test_image(pixmap_full_path)
        
        thumbnail_full_path = os.path.join(
            proj.code, "Assets", asset.type, asset.code, "Thumbnail",
            asset.code + "_thumbnail.jpg"
        )
        
        # now upload a thumbnail
        ui_utils.upload_thumbnail(asset, pixmap_full_path)
        
        # now check if asset.thumbnail is correctly set
        self.assertEqual(asset.thumbnail_full_path, thumbnail_full_path)
        
        # and the file is placed to the correct placement
        self.assertTrue(
            os.path.exists(
                os.path.join(
                    proj.path, thumbnail_full_path 
                ) 
            )
        )
