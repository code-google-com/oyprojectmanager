# -*- coding: utf-8 -*-
import os
import shutil
import tempfile

import unittest
from pymel import core as pm
from oyProjectManager import conf, db, utils
from oyProjectManager.core.models import (Project, Asset, Version, VersionType,
                                          User)
from oyProjectManager.environments import mayaEnv

class MayaTester(unittest.TestCase):
    """Tests the oyProjectManager.environments.mayaEnv.Maya class
    """

    def setUp(self):
        """setup the tests
        """
        # -----------------------------------------------------------------
        # start of the setUp
        # create the environment variable and point it to a temp directory
        self.temp_config_folder = tempfile.mkdtemp()
        self.temp_projects_folder = tempfile.mkdtemp()

        os.environ["OYPROJECTMANAGER_PATH"] = self.temp_config_folder
        os.environ[conf.repository_env_key] = self.temp_projects_folder
        
        # create a test project
        self.project = Project("Test Project")
        self.project.create()

        # create a test asset
        self.asset1 = Asset(self.project, "Test Asset 1")

        # version type
        self.asset_vtypes = db.query(VersionType).\
        filter(VersionType.type_for == "Asset").all()

        self.shot_vtypes = db.query(VersionType).\
        filter(VersionType.type_for == "Shot").all()

        self.user1 = User(name="Test User 1", email="user1@test.com")

        # create a test version
        self.kwargs = {
            "version_of":self.asset1,
            "base_name":self.asset1.code,
            "type":self.asset_vtypes[0],
            "created_by":self.user1,
            "extension":"ma"
        }
        
        self.version1 = Version(**self.kwargs)
        self.version1.save()
        
        # create the environment instance
        self.mEnv = mayaEnv.Maya()

        # just renew the scene
        pm.newFile(force=True)

    def tearDown(self):
        """cleanup the test
        """
        
        # set the db.session to None
        db.session = None
        
        # delete the temp folder
        shutil.rmtree(self.temp_config_folder)
        shutil.rmtree(self.temp_projects_folder)
        
        # quit maya
        pm.runtime.Quit()
    
    def test_save_as_creates_a_maya_file_at_version_fullpath(self):
        """testing if the save_as creates a maya file at the Version.fullpath
        """
        
        # check the version file doesn't exists
        self.assertFalse(os.path.exists(self.version1.fullpath))
        
        # save the version
        self.mEnv.save_as(self.version1)
        
        # check the file exists
        self.assertTrue(os.path.exists(self.version1.fullpath))
    
    def test_save_as_sets_the_version_extension_to_ma(self):
        """testing if the save_as method sets the version extension to ma
        """
        
        self.version1.extension = ""
        self.mEnv.save_as(self.version1)
        self.assertEqual(self.version1.extension, ".ma")
    
    def test_save_as_sets_the_render_version_string(self):
        """testing if the save_as method sets the version string in the render
        settings
        """
        
        self.mEnv.save_as(self.version1)
        
        # now check if the render settings version is the same with the
        # version.version_number
        
        render_version = pm.getAttr("defaultRenderGlobals.renderVersion")
        self.assertEqual(render_version, "%03d" % self.version1.version_number)
    
    def test_save_as_sets_the_render_format_to_exr_for_mentalray(self):
        """testing if the save_as method sets the render format to exr
        """
        
        # load mayatomr plugin
        pm.loadPlugin("Mayatomr")
        
        # set the current renderer to mentalray
        dRG = pm.PyNode("defaultRenderGlobals")
        
        dRG.setAttr('currentRenderer', 'mentalRay')
        
        # dirty little maya tricks
        pm.mel.miCreateDefaultNodes()
        
        mrG = pm.PyNode("mentalrayGlobals")
        
        self.mEnv.save_as(self.version1)
        
        # now check if the render format is correctly set to exr with zip
        # compression
        self.assertEqual(dRG.getAttr("imageFormat"), 51)
        self.assertEqual(dRG.getAttr("imfkey"), "exr")
        self.assertEqual(mrG.getAttr("imageCompression"), 4)
    
    def test_save_as_sets_the_render_file_name(self):
        """testing if the save_as sets the render file name correctly
        """
        
        self.mEnv.save_as(self.version1)
        
        # check if the path equals to
        expected_path = self.version1.output_path + \
                        "<Layer>/"+ self.version1.base_name +"_" + \
                        self.version1.take_name + \
                        "_<Layer>_<RenderPass>_<Version>"
        
        # and make it relative to the workspace.images folder
        image_path = str(
            pm.workspace.getPath() + "/" + pm.workspace.fileRules["images"]
        )
        
        utils.relpath(image_path, )
