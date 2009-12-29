import os, sys
import oyAuxiliaryFunctions as oyAux
from PyQt4 import QtGui, QtCore
import assetManager_UI

import oyProjectManager
from oyProjectManager.dataModels import assetModel, projectModel, repositoryModel
from oyProjectManager.ui import assetUpdater, singletonQapplication



__version__ = "9.12.27"



#----------------------------------------------------------------------
#def UI(environmentName=None, fileName=None, path=None ):
def UI(environmentName=None, parent=None):
    """the UI
    """
    global app
    global mainWindow
    app = singletonQapplication.QApplication(sys.argv)
    
    mainWindow = MainWindow(environmentName, parent)
    mainWindow.show()
    app.setStyle('Plastique')
    app.exec_()
    app.connect(app, QtCore.SIGNAL("lastWindowClosed()"), app, QtCore.SLOT("quit()"))






########################################################################
class MainWindow(QtGui.QMainWindow, assetManager_UI.Ui_MainWindow):
    """the main dialog of the system
    """
    
    
    
    #----------------------------------------------------------------------
    #def __init__(self, environmentName=None, fileName=None, path=None):
    def __init__(self, environmentName=None, parent=None):
        QtGui.QMainWindow.__init__(self, parent)
        self.setupUi(self)
        
        # change the window title
        environmentTitle = ''
        if environmentName != None:
            environmentTitle = environmentName
        
        self.setWindowTitle( environmentTitle + ' | ' + self.windowTitle() + ' v' + __version__ + ' | ' + 'oyProjectManager v' + oyProjectManager.__version__ )
        
        # center to the window
        self._centerWindow()
        
        # setup signals
        self._setupSignals()
        
        # setup validators
        self._setupValidators()
        
        # attach new item texts
        #setattr( self.baseName_listWidget, 'newItemText', '(add new...)')
        
        # create a repository object
        self._repo = repositoryModel.Repository()
        
        # fill them later
        self._asset = None
        self._project = None
        self._sequence = None
        self._versionListBuffer = []
        
        self.environmentName = environmentName
        #self.fileName = fileName
        #self.path = path
        self.fileName = ''
        self.path = ''
        self.fullPath = ''
        
        #if (self.fileName != None and self.fileName != '') and \
           #(self.path != None and self.path != '' ):
            #self.fullPath = os.path.join(self.path, self.fileName)
        
        self.setDefaults()
        self.updateProjectList()
        
        self.getSettingsFromEnvironment()
        
        self.fillFieldsFromFileInfo()
    
    
    
    #----------------------------------------------------------------------
    def _setupSignals(self):
        """sets up the signals/slots
        """
        
        # connect SIGNALs
        # SAVE Asset
        QtCore.QObject.connect(self.save_button, QtCore.SIGNAL("clicked()"), self.saveAsset )
        QtCore.QObject.connect(self.export_button, QtCore.SIGNAL("clicked()"), self.exportAsset )
        QtCore.QObject.connect(self.open_button, QtCore.SIGNAL("clicked()"), self.openAsset )
        QtCore.QObject.connect(self.reference_button, QtCore.SIGNAL("clicked()"), self.referenceAsset )
        QtCore.QObject.connect(self.import_button, QtCore.SIGNAL("clicked()"), self.importAsset )
        
        # validate input texts
        #QtCore.QObject.connect(self.note_lineEdit1, QtCore.SIGNAL("textChanged(QString)"), self.validateNotes )
        
        # close button
        QtCore.QObject.connect(self.close_button, QtCore.SIGNAL("clicked()"), self.close )
        
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
        QtCore.QObject.connect(self.baseName_lineEdit, QtCore.SIGNAL("textChanged(QString)"), self.updateSubNameField )
        
        # subName change ---> full update assets_listWidget1
        QtCore.QObject.connect(self.project_comboBox, QtCore.SIGNAL("currentIndexChanged(int)"), self.fullUpdateAssetsListWidget )
        QtCore.QObject.connect(self.sequence_comboBox, QtCore.SIGNAL("currentIndexChanged(int)"), self.fullUpdateAssetsListWidget )
        QtCore.QObject.connect(self.assetType_comboBox1, QtCore.SIGNAL("currentIndexChanged(int)"), self.fullUpdateAssetsListWidget )
        QtCore.QObject.connect(self.shot_comboBox1, QtCore.SIGNAL("currentIndexChanged(int)"), self.fullUpdateAssetsListWidget )
        
        QtCore.QObject.connect(self.baseName_lineEdit, QtCore.SIGNAL("textChanged(QString)"), self.fullUpdateAssetsListWidget )
        QtCore.QObject.connect(self.subName_lineEdit, QtCore.SIGNAL("textChanged(QString)"), self.fullUpdateAssetsListWidget )
        
        # get latest revision --> revision
        QtCore.QObject.connect(self.revision_pushButton, QtCore.SIGNAL("clicked()"), self.updateRevisionToLatest )
        
        # get latest version --> version
        QtCore.QObject.connect(self.version_pushButton, QtCore.SIGNAL("clicked()"), self.updateVersionToLatest )
        
        # sequence, type, shotName, baseName or subName change --> revision + version
        QtCore.QObject.connect(self.sequence_comboBox, QtCore.SIGNAL("currentIndexChanged(int)"), self.updateRevisionToLatest )
        QtCore.QObject.connect(self.sequence_comboBox, QtCore.SIGNAL("currentIndexChanged(int)"), self.updateVersionToLatest )
        
        QtCore.QObject.connect(self.assetType_comboBox1, QtCore.SIGNAL("currentIndexChanged(int)"), self.updateRevisionToLatest )
        QtCore.QObject.connect(self.assetType_comboBox1, QtCore.SIGNAL("currentIndexChanged(int)"), self.updateVersionToLatest )
        
        QtCore.QObject.connect(self.shot_comboBox1, QtCore.SIGNAL("currentIndexChanged(int)"), self.updateRevisionToLatest )
        QtCore.QObject.connect(self.shot_comboBox1, QtCore.SIGNAL("currentIndexChanged(int)"), self.updateVersionToLatest )
        
        QtCore.QObject.connect(self.baseName_lineEdit, QtCore.SIGNAL("textChanged(QString)"), self.updateRevisionToLatest )
        QtCore.QObject.connect(self.baseName_lineEdit, QtCore.SIGNAL("textChanged(QString)"), self.updateVersionToLatest )
        
        QtCore.QObject.connect(self.subName_lineEdit, QtCore.SIGNAL("textChanged(QString)"), self.updateRevisionToLatest )
        QtCore.QObject.connect(self.subName_lineEdit, QtCore.SIGNAL("textChanged(QString)"), self.updateVersionToLatest )
        
        # showLastNEntry_checkbox or numberOfEntry change ->partial update assets_listWidget1
        QtCore.QObject.connect(self.showLastNEntry_checkBox, QtCore.SIGNAL("stateChanged(int)"), self.partialUpdateAssetsListWidget )
        QtCore.QObject.connect(self.numberOfEntry_spinBox, QtCore.SIGNAL("valueChanged(int)"), self.partialUpdateAssetsListWidget )
        
        # baseName_listWidget -> baseName_lineEdit
        # subName_listWidget -> subName_lineEdit
        QtCore.QObject.connect( self.baseName_listWidget, QtCore.SIGNAL("currentTextChanged(QString)"), self.updateBaseNameLineEdit )
        QtCore.QObject.connect( self.subName_listWidget, QtCore.SIGNAL("currentTextChanged(QString)"), self.updateSubNameLineEdit )
        
        
        QtCore.QMetaObject.connectSlotsByName(self)
    
    
    
    #----------------------------------------------------------------------
    def _setupValidators(self):
        """sets up the input validators
        """
        
        ## new item to the baseName_listWidget
        #QtCore.QObject.connect(self.baseName_listWidget, QtCore.SIGNAL("itemDoubleClicked(QListWidgetItem*)"), self.addNewListItem )
        
        # attach validators
        QtCore.QObject.connect(self.baseName_lineEdit, QtCore.SIGNAL("textChanged(QString)"), self.validateBaseName )
        QtCore.QObject.connect(self.subName_lineEdit, QtCore.SIGNAL("textChanged(QString)"), self.validateSubName )
    
    
    
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
        self.subName_listWidget.clear()
        self.subName_listWidget.addItem( "MAIN" )
        
        # append the users to the users list
        userInits = self._repo.getUserInitials()
        
        self.user_comboBox1.clear()
        self.user_comboBox1.addItems( userInits )
        
        # update the user with the last selected user
        lastUser = self._repo.getLastUser()
        
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
        projectName, sequenceName = self._repo.getProjectAndSequenceNameFromFilePath( self.path )
                
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
            #element = self.baseName_comboBox1
            #element = self.baseName_listWidget
            #element.setCurrentIndex( self.baseName_listWidget.indexFromItem( element.findText(baseName) )
            #self.baseName_listWidget.setCurrentIndex( self.baseName_listWidget.findItems( baseName ) )
            
            #itemCount = self.baseName_listWidget.count()
            #for i in range(itemCount):
                #currentItem = self.baseName_listWidget.item(i)
                #assert(isinstance(currentItem, QtGui.QListWidgetItem ))
                #if currentItem.text == baseName:
                    #currentItem.setSelected(True)
                    
                    #self.update
            
            #assert(isinstance(self.baseName
            #self.baseName_listWidget.find
            
            itemIndex = self.findListItemWithText( self.baseName_listWidget, baseName )
            if itemIndex != -1:
                self.baseName_listWidget.item( itemIndex ).setSelected(True)
                # update the selection
                self.updateBaseNameLineEdit( baseName )
                
        
        if not currentSequence._noSubNameField: # remove this block when the support for old version becomes obsolute
            # sub Name
            #element = self.subName_comboBox1
            #element = self.subName_listWidget
            #element.setCurrentIndex( element.findText(subName) )
            
            itemIndex = self.findListItemWithText( self.subName_listWidget, subName )
            if itemIndex != -1:
                self.subName_listWidget.item( itemIndex ).setSelected(True)
                self.updateSubNameLineEdit( subName )
        
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
        
        serverPath = self._repo.getServerPath()
        
        #projectsList = self._repo.getProjects()
        projectsList = self._repo.getValidProjects()
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
        assetTypes = currentSequence.getAssetTypes( self.environmentName )
        
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
        
        currentType = currentSequence.getAssetTypeWithName( currentTypeName )
        
        if currentType == None or currentType.isShotDependent():
            # do nothing
            return
        
        ## get the asset files of that type
        #allAssetFileNames = currentSequence.getAllAssetFileNamesForType( currentTypeName )
        ## filter for base name
        #currSGFIV = currentSequence.generateFakeInfoVariables
        #baseNamesList = [ currSGFIV(assetFileName)['baseName'] for assetFileName in allAssetFileNames ]
        
        ## remove duplicates
        #baseNamesList = oyAux.unique( baseNamesList )
        baseNamesList = currentSequence.getAssetBaseNamesForType( currentTypeName )
        
        # add them to the baseName combobox
        self.baseName_listWidget.clear()
        
        # add the list
        self.baseName_listWidget.addItems( sorted(baseNamesList) )
        
        # select the first one in the list
        if len(baseNamesList) > 0:
            listItem = self.baseName_listWidget.item(0)
            #assert(isinstance(listItem, QtGui.QListWidgetItem ))
            listItem.setSelected(True)
            
            self.updateBaseNameLineEdit( listItem.text() )
    
    
    
    #----------------------------------------------------------------------
    def updateBaseNameLineEdit(self, baseName):
        """updates the baseName_lineEdit according to the selected text in the
        baseName_listWidget
        """
        
        self.baseName_lineEdit.setText( baseName )
    
    
    
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
            self.subName_listWidget.clear()
            return
        
        currentAssetTypeName = self.getCurrentAssetType()
        
        assetTypeObj = currentSequence.getAssetTypeWithName( currentAssetTypeName )
        
        if assetTypeObj == None:
            # clear the current subName field and return
            self.subName_listWidget.clear()
            return
        
        if assetTypeObj.isShotDependent():
            currentBaseName = currentSequence.convertToShotString( self.getCurrentShotString() )
        else:
            currentBaseName = self.getCurrentBaseName()
        
        self.subName_listWidget.clear()
        
        if currentAssetTypeName == None or currentBaseName == None:
            return
        
        currentAssetType = currentSequence.getAssetTypeWithName( currentAssetTypeName )
        
        if currentAssetType == None:
            # do nothing
            return
        
        # get the asset files of that type
        allAssetFileNames = currentSequence.getAllAssetFileNamesForType( currentAssetTypeName )
        
        # filter for base name
        allAssetFileNamesFiltered = currentSequence.filterAssetNames( allAssetFileNames, baseName=currentBaseName, typeName=currentAssetTypeName ) 
        
        # get the subNames
        curSGFIV = currentSequence.generateFakeInfoVariables
        subNamesList = [ curSGFIV(assetFileName)['subName'] for assetFileName in allAssetFileNamesFiltered ]
        
        # add MAIN by default
        subNamesList.append('MAIN')
        
        # remove duplicates
        subNamesList = oyAux.unique( subNamesList )
        
        # add them to the baseName combobox
        
        # do not add an item for new items, the default should be MAIN
        # add the list
        self.subName_listWidget.addItems( sorted(subNamesList) )
        
        # update subName line edit
        self.updateSubNameLineEdit( 'MAIN' )
    
    
    
    #----------------------------------------------------------------------
    def updateSubNameLineEdit(self, subName):
        """updates the subName_lineEdit according to the selected text in the
        subName_listWidget
        """
        
        self.subName_lineEdit.setText( subName )
    
    
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
            
            self.baseName_listWidget.setEnabled( not isShotDependent )
            self.baseName_lineEdit.setEnabled( not isShotDependent )
    
    
    
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
        
        self.baseName_listWidget.setEnabled( not isShotDependent )
        self.baseName_lineEdit.setEnabled( not isShotDependent )
    
    
    
    #----------------------------------------------------------------------
    def updateVersionListBuffer(self):
        """updates the version list buffer
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
            self._versionListBuffer = sorted(allVersionsList)
        else:
            self._versionListBuffer = []
    
    
    
    #----------------------------------------------------------------------
    def partialUpdateAssetsListWidget(self):
        """just updates if the number of maximum displayable entry is changed
        """
        
        self.assets_listWidget1.clear()
        
        if self.showLastNEntry_checkBox.isChecked():
            # get the number of entry
            
            numOfEntry = min( len(self._versionListBuffer), self.numberOfEntry_spinBox.value() )
            self.assets_listWidget1.addItems( self._versionListBuffer[-numOfEntry:] )
        else:
            self.assets_listWidget1.addItems( self._versionListBuffer )
    
    
    
    #----------------------------------------------------------------------
    def fullUpdateAssetsListWidget(self):
        """invokes a version list buffer update and a assets list widget update
        """
        self.updateVersionListBuffer()
        self.partialUpdateAssetsListWidget()
    
    
    
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
        #return unicode( self.baseName_comboBox1.currentText() )
        return unicode( self.baseName_lineEdit.text() )
    
    
    
    #----------------------------------------------------------------------
    def getCurrentSubName(self):
        """returns the current subName from the UI
        """
        return unicode( self.subName_lineEdit.text() )
    
    
    
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
            self.setRevisionNumberField( 0 )
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
            self.setVersionNumberField( 1 )
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
    
    
    
    #----------------------------------------------------------------------
    def updateForNoSubName(self):
        """this method will be removed in later version, it is written just to support
        old types of assets those have no subName field
        """
        
        # if the current sequence has no support for subName fields disable them
        self._updateSequenceObject()
        currentSequence = self._sequence
        
        self.subName_listWidget.setEnabled(not currentSequence._noSubNameField)
        self.subName_lineEdit.setEnabled(not currentSequence._noSubNameField)
    
    
    
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
    def validateSubName(self, text):
        """validates the subName field by removing unneccessary characters
        """
        
        # just replace the validated text
        self.subName_lineEdit.setText( self.fieldNameValidator(text) )
    
    
    
    #----------------------------------------------------------------------
    def validateBaseName(self, text):
        """validates the baseName field by removing unneccessary characters
        """
        
        # just replace the validated text
        self.baseName_lineEdit.setText( self.fieldNameValidator(text) )
    
    
    
    #----------------------------------------------------------------------
    def fieldNameValidator(self, text):
        """a validator that validates input texts
        """
        text = unicode(text)
        
        if len(text) == 0:
            return text
        
        # validate the text
        text = oyAux.stringConditioner( text, False, True, False, False, False, False )
        
        # capitalize just the first letter
        text = text[0].upper() + text[1:]
        
        return text
    
    
    
    #----------------------------------------------------------------------
    def addNewListItem(self, inputItem):
        """adds new base name to the list
        """
        
        assert(isinstance(inputItem, QtGui.QListWidgetItem))
        inputItemText = inputItem.text()
        
        parentListWidget = inputItem.listWidget()
        assert(isinstance(parentListWidget, QtGui.QListWidget))
        
        # go ahead if user double clicked on the newItemText
        if hasattr( parentListWidget, 'newItemText' ):
            checkItemText = getattr( parentListWidget, 'newItemText' )
            
            if inputItemText == checkItemText:
                # pop up an input form to ask the user for the new item name
                newItemName, ok = QtGui.QInputDialog.getText( self, 'Enter new item name', 'Enter a new item name please:' )
                
                if ok:
                    # validate the input
                    if hasattr( parentListWidget, 'validator' ):
                        newItemName = eval('parentListWidget.validator( newItemName )')
                    
                    # add the new item to the list
                    parentListWidget.addItem( newItemName )
    
    
    
    #----------------------------------------------------------------------
    def findListItemWithText(self, listWidget, text):
        """returns the item index with given index
        """
        
        itemCount = listWidget.count()
        
        for i in range(itemCount):
            currentItem = listWidget.item(i)
            #assert(isinstance(currentItem, QtGui.QListWidgetItem ))
            #print currentItem.text()
            if currentItem.text() == text:
                return i
        
        return -1
    
    
    
    #----------------------------------------------------------------------
    # ENVIRONMENT PREPARATION
    #----------------------------------------------------------------------
    def getSettingsFromEnvironment(self):
        """gets the data from environment
        """
        
        if self.environmentName == 'MAYA':
            from oyProjectManager.environments import mayaEnv
            env = mayaEnv.MayaEnvironment()
            
        elif self.environmentName == 'NUKE':
            from oyProjectManager.environments import nukeEnv
            env = nukeEnv.NukeEnvironment()
            
        elif self.environmentName == 'HOUDINI':
            from oyProjectManager.environments import houdiniEnv
            env = houdiniEnv.HoudiniEnvironment()
        
        if self.environmentName != None and self.environmentName != '':
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
        
        # check for the new version
        if not assetObject.isNewVersion():
            
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
            if self.environmentName == 'MAYA':
                from oyProjectManager.environments import mayaEnv
                #envStatus = mayaEnv.save( assetObject )
                env = mayaEnv.MayaEnvironment( assetObject )
                
            elif self.environmentName == 'NUKE':
                from oyProjectManager.environments import nukeEnv
                #envStatus = nukeEnv.save( assetObject )
                env = nukeEnv.NukeEnvironment( assetObject )
            
            elif self.environmentName == 'HOUDINI':
                from oyProjectManager.environments import houdiniEnv
                #envStatus = houdiniEnv.save( assetObject )
                env = houdiniEnv.HoudiniEnvironment( assetObject )
            
            envStatus = env.save()
            
            # if everything worked fine close the interface
            if envStatus:
                # set the last user variable
                self._repo.setLastUser( assetObject.getUserInitials() )
                
                #print info
                if self.environmentName == 'MAYA':
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
            if self.environmentName == 'MAYA':
                from oyProjectManager.environments import mayaEnv
                #envStatus = mayaEnv.export( assetObject )
                env = mayaEnv.MayaEnvironment( assetObject )
                envSatus = env.export()
                
            elif self.environmentName == 'NUKE':
                from oyProjectManager.environments import nukeEnv
                #envStatus = nukeEnv.export( assetObject )
                env = nukeEnv.NukeEnvironment( assetObject )
                envStatus = env.export()
            
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
            if self.environmentName == 'MAYA':
                
                toUpdateList = [] # the list that holds the assets those needs to be updated
                
                from oyProjectManager.environments import mayaEnv
                env = mayaEnv.MayaEnvironment( assetObject )
                
                try:
                    envStatus, toUpdateList = env.open_()
                except RuntimeError:
                    answer = QtGui.QMessageBox.question(self, 'RuntimeError', "There are unsaved changes in the current scene\n\nDo you really want to open the file?", QtGui.QMessageBox.Yes, QtGui.QMessageBox.No )
                    
                    if answer== QtGui.QMessageBox.Yes:
                        envStatus, toUpdateList = env.open_( True )
                
                # check the toUpdateList to update old assets
                if len(toUpdateList):
                    assetNames = '\n'.join( [ assetTuple[0].getFileName() for assetTuple in toUpdateList ] )
                    
                    # display the warning
                    answer = QtGui.QMessageBox.warning(self, 'AssetVersionError', "These assets has newer versions\n\n" + assetNames + "\n\nPlease update them!", QtGui.QMessageBox.Ok )
                    
                    # print the text version
                    print "\n"
                    print "These assets has newer versions:"
                    print "--------------------------------"
                    print "\n"
                    print assetNames
                    print "\n"
                    print "Please update them!"
                    
                    ## invoke the assetUpdater for this scene
                    #assetUpdater.UI( self.environmentName, self )

                    
                
            elif self.environmentName == 'NUKE':
                from oyProjectManager.environments import nukeEnv
                #envStatus = nukeEnv.open_( assetObject )
                
                env = nukeEnv.NukeEnvironment( assetObject )
                envStatus = env.open_()
            
            elif self.environmentName == 'HOUDINI':
                from oyProjectManager.environments import houdiniEnv
                
                env = houdiniEnv.HoudiniEnvironment( assetObject )
                
                try:
                    envStatus = env.open_()
                except RuntimeError:
                    answer = QtGui.QMessageBox.question(self, 'RuntimeError', "There are unsaved changes in the current scene\n\nDo you really want to open the file?", QtGui.QMessageBox.Yes, QtGui.QMessageBox.No )
                    
                    if answer== QtGui.QMessageBox.Yes:
                        envStatus = env.open_( True )
            
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
            if self.environmentName == 'MAYA':
                from oyProjectManager.environments import mayaEnv
                env = mayaEnv.MayaEnvironment( assetObject )
                
            if self.environmentName == 'NUKE':
                from oyProjectManager.environments import nukeEnv
                env = nukeEnv.NukeEnvironment( assetObject )
            
            if self.environmentName == 'HOUDINI':
                from oyProjectManager.environments import houdiniEnv
                env = houdiniEnv.HoudiniEnvironment( assetObject )
            
            envStatus = env.import_()
                
            if envStatus:
                #self.close()
                QtGui.QMessageBox.information(self, 'Asset Import', 'Asset :\n\n'+ assetObject.getFileName() +'\n\nis imported successfuly', QtGui.QMessageBox.Ok)
                
        
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
            if self.environmentName == 'MAYA':
                from oyProjectManager.environments import mayaEnv
                env = mayaEnv.MayaEnvironment( assetObject )
                envStatus = env.reference()
            
            elif self.environmentName == 'NUKE':
                envStatus = False
                QtGui.QMessageBox.warning(self, 'Function Error', self.environmentName + " doesn't support referencing yet !!!", QtGui.QMessageBox.Ok )
            
            if envStatus:
                #self.close()
                QtGui.QMessageBox.information(self, 'Asset Reference', 'Asset :\n\n'+ assetObject.getFileName() +'\n\nis referenced successfuly', QtGui.QMessageBox.Ok)
        
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






########################################################################
class InterfaceRunner(QtCore.QThread):
    """runs the other windows as another thread
    """
    
    #----------------------------------------------------------------------
    def __init__(self, parentA=None, interface=None, **interfaceArgs):
        QtCore.QThread.__init__(self, parentA)
        self._interface = interface
        self._interfaceArgs = interfaceArgs
    
    
    
    #----------------------------------------------------------------------
    def run(self):
        """runs the thread, thus the interface
        """
        
        if self._interface != None:
            self._interface( **self._interfaceArgs )
