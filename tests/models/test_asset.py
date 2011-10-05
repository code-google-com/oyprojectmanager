# -*- coding: utf-8 -*-


import sys
import os
import shutil
import tempfile
import unittest
from xml.dom import minidom

from oyProjectManager.models import project, repository, asset






########################################################################
class AssetTester(unittest.TestCase):
    """tests the Asset class
    """
    
    
    
    #----------------------------------------------------------------------
    def setUp(self):
        """testing the settings path from the environment variable
        """
        
        # -----------------------------------------------------------------
        # start of the setUp
        # create the environment variable and point it to a temp directory
        self.temp_settings_folder = tempfile.mktemp()
        self.temp_projects_folder = tempfile.mkdtemp()
        
        # copy the test settings
        import oyProjectManager
        
        self._test_settings_folder = os.path.join(
            os.path.dirname(
                os.path.dirname(
                    oyProjectManager.__file__
                )
            ),
            "tests", "test_settings"
        )
        
        os.environ["OYPROJECTMANAGER_PATH"] = self.temp_settings_folder
        os.environ["STALKER_REPOSITORY_PATH"] = self.temp_projects_folder
        
        # copy the default files to the folder
        shutil.copytree(
            self._test_settings_folder,
            self.temp_settings_folder,
        )
        
        # change the server path to a temp folder
        repository_settings_file_path = os.path.join(
            self.temp_settings_folder, 'repositorySettings.xml')
        
        # change the repositorySettings.xml by using the minidom
        xmlDoc = minidom.parse(repository_settings_file_path)
        
        serverNodes = xmlDoc.getElementsByTagName("server")
        for serverNode in serverNodes:
            serverNode.setAttribute("windows_path", self.temp_projects_folder)
            serverNode.setAttribute("linux_path", self.temp_projects_folder)
            serverNode.setAttribute("osx_path", self.temp_projects_folder)
        
        repository_settings_file = file(repository_settings_file_path,
                                        mode='w')
        xmlDoc.writexml(repository_settings_file, "\t", "\t", "\n")
        
        
        #self._name_test_values = [
            #("test project", "TEST_PROJECT"),
            #("123123 test_project", "TEST_PROJECT"),
            #("123432!+!'^+Test_PRoject323^+'^%&+%&324", "TEST_PROJECT323324"),
            #("    ---test 9s_project", "TEST_9S_PROJECT"),
            #("    ---test 9s-project", "TEST_9S_PROJECT"),
            #(" multiple     spaces are    converted to under     scores",
             #"MULTIPLE_SPACES_ARE_CONVERTED_TO_UNDER_SCORES"),
            #("camelCase", "CAMEL_CASE"),
            #("CamelCase", "CAMEL_CASE"),
            #("_Project_Setup_", "PROJECT_SETUP_"),
            #("_PROJECT_SETUP_", "PROJECT_SETUP_"),
            #("FUL_3D", "FUL_3D"),
        #]
    
    
    
    #----------------------------------------------------------------------
    def tearDown(self):
        """remove the temp folders
        """
        
        # delete the temp folder
        shutil.rmtree(self.temp_settings_folder)
        shutil.rmtree(self.temp_projects_folder)
    
    
    
    #----------------------------------------------------------------------
    def test_output_path_with_variable_path(self):
        """testing if the output path will be correct for a path which contains
        variables inside
        """
        
        # create a new project and sequence
        # let the sequence to parse the settings
        
        proj = project.Project("TEST_PROJECT")
        proj.create()
        
        seq = project.Sequence(proj, "TEST_SEQ")
        seq.create()
        
        # get the first assetType
        asset_type = seq.getAssetTypes(None)[0]
        
        # then change its path with a path containing a variable
        asset_type.output_path = "TEST/{{assetBaseName}}/OUTPUT"
        
        # save the settings
        seq.saveSettings()
        
        # for convenience get the first asset type again
        seq = project.Sequence(proj, "TEST_SEQ")
        asset_type = seq.getAssetTypes(None)[0]
        
        self.assertTrue( "{{assetBaseName}}" in asset_type.output_path )
        
        # then probe if it is rendered correctly
        # now create a new asset with the given asset type
        new_asset = asset.Asset(proj, seq,
                                "SH001_MAIN_" + asset_type.name + \
                                "_r00_v001_oy.nk")
        
        # now get the output folder
        self.assertEqual(
            new_asset.output_path,
            "TEST/SH001/OUTPUT"
        )
    
    
    
    #----------------------------------------------------------------------
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
    
    
    
    