# -*- coding: utf-8 -*-

import shutil
import tempfile
import unittest

from oyProjectManager.core.models import Project, Sequence, Repository, Asset


class AssetTester(unittest.TestCase):
    """tests the Asset class
    """
    
    def setUp(self):
        """testing the settings path from the environment variable
        """
        
        # -----------------------------------------------------------------
        # start of the setUp
        # create the environment variable and point it to a temp directory
        self.temp_config_folder = tempfile.mkdtemp()
        self.temp_projects_folder = tempfile.mkdtemp()
    
    def tearDown(self):
        """remove the temp folders
        """
        
        # delete the temp folder
        shutil.rmtree(self.temp_config_folder)
        shutil.rmtree(self.temp_projects_folder)
    
    def test_output_path_with_variable_path(self):
        """testing if the output path will be correct for a path which contains
        variables inside
        """
        
        # create a new project and sequence
        # let the sequence to parse the settings
        
        proj = Project("TEST_PROJECT")
        proj.create()
        
        seq = Sequence(proj, "TEST_SEQ")
        seq.create()
        
        # get the first assetType
        asset_type = seq.getAssetTypes(None)[0]
        
        # then change its path with a path containing a variable
        asset_type.output_path = "TEST/{{assetBaseName}}/OUTPUT"
        
        # save the settings
        seq.save()
        
        # for convenience get the first asset type again
        seq = Sequence(proj, "TEST_SEQ")
        asset_type = seq.getAssetTypes(None)[0]
        
        self.assertTrue( "{{assetBaseName}}" in asset_type.output_path )
        
        # then probe if it is rendered correctly
        # now create a new asset with the given asset type
        new_asset = Asset(proj, seq,
                          "SH001_MAIN_" + asset_type.name + \
                          "_r00_v001_oy.nk")
        
        # now get the output folder
        self.assertEqual(
            new_asset.output_path,
            "TEST/SH001/OUTPUT"
        )
    
    def test_no_rev_number(self):
        """testing assets with sequences which has the no_rev_number set to
        True
        """
        
        # create a project
        # create a sequence
        # set the sequences no_rev_number attribute to True
        # create a new asset
        # check if the asset file name will be correctly calculated
        
        pass
    
