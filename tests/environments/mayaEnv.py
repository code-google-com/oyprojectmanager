# -*- coding: utf-8 -*-
# Copyright (c) 2009-2012, Erkan Ozgur Yilmaz
# 
# This module is part of oyProjectManager and is released under the BSD 2
# License: http://www.opensource.org/licenses/BSD-2-Clause
"""These tests should run with Maya's own ptyhon interpreter
"""

import os
import shutil
import tempfile
import unittest
import logging

from pymel import core as pm
from oyProjectManager import conf, db, utils
from oyProjectManager.core.models import (Project, Asset, Version, VersionType,
                                          User)
from oyProjectManager.environments import mayaEnv

# set level to debug
logger = logging.getLogger("oyProjectManager.environments.mayaEnv")
logger.setLevel(logging.DEBUG)

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
    
    def test_save_as_creates_a_maya_file_at_version_full_path(self):
        """testing if the save_as creates a maya file at the Version.full_path
        """
        
        # check the version file doesn't exists
        self.assertFalse(os.path.exists(self.version1.full_path))
        
        # save the version
        self.mEnv.save_as(self.version1)
        
        # check the file exists
        self.assertTrue(os.path.exists(self.version1.full_path))
    
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
                        "/<Layer>/"+ self.version1.base_name +"_" + \
                        self.version1.take_name + \
                        "_<Layer>_<RenderPass>_<Version>"
        
        image_path = os.path.join(
            pm.workspace.path,
            pm.workspace.fileRules['image']
        ).replace("\\", "/")
        
        expected_path = utils.relpath(
            image_path,
            expected_path,
        )
        
        dRG = pm.PyNode("defaultRenderGlobals")
        
        self.assertEqual(
            expected_path,
            dRG.getAttr("imageFilePrefix")
        )
    
    def test_save_as_replaces_file_image_paths(self):
        """testing if save_as method replaces image paths with workspace
        relative path
        """
        
        self.mEnv.save_as(self.version1)
        
        # create file node
        file_node = pm.createNode("file")
        
        # set it to a path in the workspace
        texture_path = os.path.join(
            pm.workspace.path, ".maya_files/textures/test.jpg"
        )
#        file_node.setAttr("fileTextureName", texture_path)
        file_node.fileTextureName.set(texture_path)
        
        # save a newer version
        version2 = Version(**self.kwargs)
        version2.save()
        
        self.mEnv.save_as(version2)
        
        # now check if the file nodes fileTextureName is converted to a
        # relative path to the current workspace
        
        expected_path = utils.relpath(
            pm.workspace.path,
            texture_path,
            "/", ".."
        )
        
        self.assertEqual(
            file_node.getAttr("fileTextureName"),
            expected_path
        )

    def test_save_as_replaces_mentalrayTexture_paths(self):
        """testing if save_as method replaces mentalrayImage paths with
        workspace relative path
        """

        self.mEnv.save_as(self.version1)

        # create mentalrayTexture node
        mentalrayTexture_node = pm.createNode("mentalrayTexture")

        # set it to a path in the workspace
        texture_path = os.path.join(
            pm.workspace.path, ".maya_files/textures/test.jpg"
        )
        mentalrayTexture_node.setAttr("fileTextureName", texture_path)

        # save a newer version
        version2 = Version(**self.kwargs)
        version2.save()

        self.mEnv.save_as(version2)

        # now check if the file nodes fileTextureName is converted to a
        # relative path to the current workspace

        expected_path = utils.relpath(
            pm.workspace.path,
            texture_path,
            "/", ".."
        )
        
        self.assertEqual(
            mentalrayTexture_node.getAttr("fileTextureName"),
            expected_path
        )
    
    def test_save_as_sets_the_resolution(self):
        """testing if save_as sets the render resolution for the current scene
        """
        
        project = self.version1.project

        width = 1920
        height = 1080
        pixel_aspect = 1.0
        
        project.width = width
        project.height = height
        project.pixel_aspect = pixel_aspect
        project.save()
        
        # save the scene
        self.mEnv.save_as(self.version1)
        
        # check the resolutions
        dRes = pm.PyNode("defaultResolution")
        self.assertEqual(dRes.width.get(), width)
        self.assertEqual(dRes.height.get(), height)
        self.assertEqual(dRes.pixelAspect.get(), pixel_aspect)
    
    def test_save_as_fills_the_referenced_versions_list(self):
        """testing if the save_as method updates the Version.references list
        with the current references list from the Maya
        """
        
        # create a couple of versions and reference them to each other
        # and reference them to the the scene and check if maya updates the
        # Version.references list
        
        versionBase = Version(**self.kwargs)
        versionBase.save()
        
        # change the take naem
        self.kwargs["take_name"] = "Take1"
        version1 = Version(**self.kwargs)
        version1.save()
        
        self.kwargs["take_name"] = "Take2"
        version2 = Version(**self.kwargs)
        version2.save()
        
        self.kwargs["take_name"] = "Take3"
        version3 = Version(**self.kwargs)
        version3.save()
        
        # now create scenes with these files
        self.mEnv.save_as(version1)
        self.mEnv.save_as(version2)
        self.mEnv.save_as(version3) # this is the dummy version
        
        # create a new scene
        pm.newFile(force=True)
        
        # check if the versionBase.references is an empty list
        self.assertTrue(versionBase.references==[])
        
        # reference the given versions
        self.mEnv.reference(version1)
        self.mEnv.reference(version2)
        
        # save it as versionBase
        self.mEnv.save_as(versionBase)
        
        # now check if versionBase.references is updated
        self.assertTrue(len(versionBase.references)==2)
        
        self.assertTrue(version1 in versionBase.references)
        self.assertTrue(version2 in versionBase.references)

    def test_open_updates_the_referenced_versions_list(self):
        """testing if the open method updates the Version.references list with
        the current references list from the Maya
        """

        # create a couple of versions and reference them to each other
        # and reference them to the the scene and check if maya updates the
        # Version.references list

        versionBase = Version(**self.kwargs)
        versionBase.save()

        # change the take naem
        self.kwargs["take_name"] = "Take1"
        version1 = Version(**self.kwargs)
        version1.save()

        self.kwargs["take_name"] = "Take2"
        version2 = Version(**self.kwargs)
        version2.save()

        self.kwargs["take_name"] = "Take3"
        version3 = Version(**self.kwargs)
        version3.save()

        # now create scenes with these files
        self.mEnv.save_as(version1)
        self.mEnv.save_as(version2)
        self.mEnv.save_as(version3) # this is the dummy version

        # create a new scene
        pm.newFile(force=True)

        # check if the versionBase.references is an empty list
        self.assertTrue(versionBase.references==[])

        # reference the given versions
        self.mEnv.reference(version1)
        self.mEnv.reference(version2)

        # save it as versionBase
        self.mEnv.save_as(versionBase)

        # now check if versionBase.references is updated
        # this part is already tested in save_as
        self.assertTrue(len(versionBase.references)==2)
        self.assertTrue(version1 in versionBase.references)
        self.assertTrue(version2 in versionBase.references)
        
        # now remove references
        ref_data = self.mEnv.get_referenced_versions()
        for data in ref_data:
            ref_node = data[1]
            ref_node.remove()

        # do a save (not save_as)
        pm.saveFile()
        
        # clean scene
        pm.newFile(force=True)
        
        # open the same asset
        self.mEnv.open_(versionBase, force=True)
        
        # and check the references is updated
        self.assertEqual(len(versionBase.references), 0)
        self.assertEqual(versionBase.references, [])
    
    def test_save_as_in_another_project_updates_paths_correctly(self):
        """testing if the external paths are updated correctly if the document
        is created in one maya project but it is saved under another one.
        """
        
        # create a new scene
        # save it under one Asset Version with name Asset1
        
        asset1 = Asset(self.project, "Asset 1")
        asset1.save()
        
        self.kwargs["version_of"] = asset1
        self.kwargs["base_name"] = asset1.code
        version1 = Version(**self.kwargs)
        version1.save()
        
        self.kwargs["take_name"] = "References1"
        version_ref1 = Version(**self.kwargs)
        version_ref1.save()
        
        self.kwargs["take_name"] = "References2"
        version_ref2 = Version(**self.kwargs)
        version_ref2.save()
        
        # save a maya file with this references
        self.mEnv.save_as(version_ref1)
        self.mEnv.save_as(version_ref2)
        
        # save the original version
        self.mEnv.save_as(version1)
        
        # create a couple of file textures
        file_texture1 = pm.createNode("file")
        file_texture2 = pm.createNode("file")
        
        path1 = ".maya_files/TEXTURES/a.jpg"
        path2 = ".maya_files/TEXTURES/b.jpg"
        
        # set them to some relative paths
        file_texture1.fileTextureName.set(path1)
        file_texture2.fileTextureName.set(path2)
        
        # create a couple of references in the same project
        self.mEnv.reference(version_ref1)
        self.mEnv.reference(version_ref2)
        
        # save again
        self.mEnv.save_as(version1)

        # then save it under another Asset with name Asset2
        # because with this new system all the Assets folders are a maya
        # project, the references should be updated correctly
        asset2 = Asset(self.project, "Asset 2")
        asset2.save()
        
        # create a new Version for Asset 2
        self.kwargs["version_of"] = asset2
        self.kwargs["base_name"] = asset2.code
        version2 = Version(**self.kwargs)
        
        # now save it under that asset
        self.mEnv.save_as(version2)
        
        # check if the paths are updated
        self.assertEqual(
            file_texture1.fileTextureName.get(),
            "../Asset_1/.maya_files/TEXTURES/a.jpg"
        )

        self.assertEqual(
            file_texture2.fileTextureName.get(),
            "../Asset_1/.maya_files/TEXTURES/b.jpg"
        )
    
    def test_save_as_sets_the_fps(self):
        """testing if the save_as method sets the fps value correctly
        """
        
        # create two projects with different fps values
        # first create a new scene and save it under the first project
        # and then save it under the other project
        # and check if the fps follows the project values
        
        project1 = Project("FPS_TEST_PROJECT_1")
        project1.fps = 24
        project1.create()
        
        project2 = Project("FPS_TEST_PROJECT_2")
        project2.fps = 30
        project2.save()
        
        # create assets
        asset1 = Asset(project1, "Test Asset 1")
        asset1.save()
        
        asset2 = Asset(project2, "Test Asset 2")
        asset2.save()
        
        # create versions
        version1 = Version(
            version_of=asset1,
            base_name=asset1.code,
            type=self.asset_vtypes[0],
            created_by=self.user1
        )
        
        version2 = Version(
            version_of=asset2,
            base_name=asset2.code,
            type=self.asset_vtypes[0],
            created_by=self.user1
        )
        
        # save the current scene for asset1
        self.mEnv.save_as(version1)
        
        # check the fps value
        self.assertEqual(
            self.mEnv.get_fps(),
            24
        )
        
        # now save it for asset2
        self.mEnv.save_as(version2)
        
        # check the fps value
        self.assertEqual(
            self.mEnv.get_fps(),
            30
        )
