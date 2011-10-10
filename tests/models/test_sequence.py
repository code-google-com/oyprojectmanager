# -*- coding: utf-8 -*-



import os
import shutil
import tempfile
import unittest
from xml.dom import minidom
from oyProjectManager import db
from oyProjectManager.models import project, repository, asset
from oyProjectManager.models.project import Project, Sequence
from oyProjectManager import conf


class SequenceTester(unittest.TestCase):
    """tests the Sequence class
    """


    @classmethod
    def setUpClass(cls):
        """set up the test in class level
        """

        # setup environment variable for default settings

        import os
        import oyProjectManager

        oyProjectManager_path = os.path.sep.join(
            oyProjectManager.__file__.split(os.path.sep)[:-2]
        )

        test_settings_path = os.path.join(oyProjectManager_path,
                                          "tests/test_settings")

        # append or update the environment key to point the test_settings path
        os.environ["OYPROJECTMANAGER_PATH"] = test_settings_path

        # create the test folder
        os.makedirs("/tmp/JOBs")


    @classmethod
    def tearDownClass(cls):
        """cleanup test
        """

        # remove the temp project path
        shutil.rmtree("/tmp/JOBs")


    def setUp(self):
        """set up the per test level
        """

        self.created_projects = []


    def tearDown(self):
        """clean the tests
        """

        # clean up projects
        for proj in self.created_projects:
            shutil.rmtree(proj.fullPath)


    def test_setup_is_working_fine(self):
        """testing if test setup is working fine
        """

        # now create a repository and ask the server path and check if it
        # matches the test_settings
        repo = repository.Repository()

        # BUG: works only under linux fix it later
        self.assertEqual(repo.server_path, "/tmp/JOBs")


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
        
        self.assertEqual(output_folders, [])


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
            open(settingsFileFullPath, "w"),
            "\t", "\t", "\n"
        )

        # now create another sequence object showing the same sequence before
        # and check if it is going to be able to read the file
        new_seq = test_proj.sequences()[0]

        assert(isinstance(new_seq, project.Sequence))

        # check if for every assetType defined there is an output_path 
        for asset_type in new_seq.getAssetTypes(None):
            assert(isinstance(asset_type, asset.AssetType))
            self.assertNotEqual(asset_type.output_path, "")

        # by using the dom check if the settings is converted to the new format
        settings = minidom.parse(settingsFileFullPath)

        self.assertEqual(settings.getElementsByTagName("outputFolders"), [])


    def test___eq___operator(self):
        """testing the __eq__ (equal) operator
        """

        # create a new project and two sequence
        # then create three new sequence objects to compare each of them
        # with the other

        new_proj = project.Project("TEST_PROJECT")
        new_proj.create()
        
        seq1 = project.Sequence(new_proj, "SEQ1")
        seq2 = project.Sequence(new_proj, "SEQ1")
        seq3 = project.Sequence(new_proj, "SEQ2")

        new_proj2 = project.Project("TEST_PROJECT2")
        new_proj2.create()
        
        seq4 = project.Sequence(new_proj2, "SEQ3")

        self.assertTrue(seq1 == seq2)
        self.assertFalse(seq1 == seq3)
        self.assertFalse(seq1 == seq4)
        self.assertFalse(seq3 == seq4)


    def test___ne___operator(self):
        """testing the __ne__ (not equal) operator
        """

        # create a new project and two sequence
        # then create three new sequence objects to compare each of them
        # with the other

        new_proj = project.Project("TEST_PROJECT")
        new_proj.create()
        
        seq1 = project.Sequence(new_proj, "SEQ1")
        seq2 = project.Sequence(new_proj, "SEQ1")
        seq3 = project.Sequence(new_proj, "SEQ2")

        new_proj2 = project.Project("TEST_PROJECT2")
        new_proj2.create()
        seq4 = project.Sequence(new_proj2, "SEQ3")

        self.assertFalse(seq1 != seq2)
        self.assertTrue(seq1 != seq3)
        self.assertTrue(seq1 != seq4)
        self.assertTrue(seq3 != seq4)


class Sequence_To_NewType_Conversion(unittest.TestCase):
    """tests the conversion of old type Sequences to new type Sequences with
    SQLite3 databases.
    """

    def setUp(self):
        """testing the settings path from the environment variable
        """
        
        # create an old type sequence
        # and check if it is correctly converted to a new type database
        
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
            self.temp_settings_folder
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

        self._name_test_values = [
            ("test project", "TEST_PROJECT"),
            ("123123 test_project", "TEST_PROJECT"),
            ("123432!+!'^+Test_PRoject323^+'^%&+%&324", "TEST_PROJECT323324"),
            ("    ---test 9s_project", "TEST_9S_PROJECT"),
            ("    ---test 9s-project", "TEST_9S_PROJECT"),
            (" multiple     spaces are    converted to under     scores",
             "MULTIPLE_SPACES_ARE_CONVERTED_TO_UNDER_SCORES"),
            ("camelCase", "CAMEL_CASE"),
            ("CamelCase", "CAMEL_CASE"),
            ("_Project_Setup_", "PROJECT_SETUP_"),
            ("_PROJECT_SETUP_", "PROJECT_SETUP_"),
            ("FUL_3D", "FUL_3D"),
        ]


    def tearDown(self):
        """remove the temp folders
        """
        
        # delete the temp folder
        shutil.rmtree(self.temp_settings_folder)
        shutil.rmtree(self.temp_projects_folder)



class Sequence_NewType_Tester(unittest.TestCase):
    """Tests the new type Sequence class
    """
    
    #----------------------------------------------------------------------
    def setUp(self):
        
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
            self.temp_settings_folder
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
    
    
    def tearDown(self):
        """clean up the test
        """
        
        # delete the temp folder
        shutil.rmtree(self.temp_settings_folder)
        shutil.rmtree(self.temp_projects_folder)
    
    
    def test_sequence_raises_error_when_the_given_project_is_not_created_yet(self):
        """testing if the sequence raises an error when the project is not
        created yet
        """
        
        new_proj = Project(name="TEST_PROJECT")
        self.assertRaises(RuntimeError, Sequence, new_proj, name="TEST_SEQ")
    
    
    
#    def test_database_file_is_created(self):
#        """testing if a database file is created
#        """
#        
#        new_proj = Project(name="TEST_PROJECT")
#        new_proj.create()
#        
#        new_seq = Sequence(new_proj, "TEST_SEQ1")
#        new_seq.create()
#        
#        self.assertTrue(
#            os.path.exists(
#                os.path.join(
#                    new_seq.fullPath,
#                    conf.DATABASE_FILE_NAME
#                )
#            )
#        )
    
    def test_sequence_session_is_project_session(self):
        """testing if the session instance is passed correctly to the sequence
        instance
        """
        
        new_proj = Project(name="TEST_PROJECT")
        new_proj.create()
        
        new_seq = Sequence(new_proj, name="TEST_SEQ")
        new_seq.create()
        
        self.assertIs(new_proj.session, new_seq.session)
    
    
    def test_database_simple_data(self):
        """testing if the database file has the necessary information related to
        the Sequence
        """
        
        new_proj = Project(name="TEST_PROJECT")
        new_proj.create()
        
        test_seq_name = "TEST_SEQ1"
        new_seq = Sequence(new_proj, test_seq_name)
        new_seq.create()
        
        # fill it with some non default values
        shotPrefix = new_seq.shotPrefix = "PL"
        shotPadding = new_seq.shotPadding = 13
        revPrefix = new_seq.revPrefix = "rev"
        revPadding = new_seq.revPadding = 18
        verPrefix = new_seq.verPrefix = "ver"
        verPadding = new_seq.verPadding = 8
        
        print new_seq.fullPath
        
        new_seq.create()
        
        # now check if the database is created correctly
        del new_seq
        
        # create the seq from scratch and let it read the database
        new_seq = db.session.query(Sequence).first()
        
        # now check if it was able to get these data
        self.assertEqual(shotPrefix, new_seq.shotPrefix)
        self.assertEqual(shotPadding, new_seq.shotPadding)
        self.assertEqual(revPrefix, new_seq.revPrefix)
        self.assertEqual(revPadding, new_seq.revPadding)
        self.assertEqual(verPrefix, new_seq.verPrefix)
        self.assertEqual(verPadding, new_seq.verPadding)

    
    def test_database_recreation_of_sequence_object(self):
        """testing if the database file has the necessary information related to
        the Sequence
        """
        
        new_proj = Project(name="TEST_PROJECT")
        new_proj.create()
        
        print "new_proj.fullPath: ", new_proj.fullPath
        
        test_seq_name = "TEST_SEQ1"
        new_seq = Sequence(new_proj, test_seq_name)
        
        # fill it with some non default values
        shotPrefix = new_seq.shotPrefix = "PL"
        shotPadding = new_seq.shotPadding = 13
        revPrefix = new_seq.revPrefix = "rev"
        revPadding = new_seq.revPadding = 18
        verPrefix = new_seq.verPrefix = "ver"
        verPadding = new_seq.verPadding = 8
        
        print "new_seq.fullPath: ", new_seq.fullPath
        
        new_seq.create()
        
        # now check if the database is created correctly
        del new_seq
        
        # create the seq from scratch and let it read the database
        print "TEST CREATING A NEW SEQ"
        new_seq = Sequence(new_proj, test_seq_name)
        
        # now check if it was able to get these data
        self.assertEqual(shotPrefix, new_seq.shotPrefix)
        self.assertEqual(shotPadding, new_seq.shotPadding)
        self.assertEqual(revPrefix, new_seq.revPrefix)
        self.assertEqual(revPadding, new_seq.revPadding)
        self.assertEqual(verPrefix, new_seq.verPrefix)
        self.assertEqual(verPadding, new_seq.verPadding)
    
    
    def test_calling_create_multiple_times(self):
        """testing if no error will be raised when calling Sequence.create
        multiple times
        """
        
        new_proj = Project(name="TEST_PROJECT")
        new_proj.create()
        
        new_seq = Sequence(new_proj, "TEST_SEQ")
        
        # now call create multiple times
        new_seq.create()
        new_seq.create()
        new_seq.create()
        new_seq.create()
        new_seq.create()
    
    
    def test_creating_two_different_shots_and_calling_create(self):
        """testing if no error will be raised when creating two different
        sequences for the same Project and calling the create of the Sequences
        in mixed order
        """
        
        new_proj = Project(name="TEST_PROJECT")
        new_proj.create()
        
        new_seq1 = Sequence(new_proj, "TEST_SEQ1")
        new_seq2 = Sequence(new_proj, "TEST_SEQ2")
        
        print "calling new_seq1.create"
        new_seq1.create()
        print "calling new_seq2.create"
        new_seq2.create()
        
    
