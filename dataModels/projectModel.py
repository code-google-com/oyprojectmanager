import os, re, shutil, glob
from xml.dom import minidom
import oyAuxiliaryFunctions as oyAux
from oyProjectManager.tools import cache, rangeTools
from oyProjectManager.dataModels import assetModel, userModel, repositoryModel



__version__ = "9.12.29"






########################################################################
class Project(object):
    """Project object to help manage project data
    """
    
    
    
    #----------------------------------------------------------------------
    def __init__(self, projectName, repositoryObj = None):
        
        if repositoryObj == None:
            self._repository = repositoryModel.Repository()
        else:
            self._repository = repositoryObj
        
        self._name = oyAux.stringConditioner( projectName, False, True, False, True, True, False )
        self._path = ''
        self._fullPath = ''
        
        self._initPathVariables()
        
        self._sequenceList = []
        
        self._exists = self.exists()
    
    
    
    #----------------------------------------------------------------------
    def _initPathVariables(self):
        self._path = self._repository._projectsFolderFullPath
        self._fullPath = os.path.join( self._path, self._name)
    
    
    
    #----------------------------------------------------------------------
    def create(self):
        """creates the project
        """
        # check if the folder allready exists
        oyAux.createFolder( self._fullPath )
        self._exists = self.exists()
    
    
    
    #----------------------------------------------------------------------
    def createSequence(self, sequenceName, shots ):
        """creates a sequence and returns the sequence object
        """
        newSequence = Sequence( self, sequenceName )
        newSequence.addShots( shots )
        newSequence.create()
        
        return newSequence
    
    
    
    #----------------------------------------------------------------------
    @cache.CachedMethod
    def getSequenceNames(self):
        """returns the sequence names of that project
        """
        self.updateSequenceList()
        return self._sequenceList
    
    
    
    #----------------------------------------------------------------------
    @cache.CachedMethod
    def getSequences(self):
        """returns the sequences as sequence objects
        
        don't use it offen, because it causes the system to parse all the sequence settings
        for all the sequences under that project
        
        it is now using the caching mechanism use it freely
        """
        
        self.updateSequenceList()
        sequences = [] * 0
        
        for sequenceName in self._sequenceList:
            sequences.append( Sequence( self, sequenceName) )
        
        return sequences
    
    
    
    #----------------------------------------------------------------------
    def updateSequenceList(self):
        """updates the sequenceList variable
        """
        self._sequenceList = os.listdir( self._fullPath )
        self._sequenceList.sort()
    
    
    
    #----------------------------------------------------------------------
    def getFullPath(self):
        return self._fullPath
    
    
    
    #----------------------------------------------------------------------
    def getRepository(self):
        """returns the current project repository object
        """
        return self._repository
    
    
    
    #----------------------------------------------------------------------
    def setRepository(self, repository ):
        """sets the project repository object
        """
        
        self._repository = repository
        
        # reset the path variables
        self._initPathVariables
    
    
    
    #----------------------------------------------------------------------
    def getName(self):
        """ returns the name of the project
        """
        return self._name
    
    
    
    #----------------------------------------------------------------------
    def exists(self):
        """returns True if the project folder exists
        """
        
        return os.path.exists( self._fullPath )
    
    
    
    ##----------------------------------------------------------------------
    #def setProject(self, projectName):
        #"""renews the object to a new project
        #"""
        
        #self = Project( projectName )






########################################################################
class Sequence(object):
    """Sequence object to help manage sequence data
    
    the class should be initialized with the projectName a sequenceName
    """
    
    
    
    #----------------------------------------------------------------------
    def __init__(self, project, sequenceName):
        # create the parent project with projectName
        
        assert(isinstance(project, Project) )
        
        self._parentProject = project
        self._repository = self._parentProject.getRepository()
        
        self._name = oyAux.stringConditioner( sequenceName, False, True, False, True, True, False )
        
        self._path = self._parentProject.getFullPath()
        self._fullPath = os.path.join( self._path, self._name )
        
        self._settingsFile = ".settings.xml"
        self._settingsFilePath = self._fullPath
        self._settingsFileFullPath = os.path.join( self._settingsFilePath, self._settingsFile )
        self._settingsFileExists = False
        
        self._structure = Structure()
        self._assetTypes = [ assetModel.AssetType() ] * 0
        self._shotList = [] * 0 # should be a string
        self._shots = [] # the new shot objects
        
        self._shotPrefix = 'SH'
        self._shotPadding = 3
        self._revPrefix = 'r' # revision number prefix
        self._revPadding = 2
        self._verPrefix = 'v' # version number prefix
        self._verPadding = 3
        
        self._extensionsToIgnore = [] * 0
        self._noSubNameField = False # to support the old types of projects
        
        self._environment = None # the working environment
        
        self._exists = False
        
        self.readSettings()
    
    
    
    #----------------------------------------------------------------------
    def readSettings(self):
        """reads the settingsFile
        """
        
        # check if there is a settings file
        if not os.path.exists( self._settingsFileFullPath ):
            #print "ERROR: no settings file in the sequence..."
            # TODO: assume that it is an old project and try to get
            # the data (just shot list) from the folders
            return
        else:
            self._settingsFileExists = True
            self._exists = True
        
        #print (self._settingsFileFullPath)
        settingsAsXML = minidom.parse( self._settingsFileFullPath )
        
        rootNode = settingsAsXML.childNodes[0]
        
        # -----------------------------------------------------
        # get main nodes
        
        # remove databaseData if exists
        doRemoveDatabaseDataNode = False
        databaseDataNode = rootNode.getElementsByTagName('databaseData')
        
        if len(databaseDataNode) > 0:
            # there should be a databaseData node
            doRemoveDatabaseDataNode = True
            
            # parse the databaseData nodes attributes as if it is a
            # sequenceDataNode
            self._parseSequenceDataNodesAttributes( databaseDataNode[0] )
        
        sequenceDataNode = rootNode.getElementsByTagName('sequenceData')[0]
        
        if not doRemoveDatabaseDataNode:
            self._parseSequenceDataNodesAttributes( sequenceDataNode ) 
        
        # -----------------------------------------------------
        # get sequence nodes
        structureNode = sequenceDataNode.getElementsByTagName('structure')[0]
        assetTypesNode = sequenceDataNode.getElementsByTagName('assetTypes')[0]
        shotDataNodes = sequenceDataNode.getElementsByTagName('shotData')
        
        
        doConvertionToShotData = False
        
        if len(shotDataNodes) == 0:
            doConvertionToShotData = True
        
        # parse all nodes
        self._parseAssetTypesNode( assetTypesNode )
        self._parseStructureNode( structureNode )
        
        if doConvertionToShotData:
            # 
            # it should be an old type of settings file
            # convert it to the new shotData concept
            # 
            shotListNode = sequenceDataNode.getElementsByTagName('shotList')[0]
            #print "converting to shotData concept !!!"
            
            # read the shot numbers from the shotList node and create appropriate
            # shot data nodes
            
            # parse the shotListNode to get the shot list
            self._parseShotListNode( shotListNode )
            
            self._convertShotListToShotData()
            
            # update the settings file
            self.saveSettings()
        else:
            self._parseShotDataNode( shotDataNodes[0] )
        
        if doRemoveDatabaseDataNode:
            # just save the settings over it self, it should be fine
            self.saveSettings()
    
    
    
    #----------------------------------------------------------------------
    def _parseSequenceDataNodesAttributes(self, sequenceDataNode ):
        """parses sequenceDataNode nodes attributes
        """
        
        #assert( isinstance( sequenceDataNode, minidom.Element) )
        
        self._shotPrefix = sequenceDataNode.getAttribute('shotPrefix')
        self._shotPadding = int( sequenceDataNode.getAttribute('shotPadding') )
        self._revPrefix = sequenceDataNode.getAttribute('revPrefix')
        self._revPadding = sequenceDataNode.getAttribute('revPadding')
        self._verPrefix = sequenceDataNode.getAttribute('verPrefix')
        self._verPadding = sequenceDataNode.getAttribute('verPadding')
        
        if sequenceDataNode.hasAttribute('extensionsToIgnore'):
            self._extensionsToIgnore = sequenceDataNode.getAttribute('extensionsToIgnore').split(',')
        
        if sequenceDataNode.hasAttribute('noSubNameField'):
            self._noSubNameField = bool( eval( sequenceDataNode.getAttribute('noSubNameField') ) )
    
    
    
    #----------------------------------------------------------------------
    def _parseStructureNode(self, structureNode):
        """parses structure node from the XML file
        """
        
        #assert( isinstance( structureNode, minidom.Element ) )
        
        # -----------------------------------------------------
        # get shot dependent/independent folders
        shotDependentFoldersNode = structureNode.getElementsByTagName('shotDependent')[0]
        shotDependentFoldersList = shotDependentFoldersNode.childNodes[0].wholeText.split('\n')
        
        shotIndependentFoldersNode = structureNode.getElementsByTagName('shotIndependent')[0]
        shotIndependentFoldersList = shotIndependentFoldersNode.childNodes[0].wholeText.split('\n')
        
        # strip the elements and remove empty elements
        shotDependentFoldersList = [ folder.strip() for folder in shotDependentFoldersList if folder.strip() != ""  ]
        shotIndependentFoldersList = [ folder.strip() for folder in shotIndependentFoldersList if folder.strip() != ""  ]
        
        # fix path issues for windows
        osName = os.name
        
        if osName=='nt':
            shotDependentFoldersList = [ oyAux.fixWindowsPath(path) for path in shotDependentFoldersList]
            shotIndependentFoldersList = [ oyAux.fixWindowsPath(path) for path in shotIndependentFoldersList]
        
        # set the structure
        self._structure.setShotDependentFolders( shotDependentFoldersList )
        self._structure.setShotIndependentFolders( shotIndependentFoldersList )
        
        # read the output folders node
        outputFoldersNode = structureNode.getElementsByTagName('outputFolders')[0]
        outputNodes = outputFoldersNode.getElementsByTagName('output')
        
        # clear the data
        self._structure._outputFolders = list()
        for outputNode in outputNodes:
            #assert(isinstance(outpuNode, minidom.Element))
            name = outputNode.getAttribute('name')
            path = outputNode.getAttribute('path')
            
            # fixe path issues for windows
            if osName == 'nt':
                path = oyAux.fixWindowsPath( path )
            
            self._structure.addOutputFolder( name, path )
    
    
    
    #----------------------------------------------------------------------
    def _parseAssetTypesNode(self, assetTypesNode):
        """parses assetTypes node from the XML file
        """
        
        #assert( isinstance( assetTypesNode, minidom.Element) )
        
        # -----------------------------------------------------
        # read asset types
        self._assetTypes = [] * 0
        for node in assetTypesNode.getElementsByTagName('type'):
            #assert( isinstance( node, minidom.Element) )
            
            name = node.getAttribute('name')
            path = node.getAttribute('path')
            shotDependency = bool( int( node.getAttribute('shotDependent') ) )
            playblastFolder = node.getAttribute('playblastFolder')
            environments = node.getAttribute('environments').split(",")
            
            # fix path issues for windows
            if os.name == 'nt':
                path = oyAux.fixWindowsPath( path )
                playblastFolder = oyAux.fixWindowsPath( playblastFolder )
            
            self._assetTypes.append( assetModel.AssetType( name, path, shotDependency, playblastFolder, environments) )
    
    
    
    #----------------------------------------------------------------------
    def _parseShotListNode(self, shotListNode):
        """parses shotList node from the XML file
        """
        
        #assert( isinstance( shotListNode, minidom.Element) )
        
        # -----------------------------------------------------
        # get shot list only if the current shot list is empty
        if len(self._shotList) == 0:
            if len(shotListNode.childNodes):
                self._shotList  = [ shot.strip() for shot in shotListNode.childNodes[0].wholeText.split('\n') if shot.strip() != "" ]
        
        # sort the shot list
        self._shotList = oyAux.sort_strings_with_embedded_numbers( self._shotList )
    
    
    
    #----------------------------------------------------------------------
    def _parseShotDataNode(self, shotDataNode):
        """parses shotData node from the XML file
        """
        
        #assert( isinstance( shotDataNode, minidom.Element) )
        
        for shotNode in shotDataNode.getElementsByTagName('shot'):
            #assert( isinstance( shotNode, minidom.Element ) )
            
            startFrame = shotNode.getAttribute( 'startFrame' )
            endFrame = shotNode.getAttribute( 'endFrame' )
            name = shotNode.getAttribute( 'name' )
            description = shotNode.getElementsByTagName('description')[0].childNodes[0].wholeText.strip()
            
            if startFrame != '':
                startFrame = int(startFrame)
            else:
                startFrame = 0
            
            if endFrame != '':
                endFrame = int(endFrame)
            else:
                endFrame = 0
            
            # create shot objects with the data
            newShot = Shot()
            newShot.startFrame = startFrame
            newShot.endFrame = endFrame
            newShot.name = name
            newShot.description = description
            
            # append the shot to the self._shots
            self._shots.append( newShot )
            
            # also append the name to the shotList
            self._shotList.append( name )
        
        # sort the shot list
        self._shotList = oyAux.sort_strings_with_embedded_numbers( self._shotList )
        
        
    
    
    #----------------------------------------------------------------------
    def _convertShotListToShotData(self):
        """converts the shot list node in the settings to shotData node
        """
        
        # now we should have the self._shotList filled
        # create the shot objects with default values and the shot names from
        # the shotList
        
        for shotName in self._shotList:
            newShot = Shot()
            newShot.name = shotName
            self._shots.append( newShot )
    
    
    
    #----------------------------------------------------------------------
    def saveSettings(self):
        """saves the settings as XML
        """
        
        # create nodes
        rootNode = minidom.Element('root')
        sequenceDataNode = minidom.Element('sequenceData')
        structureNode = minidom.Element('structure')
        shotDependentNode = minidom.Element('shotDependent')
        shotDependentNodeText = minidom.Text()
        shotIndependentNode = minidom.Element('shotIndependent')
        shotIndependentNodeText = minidom.Text()
        assetTypesNode = minidom.Element('assetTypes')
        typeNode = minidom.Element('type')
        
        #shotListNode = minidom.Element('shotList')
        #shotListNodeText = minidom.Text()
        
        shotDataNode = minidom.Element('shotData')
        
        
        
        #----------------------------------------------------------------------
        # SEQUENCE DATA and childs
        #----------------------------------------------------------------------
        # set repository node attributes
        sequenceDataNode.setAttribute('shotPrefix', self._shotPrefix)
        sequenceDataNode.setAttribute('shotPadding', unicode( self._shotPadding ) )
        sequenceDataNode.setAttribute('revPrefix', self._revPrefix)
        sequenceDataNode.setAttribute('revPadding', unicode( self._revPadding ) )
        sequenceDataNode.setAttribute('verPrefix', self._verPrefix)
        sequenceDataNode.setAttribute('verPadding', unicode( self._verPadding ) )
        sequenceDataNode.setAttribute('extensionsToIgnore', unicode( ','.join(self._extensionsToIgnore)) )
        
        if self._noSubNameField:
            sequenceDataNode.setAttribute('noSubNameField', unicode( self._noSubNameField ) )
        #----------------------------------------------------------------------
        
        
        
        
        #----------------------------------------------------------------------
        # SHOT DEPENDENT / INDEPENDENT FOLDERS
        #----------------------------------------------------------------------
        # create shot dependent/independent folders
        shotDependentNodeText.data = '\n'.join( self._structure.getShotDependentFolders() ).replace('\\','/')
        shotIndependentNodeText.data = '\n'.join( self._structure.getShotIndependentFolders() ).replace('\\','/')
        #----------------------------------------------------------------------
        
        
        
        #----------------------------------------------------------------------
        # SHOT DATA
        #----------------------------------------------------------------------
        
        ## create shot list text data
        ## sort the shotList
        #self._shotList = oyAux.sort_strings_with_embedded_numbers( self._shotList )
        ##shotListNodeText.data = '\n'.join( self._shotList )
        
        # create the new type of shotData nodes
        for shot in self._shots:
            # create a shot node
            #assert(isinstance(shot,Shot))
            shotNode = minidom.Element('shot')
            shotNode.setAttribute('startFrame', str(shot.startFrame) )
            shotNode.setAttribute('endFrame', str(shot.endFrame) )
            shotNode.setAttribute('name', shot.name)
            
            # create a description node and store the shot description as the node text
            descriptionNode = minidom.Element('description')
            
            # create the text node
            descriptionText = minidom.Text()
            descriptionText.data = shot.description
            
            # append the nodes to appropriate parents
            descriptionNode.appendChild( descriptionText )
            shotNode.appendChild( descriptionNode )
            shotDataNode.appendChild( shotNode )
        #----------------------------------------------------------------------
        
        
        
        #----------------------------------------------------------------------
        # ASSET TYPE
        #----------------------------------------------------------------------
        
        # create asset types
        for aType in self._assetTypes:
            #assert( isinstance( aType, assetModel.AssetType ) )
            typeNode = minidom.Element('type')
            typeNode.setAttribute( 'name', aType.getName() )
            typeNode.setAttribute( 'path', aType.getPath().replace('\\','/') )
            typeNode.setAttribute( 'shotDependent', unicode( int( aType.isShotDependent() ) ) )
            typeNode.setAttribute( 'playblastFolder', aType.getPlayblastFolder().replace('\\','/') )
            typeNode.setAttribute( 'environments', ",".join( aType.getEnvironments() ) )
            
            assetTypesNode.appendChild( typeNode )
        #----------------------------------------------------------------------
        
        
        
        #----------------------------------------------------------------------
        # OUTPUT FOLDERS
        #----------------------------------------------------------------------
        outputFoldersNode = minidom.Element('outputFolders')
        for fTuple in self._structure.getOutputFolders():
            
            outputNode = minidom.Element('output')
            outputNode.setAttribute( 'name', fTuple[0] )
            outputNode.setAttribute( 'path', fTuple[1].replace('\\','/') )
            
            outputFoldersNode.appendChild( outputNode )
        #----------------------------------------------------------------------
        
        
        
        # append childs
        rootNode.appendChild( sequenceDataNode )
        
        sequenceDataNode.appendChild( structureNode )
        sequenceDataNode.appendChild( assetTypesNode )
        sequenceDataNode.appendChild( shotDataNode )
        
        structureNode.appendChild( shotDependentNode )
        structureNode.appendChild( shotIndependentNode )
        structureNode.appendChild( outputFoldersNode )
        
        shotDependentNode.appendChild( shotDependentNodeText )
        shotIndependentNode.appendChild( shotIndependentNodeText )
        
        #shotListNode.appendChild( shotListNodeText )
        
        # create XML file
        settingsXML = minidom.Document()
        settingsXML.appendChild( rootNode )
        
        try:
            # if there is a settings file backit up
            oyAux.backupFile( self._settingsFileFullPath )
            settingsFile = open( self._settingsFileFullPath, 'w' )
        except IOError:
            #print "couldn't open the settings file"
            pass
        finally:
            settingsXML.writexml( settingsFile, "\t", "\t", "\n" )
            settingsFile.close()
            self._settingsFileExists = True
    
    
    
    #----------------------------------------------------------------------
    def create(self):
        """creates the sequence
        """
        
        # if the sequence doesn't exist create the folder
        
        if not self._exists:
            # create a folder with sequenceName
            exists = oyAux.createFolder( self._fullPath )
            
            # copy the settings file to the root of the sequence
            shutil.copy( self._repository._defaultSettingsFullPath, self._settingsFileFullPath )
        
        # just read the structure from the XML
        self.readSettings()
        
        # tell the sequence to create its own structure
        self.createStructure()
        
        # and create the shots
        self.createShots()
        
        # copy any file to the sequence
        # (like workspace.mel)
        for _fileInfo in self._repository.getDefaultFiles():
            sourcePath = os.path.join( _fileInfo[2], _fileInfo[0] )
            targetPath = os.path.join( self._fullPath, _fileInfo[1], _fileInfo[0] )
            
            shutil.copy( sourcePath, targetPath )
    
    
    
    #----------------------------------------------------------------------
    def addShots(self, shots ):
        """adds new shots to the sequence
        
        shots should be a range in on of the following format:
        #
        #,#
        #-#
        #,#-#
        #,#-#,#
        #-#,#
        etc.
        
        you need to invoke self.createShots to make the changes permenant
        """
        
        # for now consider the shots as a string of range
        # do the hard work later
        
        newShotsList = rangeTools.RangeConverter.convertRangeToList( shots )
        
        # convert the list to strings
        newShotsList = map(str, newShotsList)
        
        # add the shotList to the current _shotList
        self._shotList = oyAux.unique( oyAux.concatenateLists( self._shotList, newShotsList ) )
        
        # sort the shotList
        self._shotList = oyAux.sort_strings_with_embedded_numbers( self._shotList )
        
        # just create shot objects with shot name and leave the start and end frame and
        # description empty, it will be edited later
        newShotObjects = []
        for shotName in newShotList:
            shot = Shot()
            shot.name = shotName
            
            newShotObjects.append( shot )
        
        # add the new shot objects to the existing ones
        self._shots = oyAux.unique( oyAux.concatenateLists( self._shots, newShotObjects ) )
        
        # sort the shot objects
        self._shots = oyAux.sort_strings_with_embedded_numbers( self._shots )
        
    
    
    
    #----------------------------------------------------------------------
    def addAlternativeShot(self, shotNumber):
        """adds a new alternative to the given shot
        
        you need to invoke self.createShots to make the changes permanent
        """
        
        # shotNumber could be an int convert it to str
        shotNumberAsString = str(shotNumber)
        
        # get the first integer as int in the string
        shotNumber = oyAux.embedded_numbers( shotNumberAsString )[1]
        
        # get the next available alternative shot number for that shot
        alternativeShotNumber = self.getNextAlternateShotNumber( shotNumber )
        
        # add that alternative shot to the shot list
        if alternativeShotNumber != None:
            self._shotList.append( alternativeShotNumber )
    
    
    
    #----------------------------------------------------------------------
    def getNextAlternateShotNumber(self, shot):
        """returns the next alternate shot number for the given shot number
        """
        
        # get the shot list
        shotList = self.getShotList()
        alternateLetters = 'ABCDEFGHIJKLMNOPRSTUVWXYZ'
        
        for letter in alternateLetters:
            #check if the alternate is in the list
            
            newShotNumber = str(shot) + letter
            
            if not newShotNumber in shotList:
                return newShotNumber
        
        return None
    
    
    
    #----------------------------------------------------------------------
    def createShots(self):
        """creates the shot folders in the structure
        """
        if not self._exists:
            return
        
        #for folder in self._shotFolders:
        for folder in self._structure.getShotDependentFolders():
            for shotNumber in self._shotList:
                # get a shotString for that number
                shotString = self.convertToShotString( shotNumber )
                
                # create the folder with that name
                shotFullPath = os.path.join ( self._fullPath, folder, shotString )
                
                #self._repository._create_folder( shotFullPath )
                oyAux.createFolder( shotFullPath )
        
        # update settings
        self.saveSettings()
    
    
    
    #----------------------------------------------------------------------
    def getShotFolders(self):
        """returns the shot folder paths
        """
        if not self._exists:
            return
        
        return self._structure.getShotDependentFolders()
    
    
    
    #----------------------------------------------------------------------
    def getShotList(self):
        """returns the shot list object
        """
        return self._shotList
    
    
    
    #----------------------------------------------------------------------
    def getStructure(self):
        """returns the structure object
        """
        return self._structure
    
    
    
    #----------------------------------------------------------------------
    def createStructure(self):
        """creates the folders defined by the structure
        """
        if not self._exists:
            return
        
        createFolder = oyAux.createFolder
        
        # create the structure
        for folder in self._structure.getShotDependentFolders():
            createFolder( os.path.join( self._fullPath, folder ) )
        
        for folder in self._structure.getShotIndependentFolders():
            createFolder( os.path.join( self._fullPath, folder ) )
    
    
    
    #----------------------------------------------------------------------
    def convertToShotString(self, shotNumber ):
        """ converts the input shot number to a padded shot string
        
        for example it converts:
        1   --> SH001
        10  --> SH010
        
        if there is an alternate letter it will add it to the end of the
        shot string, like:
        1a  --> SH001A
        10S --> SH010S
        
        it also properly converts inputs like this
        abc92a --> SH092A
        abc323d432e --> SH323D
        abc001d --> SH001D
        
        if the shotNumber argument is None it will return None
        
        for now it can't convert properly if there is more than one letter at the end like:
        abc23defg --> SH023DEFG
        """
        
        pieces = oyAux.embedded_numbers( unicode(shotNumber) )
        
        if len(pieces) <= 1:
            return None
        
        number = pieces[1]
        alternateLetter = pieces[2]
        
        return self._shotPrefix + oyAux.padNumber( number, self._shotPadding ) + alternateLetter.upper()
    
    
    
    #----------------------------------------------------------------------
    def convertToRevString(self, revNumber):
        """converts the input revision number to a padded revision string
        
        for example it converts:
        1  --> r01
        10 --> r10
        """
        return self._revPrefix + oyAux.padNumber( revNumber, self._revPadding )
    
    
    
    #----------------------------------------------------------------------
    def convertToVerString(self, verNumber):
        """converts the input version number to a padded version string
        
        for example it converts:
        1  --> v001
        10 --> v010
        """
        return self._verPrefix + oyAux.padNumber( verNumber, self._verPadding )
    
    
    
    #----------------------------------------------------------------------
    def convertToShotNumber(self, shotString):
        """beware that it returns a string, it returns the number plus the alternative
        letter (if exists) as a string
        
        for example it converts:
        
        SH001 --> 1
        SH041a --> 41a
        etc.
        """
        
        # remove the shot prefix
        remainder = shotString[ len(self._shotPrefix) : len(shotString) ]
        
        # get the integer part
        matchObj = re.match('[0-9]+',remainder)
        
        if matchObj:
            numberAsStr = matchObj.group()
        else:
            return None
        
        alternateLetter = ''
        if len(numberAsStr) < len(remainder):
            alternateLetter = remainder[len(numberAsStr):len(remainder)]
        
        # convert the numberAsStr to a number then to a string then add the alternate letter
        return unicode(int(numberAsStr)) + alternateLetter
    
    
    
    #----------------------------------------------------------------------
    def convertToRevNumber(self, revString):
        """converts the input revision string to a revision number
        
        for example it converts:
        r01 --> 1
        r10 --> 10
        """
        return int(revString[len(self._revPrefix):len(revString)])
    
    
    
    #----------------------------------------------------------------------
    def convertToVerNumber(self, verString):
        """converts the input version string to a version number
        
        for example it converts:
        v001 --> 1
        v010 --> 10
        """
        return int(verString[len(self._verPrefix):len(verString)])
    
    
    
    #----------------------------------------------------------------------
    @cache.InputBasedCachedMethod
    def getAssetTypes(self, environment=None):
        """returns a list of AssetType objects that this project has
        
        if the environment is set something other then None only the assetTypes
        for that environment is returned
        """
        
        
        if environment==None:
            return self._assetTypes
        else:
            aTypesList = [] * 0
            
            for aType in self._assetTypes:
                #assert(isinstance(aType, assetModel.AssetType) )
                if environment in aType.getEnvironments():
                    aTypesList.append( aType )
            
            return aTypesList
    
    
    
    #----------------------------------------------------------------------
    @cache.InputBasedCachedMethod
    def getAssetTypeWithName(self, typeName):
        """returns the assetType object that has the name typeName.
        if it can't find any assetType that has the name typeName it returns None
        """
        
        for aType in self._assetTypes:
            if aType.getName() == typeName:
                return aType
        
        return None
    
    
    
    #----------------------------------------------------------------------
    def getName(self):
        """returns the name of the sequence
        """
        return self._name
    
    
    
    #----------------------------------------------------------------------
    def getPath(self):
        """returns the path of the sequence
        """
        return self._path
    
    
    
    #----------------------------------------------------------------------
    def getFullPath(self):
        """returns the full path of the sequence
        """
        return self._fullPath
    
    
    
    #----------------------------------------------------------------------
    def getProject(self):
        """returns the parent project
        """
        return self._parentProject
    
    
    
    #----------------------------------------------------------------------
    def getProjectName(self):
        """returns the parent projects name
        """
        return self._parentProject.getName()
    
    
    
    #----------------------------------------------------------------------
    @cache.CachedMethod
    def getAssetFolders(self):
        """returns all asset folders
        """
        
        # look at the assetType folders
        assetFolders = [] * 0
        
        for aType in self._assetTypes:
            #assert(isinstance(aType, AssetType))
            assetFolders.append( aType.getPath() )
        
        return assetFolders
    
    
    
    #----------------------------------------------------------------------
    @cache.CachedMethod
    def getAllAssets(self):
        """returns Asset objects for all the assets of the sequence
        beware that this method uses a very simple caching algorithm, so it
        tries to reduce file system overhead
        """
        
        # get asset folders
        # look at the child folders
        # and then look at the files under the child folders
        # if a file starts with the folder name
        # mark it as an asset
        
        assets = [] * 0
        
        # get the asset folders
        assetFolders = self.getAssetFolders()
        
        
        # optimization variables
        osPathJoin = os.path.join
        oyAuxGetChildFolders = oyAux.getChildFolders
        osPathBaseName = os.path.basename
        globGlob = glob.glob
        assetModelAsset = assetModel.Asset
        assetsAppend = assets.append
        selfFullPath = self._fullPath
        selfProject = self.getProject()
        
        # for each folder search child folders
        for folder in assetFolders:
            fullPath = osPathJoin( selfFullPath, folder)
            
            # 
            # skip if the folder doesn't exists
            # 
            # it is a big problem in terms of management but some old type projects
            # has missing folders, because the folders will be created whenever somebody
            # uses that folder while saving an asset, we don't care about its non existancy
            #
            #if not os.path.exists( fullPath ):
##            if not osPathExists( fullPath ):
##                continue
            
            # use glob instead of doing it by hand
            childFolders = oyAuxGetChildFolders( fullPath, True )
            
            for folder in childFolders:
                # get possible asset files directly by using glob
                pattern = osPathBaseName( folder ) + '*'
                
                # files are in fullpath format
                matchedFiles = globGlob( osPathJoin( folder, pattern ) )
                
                matchedFileCount = len(matchedFiles)
                
                if matchedFileCount > 0:
                    # there should be some files matching the pattern
                    # check if they are valid assets
                    
                    matchedAssets = map( assetModelAsset, [selfProject] * matchedFileCount, [self] * matchedFileCount, map(osPathBaseName, matchedFiles) )
                    
                    # append them to the main assets list
                    [ assetsAppend(matchedAsset) for matchedAsset in matchedAssets if matchedAsset.isValidAsset() ]
        
        return assets
    
    
    
    #----------------------------------------------------------------------
    @cache.InputBasedCachedMethod
    def getAllAssetsForType(self, typeName):
        """returns Asset objects for just the given type of the sequence
        """
        
        # get asset folders
        # look at the child folders
        # and then look at the files under the child folders
        # if a file starts with the folder name
        # mark it as an asset
        
        assets = [] * 0
        
        # get the asset folders
        #assetFolders = self.getAssetFolders()
        
        aType = self.getAssetTypeWithName( typeName )
        
        #assert(isinstance(aType,assetModel.AssetType))
        assetFolder = aType.getPath()
        
        # optimization variables
        osPathExists = os.path.exists
        osPathJoin = os.path.join
        oyAuxGetChildFolders = oyAux.getChildFolders
        osPathBaseName = os.path.basename
        globGlob = glob.glob
        assetModelAsset = assetModel.Asset
        assetsAppend = assets.append
        selfFullPath = self._fullPath
        selfProject = self.getProject()
        
        fullPath = osPathJoin( selfFullPath, assetFolder)
        
        # 
        # skip if the folder doesn't exists
        # 
        # it is a big problem in terms of management but some old type projects
        # has missing folder, because the folders will be created whenever somebody
        # uses that folder while saving an asset, we don't care about its non existancy
        #
        #if not os.path.exists( fullPath ):
        if not osPathExists( fullPath ):
            return []
        
        # use glob instead of doing it by hand
        childFolders = oyAuxGetChildFolders( fullPath, True )
        
        for folder in childFolders:
            # get possible asset files directly by using glob
            pattern = osPathBaseName( folder ) + '*'
            
            # files are in fullpath format
            matchedFiles = globGlob( osPathJoin( folder, pattern ) )
            
            matchedFileCount = len(matchedFiles)
            
            if matchedFileCount > 0:
                # there should be some files matching the pattern
                # check if they are valid assets
                
                matchedAssets = map( assetModelAsset, [selfProject] * matchedFileCount, [self] * matchedFileCount, map(osPathBaseName, matchedFiles) )
                
                # append them to the main assets list
                [ assetsAppend(matchedAsset) for matchedAsset in matchedAssets if matchedAsset.isValidAsset() ]
        return assets
    
    
    
    #----------------------------------------------------------------------
    @cache.InputBasedCachedMethod
    def getAllAssetFileNamesForType(self, typeName):
        """returns Asset objects for just the given type of the sequence
        """
        
        # get asset folders
        # look at the child folders
        # and then look at the files under the child folders
        # if a file starts with the folder name
        # mark it as an asset
        
        assetFiles = [] * 0
        
        # get the asset folders
        aType = self.getAssetTypeWithName( typeName )
        
        #assert(isinstance(aType,assetModel.AssetType))
        assetFolder = aType.getPath()
        
        # optimization variables
        osPathExists = os.path.exists
        osPathJoin = os.path.join
        osPathBaseName = os.path.basename
        globGlob = glob.glob
        assetFilesAppend = assetFiles.append
        selfFullPath = self._fullPath
        selfProject = self.getProject()
        
        fullPath = osPathJoin( selfFullPath, assetFolder)
        
        # 
        # skip if the folder doesn't exists
        # 
        # it is a big problem in terms of management but some old type projects
        # has missing folder, because the folders will be created whenever somebody
        # uses that folder while saving an asset, we don't care about its non existancy
        #
        #if not os.path.exists( fullPath ):
        if not osPathExists( fullPath ):
            return []
        
        childFolders = oyAux.getChildFolders( fullPath, True )
        
        for folder in childFolders:
            pattern = osPathBaseName( folder ) + '*'
            
            matchedFiles = globGlob( osPathJoin( folder, pattern ) )
            
            matchedFileCount = len( matchedFiles )
            
            if matchedFileCount > 0:
                [ assetFilesAppend(matchedFile) for matchedFile in matchedFiles if self.isValidExtension( os.path.splitext(matchedFile)[1].split('.')[1] ) ]
        
        assetFiles = map( os.path.basename, assetFiles )
        
        return assetFiles
    
    
    
    #----------------------------------------------------------------------
    def getAssetBaseNamesForType(self, typeName):
        """returns all asset baseNames for the given type
        """
        
        # get the asset files of that type
        allAssetFileNames = self.getAllAssetFileNamesForType( typeName )
        
        # filter for base name
        sGFIV = self.generateFakeInfoVariables
        baseNamesList = [ sGFIV(assetFileName)['baseName'] for assetFileName in allAssetFileNames ]
        
        # remove duplicates
        baseNamesList = oyAux.unique( baseNamesList )
        
        return baseNamesList
    
    
    
    #----------------------------------------------------------------------
    @cache.InputBasedCachedMethod
    def getAllAssetsForTypeAndBaseName(self, typeName, baseName):
        """returns Asset objects of the sequence for just the given type and basename
        """
        
        # get asset folders
        # look at the child folders
        # and then look at the files under the child folders
        # if a file starts with the folder name
        # mark it as an asset
        
        assets = [] * 0
        
        # get the asset folder
        aType = self.getAssetTypeWithName( typeName )
        assetFolder = aType.getPath()
        
        # optimization variables
        osPathJoin = os.path.join
        osPathExists = os.path.exists
        selfFullPath = self._fullPath
        assetModelAsset = assetModel.Asset
        selfProject = self._parentProject
        assetsAppend = assets.append
        
        osPathBaseName = os.path.basename
        globGlob = glob.glob
        
        fullPath = osPathJoin( selfFullPath, assetFolder)
        
        # 
        # skip if the folder doesn't exists
        # 
        # it is a big problem in terms of management but some old type projects
        # has missing folder, because the folders will be created whenever somebody
        # uses that folder while saving an asset, we don't care about its non existancy
        #
        if not osPathExists( fullPath ):
            return []
        
        childFolder = baseName
        childFolderFullPath = osPathJoin( fullPath, childFolder )
        
        # use glob instead of doing it by hand
        
        # get possible asset files directly by using glob
        pattern = osPathBaseName( baseName ) + '*'
        
        # files are in fullpath format
        matchedFiles = globGlob( osPathJoin( childFolderFullPath, pattern ) )
        
        matchedFileCount = len(matchedFiles)
        
        if matchedFileCount > 0:
            # there should be some files matching the pattern
            # check if they are valid assets
            
            matchedAssets = map( assetModelAsset, [selfProject] * matchedFileCount, [self] * matchedFileCount, map(osPathBaseName, matchedFiles) )
            
            # append them to the main assets list
            [ assetsAppend(matchedAsset) for matchedAsset in matchedAssets if matchedAsset.isValidAsset() ]
        
        return assets
    
    
    
    ##----------------------------------------------------------------------
    #def getAllBaseNamesForType(self, typeName):
        #"""
        #"""
        
        #aType = self.getAssetTypeWithName( typeName )
        
        ##assert(isinstance(aType,assetModel.AssetType))
        
        #typeFolder = aType.getPath
        
        #os.listdir( typeFolder )
    
    
    
    #----------------------------------------------------------------------
    def filterAssets(self, assetList, **kwargs):
        """filters the given asset list with the key word arguments
        
        the kwargs should have at least on of these keywords:
        
        baseName
        subName
        typeName
        rev
        revString
        ver
        verString
        userInitials
        notes
        fileName
        """
        
        newKwargs = dict()
        
        # remove empty keywords
        for k in kwargs:
            if kwargs[k] != '':
                newKwargs[k] = kwargs[k]
        
        # get all the info variables of the assets
        assetInfos = map( assetModel.Asset.getInfoVariables, assetList )
        
        filteredAssetInfos = self.aFilter( assetInfos, **kwargs)
        
        # recreate assets and return
        # TODO: return without recreating the assets
        return [ assetModel.Asset(self._parentProject, self, x['fileName']) for x in filteredAssetInfos ]
    
    
    
    #----------------------------------------------------------------------
    def filterAssetNames(self, assetFileNames, **kwargs):
        """a fake filter for quick retrieval of infos from asset file names
        
        use filterAsset for filtering with asset objects as input
        
        the kwargs should have at least on of these keywords:
        
        baseName
        subName
        typeName
        """
        
        # generate dictionaries
        assetInfos = map( self.generateFakeInfoVariables, assetFileNames )
        
        filteredAssetFileNames = self.aFilter( assetInfos, **kwargs )
        
        return [ info['fileName'] for info in filteredAssetFileNames ]
    
    
    
    #----------------------------------------------------------------------
    @cache.InputBasedCachedMethod
    def generateFakeInfoVariables(self, assetFileName):
        """generates fake info variables from assetFileNames by splitting the file name
        from '_' characters and trying to get information from those splits
        """
        #assert(isinstance(assetFileName, str))
        splits = assetFileName.split('_') # replace it with data seperator
        
        infoVars = dict()
        
        infoVars['fileName'] = assetFileName
        infoVars['baseName'] = ''
        infoVars['subName'] = ''
        infoVars['typeName'] = ''
        
        if len(splits) > 1:
            if not self._noSubNameField:
                infoVars['baseName'] = splits[0]
                infoVars['subName'] = splits[1]
                infoVars['typeName'] = splits[2]
            else:
                infoVars['baseName'] = splits[0]
                infoVars['subName'] = ''
                infoVars['typeName'] = splits[1]
        
        return infoVars
    
    
    
    #----------------------------------------------------------------------
    def aFilter(self, dicts, **kwargs):
        """filters dictionaries for criteria
        dicts is a list of dictionaries
        the function returns the dictionaries that has all the kwargs
        """
        return [ d for d in dicts if all(d.get(k) == kwargs[k] for k in kwargs)]
    
    
    
    #----------------------------------------------------------------------
    def getRevPrefix(self):
        """returns revPrefix
        """
        return self._revPrefix
    
    
    
    #----------------------------------------------------------------------
    def getVerPrefix(self):
        """returns verPrefix
        """
        return self._verPrefix
    
    
    
    #----------------------------------------------------------------------
    def getInvalidExtensions(self):
        """returns invalid extensions for the sequence
        """
        return self._extensionsToIgnore
    
    
    
    #----------------------------------------------------------------------
    @cache.InputBasedCachedMethod
    def isValidExtension(self, extensionString):
        """checks if the given extension is in extensionsToIgnore list
        """
        
        if len(self._extensionsToIgnore) == 0 :
            # no extensions to ignore
            return True
        
        #assert(isinstance(extensionString,str))
        
        if extensionString.lower() in self._extensionsToIgnore:
            return False
        
        return True
    
    
    #----------------------------------------------------------------------
    def isValid(self):
        """checks if the sequence is valid
        """
        
        # a valid should:
        # - be exist
        # - have a .settings.xml file inside it
        
        if self._exists and self._settingsFileExists:
            return True
        
        return False
    
    
    
    #----------------------------------------------------------------------
    def addExtensionToIgnoreList(self, extension):
        """adds new extension to ignore list
        
        you need to invoke self.saveSettings to make the changes permenant
        """
        self._extensionsToIgnore.append( extension )
    
    
    
    #----------------------------------------------------------------------
    def removeExtensionFromIgnoreList(self, extension):
        """remove the extension from the ignroe list
        
        you need to invoke self.saveSettings to make the changes permenant
        """
        
        if extension in self._extensionsToIgnore:
            self._extensionsToIgnore.remove( extension )
    
    
    
    #----------------------------------------------------------------------
    def addNewAssetType(self, name='', path='', shotDependent=False, playblastFolder='', environments=None):
        """adds a new asset type to the sequence
        
        you need to invoke self.saveSettings to make the changes permenant
        """
        
        assert(isinstance(environments, list))
        
        # check if there is allready an assetType with the same name
        
        # get the names of the asset types and convert them to upper case
        assetTypeName = [ assetType.getName().upper() for assetType in self._assetTypes ]
        
        if name.upper() not in assetTypeName:
            # create the assetType object with the input
            newAType = assetModel.AssetType( name, path, shotDependent, playblastFolder, environments )
            
            # add it to the list
            self._assetTypes.append( newAType )
        #else:
            #print name, "is allready on the list, skipping"
    
    
    
    ##----------------------------------------------------------------------
    #def addNewShotDependentFolder(self, folderPath):
        #"""adds new shot dependent folder
        
        #folderPath should be relative to sequence root
        
        #you need to invoke self.createStructure and then self.saveSettings
        #to make the changes permenant
        #"""
        
        #self._structure.addShotDependentFolder( folderPath )
    
    
    
    ##----------------------------------------------------------------------
    #def addNewShotIndependentFolder(self, folderPath):
        #"""adds new shot independent folder
        
        #folderPath should be relative to sequence root
        
        #you need to invoke self.createStructure and then self.saveSettings
        #to make the changes permenant
        #"""
        
        #self._structure.addShotIndependentFolder( folderPath )
    
    
    
    ##----------------------------------------------------------------------
    #def addNewOutputFolder(self, name, path):
        #"""adds new output folder to the structure
        
        #you need to invoke self.saveSettings to make the changes permenant
        #"""
        
        #self._structure.addOutputFolder( name, path )
    
    
    
    ##----------------------------------------------------------------------
    #def removeOutputFolder(self, name):
        #"""removes the specified output folder
        
        #you need to invoke self.saveSettings to make the changes permenant
        #"""
        
        #self._structure.removeOutputFolder( name )
    
    
    
    #----------------------------------------------------------------------
    def exists(self):
        """returns True if the sequence itself exists, False otherwise
        """
        
        return self._exists
    
    
    
    #----------------------------------------------------------------------
    def noSubNameField(self):
        """returns True if the sequence doesn't support subName fields (old-style)
        """
        
        return self._noSubNameField
    
    
    
    #----------------------------------------------------------------------
    def undoChange(self):
        """undos the last change to the .settings.xml file if there is a
        backup of the .settings.xml file
        """
        
        # get the backup files of the .settings.xml
        backupFiles = oyAux.getBackupFiles( self._settingsFileFullPath )
        
        if len(backupFiles) > 0 :
            #print backupFiles
            # there is at least one backup file
            # delete the current .settings.xml
            # and rename the last backup to .settings.xml
            
            print "replacing with : ", os.path.basename( backupFiles[-1] )
            
            shutil.copy( backupFiles[-1], self._settingsFileFullPath )
            os.remove( backupFiles[-1] )
        






########################################################################
class Structure(object):
    """The class that helps to hold data about structures in a sequence
    
    outputFolders should be a list of tuples showing the name and path of the outputFolder
    """
    
    
    
    #_shotDependentFolders = list()
    #_shotIndependentFolders = list()
    
    
    
    #----------------------------------------------------------------------
    def __init__(self, shotDependentFolders=None, shotIndependentFolders=None, outputFolders=None):
        
        self._shotDependentFolders = shotDependentFolders # should be a list of str or unicode
        self._shotIndependentFolders = shotIndependentFolders # should be a list of str or unicode
        self._outputFolders = outputFolders # should be a list of tuples
    
    
    
    #----------------------------------------------------------------------
    def setShotDependentFolders(self, folders):
        """sets shot dependent folders
        """
        self._shotDependentFolders = folders
    
    
    
    #----------------------------------------------------------------------
    def setShotIndependentFolders(self, folders):
        """sets shot independent folders
        """
        self._shotIndependentFolders = folders
    
    
    
    #----------------------------------------------------------------------
    def setOutputFolders(self, folders):
        """sets the output folders from a dictionary
        folders should be a list of tuples, the first element of the tuple
        should contain the name and the second should contain the path of that
        output folder
        """
        self._outputFolders = folders
    
    
    
    #----------------------------------------------------------------------
    def addOutputFolder(self, name, path):
        """adds new output folder to the structure
        """
        if self._outputFolders == None:
            self._outputFolders = [] * 0
        
        outputFolderTupple = (name, path)
        
        if outputFolderTupple not in self._outputFolders:
            self._outputFolders.append( outputFolderTupple )
    
    
    
    #----------------------------------------------------------------------
    def addShotDependentFolder(self, folderPath):
        """adds new shot dependent folder
        
        folderPath should be relative to sequence root
        """
        if folderPath not in self._shotDependentFolders:
            self._shotDependentFolders.append( folderPath )
            self._shotDependentFolders = sorted( self._shotDependentFolders )
    
    
    
    #----------------------------------------------------------------------
    def addShotIndependentFolder(self, folderPath):
        """adds new shot independent folder
        
        folderPath should be relative to sequence root
        """
        
        if folderPath not in self._shotIndependentFolders:
            self._shotIndependentFolders.append( folderPath )
            self._shotIndependentFolders = sorted( self._shotIndependentFolders )
    
    
    
    #----------------------------------------------------------------------
    def getShotDependentFolders(self):
        """returns shot dependent folders as list
        """
        return self._shotDependentFolders
    
    
    
    #----------------------------------------------------------------------
    def getShotIndependentFolders(self):
        """returns shot independent folders as list
        """
        return self._shotIndependentFolders
    
    
    
    #----------------------------------------------------------------------
    def getOutputFolders(self):
        """returns the output folders as a dictionary
        """
        return self._outputFolders
    
    
    
    #----------------------------------------------------------------------
    def getOutputFolderPathOf(self, name):
        """returns the output folder path with the name
        returns none if name is not in the list
        """
        for oFolderT in self._outputFolders:
            if oFolderT[0] == name:
                return oFolderT[1]
        
        return None
    
    
    
    #----------------------------------------------------------------------
    def removeOutputFolder(self, name):
        """removes the specified output folder
        """
        
        path = self.getOutputFolderPathOf( name )
        oTuple = (name, path)
        self._outputFolders.remove( oTuple )
    
    
    
    #----------------------------------------------------------------------
    def removeShotDependentFolder(self, folderPath):
        """removes the shot dependent folder from the structure
        
        beware that if the parent sequence uses that folder as a assetType folder
        you introduce an error to the sequence
        """
        
        self._shotDependentFolders.remove( folderPath )
    
    
    
    #----------------------------------------------------------------------
    def removeShotIndependentFolder(self, folderPath):
        """removes the shot independent folder from the structure
        
        beware that if the parent sequence uses that folder as a assetType folder
        you introduce an error to the sequence
        """
        
        self._shotIndependentFolders.remove( folderPath )
    
    
    
    #----------------------------------------------------------------------
    def fixPathIssues(self):
        """fixes path issues in the folder data variables
        """
        
        # replaces "\" with "/"
        for i,folder in enumerate(self._shotDependentFolders):
            self._shotDependentFolders[i] = folder.replace('\\','/')
        
        for i,folder in enumerate(self._shotIndependentFolders):
            self._shotIndependentFolders[i] = folder.replace('\\','/')
        
        for i,folderTuple in enumerate(self._outputFolders):
            self._outputFolders[i] = ( folderTuple[0], folderTuple[1].replace('\\','/') )
    
    
    
    #----------------------------------------------------------------------
    def removeDuplicate(self):
        """removes any duplicate entry
        """
        
        # remove any duplicates
        self._shotDependentFolders = sorted(oyAux.unique( self._shotDependentFolders ))
        self._shotIndependentFolders = sorted(oyAux.unique( self._shotIndependentFolders ))
        self._outputFolders = sorted(oyAux.unique( self._outputFolders ))






########################################################################
class Shot(object):
    """The class that enables the system to manage shot data
    """

    #----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""
        self._name = ''
        self._duration = 0
        self._startFrame = 1
        self._endFrame = 1
        self._description = ''
        #self._cutSummary = ''
        self._parentSequence = None
    
    
    
    #----------------------------------------------------------------------
    def __str__(self):
        """returns the string representation of the object
        """
        return self._name
    
    
    
    #----------------------------------------------------------------------
    def _getStartFrame(self):
        """returns the start frame
        """
        return self._startFrame
    
    
    
    #----------------------------------------------------------------------
    def _setStartFrame(self, frame):
        """sets the start frame
        """
        self._startFrame = frame
        # update the duration
        self._updateDuration()
    
    startFrame = property( _getStartFrame, _setStartFrame )
    
    
    
    #----------------------------------------------------------------------
    def _getEndFrame(self):
        """returns the end frame
        """
        return self._endFrame
    
    
    
    #----------------------------------------------------------------------
    def _setEndFrame(self, frame):
        """sets the end frame
        """
        self._endFrame = frame
        # update the duration
        self._updateDuration()
    
    endFrame = property( _getEndFrame, _setEndFrame )
    
    
    
    #----------------------------------------------------------------------
    def _updateDuration(self):
        """updates the duration
        """
        self._duration = self._endFrame - self._startFrame + 1
    
    
    
    #----------------------------------------------------------------------
    def _getDescription(self):
        """returns the description
        """
        return self._description
    
    
    
    #----------------------------------------------------------------------
    def _setDescription(self, description):
        """sets the description
        """
        self._description = description
    
    description = property( _getDescription, _setDescription )
    
    
    
    #----------------------------------------------------------------------
    def _getParentSequence(self):
        """returns the parentSequence
        """
        return self._parentSequence
    
    
    
    #----------------------------------------------------------------------
    def _setParentSequence(self, seq):
        """sets the parentSequence
        """
        self._parentSequence = seq
    
    parentSequence = property( _getParentSequence, _setParentSequence )
    
    
    
    #----------------------------------------------------------------------
    def _getName(self):
        """returns the name of the shot
        """
        return self._name
    
    
    
    #----------------------------------------------------------------------
    def _setName(self, name):
        """sets the shot name
        """
        self._name = name
    
    name = property( _getName, _setName )
    
    
    
    
    
    
#########################################################################
#class Environment(object):
    #"""holds environment data
    #"""
    
    ##----------------------------------------------------------------------
    #def __init__(self, name):
        
        #self._name = name
        
        #self._recentFilesList = []
    
    
    
    ##----------------------------------------------------------------------
    #def addRecentFile(self, recentFile):
        #"""adds the given file name to the recent files list
        #"""
        #self._recentFilesList.append( recentFile )
    
    
    ##----------------------------------------------------------------------
    #def getRecentFiles(self):
        #"""returns the recent files list
        #"""
        #return self._recentFilesList
    
    
    
    ##----------------------------------------------------------------------
    #def setRecentFiles(self, recentFiles):
        #"""sets the recent files
        #"""
        #self._recentFilesList = recentFiles
    
    #recentFilesList = property( getRecentFiles, setRecentFiles )