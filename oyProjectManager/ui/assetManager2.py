# -*- coding: utf-8 -*-



import os, sys
from PyQt4 import QtGui, QtCore
import assetManager2_UI

import oyProjectManager
from oyProjectManager import utils
from oyProjectManager.core.models import Asset, Project, Sequence, Repository
from oyProjectManager.environments import environmentFactory
from oyProjectManager.ui import assetUpdater, singletonQApplication
from oyProjectManager.ui import assetCreator_UI




def UI( environmentName=None ):
    """the UI to call the dialog by itself
    """
    global app
    global mainDialog
    app = singletonQApplication.QApplication(sys.argv)
    mainDialog = MainDialog( environmentName )
    mainDialog.show()
    #app.setStyle('Plastique')
    app.exec_()
    app.connect(app, QtCore.SIGNAL("lastWindowClosed()"), app, QtCore.SLOT("quit()"))






########################################################################
class MainDialog(QtGui.QDialog, assetManager2_UI.Ui_Dialog):
    """the main dialog of the system
    """
    
    
    
    
    def __init__(self, environmentName=None, parent=None):
        super(MainDialog,self).__init__(parent)
        
        self.setupUi(self)
        
        # create the assetCreator_UI
        self.assetCreatorUI = assetCreator_UI.AssetCreator( self.saveAsset_groupBox )
        self.saveAsset_groupBox.adjustSize()
        
        # change the window title
        environmentTitle = ''
        if environmentName != None:
            environmentTitle = environmentName
        
        self._environmentFactory = environmentFactory.EnvironmentFactory()
        
        self.setWindowTitle( environmentTitle + ' | ' + self.windowTitle() + ' v' + __version__ + ' | ' + 'oyProjectManager v' + oyProjectManager.__version__ )
        
        # center to the window
        self._centerWindow()
        
        
        # setup validators
        self._setupValidators()
        
        # create a repository object
        self._repo = repository.Repository()
        
        # fill them later
        self._asset = None
        self._environment = None
        self._project = None
        self._sequence = None
        self._versionListBuffer = []
        self._lastValidShotSelection = None
        
        # create the environment object
        self._setEnvironment( environmentName )
        
        self.fileName = ''
        self.path = ''
        self.fullPath = ''
        
        # setup signals
        self._setupSignals()
        
        self._setDefaults()
        self.update_project_list()
        
        self.getSettingsFromEnvironment()
        
        #self.fillFieldsFromFileInfo()
    
    
    
    
    def _setEnvironment(self, environmentName):
        """sets the environment object from the environemnt name
        """
        #self._environment = environmentFactory.EnvironmentFactory.create( self._asset, environmentName )
        self._environment = self._environmentFactory.create( self._asset, environmentName )
    
    
    
    
    def _setupSignals(self):
        """sets up the signals/slots
        """
        
        # connect SIGNALs
        # SAVE
        QtCore.QObject.connect( self.save_button,
                                QtCore.SIGNAL("clicked()"),
                                self.saveAsset )
        
        # EXPORT
        QtCore.QObject.connect( self.export_button,
                                QtCore.SIGNAL("clicked()"),
                                self.exportAsset )
        
        # OPEN
        QtCore.QObject.connect( self.open_button,
                                QtCore.SIGNAL("clicked()"),
                                self.openAsset )
        # add double clicking to assetList too
        QtCore.QObject.connect( self.assets_tableWidget1,
                                QtCore.SIGNAL("cellDoubleClicked(int,int)"),
                                self.openAsset )
        
        # REFERENCE
        QtCore.QObject.connect( self.reference_button,
                                QtCore.SIGNAL("clicked()"),
                                self.referenceAsset )
        
        # IMPORT
        QtCore.QObject.connect( self.import_button,
                                QtCore.SIGNAL("clicked()"),
                                self.importAsset )
        
        # validate input texts
        #QtCore.QObject.connect( self.note_lineEdit1,
                                #QtCore.SIGNAL("textChanged(QString)"),
                                #self.validateNotes )
        
        # close button
        QtCore.QObject.connect( self.close_button,
                                QtCore.SIGNAL("clicked()"),
                                self.close )
        
        # project change ---> update sequence
        QtCore.QObject.connect( self.assetCreatorUI.project_comboBox,
                                QtCore.SIGNAL("currentIndexChanged(int)"),
                                self._updateProjectObject )
        
        QtCore.QObject.connect( self.assetCreatorUI.project_comboBox,
                                QtCore.SIGNAL("currentIndexChanged(int)"),
                                self.updateSequenceList )
        
        # sequence change ---> update noSubNameField
        QtCore.QObject.connect( self.assetCreatorUI.sequence_comboBox,
                                QtCore.SIGNAL("currentIndexChanged(int)"),
                                self._updateSequenceObject )
        
        QtCore.QObject.connect( self.assetCreatorUI.sequence_comboBox,
                                QtCore.SIGNAL("currentIndexChanged(int)"),
                                self.updateForNoSubName )
        
        # sequence change ---> update asset type
        QtCore.QObject.connect( self.assetCreatorUI.sequence_comboBox,
                                QtCore.SIGNAL("currentIndexChanged(int)"),
                                self.updateAssetTypeList )
        
        # sequence change ---> update shot lists
        QtCore.QObject.connect( self.assetCreatorUI.sequence_comboBox,
                                QtCore.SIGNAL("currentIndexChanged(int)"),
                                self.updateShotList )
        
        # type change ---> base and shot enable disable
        QtCore.QObject.connect( self.assetCreatorUI.assetType_comboBox1,
                                QtCore.SIGNAL("currentIndexChanged(int)"),
                                self.updateShotDependentFields )
        
        # type change ---> fill baseName comboBox and update subName
        QtCore.QObject.connect( self.assetCreatorUI.assetType_comboBox1,
                                QtCore.SIGNAL("currentIndexChanged(int)"),
                                self.updateBaseNameField )
        
        QtCore.QObject.connect( self.assetCreatorUI.assetType_comboBox1,
                                QtCore.SIGNAL("currentIndexChanged(int)"),
                                self.updateSubNameField )
        
        # shotName change ---> update frame ranges
        QtCore.QObject.connect( self.assetCreatorUI.shot_comboBox1,
                                QtCore.SIGNAL("currentIndexChanged(int)"),
                                self.updateShotDataFields )
        
        # shotName or baseName change ---> fill subName comboBox
        QtCore.QObject.connect( self.assetCreatorUI.shot_comboBox1,
                                QtCore.SIGNAL("currentIndexChanged(int)"),
                                self.updateSubNameField )
        
        QtCore.QObject.connect( self.assetCreatorUI.baseName_lineEdit, #self.baseName_lineEdit,
                                QtCore.SIGNAL("textChanged(QString)"),
                                self.updateSubNameField )
        
        # subName change ---> full update assets_tableWidget1
        QtCore.QObject.connect( self.assetCreatorUI.project_comboBox,
                                QtCore.SIGNAL("currentIndexChanged(int)"),
                                self.fullUpdateAssetsTableWidget )
        
        QtCore.QObject.connect( self.assetCreatorUI.sequence_comboBox,
                                QtCore.SIGNAL("currentIndexChanged(int)"),
                                self.fullUpdateAssetsTableWidget )
        
        QtCore.QObject.connect( self.assetCreatorUI.assetType_comboBox1,
                                QtCore.SIGNAL("currentIndexChanged(int)"),
                                self.fullUpdateAssetsTableWidget )
        
        QtCore.QObject.connect( self.assetCreatorUI.shot_comboBox1,
                                QtCore.SIGNAL("currentIndexChanged(int)"),
                                self.fullUpdateAssetsTableWidget )
        
        QtCore.QObject.connect( self.assetCreatorUI.baseName_lineEdit,
                                QtCore.SIGNAL("textChanged(QString)"),
                                self.fullUpdateAssetsTableWidget )
        
        QtCore.QObject.connect( self.assetCreatorUI.subName_lineEdit,
                                QtCore.SIGNAL("textChanged(QString)"),
                                self.fullUpdateAssetsTableWidget )
        
        # get latest revision --> revision
        QtCore.QObject.connect( self.assetCreatorUI.revision_pushButton,
                                QtCore.SIGNAL("clicked()"),
                                self.updateRevisionToLatest )
        
        # get latest version --> version
        QtCore.QObject.connect( self.assetCreatorUI.version_pushButton,
                                QtCore.SIGNAL("clicked()"),
                                self.updateVersionToLatest )
        
        # sequence, type, shotName, baseName or subName change --> revision + version
        QtCore.QObject.connect( self.assetCreatorUI.sequence_comboBox,
                                QtCore.SIGNAL("currentIndexChanged(int)"),
                                self.updateRevisionToLatest )
        
        QtCore.QObject.connect( self.assetCreatorUI.sequence_comboBox,
                                QtCore.SIGNAL("currentIndexChanged(int)"),
                                self.updateVersionToLatest )
        
        QtCore.QObject.connect( self.assetCreatorUI.assetType_comboBox1,
                                QtCore.SIGNAL("currentIndexChanged(int)"),
                                self.updateRevisionToLatest )
        
        QtCore.QObject.connect( self.assetCreatorUI.assetType_comboBox1,
                                QtCore.SIGNAL("currentIndexChanged(int)"),
                                self.updateVersionToLatest )
        
        QtCore.QObject.connect( self.assetCreatorUI.shot_comboBox1,
                                QtCore.SIGNAL("currentIndexChanged(int)"),
                                self.updateRevisionToLatest )
        
        QtCore.QObject.connect( self.assetCreatorUI.shot_comboBox1,
                                QtCore.SIGNAL("currentIndexChanged(int)"),
                                self.updateVersionToLatest )
        
        QtCore.QObject.connect( self.assetCreatorUI.baseName_lineEdit,
                                QtCore.SIGNAL("textChanged(QString)"),
                                self.updateRevisionToLatest )
        
        QtCore.QObject.connect( self.assetCreatorUI.baseName_lineEdit,
                                QtCore.SIGNAL("textChanged(QString)"),
                                self.updateVersionToLatest )
        
        QtCore.QObject.connect( self.assetCreatorUI.subName_lineEdit,
                                QtCore.SIGNAL("textChanged(QString)"),
                                self.updateRevisionToLatest )
        
        QtCore.QObject.connect( self.assetCreatorUI.subName_lineEdit,
                                QtCore.SIGNAL("textChanged(QString)"),
                                self.updateVersionToLatest )
        
        # showLastNEntry_checkbox or numberOfEntry change -> partial update assets_tableWidget1
        QtCore.QObject.connect( self.showLastNEntry_checkBox,
                                QtCore.SIGNAL("stateChanged(int)"),
                                self.partialUpdateAssetsTableWidget )
        
        QtCore.QObject.connect( self.numberOfEntry_spinBox,
                                QtCore.SIGNAL("valueChanged(int)"),
                                self.partialUpdateAssetsTableWidget )
        
        # baseName_listWidget -> baseName_lineEdit
        # subName_listWidget -> subName_lineEdit
        QtCore.QObject.connect( self.assetCreatorUI.baseName_listWidget,
                                QtCore.SIGNAL("currentTextChanged(QString)"),
                                self.updateBaseNameLineEdit )
        
        QtCore.QObject.connect( self.assetCreatorUI.subName_listWidget,
                                QtCore.SIGNAL("currentTextChanged(QString)"),
                                self.updateSubNameLineEdit )
        
        
        QtCore.QMetaObject.connectSlotsByName(self)
    
    
    
    
    def _setupValidators(self):
        """sets up the input validators
        """
        
        ## new item to the baseName_listWidget
        #QtCore.QObject.connect(self.baseName_listWidget, QtCore.SIGNAL("itemDoubleClicked(QListWidgetItem*)"), self.addNewListItem )
        
        # attach validators
        QtCore.QObject.connect( self.assetCreatorUI.baseName_lineEdit,
                                QtCore.SIGNAL("textChanged(QString)"),
                                self.validateBaseName )
        
        QtCore.QObject.connect( self.assetCreatorUI.subName_lineEdit,
                                QtCore.SIGNAL("textChanged(QString)"),
                                self.validateSubName )
    
    
    
    
    def _centerWindow(self):
        """centers the window to the screen
        """
        
        screen = QtGui.QDesktopWidget().screenGeometry()
        size =  self.geometry()
        self.move((screen.width()-size.width())/2, (screen.height()-size.height())/2)
    
    
    
    
    def _setDefaults(self):
        """sets the default values
        """
        
        # set sub name to MAIN by default
        self.assetCreatorUI.subName_listWidget.clear()
        self.assetCreatorUI.subName_listWidget.addItem( "MAIN" )
        
        # append the users to the users list
        userInits = self._repo.user_initials
        
        self.assetCreatorUI.user_comboBox1.clear()
        self.assetCreatorUI.user_comboBox1.addItems( userInits )
        
        # update the user with the last selected user
        last_user = self._repo.last_user
        
        userIndex = -1
        if last_user != '' and last_user != None:
            userIndex = self.assetCreatorUI.user_comboBox1.findText(last_user) 
        
        if userIndex == -1:
            userIndex = 0
        
        self.assetCreatorUI.user_comboBox1.setCurrentIndex( userIndex )
        
        # add the assets_tableWidget1 horizontal header labels
        self._horizontalLabels = [ 'Asset FileName', 'File Size', 'Date Updated' ]
        self.assets_tableWidget1.setHorizontalHeaderLabels( self._horizontalLabels )
        
        # set spinbox default value to 10
        self.numberOfEntry_spinBox.setValue(10)
    
    
    
    
    def fillFieldsFromFileInfo(self):
        """fills the ui fields from the data that comes from the fileName and path
        """
        
        # no use without the path
        if self.path == None or self.path == '':
            return
        
        # get the project and sequence names
        projectName, sequenceName = self._repo.get_project_and_sequence_name_from_file_path( self.path )
                
        if projectName == None or projectName == '' or sequenceName == None or sequenceName == '':
            return
        
        currentProject = project.Project( projectName )
        
        if not currentProject.exists:
            return
        
        currentSequence = project.Sequence( currentProject, sequenceName )
        
        if not currentSequence.exists:
            return
        
        # set the project and sequence
        self.setProjectName( projectName )
        self.setSequenceName( sequenceName )
        
        # no file name no use of the rest
        if self.fileName == None:
            return
        
        # fill the fields with those info
        # create an asset with the file name and get the information from that asset object
        
        assetObj = Asset( currentProject, currentSequence, self.fileName )
        
        if not assetObj.isValidAsset and not assetObj.exists:
            return
        
        assetType = assetObj.type.name
        shotNumber = assetObj.shotNumber
        baseName = assetObj.baseName
        subName = assetObj.subName
        revNumber = assetObj.revisionNumber
        verNumber = assetObj.versionNumber
        userInitials = assetObj.userInitials
        notes = assetObj.notes
        
        # fill the fields
        # assetType
        element = self.assetCreatorUI.assetType_comboBox1
        element.setCurrentIndex( element.findText( assetType ) )
        
        # ----------------------------------------------------------------------
        # shotNumber and baseName
        if assetObj.isShotDependent:
            element = self.assetCreatorUI.shot_comboBox1
            element.setCurrentIndex( element.findText( shotNumber) )
            
            # update self._lastValidShotSelection
            self._lastValidShotSelection = shotNumber
        
        else:
            
            itemIndex = self.findListItemWithText( self.assetCreatorUI.baseName_listWidget, baseName )
            if itemIndex != -1:
                # get the item and set it selected and current item on the list
                item = self.assetCreatorUI.baseName_listWidget.item( itemIndex )
                item.setSelected(True)
                self.assetCreatorUI.baseName_listWidget.setCurrentItem( item )
                
                # update the selection
                self.updateBaseNameLineEdit( baseName )
        # ----------------------------------------------------------------------
        
        
        
        # ----------------------------------------------------------------------
        # sub Name
        if not currentSequence.no_sub_name_field: # remove this block when the support for old version becomes obsolute
            
            itemIndex = self.findListItemWithText( self.assetCreatorUI.subName_listWidget, subName )
            if itemIndex != -1:
                # get the item and set it selected and current item on the list
                item = self.assetCreatorUI.subName_listWidget.item( itemIndex )
                item.setSelected(True)
                self.assetCreatorUI.subName_listWidget.setCurrentItem( item )
                
                self.updateSubNameLineEdit( subName )
        # ----------------------------------------------------------------------
        
        
        # revision
        self.assetCreatorUI.revision_spinBox.setValue( revNumber )
        
        # version : set the version and increase it by one
        self.assetCreatorUI.version_spinBox.setValue( verNumber )
        self.updateVersionToLatest()
        
        # notes
        self.assetCreatorUI.note_lineEdit1.setText( notes )
    
    
    
    
    def update_project_list(self):
        """updates projects list
        """
        
        server_path = self._repo.server_path
        
        projectsList = self._repo.valid_projects
        projectsList.sort()
        
        self.assetCreatorUI.server_comboBox.clear()
        self.assetCreatorUI.project_comboBox.clear()
        self.assetCreatorUI.server_comboBox.addItem( server_path )
        self.assetCreatorUI.project_comboBox.addItems( projectsList )
    
    
    
    
    def updateSequenceList(self, *arg):
        """updates the sequence according to selected project
        """
        
        self._updateProjectObject()
        currentProjet = self._project
        
        # create a project and ask the child sequences
        self.assetCreatorUI.sequence_comboBox.clear()
        sequences = currentProjet.sequenceNames()
        
        self.assetCreatorUI.sequence_comboBox.addItems( sequences )
        
        self._updateSequenceObject() # it is not needed but do it for now
    
    
    
    
    def updateAssetTypeList(self):
        """updates asset types
        """
        
        # get the asset types of that sequence
        self._updateSequenceObject()
        currentSequence = self._sequence
        
        # get asset types
        assetTypes = currentSequence.getAssetTypes( self._environment.name )
        
        assetTypeNames = [ assetType.name for assetType in assetTypes ]
        
        
        # clear and update the comboBoxes
        # try to keep the same item in the list
        lastSelectedItem = self.assetCreatorUI.assetType_comboBox1.currentText()
        self.assetCreatorUI.assetType_comboBox1.clear()
        self.assetCreatorUI.assetType_comboBox1.addItems( assetTypeNames )
        # reselect the last selected item
        
        if lastSelectedItem != "":
            self.assetCreatorUI.assetType_comboBox1.setCurrentIndex( self.assetCreatorUI.assetType_comboBox1.findText( lastSelectedItem ) )
    
    
    
    
    def updateShotList(self):
        """updates shot list
        """
        
        self._updateSequenceObject()
        
        # try to keep the selection
        lastSelectedShot = self.assetCreatorUI.shot_comboBox1.currentText()
        
        # clear and update the list
        self.assetCreatorUI.shot_comboBox1.clear()
        self.assetCreatorUI.shot_comboBox1.addItems( self._sequence.shotList )
        
        index = -1
        
        if self._lastValidShotSelection != "" and self._lastValidShotSelection != None:
            index = self.assetCreatorUI.assetType_comboBox1.findText( self._lastValidShotSelection )
            
            if index != -1:
                self.assetCreatorUI.shot_comboBox1.setCurrentIndex( index )
            
        else:
            self._lastValidShotSelection = self.assetCreatorUI.assetType_comboBox1.currentText()
    
    
    
    
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
        
        if currentType == None or currentType.isShotDependent:
            # do nothing
            return
        
        # remove duplicates
        baseNamesList = currentSequence.getAssetBaseNamesForType( currentTypeName )
        
        # add them to the baseName combobox
        self.assetCreatorUI.baseName_listWidget.clear()
        
        # add the list
        self.assetCreatorUI.baseName_listWidget.addItems( sorted(baseNamesList) )
        
        # select the first one in the list
        if len(baseNamesList) > 0:
            listItem = self.assetCreatorUI.baseName_listWidget.item(0)
            #assert(isinstance(listItem, QtGui.QListWidgetItem ))
            listItem.setSelected(True)
            
            self.updateBaseNameLineEdit( listItem.text() )
    
    
    
    
    def updateBaseNameLineEdit(self, baseName):
        """updates the baseName_lineEdit according to the selected text in the
        baseName_listWidget
        """
        
        self.assetCreatorUI.baseName_lineEdit.setText( baseName )
    
    
    
    
    def updateSubNameField(self):
        """updates the subName fields with current asset subNames for selected
        baseName, if the type is not shot dependent
        """
        
        # if the current selected type is not shot dependent
        # get all the assets of that type and get their baseNames
        self._updateSequenceObject()
        currentSequence = self._sequence
        
        # if the current sequence doesn't support subName field just return
        if currentSequence.no_sub_name_field:
            self.assetCreatorUI.subName_listWidget.clear()
            return
        
        currentAssetTypeName = self.getCurrentAssetType()
        
        assetTypeObj = currentSequence.getAssetTypeWithName( currentAssetTypeName )
        
        if assetTypeObj == None:
            # clear the current subName field and return
            self.assetCreatorUI.subName_listWidget.clear()
            return
        
        if assetTypeObj.isShotDependent:
            currentBaseName = currentSequence.convertToShotString( self.getCurrentShotString() )
        else:
            currentBaseName = self.getCurrentBaseName()
        
        self.assetCreatorUI.subName_listWidget.clear()
        
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
        subNamesList = utils.unique( subNamesList )
        
        # add them to the baseName combobox
        
        # do not add an item for new items, the default should be MAIN
        # add the list
        self.assetCreatorUI.subName_listWidget.addItems( sorted(subNamesList) )
        
        # update subName line edit
        self.updateSubNameLineEdit( 'MAIN' ) #, 'updateSubNameField' )
    
    
    
    
    def updateSubNameLineEdit( self, subName ):#, caller_id=None):
        """updates the subName_lineEdit according to the selected text in the
        subName_listWidget
        """
        #print "updateSubNAmeLineEdit.caller_id -> ", caller_id
        #print "subName -> ", subName
        self.assetCreatorUI.subName_lineEdit.setText( subName )
    
    
    
    #
    #def updateSubNameLineEditFromSignal(self):
        #"""updates the subName_lineEdit triggered by a signal
        #"""
        
        
        
        ## get the current item text
        ##itemIndex = self.findListItemWithText( self.subName_listWidget, 
        
        #text = self.subName_listWidget.
    
    
    
    
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
        isShotDependent = assetType.isShotDependent
        self.assetCreatorUI.shot_comboBox1.setEnabled( isShotDependent )
        
        self.assetCreatorUI.baseName_listWidget.setEnabled( not isShotDependent )
        self.assetCreatorUI.baseName_lineEdit.setEnabled( not isShotDependent )
    
    
    
    
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
        if currentSequence.getAssetTypeWithName( typeName ).isShotDependent:
            baseName = currentSequence.convertToShotString( self.getCurrentShotString() )
        else:
            baseName = self.getCurrentBaseName()
        
        
        if not currentSequence.no_sub_name_field:
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
        
        self._versionListBuffer = []
        
        if len(allVersionsList) > 0:
            self._versionListBuffer = sorted( filter( self._environment.hasValidExtension, allVersionsList ) )
    
    
    
    
    def partialUpdateAssetsTableWidget(self):
        """just updates if the number of maximum displayable entry is changed
        """
        
        _buffer = []
        if self.showLastNEntry_checkBox.isChecked():
            
            # get the number of entry
            numOfEntry = min( len(self._versionListBuffer), self.numberOfEntry_spinBox.value() )
            
            # fill the list
            _buffer = self._versionListBuffer[-numOfEntry:]
            
        else:
            _buffer = self._versionListBuffer
        
        self.fillAssetsTableWidget( _buffer )
    
    
    
    
    def fillAssetsTableWidget(self, assetFileNames):
        """fills the assets table widget with given assets
        """
        
        assetCount = len(assetFileNames)
        
        
        self.assets_tableWidget1.clear()
        self.assets_tableWidget1.setRowCount( assetCount )
        
        # set the labels
        self.assets_tableWidget1.setHorizontalHeaderLabels( self._horizontalLabels )
        
        data = []
        
        if assetCount == 0 :
            return
        
        for i,assetFileName in enumerate(assetFileNames):
            #assert( isinstance(asset, asset.Asset))
            
            if assetFileName is None:
                continue
            
            assetObj = Asset( self._project, self._sequence, assetFileName )
            
            fileName = assetObj.fileName
            fileSize = assetObj.fileSizeFormated
            dateUpdated = assetObj.dateUpdated
            
            if fileName is None or dateUpdated is None or fileSize is None:
                continue
            
            #print fileName, dateUpdated
            data.append( ( assetObj, fileName, fileSize, dateUpdated ) )
            
            # ------------------------------------
            # asset fileName
            assetFileName_tableWI = QtGui.QTableWidgetItem( fileName )
            # align to left and verticle center
            assetFileName_tableWI.setTextAlignment( 0x0001 | 0x0080  )
            self.assets_tableWidget1.setItem( i, 0, assetFileName_tableWI )
            # ------------------------------------
            
            # ------------------------------------
            # asset fileSize
            assetFileSize_tableWI = QtGui.QTableWidgetItem( fileSize )
            # align to center and verticle center
            assetFileSize_tableWI.setTextAlignment( 0x0002 | 0x0080  )
            self.assets_tableWidget1.setItem( i, 1, assetFileSize_tableWI )
            # ------------------------------------
            
            # ------------------------------------
            # asset dateUpdated
            assetDateUpdated_tableWI = QtGui.QTableWidgetItem( dateUpdated )
            # align to left and verticle center
            assetDateUpdated_tableWI.setTextAlignment( 0x0004 | 0x0080  )
            self.assets_tableWidget1.setItem( i, 2, assetDateUpdated_tableWI )
            # ------------------------------------
        
        # check and create the table data attr
        setattr( self.assets_tableWidget1, 'tableData', data )
        
        # resize the first column
        self.assets_tableWidget1.resizeColumnToContents(0)
    
    
    
    
    def fullUpdateAssetsTableWidget(self):
        """invokes a version list buffer update and a assets list widget update
        """
        self.updateVersionListBuffer()
        self.partialUpdateAssetsTableWidget()
    
    
    
    
    def getCurrentProjectName(self):
        """returns the current project name
        """
        return unicode( self.assetCreatorUI.project_comboBox.currentText() )
    
    
    
    
    def getCurrentSequenceName(self):
        """returns the current sequence name
        """
        return unicode( self.assetCreatorUI.sequence_comboBox.currentText() )
    
    
    
    
    def getCurrentAssetType(self):
        """returns the current assetType from the UI
        """
        return unicode( self.assetCreatorUI.assetType_comboBox1.currentText() )
    
    
    
    
    def getCurrentShotString(self):
        """returns the current shot string from the UI
        """
        return unicode( self.assetCreatorUI.shot_comboBox1.currentText() )
    
    
    
    
    def getCurrentBaseName(self):
        """returns the current baseName from the UI
        """
        #return unicode( self.baseName_comboBox1.currentText() )
        return unicode( self.assetCreatorUI.baseName_lineEdit.text() )
    
    
    
    
    def getCurrentSubName(self):
        """returns the current subName from the UI
        """
        return unicode( self.assetCreatorUI.subName_lineEdit.text() )
    
    
    
    
    def getCurrentRevNumber(self):
        """returns the current revision number from the UI
        """
        return unicode( self.assetCreatorUI.revision_spinBox.value() )
    
    
    
    
    def getCurrentVerNumber(self):
        """returns the current version number from the UI
        """
        return unicode( self.assetCreatorUI.version_spinBox.value() )
    
    
    
    
    def getCurrentUserInitials(self):
        """returns the current user initials from the UI
        """
        return unicode( self.assetCreatorUI.user_comboBox1.currentText() )
    
    
    
    
    def getCurrentNote(self):
        """returns the current note from the UI
        """
        return unicode( self.assetCreatorUI.note_lineEdit1.text() )
    
    
    
    
    def updateRevisionToLatest(self):
        """ tries to get the latest revision
        """
        
        # get the asset object from fields
        self._createAssetObjectFromSaveFields()#'updateRevisionToLatest' )
        
        #if assetObj == None or not asset.isValidAsset:
        if self._asset == None or not self._asset.isValidAsset:
            self.setRevisionNumberField( 0 )
            return
        
        maxRevAsset, maxRevNumber = self._asset.latestRevision2
        
        if maxRevNumber == None:
            maxRevNumber = 0
            
        # update the field
        self.setRevisionNumberField( maxRevNumber )
    
    
    
    
    def updateVersionToLatest(self):
        """ tries to get the latest version
        """
        
        # get the asset objet from fields
        self._createAssetObjectFromSaveFields()#'updateVersionToLatest' )
        
        if self._asset == None or not self._asset.isValidAsset:
            self.setVersionNumberField( 1 )
            return
        
        maxVerAsset, maxVerNumber = self._asset.latestVersion2
        
        if maxVerNumber == None:
            maxVerNumber = 0
        
        # update the field
        self.setVersionNumberField( maxVerNumber + 1 )
    
    
    
    
    def setProjectName(self, projectName):
        """sets the project in the combobox
        """
        if projectName == None:
            return
        
        index = self.assetCreatorUI.project_comboBox.findText( projectName )
        
        if index != -1:
            self.assetCreatorUI.project_comboBox.setCurrentIndex( index )
        
        # be sure it is updated
        self.assetCreatorUI.project_comboBox.update()
    
    
    
    
    def setSequenceName(self, sequenceName):
        """sets the sequence in the combobox
        """
        if sequenceName == None:
            return
        
        currentIndex = self.assetCreatorUI.sequence_comboBox.currentIndex()
        
        index = self.assetCreatorUI.sequence_comboBox.findText( sequenceName )
        
        if index != -1:
            self.assetCreatorUI.sequence_comboBox.setCurrentIndex( index )
        
        # be sure it is updated
        self.assetCreatorUI.sequence_comboBox.update()
    
    
    
    
    def _createAssetObjectFromSaveFields(self):#, caller_id=None):
        """returns the asset object from the fields
        """
        
        if self._project == None or self._sequence == None:
            return None
        
        assetObj = Asset( self._project, self._sequence )
        
        # gather information
        typeName = self.getCurrentAssetType()
        
        assetTypeObj = self._sequence.getAssetTypeWithName(typeName)
        
        if assetTypeObj == None:
            return
        
        isShotDependent = assetTypeObj.isShotDependent
        if isShotDependent:
            baseName = self._sequence.convertToShotString( self.getCurrentShotString() )
        else:
            baseName = self.getCurrentBaseName()
        
        subName = self.getCurrentSubName()
        rev = self.getCurrentRevNumber()
        ver = self.getCurrentVerNumber()
        userInitials = self.getCurrentUserInitials()
        notes = self.getCurrentNote()
        
        
        #print "_createAssetObjectFromSaveFields, caller_id ->", caller_id
        #print "baseName -> ", baseName
        #print "subName -> ", subName
        
        
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
        
        self._asset = assetObj
        # set the environment to the current asset object
        self._environment.asset = self._asset
        
    
    
    
    
    def _createAssetObjectFromOpenFields(self):
        """retriewes the file name from the open asset fields
        """
        
        index = self.assets_tableWidget1.currentIndex().row()
        assetFileName = unicode(self.assets_tableWidget1.tableData[index][1])
        self._asset = Asset( self._project, self._sequence, assetFileName )
        self._environment.asset = self._asset
    
    
    
    
    def getFileNameFromSaveFields(self):
        """returns the file name from the fields
        """
        # get the asset object from fields
        self._createAssetObjectFromSaveFields()#'getFileNameFromSaveFields' )
        
        if self._asset == None:
            return None, None
        
        return self._asset.pathVariables, self._asset
    
    
    
    
    def setRevisionNumberField(self, revNumber):
        """sets the revision number field in the interface
        """
        self.assetCreatorUI.revision_spinBox.setValue( revNumber )
    
    
    
    
    def setVersionNumberField(self, verNumber):
        """sets the version number field in the interface
        """
        self.assetCreatorUI.version_spinBox.setValue( verNumber )
    
    
    
    def updateShotDataFields(self, index):
        """updates the shot data fields like the frame range fields and the
        shot description fields according to the current shot
        """
        
        # get the shot object from the sequence
        shot = self._sequence.shots[ index ]
        
        self.startFrame_spinBox.setValue( shot.startFrame )
        self.endFrame_spinBox.setValue( shot.endFrame )
        
        self.shotDescription_textEdit.setText( shot.description )
    
    
    
    
    def updateForNoSubName(self):
        """this method will be removed in later version, it is written just to support
        old types of assets those have no subName field
        """
        
        # if the current sequence has no support for subName fields disable them
        self._updateSequenceObject()
        currentSequence = self._sequence
        
        self.assetCreatorUI.subName_listWidget.setEnabled(not currentSequence.no_sub_name_field)
        self.assetCreatorUI.subName_lineEdit.setEnabled(not currentSequence.no_sub_name_field)
    
    
    
    
    def _updateProjectObject(self):
        """updates the project object if it is changed
        it is introduced to take advantege of the cache system
        """
        
        currentProjectName = self.getCurrentProjectName()
        
        if self._project == None or self._project.name != currentProjectName or (currentProjectName != "" or currentProjectName != None ):
            self._project = project.Project( currentProjectName )
    
    
    
    def _updateSequenceObject(self):
        """updates the sequence object if it is not
        """
        
        currentSequenceName = self.getCurrentSequenceName()
        
        #assert(isinstance(self._sequence,Sequence))
        if self._sequence == None or self._sequence.name != currentSequenceName and (currentSequenceName != "" or currentSequenceName != None ) or \
           self._sequence.projectName != self._project.name:
            self._updateProjectObject()
            newSeq = project.Sequence( self._project, currentSequenceName )
            if newSeq._exists:
                self._sequence = newSeq
    
    
    
    
    def validateSubName(self, text):
        """validates the subName field by removing unneccessary characters
        """
        
        # just replace the validated text
        self.assetCreatorUI.subName_lineEdit.setText( self.fieldNameValidator(text) )
    
    
    
    
    def validateBaseName(self, text):
        """validates the baseName field by removing unneccessary characters
        """
        
        # just replace the validated text
        self.assetCreatorUI.baseName_lineEdit.setText( self.fieldNameValidator(text) )
    
    
    
    
    def fieldNameValidator(self, text):
        """a validator that validates input texts
        """
        text = unicode(text)
        
        if not len(text):
            return text
        
        # first remove invalid chars
        text = utils.invalidCharacterRemover(text, utils.validFileNameChars)
        
        # validate the text
        text = utils.stringConditioner( text, capitalize=False )
        
        # capitalize just the first letter
        text = text[0].upper() + text[1:]
        
        return text
    
    
    
    
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
    
    
    
    
    # ENVIRONMENT PREPARATION
    
    def getSettingsFromEnvironment(self):
        """gets the data from environment
        """
        
        if self._environment.name != None and self._environment.name != '':
            self.fileName, self.path = self._environment.getPathVariables()
            
            # update the interface
            self.fillFieldsFromFileInfo()
    
    
    
    
    # SAVE & OPEN & IMPORT & REFERENCE ACTIONS FOR ENVIRONMENTS
    
    
    def checkOutputAsset(self, assetObject):
        """check if the asset is a valid asset
        """
        return assetObject.isValidAsset
    
    
    
    
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
                
                self.setVersionNumberField( assetObject.versionNumber )
                
                verStatus = True
        else:
            verStatus = True
        
        return verStatus
    
    
    
    
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
                
                self.setRevisionNumberField( assetObject.revisionNumber )
                
                revStatus = True
        else:
            revStatus = True
        
        return revStatus
    
    
    
    
    def checkOutputFileOverwrite(self, assetObject):
        """checks if the assetObject already exists, so user tries to overwrite
        """
        
        overwriteStatus = False
        
        # check for overwrites
        if assetObject.exists:
            answer = QtGui.QMessageBox.question(self, 'File Error', 'owerwrite?', QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
            if answer == QtGui.QMessageBox.Yes:
                overwriteStatus = True
        else:
            overwriteStatus = True
        
        return overwriteStatus
    
    
    
    
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
        self._createAssetObjectFromSaveFields()#'saveAsset' )
        
        if self._asset == None:
            return
        
        # check the file conditions
        assetStatus = self.checkOutputAsset( self._asset )
        verStatus = self.checkOutputFileVersion( self._asset )
        revStatus = self.checkOutputFileRevision( self._asset )
        overwriteStatus = self.checkOutputFileOverwrite( self._asset )
        
        envStatus = False
        
        if assetStatus and verStatus and revStatus and overwriteStatus:
            
            # before saving check the frame range
            # -----------------------------------------------------------------
            # check the frame range
            # -----------------------------------------------------------------
            # check the range if and only if the asset is shot dependent
            if self._asset.isShotDependent:
                # get the frame range from environment
                returnStat = self.adjustFrameRange()
                if returnStat == -1:
                    return
            # -----------------------------------------------------------------
            
            
            # check the timeUnit
            self.adjustTimeUnit()
            
            #everything is ok now save in the host application
            envStatus = self._environment.save()
            
            # if everything worked fine close the interface
            if envStatus:
                # set the last user variable
                self._repo.last_user = self._asset.userInitials
                
                #print info
                if self._environment.name == 'MAYA':
                    self.printInfo( self._asset,  "saved" )
                    
                self.close()
    
    
    
    
    def exportAsset(self):
        """prepares the data and sends the asset object to the function
        specially written for the host environment to open the asset file
        """
        
        # get the asset object
        self._createAssetObjectFromSaveFields() #'exportAsset' )
        
        if self._asset == None:
            return
        
        # check the file conditions
        assetStatus = self.checkOutputAsset( self._asset )
        verStatus = self.checkOutputFileVersion( self._asset )
        revStatus = self.checkOutputFileRevision( self._asset )
        overwriteStatus = self.checkOutputFileOverwrite( self._asset )
        
        envStatus = False
        
        if assetStatus and verStatus and revStatus and overwriteStatus:
            # everything is ok now save in the host application
            envStatus = self._environment.export()
            
            # if everything worked fine close the interface
            if envStatus:
                # do not set the last user variable
                
                # inform the user for successful operation
                
                QtGui.QMessageBox.information(self, 'Asset Export', 'Asset :\n\n'+ self._asset.fileName +'\n\nis exported successfuly', QtGui.QMessageBox.Ok)
                
                self.close()
    
    
    
    
    def openAsset(self):
        """prepares the data and sends the asset object to the function
        specially written for the host environment to open the asset file
        """
        
        # get the asset object
        self._createAssetObjectFromOpenFields()
        
        # check the file existancy
        exists = os.path.exists( self._asset.fullPath )
        
        envStatus = False
        
        # open the asset in the environment
        if exists:
            if self._environment.name == 'MAYA':
                
                toUpdateList = [] # the list that holds the assets those needs to be updated
                
                try:
                    envStatus, toUpdateList = self._environment.open_()
                except RuntimeError:
                    answer = QtGui.QMessageBox.question(self, 'RuntimeError', "There are <b>unsaved changes</b> in the current scene<br><br>Do you really want to open the file?", QtGui.QMessageBox.Yes, QtGui.QMessageBox.No )
                    
                    envStatus = False
                    
                    if answer== QtGui.QMessageBox.Yes:
                        envStatus, toUpdateList = self._environment.open_( True )
                    else:
                        return
                
                # check the toUpdateList to update old assets
                if len(toUpdateList):
                    # invoke the assetUpdater for this scene
                    assetUpdaterMainDialog = assetUpdater.MainDialog( self._environment.name, self )
                    assetUpdaterMainDialog.exec_()
                    
                # load references (Maya Only - for now)
                self._environment.load_references()
                
            elif self._environment.name == 'NUKE':
                envStatus = self._environment.open_()
            
            elif self._environment.name == 'HOUDINI':
                try:
                    envStatus = self._environment.open_()
                except RuntimeError:
                    answer = QtGui.QMessageBox.question(self, 'RuntimeError', "There are unsaved changes in the current scene\n\nDo you really want to open the file?", QtGui.QMessageBox.Yes, QtGui.QMessageBox.No )
                    
                    if answer== QtGui.QMessageBox.Yes:
                        envStatus = self._environment.open_( True )
            
            if envStatus:
                # -----------------------------------------------------------------
                # check the frame range
                # -----------------------------------------------------------------
                # check the range if and only if the asset is shot dependent
                
                if self._asset.isShotDependent and self._environment.name != 'NUKE':
                    # get the frame range from environment
                    self.adjustFrameRange()
                # -----------------------------------------------------------------
                self.close()
        
        else:
            # warn the user for non existing asset files
            answer = QtGui.QMessageBox.question(self, 'File Error', self._asset.fullPath + "\n\nAsset doesn't exist !!!", QtGui.QMessageBox.Ok )
    
    
    
    
    def importAsset(self):
        """prepares the data and sends the asset object to the function
        specially written for the host environment to import the asset file
        """
        
        # get the asset object
        self._createAssetObjectFromOpenFields()
        
        # check the file existancy
        exists = os.path.exists( self._asset.fullPath )
        
        envStatus = False
        
        # open the asset in the environment
        if exists:
            envStatus = self._environment.import_()
            
            if envStatus:
                #self.close()
                QtGui.QMessageBox.information(self, 'Asset Import', 'Asset :\n\n'+ self._asset.fileName +'\n\nis imported successfuly', QtGui.QMessageBox.Ok)
        
        else:
            # warn the user for non existing asset files
            answer = QtGui.QMessageBox.question(self, 'File Error', self._asset.fullPath + "\n\nAsset doesn't exist !!!", QtGui.QMessageBox.Ok )
    
    
    
    
    def referenceAsset(self):
        """prepares the data and sends the asset object to the function
        specially written for the host environment to reference the asset file
        
        beware that not all environments supports this action
        """
        
        # get the asset object
        self._createAssetObjectFromOpenFields()
        
        # check the file existancy
        exists = os.path.exists( self._asset.fullPath )
        
        envStatus = False
        
        # open the asset in the environment
        if exists:
            envStatus = self._environment.reference()
            
            if envStatus:
                QtGui.QMessageBox.information(self, 'Asset Reference', 'Asset :\n\n'+ self._asset.fileName +'\n\nis referenced successfuly', QtGui.QMessageBox.Ok)
        
        else:
            # warn the user for non existing asset files
            answer = QtGui.QMessageBox.question(self, 'File Error', self._asset.fullPath + "\n\nAsset doesn't exist !!!", QtGui.QMessageBox.Ok )
    
    
    
    
    def printInfo(self, assetObject, actionName):
        """prints info about action
        """
        
        print "-----------------------------------"
        print "AssetManager " + __version__
        print assetObject.fileName
        print actionName + " succesfully"
    
    
    
    
    def adjustFrameRange(self):
        """adjusts the frame range to match the shot settings
        
        returns
        -1 : Cancel
         0 : No
         1 : Yes
        """
        
        returnStat = 1
        # get the frame range from environment
        envStart, envEnd = self._environment.getFrameRange()
        
        # get the frame range from the sequence settings
        seq = self._asset.sequence
        #assert(isinstance(seq, project.Sequence))
        shot = seq.getShot( self._asset.shotNumber )
        
        if shot != None and envStart != None and envEnd != None:
            shotStart = shot.startFrame
            shotEnd = shot.endFrame
            
            if envStart != shotStart or envEnd != shotEnd:
                answer = QtGui.QMessageBox.question(self, 'FrameRange Error', "The current frame range is:<br><b>" + \
                                                    str(envStart) + "-" + str(envEnd) + "</b><br><br>The frame range of shot <b>" + shot.name + "</b> is:<br><b>" + \
                                                    str(shotStart) + "-" + str(shotEnd) + "</b><br><br>should your frame range be adjusted?", \
                                                    QtGui.QMessageBox.Yes, QtGui.QMessageBox.No, QtGui.QMessageBox.Cancel )
                
                if answer == QtGui.QMessageBox.Yes:
                    self._environment.setFrameRange( shotStart, shotEnd )
                    return 1
                if answer == QtGui.QMessageBox.Cancel:
                    # do nothing
                    return -1
            else: # set it incase the render frames are wrong
                self._environment.setFrameRange( shotStart, shotEnd )
                return 1
    
    
    
    
    def adjustTimeUnit(self):
        """adjusts the timeUnit to match the settings
        """
        
        # get the timeUnit of the environment
        timeUnit = self._environment.getTimeUnit()
        
        # get the timeUnit of the sequence
        seq = self._asset.sequence
        
        assert(isinstance(seq, project.Sequence))
        
        seqTimeUnit = seq.timeUnit
        
        if seq.timeUnit != timeUnit:
            answer = QtGui.QMessageBox.question(self, 'TimeUnit Error', "The current time unit is:<br><b>" + \
                                                timeUnit + \
                                                "</b><br><br>The time unit of the sequence is :<br><b>" + \
                                                seqTimeUnit + \
                                                "</b><br><br>your time unit will be adjusted!", \
                                                QtGui.QMessageBox.Ok )
            # adjust the time unit
            self._environment.setTimeUnit( seqTimeUnit )
