# -*- coding: utf-8 -*-



import os, sys, shutil
import unittest
from xml.dom import minidom
from oyProjectManager.models import project, repository, asset






########################################################################
class SequenceTester(unittest.TestCase):
    """tests the Sequence class
    """
    
    
    
    #----------------------------------------------------------------------
    @classmethod
    def setUpClass(cls):
        """set up the test in class level
        """
        
        # setup environment variable for default settings
        
        import os, sys
        import oyProjectManager
        
        oyProjectManager_path = os.path.sep.join(
            oyProjectManager.__file__.split(os.path.sep)[:-2]
        )
        
        test_settings_path = os.path.join(oyProjectManager_path,
                                          "tests/test_settings")
        
        # append or update the environment key to point the test_settings path
        os.environ["OYPROJECTMANAGER_PATH"] = test_settings_path
    
    
    
    #----------------------------------------------------------------------
    def setUp(self):
        """set up the per test level
        """
        
        self.created_projects = []
    
    
    
    #----------------------------------------------------------------------
    def tearDown(self):
        """clean the tests
        """
        
        # clean up projects
        for proj in self.created_projects:
            shutil.rmtree(proj.fullPath)
        
    
    
    
    #----------------------------------------------------------------------
    def test_setup_is_working_fine(self):
        """testing if test setup is working fine
        """
        
        # now create a repository and ask the server path and check if it
        # matches the test_settings
        repo = repository.Repository()
        
        # BUG: works only under linux fix it later
        self.assertEquals(repo.server_path, "/tmp/JOBs")
    
    
    
    #----------------------------------------------------------------------
    def test_if_a_newly_created_sequence_dont_have_output_folders_object(self):
        """testing if a newly created sequence doesn't have any output_folders
        node in its settings
        """
        
        # create a project
        test_proj = project.Project("TEST_PROJECT")
        test_proj.create()
        
        self.created_projects.append(test_proj)
        
        # create a sequence
        test_seq = test_proj.createSequence("TEST_SEQ", "1")
        
        # now get the settings path and check if there is a node called
        # output folders by using the minidom
        document = minidom.parse(
            os.path.join(test_seq.fullPath, ".settings.xml")
        )
        
        output_folders = document.getElementsByTagName("output_folders")
        
        self.assertEquals(output_folders, [])
    
    
    
    #----------------------------------------------------------------------
    def test_if_an_old_sequence_with_and_old_settings_is_parsed_correctly(self):
        """testing if an old sequence which has an output_folders node is
        parsed without any problem
        """
        
        # create a new project and by using the minidom add output_folders node
        # and some output nodes as children
        
        # create a project
        test_proj = project.Project("TEST_PROJECT")
        test_proj.create()
        
        self.created_projects.append(test_proj)
        
        # create a sequence
        test_seq = test_proj.createSequence("TEST_SEQ", "1")
        
        # now by using the minidom add output_folders to the structure node
        settingsFileFullPath = os.path.join(test_seq.fullPath, ".settings.xml")
        
        settings = minidom.parse(settingsFileFullPath)
        
        outputFoldersNode = minidom.Element("outputFolders")
        
        # move all the output_path information to outputFolders node
        
        # and remove the output_path from any type node under the assetTypes
        # node
        assetTypesNode = settings.getElementsByTagName("assetTypes")[0]
        assert(isinstance(assetTypesNode, minidom.Element))
        
        for child in assetTypesNode.getElementsByTagName("type"):
            assert(isinstance(child, minidom.Element))
            
            # create an output node
            temp_output_node = minidom.Element("output")
            temp_output_node.setAttribute("name", child.getAttribute("name"))
            temp_output_node.setAttribute("path",
                                          child.getAttribute("output_path"))
            
            outputFoldersNode.appendChild(temp_output_node)
            
            # now remove the output_path attribute from the type node
            child.removeAttribute("output_path")
        
        structureNode = settings.getElementsByTagName("structure")[0]
        
        assert(isinstance(structureNode, minidom.Element))
        structureNode.appendChild(outputFoldersNode)
        
        # now save the settings file
        settings.writexml(
            open(settingsFileFullPath,"w"),
            "\t", "\t", "\n"
        )
        
        # now create another sequence object showing the same sequence before
        # and check if it is going to be able to read the file
        new_seq = test_proj.sequences()[0]
        
        assert(isinstance(new_seq, project.Sequence))
        
        # check if for every assetType defined there is an ouput_path 
        for asset_type in new_seq.getAssetTypes():
            assert(isinstance(asset_type, asset.AssetType))
            self.assertNotEqual(asset_type.output_path, "")
        
        # by using the dom check if the settings is converted to the new format
        settings = minidom.parse(settingsFileFullPath)
        
        self.assertEquals(settings.getElementsByTagName("outputFolders"), [])



