import os, sys
import oyAuxiliaryFunctions as oyAux
from PyQt4 import QtGui, QtCore
import assetManager_UI

from oyProjectManager.dataModels import assetModel, projectModel
from oyProjectManager import __version__



#----------------------------------------------------------------------
def UI(environment=None, fileName=None, path=None ):
    """the UI
    """
    global app
    global mainWindow
    app = QtGui.QApplication(sys.argv)
    mainWindow = MainWindow(environment, fileName, path)
    returnValue = mainWindow.show()
    app.setStyle('Plastique')
    app.exec_()
    app.connect(app, QtCore.SIGNAL("lastWindowClosed()"), app, QtCore.SLOT("quit()"))






########################################################################
class MainWindow(QtGui.QMainWindow, assetManager_UI.Ui_MainWindow):
    """the main dialog of the system
    """
    
    
    
    #----------------------------------------------------------------------
    def __init__(self, environment=None, fileName=None, path=None):
        QtGui.QMainWindow.__init__(self)
        self.setupUi(self)
        
        # change the window title
        self.setWindowTitle( self.windowTitle() + ' v' + __version__ )
        
        # center to the window
        self._centerWindow()
        
        # connect SIGNALs
        # SAVE Asset
        QtCore.QObject.connect(self.save_button, QtCore.SIGNAL("clicked()"), self.saveAsset )
        QtCore.QObject.connect(self.export_button, QtCore.SIGNAL("clicked()"), self.exportAsset )
        QtCore.QObject.connect(self.open_button, QtCore.SIGNAL("clicked()"), self.openAsset )
        QtCore.QObject.connect(self.reference_button, QtCore.SIGNAL("clicked()"), self.referenceAsset )
        QtCore.QObject.connect(self.import_button, QtCore.SIGNAL("clicked()"), self.importAsset )
        
        # validate input texts
        QtCore.QObject.connect(self.baseName_comboBox1, QtCore.SIGNAL("editTextChanged(QString)"), self.validateBaseName )
        QtCore.QObject.connect(self.subName_comboBox1, QtCore.SIGNAL("editTextChanged(QString)"), self.validateSubName )
        #QtCore.QObject.connect(self.note_lineEdit1, QtCore.SIGNAL("textChanged(QString)"), self.validateNotes )
        
        # close button
        #QtCore.QObject.connect(self.cancel_button1, QtCore.SIGNAL("clicked()"), self.close )
        QtCore.QObject.connect(self.cancel_button2, QtCore.SIGNAL("clicked()"), self.close )
        
        # project change ---> update sequence
        QtCore.QObject.connect(self.project_comboBox, QtCore.SIGNAL("currentIndexChanged(int)"), self._updateProjectObject )
        QtCore.QObject.connect(self.project_comboBox, QtCore.SIGNAL("currentIndexChanged(int)"), self.updateSequenceList)
        
        # sequence change ---> update _noSubNameField
        QtCore.QObject.connect(self.sequence_comboBox, QtCore.SIGNAL("currentIndexChanged(int)"), self._updateSequenceObject )
        QtCore.QObject.connect(self.sequence_comboBox, QtCore.SIGNAL("currentIndexChanged(int)"), self.updateForNoSubName)
        
        # sequence change ---> update asset type
        QtCore.QObject.connect(self.sequence_comboBox, QtCore.SIGNAL("currentIndexChanged(int)"), self.updateAssetTypeList)
        
        # sequence change ---> update shot lists
        QtCore.QObject.connect(self.sequence_comboBox, QtCore.SIGNAL("currentIndexChanged(int)"), self.updateShotList )
        
        # type change ---> base and shot enable disable
        QtCore.QObject.connect(self.assetType_comboBox1, QtCore.SIGNAL("currentIndexChanged(int)"), self.updateShotDependentFields )
        
        # type change ---> fill baseName comboBox and update subName
        QtCore.QObject.connect(self.assetType_comboBox1, QtCore.SIGNAL("currentIndexChanged(int)"), self.updateBaseNameField )
        QtCore.QObject.connect(self.assetType_comboBox1, QtCore.SIGNAL("currentIndexChanged(int)"), self.updateSubNameField )
        
        # shotName or baseName change ---> fill subName comboBox
        QtCore.QObject.connect(self.shot_comboBox1, QtCore.SIGNAL("currentIndexChanged(int)"), self.updateSubNameField )
        QtCore.QObject.connect(self.baseName_comboBox1, QtCore.SIGNAL("currentIndexChanged(int)"), self.updateSubNameField )
        
        # subName change ---> fill assets_listWidget1
        QtCore.QObject.connect(self.project_comboBox, QtCore.SIGNAL("currentIndexChanged(int)"), self.updateAssetsListWidget )
        QtCore.QObject.connect(self.sequence_comboBox, QtCore.SIGNAL("currentIndexChanged(int)"), self.updateAssetsListWidget )
        QtCore.QObject.connect(self.assetType_comboBox1, QtCore.SIGNAL("currentIndexChanged(int)"), self.updateAssetsListWidget )
        QtCore.QObject.connect(self.shot_comboBox1, QtCore.SIGNAL("currentIndexChanged(int)"), self.updateAssetsListWidget )
        QtCore.QObject.connect(self.baseName_comboBox1, QtCore.SIGNAL("currentIndexChanged(int)"), self.updateAssetsListWidget )
        QtCore.QObject.connect(self.subName_comboBox1, QtCore.SIGNAL("currentIndexChanged(int)"), self.updateAssetsListWidget )
        
        # get latest revision --> revision
        QtCore.QObject.connect(self.revision_pushButton, QtCore.SIGNAL("clicked()"), self.updateRevisionToLatest )
        
        # get latest version --> version
        QtCore.QObject.connect(self.version_pushButton, QtCore.SIGNAL("clicked()"), self.updateVersionToLatest )
        
        # shotName, baseName or subName change --> revision + version
        QtCore.QObject.connect(self.shot_comboBox1, QtCore.SIGNAL("currentIndexChanged(int)"), self.updateRevisionToLatest )
        QtCore.QObject.connect(self.shot_comboBox1, QtCore.SIGNAL("currentIndexChanged(int)"), self.updateVersionToLatest )
        
        QtCore.QObject.connect(self.baseName_comboBox1, QtCore.SIGNAL("currentIndexChanged(int)"), self.updateRevisionToLatest )
        QtCore.QObject.connect(self.baseName_comboBox1, QtCore.SIGNAL("currentIndexChanged(int)"), self.updateVersionToLatest )
        
        QtCore.QObject.connect(self.subName_comboBox1, QtCore.SIGNAL("currentIndexChanged(int)"), self.updateRevisionToLatest )
        QtCore.QObject.connect(self.subName_comboBox1, QtCore.SIGNAL("currentIndexChanged(int)"), self.updateVersionToLatest )
        
        QtCore.QMetaObject.connectSlotsByName(self)
        
        # create a database
        self._db = projectModel.Database()
        
        # fill them later
        self._asset = None
        self._project = None
        self._sequence = None
        
        self.environment = environment
        self.fileName = fileName
        self.path = path
        self.fullPath = ''
        
        if (self.fileName != None and self.fileName != '') and \
           (self.path != None and self.path != '' ):
            self.fullPath = os.path.join(self.path, self.fileName)
        
        self.setDefaults()
        self.updateProjectList()
        
        self.getSettingsFromEnvironment()
        
        self.fillFieldsFromFileInfo()
    
    
    
    #----------------------------------------------------------------------
    def _centerWindow(self):
        """centers the window to the screen
        """
        
        screen = QtGui.QDesktopWidget().screenGeometry()
        size =  self.geometry()
        self.move((screen.width()-size.width())/2, (screen.height()-size.height())/2)
    
    
    
    #----------------------------------------------------------------------
    def setDefaults(self):
        """sets the default values
        """
        
        # set sub name to MAIN by default
        self.subName_comboBox1.clear()
        self.subName_comboBox1.addItem( "MAIN" )
        
        # append the users to the users list
        userInits = self._db.getUserInitials()
        
        self.user_comboBox1.clear()
        self.user_comboBox1.addItems( userInits )
        
        # update the user with the last selected user
        lastUser = self._db.getLastUser()
        
        userIndex = -1
        if lastUser != '' and lastUser != None:
            userIndex = self.user_comboBox1.findText(lastUser) 
        
        if userIndex == -1:
            userIndex = 0
        
        self.user_comboBox1.setCurrentIndex( userIndex )
    
    
    
    #----------------------------------------------------------------------
    def fillFieldsFromFileInfo(self):
        """fills the ui fields from the data that comes from the fileName and path
        """
        
        # no use without the path
        if self.path == None or self.path == '':
            return
        
        # get the project and sequence names
        projectName, sequenceName = self._db.getProjectAndSequenceNameFromFilePath( self.path )
                
        if projectName == None or projectName == '' or sequenceName == None or sequenceName == '':
            return
        
        currentProject = projectModel.Project( projectName )
        currentSequence = projectModel.Sequence( currentProject, sequenceName )
        
        # set the project and sequence
        self.setProjectName( projectName )
        self.setSequenceName( sequenceName )
        
        # no file name no use of the rest
        if self.fileName == None:
            return
        
        # fill the fields with those info
        # create an asset with the file name and get the information from that asset object
        
        assetObj = assetModel.Asset( currentProject, currentSequence, self.fileName )
        
        if not assetObj.isValidAsset():
            return
        
        assetType = assetObj.getTypeName()
        shotNumber = assetObj.getShotNumber()
        baseName = assetObj.getBaseName()
        subName = assetObj.getSubName()
        revNumber = assetObj.getRevisionNumber()
        verNumber = assetObj.getVersionNumber()
        userInitials = assetObj.getUserInitials()
        notes = assetObj.getNotes()
        
        # fill the fields
        # assetType
        element = self.assetType_comboBox1
        element.setCurrentIndex( element.findText( assetType ) )
        
        # shotNumber and baseName
        if assetObj.isShotDependent():
            element = self.shot_comboBox1
            element.setCurrentIndex( element.findText( shotNumber) )
        else:
            element = self.baseName_comboBox1
            element.setCurrentIndex( element.findText(baseName) )
        
        if not currentSequence._noSubNameField: # remove this block when the support for old version becomes obsolute
            # sub Name
            element = self.subName_comboBox1
            element.setCurrentIndex( element.findText(subName) )
        
        # revision
        self.revision_spinBox.setValue( revNumber )
        
        # version : set the version and increase it by one
        self.version_spinBox.setValue( verNumber )
        self.updateVersionToLatest()
        
        # notes
        self.note_lineEdit1.setText( notes )
    
    
    
    #----------------------------------------------------------------------
    def updateProjectList(self):
        """updates projects list
        """
        
        serverPath = self._db.getServerPath()
        
        #projectsList = self._db.getProjects()
        projectsList = self._db.getVaildProjects()
        projectsList.sort()
        
        self.server_comboBox.clear()
        self.project_comboBox.clear()
        self.server_comboBox.addItem( serverPath )
        self.project_comboBox.addItems( projectsList )
    
    
    
    #----------------------------------------------------------------------
    def updateSequenceList(self, *arg):
        """updates the sequence according to selected project
        """
        
        self._updateProjectObject()
        currentProjet = self._project
        
        # create a project and ask the child sequences
        self.sequence_comboBox.clear()
        sequences = currentProjet.getSequenceNames()
        
        self.sequence_comboBox.addItems( sequences )
        
        self._updateSequenceObject() # it is not needed but do it for now
    
    
    
    #----------------------------------------------------------------------
    def updateAssetTypeList(self):
        """updates asset types
        """
        
        # get the asset types of that sequence
        self._updateSequenceObject()
        currentSequence = self._sequence
        
        # get asset types
        assetTypes = currentSequence.getAssetTypes( self.environment )
        
        assetTypeNames = [ assetType.getName() for assetType in assetTypes ]
        
        # clear and update the comboBoxes
        # try to keep the same item in the list
        lastSelectedItem = self.assetType_comboBox1.currentText()
        self.assetType_comboBox1.clear()
        self.assetType_comboBox1.addItems( assetTypeNames )
        # reselect the last selected item
        
        if lastSelectedItem != "":
            self.assetType_comboBox1.setCurrentIndex( self.assetType_comboBox1.findText( lastSelectedItem ) )
    
    
    
    #----------------------------------------------------------------------
    def updateShotList(self):
        """updates shot list
        """
        
        self._updateSequenceObject()
        currentSequence = self._sequence
        
        # get shot list
        shotList = currentSequence.getShotList()
        
        # clear and update the list
        self.shot_comboBox1.clear()
        self.shot_comboBox1.addItems( shotList )
    
    
    
    #----------------------------------------------------------------------
    def updateBaseNameField(self):
        """updates the baseName fields with current asset baseNames for selected
        type, if the type is not shot dependent
        """
        
        # if the current selected type is not shot dependent
        # get all the assets of that type and get their baseNames

        self._updateSequenceObject()
        currentSequence = self._sequence
        
        currentTypeName = self.getCurrentAssetType()
        
        if currentTypeName == None:
            return
        
        comboBox = self.baseName_comboBox1
        
        currentType = currentSequence.getAssetTypeWithName( currentTypeName )
        
        if currentType == None or currentType.isShotDependent():
            # do nothing
            return
        
        # get the asset files of that type
        allAssetFileNames = currentSequence.getAllAssetFileNamesForType( currentTypeName )
        # filter for base name
        currSGFIV = currentSequence.generateFakeInfoVariables
        baseNamesList = [ currSGFIV(assetFileName)['baseName'] for assetFileName in allAssetFileNames ]
        
        # remove duplicates
        baseNamesList = oyAux.unique( baseNamesList )
        
        # add them to the baseName combobox
        comboBox.clear()
        
        # add an item for new items
        comboBox.addItem("")
        
        # add the list
        comboBox.addItems( sorted(baseNamesList) )
    
    
    
    #----------------------------------------------------------------------
    def updateSubNameField(self):
        """updates the subName fields with current asset subNames for selected
        baseName, if the type is not shot dependent
        """
        
        # if the current selected type is not shot dependent
        # get all the assets of that type and get their baseNames
        self._updateSequenceObject()
        currentSequence = self._sequence
        
        # if the current sequence doesn't support subName field just return
        if currentSequence._noSubNameField:
            self.subName_comboBox1.clear()
            return
        
        currentAssetTypeName = self.getCurrentAssetType()
        
        assetTypeObj = currentSequence.getAssetTypeWithName( currentAssetTypeName )
        
        if assetTypeObj == None:
            # clear the current subName field and return
            self.subName_comboBox1.clear()
            return
        
        if assetTypeObj.isShotDependent():
            currentBaseName = currentSequence.convertToShotString( self.getCurrentShotString() )
        else:
            currentBaseName = self.getCurrentBaseName()
        
        self._updateSubNameField( currentSequence, currentAssetTypeName, currentBaseName, self.subName_comboBox1 )
    
    
    
    #----------------------------------------------------------------------
    def _updateSubNameField(self, currentSequence, currentTypeName, currentBaseName, comboBox):
        """updates the subName field to correctly reflect the behaviour of the current sequence
        """
        
        if currentTypeName == None or currentBaseName == None:
            comboBox.clear()
            return
        
        currentType = currentSequence.getAssetTypeWithName( currentTypeName )
        
        if currentType == None:
            # do nothing
            comboBox.clear()
            return
        
        # get the asset files of that type
        allAssetFileNames = currentSequence.getAllAssetFileNamesForType( currentTypeName )
        # filter for base name
        allAssetFileNamesFiltered = currentSequence.filterAssetNames( allAssetFileNames, baseName=currentBaseName, typeName=currentTypeName ) 
        
        # get the subNames
        curSGFIV = currentSequence.generateFakeInfoVariables
        subNamesList = [ curSGFIV(assetFileName)['subName'] for assetFileName in allAssetFileNamesFiltered ]
        
        # add MAIN by default
        subNamesList.append('MAIN')
        
        # remove duplicates
        subNamesList = oyAux.unique( subNamesList )
        
        # add them to the baseName combobox
        comboBox.clear()
        
        # do not add an item for new items, the default should be MAIN
        # add the list
        comboBox.addItems( sorted(subNamesList) )
    
    
    
    #----------------------------------------------------------------------
    def updateShotDependentFields(self):
        """updates shot dependent fields like the shotList and basName
        """
        
        self._updateSequenceObject()
        currentSequence = self._sequence
        
        # get selected asset type name
        assetTypeName = self.getCurrentAssetType()
        
        assetType = currentSequence.getAssetTypeWithName( assetTypeName )
        
        if assetType != None:
            # enable the shot if the asset type is shot dependent
            isShotDependent = assetType.isShotDependent() 
            self.shot_comboBox1.setEnabled( isShotDependent )
            self.baseName_comboBox1.setEnabled( not isShotDependent )
    
    
    
    #----------------------------------------------------------------------
    def updateShotDependentFields(self):
        """updates shot dependent fields like the shotList and baseName
        """
        
        self._updateSequenceObject()
        currentSequence = self._sequence
        
        # get selected asset type name
        assetTypeName = self.getCurrentAssetType()
        
        assetType = currentSequence.getAssetTypeWithName( assetTypeName )
        
        if assetType == None:
            return
        
        # enable the shot if the asset type is shot dependent
        isShotDependent = assetType.isShotDependent() 
        self.shot_comboBox1.setEnabled( isShotDependent )
        self.baseName_comboBox1.setEnabled( not isShotDependent )
    
    
    
    #----------------------------------------------------------------------
    def updateAssetsListWidget(self):
        """fills the assets listWidget with assets
        """
        
        self._updateProjectObject()
        self._updateSequenceObject()
        
        currentProject = self._project
        currentSequence = self._sequence
        
        typeName = self.getCurrentAssetType()
        
        if typeName == '' or typeName == None:
            return
        
        # if the type is shot dependent get the shot number
        # if it is not use the baseName
        if currentSequence.getAssetTypeWithName( typeName ).isShotDependent():
            baseName = currentSequence.convertToShotString( self.getCurrentShotString() )
        else:
            baseName = self.getCurrentBaseName()
        
        
        if not currentSequence.noSubNameField():
            subName = self.getCurrentSubName()
        else:
            subName = ''
        
        # construct the dictionary
        assetInfo = dict()
        assetInfo['baseName'] = baseName
        assetInfo['subName' ] = subName
        assetInfo['typeName'] = typeName
        
        # get all asset files of that type
        allAssetFileNames = currentSequence.getAllAssetFileNamesForType( typeName )
        # filter for assetInfo
        allAssetFileNamesFiltered = currentSequence.filterAssetNames( allAssetFileNames, **assetInfo ) 
        
        # get the fileNames
        currSGFIV = currentSequence.generateFakeInfoVariables
        allVersionsList = [ currSGFIV(assetFileName)['fileName'] for assetFileName in allAssetFileNamesFiltered ]
        
        # append them to the asset list view
        self.assets_listWidget1.clear()
        
        if len(allVersionsList) > 0:
            self.assets_listWidget1.addItems( sorted(allVersionsList) )
    
    
    
    #----------------------------------------------------------------------
    def getCurrentProjectName(self):
        """returns the current project name
        """
        return unicode( self.project_comboBox.currentText() )
    
    
    
    def getCurrentSequenceName(self):
        """returns the current sequence name
        """
        return unicode( self.sequence_comboBox.currentText() )
    
    
    
    #----------------------------------------------------------------------
    def getCurrentAssetType(self):
        """returns the current assetType from the UI
        """
        return unicode( self.assetType_comboBox1.currentText() )
    
    
    
    #----------------------------------------------------------------------
    def getCurrentShotString(self):
        """returns the current shot string from the UI
        """
        return unicode( self.shot_comboBox1.currentText() )
    
    
    
    #----------------------------------------------------------------------
    def getCurrentBaseName(self):
        """returns the current baseName from the UI
        """
        return unicode( self.baseName_comboBox1.currentText() )
    
    
    
    #----------------------------------------------------------------------
    def getCurrentSubName(self):
        """returns the current subName from the UI
        """
        return unicode( self.subName_comboBox1.currentText() )
    
    
    
    #----------------------------------------------------------------------
    def getCurrentRevNumber(self):
        """returns the current revision number from the UI
        """
        return unicode( self.revision_spinBox.value() )
    
    
    
    #----------------------------------------------------------------------
    def getCurrentVerNumber(self):
        """returns the current version number from the UI
        """
        return unicode( self.version_spinBox.value() )
    
    
    
    #----------------------------------------------------------------------
    def getCurrentUserInitials(self):
        """returns the current user initials from the UI
        """
        return unicode( self.user_comboBox1.currentText() )
    
    
    
    #----------------------------------------------------------------------
    def getCurrentNote(self):
        """returns the current note from the UI
        """
        return unicode( self.note_lineEdit1.text() )
    
    
    
    #----------------------------------------------------------------------
    def updateRevisionToLatest(self):
        """ tries to get the latest revision
        """
        
        # get the asset object from fields
        asset = self.getAssetObjectFromSaveFields()
        
        if asset == None or not asset.isValidAsset():
            return
        
        maxRevAsset, maxRevNumber = asset.getLatestRevision2()
        
        if maxRevNumber == None:
            maxRevNumber = 0
            
        # update the field
        self.setRevisionNumberField( maxRevNumber )
    
    
    
    #----------------------------------------------------------------------
    def updateVersionToLatest(self):
        """ tries to get the latest version
        """
        
        # get the asset objet from fields
        asset = self.getAssetObjectFromSaveFields()
        
        if asset == None or not asset.isValidAsset():
            return
        
        maxVerAsset, maxVerNumber = asset.getLatestVersion2()
        
        if maxVerNumber == None:
            maxVerNumber = 0
        
        # update the field
        self.setVersionNumberField( maxVerNumber + 1 )
    
    
    
    #----------------------------------------------------------------------
    def setProjectName(self, projectName):
        """sets the project in the combobox
        """
        if projectName == None:
            return
        
        index = self.project_comboBox.findText( projectName )
        
        if index != -1:
            self.project_comboBox.setCurrentIndex( index )
        
        # be sure it is updated
        self.project_comboBox.update()
    
    
    
    #----------------------------------------------------------------------
    def setSequenceName(self, sequenceName):
        """sets the sequence in the combobox
        """
        if sequenceName == None:
            return
        
        currentIndex = self.sequence_comboBox.currentIndex()
        
        index = self.sequence_comboBox.findText( sequenceName )
        
        if index != -1:
            self.sequence_comboBox.setCurrentIndex( index )
        
        # be sure it is updated
        self.sequence_comboBox.update()
    
    
    
    #----------------------------------------------------------------------
    def getAssetObjectFromSaveFields(self):
        """returns the asset object from the fields
        """
        
        if self._project == None or self._sequence == None:
            return None
        
        assetObj = assetModel.Asset( self._project, self._sequence )
        
        # gather information
        typeName = self.getCurrentAssetType()
        
        assetTypeObj = self._sequence.getAssetTypeWithName(typeName)
        
        if assetTypeObj == None:
            return
        
        isShotDependent = assetTypeObj.isShotDependent()
        if isShotDependent:
            baseName = self._sequence.convertToShotString( self.getCurrentShotString() )
        else:
            baseName = self.getCurrentBaseName()
        
        subName = self.getCurrentSubName()
        rev = self.getCurrentRevNumber()
        ver = self.getCurrentVerNumber()
        userInitials = self.getCurrentUserInitials()
        notes = self.getCurrentNote()
        
        # construct info variables
        infoVars = dict()
        infoVars['baseName'] = baseName
        infoVars['subName'] = subName
        infoVars['typeName'] = typeName
        infoVars['rev'] = rev
        infoVars['ver'] = ver
        infoVars['userInitials'] = userInitials
        infoVars['notes'] = notes
        
        assetObj.setInfoVariables( **infoVars )
        
        return assetObj
    
    
    
    #----------------------------------------------------------------------
    def getAssetObjectFromOpenFields(self):
        """retriewes the file name from the open asset fields
        """
        
        assetFileName = self.assets_listWidget1.currentItem().text()
        
        assetObject = assetModel.Asset( self._project, self._sequence, assetFileName )
        
        return assetObject
    
    
    
    #----------------------------------------------------------------------
    def getFileNameFromSaveFields(self):
        """returns the file name from the fields
        """
        # get the asset object from fields
        assetObject = self.getAssetObjectFromSaveFields()
        
        if assetObject == None:
            return None, None
        
        return assetObject.getPathVariables(), assetObject
    
    
    
    #----------------------------------------------------------------------
    def setRevisionNumberField(self, revNumber):
        """sets the revision number field in the interface
        """
        self.revision_spinBox.setValue( revNumber )
    
    
    
    #----------------------------------------------------------------------
    def setVersionNumberField(self, verNumber):
        """sets the version number field in the interface
        """
        self.version_spinBox.setValue( verNumber )
    
    
    
    ##----------------------------------------------------------------------
    #def validateFieldInput(self, UIElement):
        #"""validates the fields input
        #"""
        #pass
        ##if type(UIElement) == type(QtGui.QComboBox):
            ### validate the item
            ##assert(isinstance(UIElement, QtGui.QComboBox))
            
            ##UIElement.a oyAux.file_name_conditioner( UIElement.currentText() )
    
    
    
    #----------------------------------------------------------------------
    def updateForNoSubName(self):
        """this method will be removed in later version, it is written just to support
        old types of assets those have no subName field
        """
        
        # if the current sequence has no support for subName fields disable them
        self._updateSequenceObject()
        currentSequence = self._sequence
        
        self.subName_comboBox1.setEnabled(not currentSequence._noSubNameField)
    
    
    
    #----------------------------------------------------------------------
    def _updateProjectObject(self):
        """updates the project object if it is changed
        it is introduced to take advantege of the cache system
        """
        
        currentProjectName = self.getCurrentProjectName()
        
        if self._project == None or self._project.getName() != currentProjectName or (currentProjectName != "" or currentProjectName != None ):
            self._project = projectModel.Project( currentProjectName )
    
    
    #----------------------------------------------------------------------
    def _updateSequenceObject(self):
        """updates the sequence object if it is not
        """
        
        currentSequenceName = self.getCurrentSequenceName()
        
        #assert(isinstance(self._sequence,Sequence))
        
        if self._sequence == None or self._sequence.getName() != currentSequenceName and (currentSequenceName != "" or currentSequenceName != None ) or \
           self._sequence.getProjectName() != self._project.getName():
            self._updateProjectObject()
            newSeq = projectModel.Sequence( self._project, currentSequenceName )
            if newSeq._exists:
                self._sequence = newSeq
    
    
    
    #----------------------------------------------------------------------
    def validateSubName(self):
        """validates the subName field by removing unneccessary characters
        """
        
        # get the text
        text = unicode( self.subName_comboBox1.currentText() )
        
        if len(text) == 0:
            return
        
        # validate the text
        text = oyAux.stringConditioner( text, False, True, False, False, False, False )
        
        # capitalize just the first letter
        text = text[0].upper() + text[1:]
        
        # set it back
        self.subName_comboBox1.setEditText( text )
    
    
    
    #----------------------------------------------------------------------
    def validateBaseName(self):
        """validates the baseName field by removing unneccessary characters
        """
        
        # get the text
        text = unicode( self.baseName_comboBox1.currentText() )
        
        if len(text) == 0:
            return
        
        # validate the text
        text = oyAux.stringConditioner( text, False, True, False, False, False, False )
        
        # capitalize just the first letter
        text = text[0].upper() + text[1:]
        
        # set it back
        self.baseName_comboBox1.setEditText( text )
    
    
    
    #----------------------------------------------------------------------
    # ENVIRONMENT PREPARATION
    #----------------------------------------------------------------------
    def getSettingsFromEnvironment(self):
        """gets the data from environment
        """
        
        if self.environment == 'MAYA':
            from oyProjectManager.environments import mayaEnv
            env = mayaEnv
        elif self.environment == 'NUKE':
            from oyProjectManager.environments import nukeEnv
            env = nukeEnv
        
        if self.environment != None and self.environment != '':
            self.fileName, self.path = env.getPathVariables()
            
            # update the interface
            self.fillFieldsFromFileInfo()
    
    
    
    #----------------------------------------------------------------------
    # SAVE & OPEN & IMPORT & REFERENCE ACTIONS FOR ENVIRONMENTS
    #----------------------------------------------------------------------
    #----------------------------------------------------------------------
    def checkOutputAsset(self, assetObject):
        """check if the asset is a valid asset
        """
        return assetObject.isValidAsset()
    
    
    
    #----------------------------------------------------------------------
    def checkOutputFileVersion(self, assetObject):
        """checks if the asset is set to latest version for its own kind
        """
        
        verStatus = False
        
        # check for the latest version
        if not assetObject.isLatestVersion():
            
            # ask permission to update the fields automatically
            answer = QtGui.QMessageBox.question(self, 'Version Error', 'it is not the latest version\nshould I increase the version number?', QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
            
            if answer == QtGui.QMessageBox.Yes:
                assetObject.setVersionToNextAvailable()
                
                self.setVersionNumberField( assetObject.getVersionNumber() )
                
                verStatus = True
        else:
            verStatus = True
        
        return verStatus
    
    
    
    #----------------------------------------------------------------------
    def checkOutputFileRevision(self, assetObject):
        """checks if the asset is set to latest revision for its own kind
        """
        
        revStatus = False
        
        # check for latest revision
        if not assetObject.isLatestRevision():
            # ask permission to update the fields automatically
            answer = QtGui.QMessageBox.question(self, 'Revision Error', 'it is not the latest revision\nshould I increase the revision number?', QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
            
            if answer == QtGui.QMessageBox.Yes:
                assetObject.setRevisionToNextAvailable()
                
                self.setRevisionNumberField( assetObject.getRevisionNumber() )
                
                revStatus = True
        else:
            revStatus = True
        
        return revStatus
    
    
    
    #----------------------------------------------------------------------
    def checkOutputFileOverwrite(self, assetObject):
        """checks if the assetObject already exists, so user tries to overwrite
        """
        
        overwriteStatus = False
        
        # check for overwrites
        if assetObject.exists():
            answer = QtGui.QMessageBox.question(self, 'File Error', 'owerwrite?', QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
            if answer == QtGui.QMessageBox.Yes:
                overwriteStatus = True
        else:
            overwriteStatus = True
        
        return overwriteStatus
    
    
    
    #----------------------------------------------------------------------
    def saveAsset(self):
        """prepares the data and sends the asset object to the function
        specially written for the host environment to save the asset file
        """
        
        envStatus = False
        verStatus = False
        revStatus = False
        overwriteStatus = False
        assetStatus = False
        
        # get the asset object
        assetObject = self.getAssetObjectFromSaveFields()
        
        if assetObject == None:
            return
        
        # check the file conditions
        assetStatus = self.checkOutputAsset(assetObject)
        verStatus = self.checkOutputFileVersion( assetObject )
        revStatus = self.checkOutputFileRevision( assetObject )
        overwriteStatus = self.checkOutputFileOverwrite( assetObject )
        
        envStatus = False
        
        if assetStatus and verStatus and revStatus and overwriteStatus:
            
            # everything is ok now save in the host application
            if self.environment == 'MAYA':
                from oyProjectManager.environments import mayaEnv
                envStatus = mayaEnv.save( assetObject )
                
            elif self.environment == 'NUKE':
                from oyProjectManager.environments import nukeEnv
                envStatus = nukeEnv.save( assetObject )
                
            
            # if everything worked fine close the interface
            if envStatus:
                # set the last user variable
                self._db.setLastUser( assetObject.getUserInitials() )
                
                #print info
                self.printInfo( assetObject,  "saved" )
                self.close()
    
    
    
    #----------------------------------------------------------------------
    def exportAsset(self):
        """prepares the data and sends the asset object to the function
        specially written for the host environment to open the asset file
        """
        
        # get the asset object
        assetObject = self.getAssetObjectFromSaveFields()
        
        if assetObject == None:
            return
        
        # check the file conditions
        assetStatus = self.checkOutputAsset(assetObject)
        verStatus = self.checkOutputFileVersion( assetObject )
        revStatus = self.checkOutputFileRevision( assetObject )
        overwriteStatus = self.checkOutputFileOverwrite( assetObject )
        
        envStatus = False
        
        if assetStatus and verStatus and revStatus and overwriteStatus:
            # everything is ok now save in the host application
            if self.environment == 'MAYA':
                
                from oyProjectManager.environments import mayaEnv
                envStatus = mayaEnv.export( assetObject )
            elif self.environment == 'NUKE':
                from oyProjectManager.environments import nukeEnv
                envStatus = nukeEnv.export( assetObject )
            
            # if everything worked fine close the interface
            if envStatus:
                # do not set the last user variable
                
                # inform the user for successful operation
                
                QtGui.QMessageBox.information(self, 'Asset Export', 'Asset :\n\n'+ assetObject.getFileName() +'\n\nis exported successfuly', QtGui.QMessageBox.Ok)
                
                self.close()
    
    
    
    #----------------------------------------------------------------------
    def openAsset(self):
        """prepares the data and sends the asset object to the function
        specially written for the host environment to open the asset file
        """
        
        # get the asset object
        assetObject = self.getAssetObjectFromOpenFields()
        
        # check the file existancy
        exists = os.path.exists( assetObject.getFullPath() )
        
        envStatus = False
        
        # open the asset in the environment
        if exists:
            if self.environment == 'MAYA':
                from oyProjectManager.environments import mayaEnv
                try:
                    envStatus = mayaEnv.open_( assetObject )
                except RuntimeError:
                    answer = QtGui.QMessageBox.question(self, 'RuntimeError', "There are unsaved changes in the current scene\n\nDo you really want to open the file?", QtGui.QMessageBox.Yes, QtGui.QMessageBox.No )
                    
                    if answer== QtGui.QMessageBox.Yes:
                        envStatus = mayaEnv.open_( assetObject, True )
            elif self.environment == 'NUKE':
                from oyProjectManager.environments import nukeEnv
                envStatus = nukeEnv.open_( assetObject )
            
            if envStatus:
                self.close()
        
        else:
            # warn the user for non existing asset files
            answer = QtGui.QMessageBox.question(self, 'File Error', assetObject.getFullPath() + "\n\nAsset doesn't exist !!!", QtGui.QMessageBox.Ok )
    
    
    
    #----------------------------------------------------------------------
    def importAsset(self):
        """prepares the data and sends the asset object to the function
        specially written for the host environment to import the asset file
        """
        
        # get the asset object
        assetObject = self.getAssetObjectFromOpenFields()
        
        # check the file existancy
        exists = os.path.exists( assetObject.getFullPath() )
        
        envStatus = False
        
        # open the asset in the environment
        if exists:
            if self.environment == 'MAYA':
                from oyProjectManager.environments import mayaEnv
                envStatus = mayaEnv.import_( assetObject )
            if self.environment == 'NUKE':
                from oyProjectManager.environments import nukeEnv
                envStatus = nukeEnv.import_( assetObject )
            
            if envStatus:
                self.close()
        
        else:
            # warn the user for non existing asset files
            answer = QtGui.QMessageBox.question(self, 'File Error', assetObject.getFullPath() + "\n\nAsset doesn't exist !!!", QtGui.QMessageBox.Ok )
    
    
    
    #----------------------------------------------------------------------
    def referenceAsset(self):
        """prepares the data and sends the asset object to the function
        specially written for the host environment to reference the asset file
        
        beware that not all environments supports this action
        """
        
        # get the asset object
        assetObject = self.getAssetObjectFromOpenFields()
        
        # check the file existancy
        exists = os.path.exists( assetObject.getFullPath() )
        
        envStatus = False
        
        # open the asset in the environment
        if exists:
            if self.environment == 'MAYA':
                from oyProjectManager.environments import mayaEnv
                envStatus = mayaEnv.reference( assetObject )
            elif self.environment == 'NUKE':
                envStatus = False
                QtGui.QMessageBox.warning(self, 'Function Error', self.environment + " doesn't support referencing yet !!!", QtGui.QMessageBox.Ok )
            
            
            if envStatus:
                self.close()
        
        else:
            # warn the user for non existing asset files
            answer = QtGui.QMessageBox.question(self, 'File Error', assetObject.getFullPath() + "\n\nAsset doesn't exist !!!", QtGui.QMessageBox.Ok )
    
    
    
    #----------------------------------------------------------------------
    def printInfo(self, assetObject, actionName):
        """prints info about action
        """
        
        print "-----------------------------------"
        print "AssetManager " + __version__
        print assetObject.getFileName()
        print actionName + " succesfully"
        