# -*- coding: utf-8 -*-
# Copyright (c) 2009-2012, Erkan Ozgur Yilmaz
# 
# This module is part of oyProjectManager and is released under the BSD 2
# License: http://www.opensource.org/licenses/BSD-2-Clause

import sys
import os
import logging
from sqlalchemy.exc import IntegrityError

from sqlalchemy.sql.expression import distinct

from PySide import QtGui, QtCore
import version_creator_UI

import oyProjectManager
from oyProjectManager import utils, config, db
from oyProjectManager.core.models import (Asset, Project, Sequence, Repository,
                                          Version, VersionType, Shot, User,
                                          VersionTypeEnvironments)
from oyProjectManager.environments import environmentFactory
from oyProjectManager.ui import version_updater, singletonQApplication

logger = logging.getLogger('beaker.container')
logger.setLevel(logging.WARNING)

# create a logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)

conf = config.Config()

def UI(environment):
    """the UI to call the dialog by itself
    """
    global app
    global mainDialog
    
#    app = singletonQApplication.QApplication()

    self_quit = False
    if QtGui.QApplication.instance() is None:
        app = QtGui.QApplication(*sys.argv)
        self_quit = True
    else:
        app = QtGui.QApplication.instance()
    
    mainDialog = MainDialog_New(environment)
    mainDialog.show()
    #app.setStyle('Plastique')
    app.exec_()
    
    if self_quit:
        app.connect(
            app,
            QtCore.SIGNAL("lastWindowClosed()"),
            app,
            QtCore.SLOT("quit()")
        )
    
    return mainDialog


class MainDialog(QtGui.QDialog, version_creator_UI.Ui_Dialog):
    """the main dialog of the system which helps to create new versions
    """
    
    def __init__(self, environmentName=None, parent=None):
        super(MainDialog, self).__init__(parent)
        self.setupUi(self)
        
        # change the window title
        environmentTitle = ''
        if environmentName is not None:
            environmentTitle = environmentName
        
        self._environmentFactory = environmentFactory.EnvironmentFactory()
        
        self.setWindowTitle(
            environmentTitle + ' | ' + self.windowTitle() + \
            ' | ' + 'oyProjectManager v' + oyProjectManager.__version__
        )
        
        # center to the window
        self._centerWindow()
        
        
        # setup validators
        self._setupValidators()
        
        # create a repository object
        self._repo = Repository()
        
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
    
    def _setEnvironment(self, environmentName):
        """sets the environment object from the environment name
        """
        self._environment = self._environmentFactory.create(self._asset, environmentName)
    
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
        QtCore.QObject.connect( self.project_comboBox,
                                QtCore.SIGNAL("currentIndexChanged(int)"),
                                self._updateProjectObject )
        
        QtCore.QObject.connect( self.project_comboBox,
                                QtCore.SIGNAL("currentIndexChanged(int)"),
                                self.updateSequenceList )
        
        # sequence change ---> update noSubNameField
        QtCore.QObject.connect( self.sequence_comboBox,
                                QtCore.SIGNAL("currentIndexChanged(int)"),
                                self._updateSequenceObject )
        
        QtCore.QObject.connect( self.sequence_comboBox,
                                QtCore.SIGNAL("currentIndexChanged(int)"),
                                self.updateForNoSubName )
        
        # sequence change ---> update asset type
        QtCore.QObject.connect( self.sequence_comboBox,
                                QtCore.SIGNAL("currentIndexChanged(int)"),
                                self.updateAssetTypeList )
        
        # sequence change ---> update shot lists
        QtCore.QObject.connect( self.sequence_comboBox,
                                QtCore.SIGNAL("currentIndexChanged(int)"),
                                self.updateShotList )
        
        # type change ---> base and shot enable disable
        QtCore.QObject.connect( self.assetType_comboBox1,
                                QtCore.SIGNAL("currentIndexChanged(int)"),
                                self.updateShotDependentFields )
        
        # type change ---> fill baseName comboBox and update subName
        QtCore.QObject.connect( self.assetType_comboBox1,
                                QtCore.SIGNAL("currentIndexChanged(int)"),
                                self.updateBaseNameField )
        
        QtCore.QObject.connect( self.assetType_comboBox1,
                                QtCore.SIGNAL("currentIndexChanged(int)"),
                                self.updateSubNameField )
        
        # shotName change ---> update frame ranges
        QtCore.QObject.connect( self.shot_comboBox1,
                                QtCore.SIGNAL("currentIndexChanged(int)"),
                                self.updateShotDataFields )
        
        # shotName or baseName change ---> fill subName comboBox
        QtCore.QObject.connect( self.shot_comboBox1,
                                QtCore.SIGNAL("currentIndexChanged(int)"),
                                self.updateSubNameField )
        
        QtCore.QObject.connect( self.baseName_lineEdit,
                                QtCore.SIGNAL("textChanged(QString)"),
                                self.updateSubNameField )
        
        # subName change ---> full update assets_tableWidget1
        QtCore.QObject.connect( self.project_comboBox,
                                QtCore.SIGNAL("currentIndexChanged(int)"),
                                self.fullUpdateAssetsTableWidget )
        
        QtCore.QObject.connect( self.sequence_comboBox,
                                QtCore.SIGNAL("currentIndexChanged(int)"),
                                self.fullUpdateAssetsTableWidget )
        
        QtCore.QObject.connect( self.assetType_comboBox1,
                                QtCore.SIGNAL("currentIndexChanged(int)"),
                                self.fullUpdateAssetsTableWidget )
        
        QtCore.QObject.connect( self.shot_comboBox1,
                                QtCore.SIGNAL("currentIndexChanged(int)"),
                                self.fullUpdateAssetsTableWidget )
        
        QtCore.QObject.connect( self.baseName_lineEdit,
                                QtCore.SIGNAL("textChanged(QString)"),
                                self.fullUpdateAssetsTableWidget )
        
        QtCore.QObject.connect( self.subName_lineEdit,
                                QtCore.SIGNAL("textChanged(QString)"),
                                self.fullUpdateAssetsTableWidget )
        
        # get latest revision --> revision
        QtCore.QObject.connect( self.revision_pushButton,
                                QtCore.SIGNAL("clicked()"),
                                self.updateRevisionToLatest )
        
        # get latest version --> version
        QtCore.QObject.connect( self.version_pushButton,
                                QtCore.SIGNAL("clicked()"),
                                self.updateVersionToLatest )
        
        # sequence, type, shotName, baseName or subName change --> revision + version
        QtCore.QObject.connect( self.sequence_comboBox,
                                QtCore.SIGNAL("currentIndexChanged(int)"),
                                self.updateRevisionToLatest )
        
        QtCore.QObject.connect( self.sequence_comboBox,
                                QtCore.SIGNAL("currentIndexChanged(int)"),
                                self.updateVersionToLatest )
        
        QtCore.QObject.connect( self.assetType_comboBox1,
                                QtCore.SIGNAL("currentIndexChanged(int)"),
                                self.updateRevisionToLatest )
        
        QtCore.QObject.connect( self.assetType_comboBox1,
                                QtCore.SIGNAL("currentIndexChanged(int)"),
                                self.updateVersionToLatest )
        
        QtCore.QObject.connect( self.shot_comboBox1,
                                QtCore.SIGNAL("currentIndexChanged(int)"),
                                self.updateRevisionToLatest )
        
        QtCore.QObject.connect( self.shot_comboBox1,
                                QtCore.SIGNAL("currentIndexChanged(int)"),
                                self.updateVersionToLatest )
        
        QtCore.QObject.connect( self.baseName_lineEdit,
                                QtCore.SIGNAL("textChanged(QString)"),
                                self.updateRevisionToLatest )
        
        QtCore.QObject.connect( self.baseName_lineEdit,
                                QtCore.SIGNAL("textChanged(QString)"),
                                self.updateVersionToLatest )
        
        QtCore.QObject.connect( self.subName_lineEdit,
                                QtCore.SIGNAL("textChanged(QString)"),
                                self.updateRevisionToLatest )
        
        QtCore.QObject.connect( self.subName_lineEdit,
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
        QtCore.QObject.connect( self.baseName_listWidget,
                                QtCore.SIGNAL("currentTextChanged(QString)"),
                                self.updateBaseNameLineEdit )
        
        QtCore.QObject.connect( self.subName_listWidget,
                                QtCore.SIGNAL("currentTextChanged(QString)"),
                                self.updateSubNameLineEdit )
        
        QtCore.QMetaObject.connectSlotsByName(self)
    
    def _setupValidators(self):
        """sets up the input validators
        """
        
        ## new item to the baseName_listWidget
        #QtCore.QObject.connect(self.baseName_listWidget, QtCore.SIGNAL("itemDoubleClicked(QListWidgetItem*)"), self.addNewListItem )
        
        # attach validators
        QtCore.QObject.connect( self.baseName_lineEdit,
                                QtCore.SIGNAL("textChanged(QString)"),
                                self.validateBaseName )
        
        QtCore.QObject.connect( self.subName_lineEdit,
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
        self.subName_listWidget.clear()
        self.subName_listWidget.addItem( "MAIN" )
        
        # append the users to the users list
        userInits = self._repo.user_initials
        
        self.user_comboBox1.clear()
        self.user_comboBox1.addItems( userInits )
        
        # update the user with the last selected user
        last_user = self._repo.last_user
        
        userIndex = -1
        if last_user != '' and last_user is not None:
            userIndex = self.user_comboBox1.findText(last_user) 
        
        if userIndex == -1:
            userIndex = 0
        
        self.user_comboBox1.setCurrentIndex( userIndex )
        
        # add the assets_tableWidget1 horizontal header labels
        self._horizontalLabels = [ 'Asset FileName', 'File Size', 'Date Updated' ]
        self.assets_tableWidget1.setHorizontalHeaderLabels( self._horizontalLabels )
        
        # set spinbox default value to 10
        self.numberOfEntry_spinBox.setValue(10)
    
    def fillFieldsFromFileInfo(self):
        """fills the ui fields from the data that comes from the fileName and
        path
        """
        
        # no use without the path
        if self.path is None or self.path == '':
            return
        
        # get the project and sequence names
        projectName, sequenceName = \
            self._repo.get_project_and_sequence_name_from_file_path( self.path )
        
        if projectName is None or projectName == '' or sequenceName is None \
            or sequenceName == '':
            return
        
        currentProject = Project( projectName )
        
        if not currentProject.exists:
            return
        
        currentSequence = Sequence( currentProject, sequenceName )
        
        if not currentSequence.exists:
            return
        
        # set the project and sequence
        self.setProjectName( projectName )
        self.setSequenceName( sequenceName )
        
        # no file name no use of the rest
        if self.fileName is None:
            return
        
        # fill the fields with those info
        # create an asset with the file name and get the information from that asset object
        
        assetObj = Asset( currentProject, currentSequence, self.fileName )
        
        if not assetObj.isValidAsset and not assetObj.exists:
            return
        
        # set the asset of the environment
        self._environment._asset = assetObj
        
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
        element = self.assetType_comboBox1
        element.setCurrentIndex( element.findText( assetType ) )
        
        # ----------------------------------------------------------------------
        # shotNumber and baseName
        if assetObj.isShotDependent:
            element = self.shot_comboBox1
            element.setCurrentIndex( element.findText( shotNumber) )
            
            # update self._lastValidShotSelection
            self._lastValidShotSelection = shotNumber
        
        else:
            
            itemIndex = self.findListItemWithText( self.baseName_listWidget, baseName )
            if itemIndex != -1:
                # get the item and set it selected and current item on the list
                item = self.baseName_listWidget.item( itemIndex )
                item.setSelected(True)
                self.baseName_listWidget.setCurrentItem( item )
                
                # update the selection
                self.updateBaseNameLineEdit( baseName )
        # ----------------------------------------------------------------------
        
        
        
        # ----------------------------------------------------------------------
        # sub Name
        if not currentSequence.no_sub_name_field: # remove this block when the support for old version becomes obsolute
            
            itemIndex = self.findListItemWithText( self.subName_listWidget, subName )
            if itemIndex != -1:
                # get the item and set it selected and current item on the list
                item = self.subName_listWidget.item( itemIndex )
                item.setSelected(True)
                self.subName_listWidget.setCurrentItem( item )
                
                self.updateSubNameLineEdit( subName )
        # ----------------------------------------------------------------------
        
        
        # revision
        self.revision_spinBox.setValue( revNumber )
        
        # version : set the version and increase it by one
        self.version_spinBox.setValue( verNumber )
        self.updateVersionToLatest()
        
        # notes
        self.note_lineEdit1.setText( notes )
    
    def update_project_list(self):
        """updates projects list
        """
        
        server_path = self._repo.server_path
        
        projectsList = self._repo.valid_projects
        projectsList.sort()
        
        self.server_comboBox.clear()
        self.project_comboBox.clear()
        self.server_comboBox.addItem( server_path )
        self.project_comboBox.addItems( projectsList )
    
    def updateSequenceList(self, *arg):
        """updates the sequence according to selected project
        """
        
        self._updateProjectObject()
        currentProject = self._project
        
        # create a project and ask the child sequences
        self.sequence_comboBox.clear()
        sequences = currentProject.sequenceNames()
        
        self.sequence_comboBox.addItems( sequences )
        
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
        lastSelectedItem = self.assetType_comboBox1.currentText()
        self.assetType_comboBox1.clear()
        self.assetType_comboBox1.addItems( assetTypeNames )
        # reselect the last selected item
        
        if lastSelectedItem != "":
            self.assetType_comboBox1.setCurrentIndex( self.assetType_comboBox1.findText( lastSelectedItem ) )
    
    def updateShotList(self):
        """updates shot list
        """
        
        self._updateSequenceObject()
        
        # try to keep the selection
#        lastSelectedShot = self.shot_comboBox1.currentText()
        
        # clear and update the list
        self.shot_comboBox1.clear()
        self.shot_comboBox1.addItems( self._sequence.shotList )
        
        index = -1
        
        if self._lastValidShotSelection != "" and \
           self._lastValidShotSelection is not None:
            index = self.assetType_comboBox1.findText( self._lastValidShotSelection )
            
            if index != -1:
                self.shot_comboBox1.setCurrentIndex( index )
            
        else:
            self._lastValidShotSelection = self.assetType_comboBox1.currentText()
    
    def updateBaseNameField(self):
        """updates the baseName fields with current asset baseNames for selected
        type, if the type is not shot dependent
        """
        
        # if the current selected type is not shot dependent
        # get all the assets of that type and get their baseNames

        self._updateSequenceObject()
        currentSequence = self._sequence
        
        currentTypeName = self.getCurrentAssetType()
        
        if currentTypeName is None:
            return
        
        currentType = currentSequence.getAssetTypeWithName( currentTypeName )
        
        if currentType is None or currentType.isShotDependent:
            # do nothing
            return
        
        # remove duplicates
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
    
    def updateBaseNameLineEdit(self, baseName):
        """updates the baseName_lineEdit according to the selected text in the
        baseName_listWidget
        """
        
        self.baseName_lineEdit.setText( baseName )
    
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
            self.subName_listWidget.clear()
            return
        
        currentAssetTypeName = self.getCurrentAssetType()
        
        assetTypeObj = currentSequence.getAssetTypeWithName( currentAssetTypeName )
        
        if assetTypeObj is None:
            # clear the current subName field and return
            self.subName_listWidget.clear()
            return
        
        if assetTypeObj.isShotDependent:
            currentBaseName = currentSequence.convertToShotString( self.getCurrentShotString() )
        else:
            currentBaseName = self.getCurrentBaseName()
        
        self.subName_listWidget.clear()
        
        if currentAssetTypeName is None or currentBaseName is None:
            return
        
        currentAssetType = currentSequence.getAssetTypeWithName( currentAssetTypeName )
        
        if currentAssetType is None:
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
        self.subName_listWidget.addItems( sorted(subNamesList) )
        
        # update subName line edit
        self.updateSubNameLineEdit( 'MAIN' ) #, 'updateSubNameField' )
    
    def updateSubNameLineEdit( self, subName ):#, caller_id=None):
        """updates the subName_lineEdit according to the selected text in the
        subName_listWidget
        """
        #print "updateSubNAmeLineEdit.caller_id -> ", caller_id
        #print "subName -> ", subName
        self.subName_lineEdit.setText( subName )
    
    
    
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
        
        if assetType is None:
            return
        
        # enable the shot if the asset type is shot dependent
        isShotDependent = assetType.isShotDependent
        self.shot_comboBox1.setEnabled( isShotDependent )
        
        self.baseName_listWidget.setEnabled( not isShotDependent )
        self.baseName_lineEdit.setEnabled( not isShotDependent )
    
    def updateVersionListBuffer(self):
        """updates the version list buffer
        """
        
        self._updateProjectObject()
        self._updateSequenceObject()
        
        currentProject = self._project
        currentSequence = self._sequence
        
        typeName = self.getCurrentAssetType()
        
        if typeName == '' or typeName is None:
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
        
        if not assetCount:
            return
        
        for i,assetFileName in enumerate(assetFileNames):
            #assert( isinstance(asset, Asset))
            
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
            # align to left and vertical center
            assetFileName_tableWI.setTextAlignment( 0x0001 | 0x0080  )
            self.assets_tableWidget1.setItem( i, 0, assetFileName_tableWI )
            # ------------------------------------
            
            # ------------------------------------
            # asset fileSize
            assetFileSize_tableWI = QtGui.QTableWidgetItem( fileSize )
            # align to center and vertical center
            assetFileSize_tableWI.setTextAlignment( 0x0002 | 0x0080  )
            self.assets_tableWidget1.setItem( i, 1, assetFileSize_tableWI )
            # ------------------------------------
            
            # ------------------------------------
            # asset dateUpdated
            assetDateUpdated_tableWI = QtGui.QTableWidgetItem( dateUpdated )
            # align to left and vertical center
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
        return unicode( self.project_comboBox.currentText() )
    
    def getCurrentSequenceName(self):
        """returns the current sequence name
        """
        return unicode( self.sequence_comboBox.currentText() )
    
    def getCurrentAssetType(self):
        """returns the current assetType from the UI
        """
        return unicode( self.assetType_comboBox1.currentText() )
    
    def getCurrentShotString(self):
        """returns the current shot string from the UI
        """
        return unicode( self.shot_comboBox1.currentText() )
    
    def getCurrentBaseName(self):
        """returns the current baseName from the UI
        """
        #return unicode( self.baseName_comboBox1.currentText() )
        return unicode( self.baseName_lineEdit.text() )
    
    def getCurrentSubName(self):
        """returns the current subName from the UI
        """
        return unicode( self.subName_lineEdit.text() )
    
    def getCurrentRevNumber(self):
        """returns the current revision number from the UI
        """
        return unicode( self.revision_spinBox.value() )
    
    def getCurrentVerNumber(self):
        """returns the current version number from the UI
        """
        return unicode( self.version_spinBox.value() )
    
    def getCurrentUserInitials(self):
        """returns the current user initials from the UI
        """
        return unicode( self.user_comboBox1.currentText() )
    
    def getCurrentNote(self):
        """returns the current note from the UI
        """
        return unicode( self.note_lineEdit1.text() )
    
    def updateRevisionToLatest(self):
        """ tries to get the latest revision
        """
        
        # get the asset object from fields
        self._createAssetObjectFromSaveFields()
        
        if self._asset is None or not self._asset.isValidAsset:
            self.setRevisionNumberField( 0 )
            return
        
        maxRevAsset, maxRevNumber = self._asset.latestRevision2
        
        if maxRevNumber is None:
            maxRevNumber = 0
            
        # update the field
        self.setRevisionNumberField( maxRevNumber )
    
    def updateVersionToLatest(self):
        """ tries to get the latest version
        """
        
        # get the asset object from fields
        self._createAssetObjectFromSaveFields()
        
        if self._asset is None or not self._asset.isValidAsset:
            self.setVersionNumberField( 1 )
            return
        
        maxVerAsset, maxVerNumber = self._asset.latestVersion2
        
        if maxVerNumber is None:
            maxVerNumber = 0
        
        # update the field
        self.setVersionNumberField( maxVerNumber + 1 )
    
    def setProjectName(self, projectName):
        """sets the project in the combobox
        """
        if projectName is None:
            return
        
        index = self.project_comboBox.findText( projectName )
        
        if index != -1:
            self.project_comboBox.setCurrentIndex( index )
        
        # be sure it is updated
        self.project_comboBox.update()
    
    def setSequenceName(self, sequenceName):
        """sets the sequence in the combobox
        """
        if sequenceName is None:
            return
        
        currentIndex = self.sequence_comboBox.currentIndex()
        
        index = self.sequence_comboBox.findText( sequenceName )
        
        if index != -1:
            self.sequence_comboBox.setCurrentIndex( index )
        
        # be sure it is updated
        self.sequence_comboBox.update()
    
    def _createAssetObjectFromSaveFields(self):#, caller_id=None):
        """returns the asset object from the fields
        """
        
        if self._project is None or self._sequence is None:
            return None
        
        assetObj = Asset( self._project, self._sequence )
        
        # gather information
        typeName = self.getCurrentAssetType()
        
        assetTypeObj = self._sequence.getAssetTypeWithName(typeName)
        
        if assetTypeObj is None:
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
        ## set the environment to the current asset object
        #self._environment.asset = self._asset
    
    def _createAssetObjectFromOpenFields(self):
        """retrieves the file name from the open asset fields
        """
        
        index = self.assets_tableWidget1.currentIndex().row()
        assetFileName = unicode(self.assets_tableWidget1.tableData[index][1])
        self._updateProjectObject()
        self._updateSequenceObject()
        self._asset = Asset(self._project, self._sequence, assetFileName)
        #self._environment.asset = self._asset
    
    def _getAssetObjectFromOpenFields(self):
        """retrieves the file name from the open asset fields
        """
        
        index = self.assets_tableWidget1.currentIndex().row()
        assetFileName = unicode(self.assets_tableWidget1.tableData[index][1])
        self._updateProjectObject()
        self._updateSequenceObject()
        return Asset(self._project, self._sequence, assetFileName)
    
    def getFileNameFromSaveFields(self):
        """returns the file name from the fields
        """
        # get the asset object from fields
        self._createAssetObjectFromSaveFields()
        
        if self._asset is None:
            return None, None
        
        return self._asset.pathVariables, self._asset
    
    def setRevisionNumberField(self, revNumber):
        """sets the revision number field in the interface
        """
        self.revision_spinBox.setValue( revNumber )
    
    def setVersionNumberField(self, verNumber):
        """sets the version number field in the interface
        """
        self.version_spinBox.setValue( verNumber )
    
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
        
        self.subName_listWidget.setEnabled(not currentSequence.no_sub_name_field)
        self.subName_lineEdit.setEnabled(not currentSequence.no_sub_name_field)
    
    def _updateProjectObject(self):
        """updates the project object if it is changed
        it is introduced to take advantage of the cache system
        """
        
        currentProjectName = self.getCurrentProjectName()
        
        if self._project is None or \
           self._project.name != currentProjectName or \
           (currentProjectName != "" or currentProjectName is not None ):
            self._project = Project( currentProjectName )
    
    def _updateSequenceObject(self):
        """updates the sequence object if it is not
        """
        
        currentSequenceName = self.getCurrentSequenceName()
        
        #assert(isinstance(self._sequence,Sequence))
        if self._sequence is None or \
           self._sequence.name != currentSequenceName and \
           (currentSequenceName != "" or currentSequenceName is not None ) or \
           self._sequence.projectName != self._project.name:
            self._updateProjectObject()
            newSeq = Sequence( self._project, currentSequenceName )
            if newSeq._exists:
                self._sequence = newSeq
    
    def validateSubName(self, text):
        """validates the subName field by removing unnecessary characters
        """
        
        # just replace the validated text
        self.subName_lineEdit.setText( self.fieldNameValidator(text) )
    
    def validateBaseName(self, text):
        """validates the baseName field by removing unnecessary characters
        """
        
        # just replace the validated text
        self.baseName_lineEdit.setText( self.fieldNameValidator(text) )
    
    def fieldNameValidator(self, text):
        """a validator that validates input texts
        """
        text = unicode(text)
        
        if not len(text):
            return text
        
        # first remove invalid chars
        text = utils.invalidCharacterRemover(text, utils.validFileNameChars)
        
        # validate the text
        text = utils.stringConditioner(text, capitalize=False)
        
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
                newItemName, ok = QtGui.QInputDialog.getText(
                    self,
                    'Enter new item name',
                    'Enter a new item name please:'
                )
                
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
        
        if self._environment.name is not None and self._environment.name != '':
            self.fileName, self.path = self._environment.get_last_version()
            
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
            answer = QtGui.QMessageBox.question(
                self,
                "Version Error",
                "it is not the latest version\nshould I increase the "
                "version number?",
                QtGui.QMessageBox.Yes,
                QtGui.QMessageBox.No
            )
            
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
            answer = QtGui.QMessageBox.question(
                self,
                "Revision Error",
                "it is not the latest revision\nshould I increase the "
                "revision number?",
                QtGui.QMessageBox.Yes,
                QtGui.QMessageBox.No
            )
            
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
            answer = QtGui.QMessageBox.question(
                self,
                'File Error',
                'overwrite?',
                QtGui.QMessageBox.Yes,
                QtGui.QMessageBox.No
            )
            
            if answer == QtGui.QMessageBox.Yes:
                overwriteStatus = True
        else:
            overwriteStatus = True
        
        return overwriteStatus
    
    def saveAsset(self):
        """prepares the data and sends the asset object to the function
        specially written for the host environment to save the asset file
        """
        
        # get the asset object
        self._createAssetObjectFromSaveFields()
        self._environment.asset = self._asset
        
        
        if self._asset is None:
            return
        
        # check the file conditions
        assetStatus = self.checkOutputAsset( self._asset )
        verStatus = self.checkOutputFileVersion( self._asset )
        revStatus = self.checkOutputFileRevision( self._asset )
        overwriteStatus = self.checkOutputFileOverwrite( self._asset )
        
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
#            print "self._environment: ", self._environment
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
        self._createAssetObjectFromSaveFields()
        
        if self._asset is None:
            return
        
        # check the file conditions
        assetStatus = self.checkOutputAsset( self._asset )
        verStatus = self.checkOutputFileVersion( self._asset )
        revStatus = self.checkOutputFileRevision( self._asset )
        overwriteStatus = self.checkOutputFileOverwrite( self._asset )
        
        envStatus = False
        
        if assetStatus and verStatus and revStatus and overwriteStatus:
            # everything is ok now save in the host application
            envStatus = self._environment.export(self._asset)
            
            # if everything worked fine close the interface
            if envStatus:
                # do not set the last user variable
                
                # inform the user for successful operation
                
                QtGui.QMessageBox.information(
                    self,
                    'Asset Export',
                    'Asset :\n\n'+ self._asset.fileName + \
                        '\n\nis exported successfully',
                    QtGui.QMessageBox.Ok
                )
                
                self.close()
    
    def openAsset(self):
        """prepares the data and sends the asset object to the function
        specially written for the host environment to open the asset file
        """
        
        # get the asset object
        self._createAssetObjectFromOpenFields()
        self._environment.asset = self._asset
        
        # check the file existence
        exists = os.path.exists( self._asset.fullPath )
        
        envStatus = False
        
        # open the asset in the environment
        if exists:
            if self._environment.name == 'MAYA':
                
                # the list that holds the assets those needs to be updated
                toUpdateList = []
                
                try:
                    envStatus, toUpdateList = self._environment.open_()
                except RuntimeError:
                    answer = QtGui.QMessageBox.question(
                        self,
                        'RuntimeError',
                        "There are <b>unsaved changes</b> in the current "
                        "scene<br><br>Do you really want to open the file?",
                        QtGui.QMessageBox.Yes,
                        QtGui.QMessageBox.No
                    )
                    
                    envStatus = False
                    
                    if answer== QtGui.QMessageBox.Yes:
                        envStatus, toUpdateList = self._environment.open_( True )
                    else:
                        return
                
                # check the toUpdateList to update old assets
                if len(toUpdateList):
                    # invoke the assetUpdater for this scene
                    assetUpdaterMainDialog = version_updater.MainDialog( self._environment.name, self )
                    assetUpdaterMainDialog.exec_()
                    
                # load references (Maya Only - for now)
                self._environment.load_references()
                
            elif self._environment.name == 'NUKE':
                envStatus = self._environment.open_()
            
            elif self._environment.name == 'HOUDINI':
                try:
                    envStatus = self._environment.open_()
                except RuntimeError:
                    answer = QtGui.QMessageBox.question(
                        self,
                        'RuntimeError',
                        "There are unsaved changes in the current "
                        "scene\n\nDo you really want to open the file?",
                        QtGui.QMessageBox.Yes,
                        QtGui.QMessageBox.No
                    )
                    
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
            answer = QtGui.QMessageBox.question(
                self,
                'File Error',
                self._asset.fullPath + "\n\nAsset doesn't exist !!!",
                QtGui.QMessageBox.Ok
            )
    
    def importAsset(self):
        """prepares the data and sends the asset object to the function
        specially written for the host environment to import the asset file
        """
        
        # get the asset object
        self._createAssetObjectFromOpenFields()
        
        # check the file existence
        exists = os.path.exists(self._asset.fullPath)
        
        envStatus = False
        
        # open the asset in the environment
        if exists:
            envStatus = self._environment.import_(self._asset)
            
            if envStatus:
                #self.close()
                QtGui.QMessageBox.information(
                    self,
                    'Asset Import',
                    'Asset :\n\n'+ self._asset.fileName + \
                       '\n\nis imported successfully',
                    QtGui.QMessageBox.Ok
                )
        
        else:
            # warn the user for non existing asset files
            answer = QtGui.QMessageBox.question(
                self,
                'File Error',
                self._asset.fullPath + "\n\nAsset doesn't exist !!!",
                QtGui.QMessageBox.Ok
            )
    
    def referenceAsset(self):
        """prepares the data and sends the asset object to the function
        specially written for the host environment to reference the asset file
        
        beware that not all environments supports this action
        """
        
        #print self._environment._asset
        
        # get the asset object
        #self._createAssetObjectFromOpenFields()
        referenced_asset = self._getAssetObjectFromOpenFields()
        
        # check the file existence
        #exists = os.path.exists(self._asset.fullpath)
        exists = os.path.exists(referenced_asset.fullPath)
        
        envStatus = False
        
        # open the asset in the environment
        if exists:
            envStatus = self._environment.reference(referenced_asset)
            
            if envStatus:
                QtGui.QMessageBox.information(
                    self,
                    'Asset Reference',
                    'Asset :\n\n'+ self._asset.fileName + \
                          '\n\nis referenced successfully',
                    QtGui.QMessageBox.Ok
                )
        
        else:
            # warn the user for non existing asset files
            answer = QtGui.QMessageBox.question(
                self,
                'File Error',
                self._asset.fullPath + "\n\nAsset doesn't exist !!!",
                QtGui.QMessageBox.Ok
            )
    
    def printInfo(self, assetObject, actionName):
        """prints info about action
        """
        
        print "-----------------------------------"
        print "AssetManager"
        print assetObject.fileName
        print actionName + " successfully"
    
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
        #assert(isinstance(seq, Sequence))
        shot = seq.getShot( self._asset.shotNumber )
        
        if shot is not None and envStart is not None and envEnd is not None:
            shotStart = shot.startFrame
            shotEnd = shot.endFrame
            
            if envStart != shotStart or envEnd != shotEnd:
                answer = QtGui.QMessageBox.question(
                    self, 'FrameRange Error',
                    
                    "The current frame range is:<br><b>" + \
                    str(envStart) + "-" + str(envEnd) + \
                    "</b><br><br>The frame range of shot <b>" + shot.name + \
                    "</b> is:<br><b>" + str(shotStart) + "-" + str(shotEnd) + \
                    "</b><br><br>should your frame range be adjusted?",
                    
                    QtGui.QMessageBox.Yes,
                    QtGui.QMessageBox.No,
                    QtGui.QMessageBox.Cancel
                )
                
                if answer == QtGui.QMessageBox.Yes:
                    self._environment.setFrameRange( shotStart, shotEnd )
                    return 1
                if answer == QtGui.QMessageBox.Cancel:
                    # do nothing
                    return -1
            else: # set it in case the render frames are wrong
                self._environment.setFrameRange( shotStart, shotEnd )
                return 1
    
    def adjustTimeUnit(self):
        """adjusts the timeUnit to match the settings
        """
        
        # get the timeUnit of the environment
        timeUnit = self._environment.getTimeUnit()
        
        # get the timeUnit of the sequence
        seq = self._asset.sequence
        
        assert(isinstance(seq, Sequence))
        
        seqTimeUnit = seq.timeUnit
        
        if seq.timeUnit != timeUnit:
            answer = QtGui.QMessageBox.question(
                self, 'TimeUnit Error',
                "The current time unit is:<br><b>" + timeUnit + \
                "</b><br><br>The time unit of the sequence is :<br><b>" + \
                seqTimeUnit + "</b><br><br>your time unit will be adjusted!",
                QtGui.QMessageBox.Ok
            )
            
            # adjust the time unit
            self._environment.setTimeUnit( seqTimeUnit )

class MainDialog_New(QtGui.QDialog, version_creator_UI.Ui_Dialog):
    """The main asset version creation dialog for the system.
    
    This is the main interface that the users of the oyProjectManager will use
    to create a 
    
    :param environment: It is an object which supplies **methods** like
      ``open``, ``save``, ``export``,  ``import`` or ``reference``. The most
      basic way to do this is to pass an instance of a class which is derived
      from the :class:`~oyProjectManager.core.models.EnvironmentBase` which has
      all this methods but produces ``NotImplemented`` errors if the child
      class has not implemented these actions.
      
      The main duty of the Environment object is to introduce the host
      application (Maya, Houdini, Nuke, etc.) to oyProjectManager and let it to
      open, save, export, import or reference a file.
    
    :param parent: The parent ``PySide.QtCore.QObject`` of this interface. It
      is mainly useful if this interface is going to be attached to a parent
      UI, like the Maya or Nuke.
    """
    
    # TODO: add only active users to the interface
    # TODO: add auto last user add support
    
    def __init__(self, environment=None, parent=None):
        logger.debug("initializing the interface")
        
#        super(QtGui.QDialog, self).__init__(parent)
        super(MainDialog_New, self).__init__(parent)
        self.setupUi(self)
        
        self.config = config.Config()
        self.repo = Repository()
        
        # setup the database
        if db.session is None:
            db.setup()
        
        self.environment = environment
        
        # create the project attribute in projects_comboBox
        # TODO: create an array of Project instances for each project_name in the comboBox
        #       but just fill them when the Project instance is created
        self.users_comboBox.users = []
        self.projects_comboBox.projects = []
        self.sequences_comboBox.sequences = []
        self.shots_listWidget.shots = []
        self.input_dialog = None
        self.previous_versions_tableWidget.versions = []
        
        # set previous_version_tableWidget.labels
        self.previous_versions_tableWidget.labels = [
#            "Name",
#            "Type",
#            "Take",
            "Version",
            "User",
            "Note",
            "File Size",
            "Path"
        ]
        
        # setup signals
        self._setup_signals()
        
        # setup defaults
        self._set_defaults()
        
        logger.debug("finished initializing the interface")
    
    def _setup_signals(self):
        """sets up the signals
        """
        
        logger.debug("start setting up interface signals")
        
        # close button
        QtCore.QObject.connect(
            self.close_pushButton,
            QtCore.SIGNAL("clicked()"),
            self.close
        )
        
        # projects_comboBox
        QtCore.QObject.connect(
            self.projects_comboBox,
            QtCore.SIGNAL("currentIndexChanged(int)"),
            self.project_changed
        )
        
        # tabWidget
        QtCore.QObject.connect(
            self.tabWidget,
            QtCore.SIGNAL("currentChanged(int)"),
            self.tabWidget_changed
        )
        
        # sequences_comboBox
        QtCore.QObject.connect(
            self.sequences_comboBox,
            QtCore.SIGNAL("currentIndexChanged(int)"),
            self.sequences_comboBox_changed
        )
        
        # assets_listWidget
        QtCore.QObject.connect(
            self.assets_listWidget,
            QtCore.SIGNAL("currentTextChanged(QString)"),
            self.asset_changed
        )
        
        # shots_listWidget
        QtCore.QObject.connect(
            self.shots_listWidget,
            QtCore.SIGNAL("currentTextChanged(QString)"),
            self.shot_changed
        )
        
#        # asset_description_edit_pushButton
#        QtCore.QObject.connect(
#            self.asset_description_edit_pushButton,
#            QtCore.SIGNAL("clicked()"),
#            self.asset_description_edit_pushButton_clicked
#        )
#        
#        # shot_description_edit_pushButton
#        QtCore.QObject.connect(
#            self.shot_description_edit_pushButton,
#            QtCore.SIGNAL("clicked()"),
#            self.shot_description_edit_pushButton_clicked
#        )
        
        # types_comboBox
        QtCore.QObject.connect(
            self.version_types_comboBox,
            QtCore.SIGNAL("currentIndexChanged(int)"),
            self.version_types_comboBox_changed
        )
        
        # take_comboBox
        QtCore.QObject.connect(
            self.takes_comboBox,
            QtCore.SIGNAL("currentIndexChanged(int)"),
            self.takes_comboBox_changed
        )
        
        # add_type_toolButton
        QtCore.QObject.connect(
            self.add_type_toolButton,
            QtCore.SIGNAL("clicked()"),
            self.add_type_toolButton_clicked
        )
        
        # custom context menu for the assets_listWidget
        self.assets_listWidget.setContextMenuPolicy(
            QtCore.Qt.CustomContextMenu
        )
        
        QtCore.QObject.connect(
            self.assets_listWidget,
            QtCore.SIGNAL("customContextMenuRequested(const QPoint&)"),
            self._show_assets_listWidget_context_menu
        )
        
        # create_asset_pushButton
        QtCore.QObject.connect(
            self.create_asset_pushButton,
            QtCore.SIGNAL("clicked()"),
            self.create_asset_pushButton_clicked
        )

        # add_take_toolButton
        QtCore.QObject.connect(
            self.add_take_toolButton,
            QtCore.SIGNAL("clicked()"),
            self.add_take_toolButton_clicked
        )

        # export_as
        QtCore.QObject.connect(
            self.export_as_pushButton,
            QtCore.SIGNAL("clicked()"),
            self.export_as_pushButton_clicked
        )

        # save_as
        QtCore.QObject.connect(
            self.save_as_pushButton,
            QtCore.SIGNAL("clicked()"),
            self.save_as_pushButton_clicked
        )

        # open
        QtCore.QObject.connect(
            self.open_pushButton,
            QtCore.SIGNAL("clicked()"),
            self.open_pushButton_clicked
        )
        
        # add double clicking to previous_versions_tableWidget too
        QtCore.QObject.connect(
            self.previous_versions_tableWidget,
            QtCore.SIGNAL("cellDoubleClicked(int,int)"),
            self.open_pushButton_clicked
        )


        # reference
        QtCore.QObject.connect(
            self.reference_pushButton,
            QtCore.SIGNAL("clicked()"),
            self.reference_pushButton_clicked
        )

        # import
        QtCore.QObject.connect(
            self.import_pushButton,
            QtCore.SIGNAL("clicked()"),
            self.import_pushButton_clicked
        )

        logger.debug("finished setting up interface signals")
    
    def _show_assets_listWidget_context_menu(self, position):
        """the custom context menu for the assets_listWidget
        """
#        print "this has been run"
        # convert the position to global screen position
        global_position = self.assets_listWidget.mapToGlobal(position)
        
        # create the menu
        self.assets_listWidget_menu = QtGui.QMenu()
        self.assets_listWidget_menu.addAction("Rename Asset")
        #self.asset_description_menu.addAction("Delete Asset")
        
        selected_item = self.assets_listWidget_menu.exec_(global_position)
        
        if selected_item:
            # something is chosen
            if selected_item.text() == "Rename Asset":
                
                # show a dialog
                self.input_dialog = QtGui.QInputDialog(self)

                new_asset_name, ok = self.input_dialog.getText(
                    self,
                    "Rename Asset",
                    "New Asset Name"
                )
                
                if ok:
                    # if it is not empty
                    if new_asset_name != "":
                        # get the asset from the list
                        asset = self.get_versionable()
                        asset.name = new_asset_name
                        asset.code = new_asset_name
                        asset.save()
                        
                        # update assets_listWidget
                        self.tabWidget_changed(0)
                
    
    def rename_asset(self, asset, new_name):
        """Renames the asset with the given new name
        
        :param asset: The :class:`~oyProjectManager.core.models.Asset` instance
          to be renamed.
        
        :param new_name: The desired new name for the asset.
        """
        pass
    
    def _set_defaults(self):
        """sets up the defaults for the interface
        """
        
        logger.debug("started setting up interface defaults")
        
        # fill the projects
        projects = db.query(Project).all()
        self.projects_comboBox.addItems(
            map(lambda x: x.name, projects)
        )
        self.projects_comboBox.projects = projects
        
        # fill the users
#        self.users_comboBox.addItems([user.name for user in self.config.users])
        users = db.query(User).all()
        self.users_comboBox.users = users
        self.users_comboBox.addItems(map(lambda x:x.name, users))
        
        # add "Main" by default to the takes_comboBox
        self.takes_comboBox.addItem(conf.default_take_name)
        
        # run the project changed item for the first time
        self.project_changed()
        
        if self.environment is not None:
            logger.debug("restoring the ui with the version from environment")
            
            # get the last version from the environment
            version_from_env = self.environment.get_last_version()
            
            logger.debug("version_from_env: %s" % version_from_env)
            
            self.restore_ui(version_from_env)
        
        logger.debug("finished setting up interface defaults")
    
    def restore_ui(self, version):
        """Restores the UI with the given Version instance
        
        :param version: :class:`~oyProjectManager.core.models.Version` instance
        """
        
        logger.debug("restoring ui with the given version: %s", version)
        
        # quit if version is None
        if version is None:
            return
        
        # set the project
        index = self.projects_comboBox.findText(version.project.name)
        self.projects_comboBox.setCurrentIndex(index)
        
        # set the versionable
        versionable = version.version_of
        
        # set the tab
        if isinstance(versionable, Asset):
            self.tabWidget.setCurrentIndex(0)
            
            # set the asset name
            items = self.assets_listWidget.findItems(
                versionable.name,
                QtCore.Qt.MatchExactly
            )
            self.assets_listWidget.setCurrentItem(items[0])
            
        else:
            self.tabWidget.setCurrentIndex(1)
            
            #the sequence
            index = self.sequences_comboBox.findText(versionable.sequence.name)
            self.sequences_comboBox.setCurrentIndex(index)
            
            # the shot code
            items = self.shots_listWidget.findItems(
                versionable.code,
                QtCore.Qt.MatchExactly
            )
            self.shots_listWidget.setCurrentItem(items[0])
            
        
        # version_type name
        type_name = version.type.name
        index = self.version_types_comboBox.findText(type_name)
        self.version_types_comboBox.setCurrentIndex(index)
        
        # take_name
        take_name = version.take_name
        index = self.takes_comboBox.findText(take_name)
        self.takes_comboBox.setCurrentIndex(index)
        
        
        
        
    
    def project_changed(self):
        """updates the assets list_widget and sequences_comboBox for the 
        """
        
        logger.debug("project_comboBox has changed in the UI")
        
        # call tabWidget_changed with the current index
        curr_tab_index = self.tabWidget.currentIndex()
        
        self.tabWidget_changed(curr_tab_index)
    
    def tabWidget_changed(self, index):
        """called when the tab widget is changed
        """
        
        proj = self.get_current_project()
        
        # if assets is the current tab
        if index == 0:
            logger.debug("tabWidget index changed to asset")
            
            # TODO: don't update if the project is the same with the cached one
            
            # get all the assets of the project
            assets = db.query(Asset).filter(Asset.project==proj).all()
            
            # add their names to the list
            self.assets_listWidget.clear()
            self.assets_listWidget.addItems([asset.name for asset in assets])
            
            # set the list to the first asset
            list_item = self.assets_listWidget.item(0)
            
            if list_item is not None:
            #            list_item.setSelected(True)
                self.assets_listWidget.setCurrentItem(list_item)
    
                # call asset update
                self.asset_changed(list_item.text())
                
#                # enable the asset_description_edit_pushButton
#                self.asset_description_edit_pushButton.setEnabled(True)
            else:
#                # disable the asset_description_edit_pushButton
#                self.asset_description_edit_pushButton.setEnabled(False)
                
                # clear the versions comboBox
                self.version_types_comboBox.clear()
                
                # set the take to default
                self.takes_comboBox.clear()
                self.takes_comboBox.addItem(conf.default_take_name)
        
        elif self.tabWidget.currentIndex() == 1:
            # TODO: don't update if the project is not changed from the last one
            
            logger.debug("tabWidget index changed to shots")
            
            # update the sequence comboBox
            seqs = db.query(Sequence).filter(Sequence.project==proj).all()
            
            self.sequences_comboBox.clear()
            self.sequences_comboBox.addItems([seq.name for seq in seqs])
            
            # attach the sequences to the sequences_comboBox
            self.sequences_comboBox.sequences = seqs
            
            if self.sequences_comboBox.count():
                self.sequences_comboBox.setCurrentIndex(0)
                self.sequences_comboBox_changed(0)
            else:
                # there is no sequence
                # clear the version comboBox
                self.version_types_comboBox.clear()
                
                # set the take to default
                self.takes_comboBox.clear()
                self.takes_comboBox.addItem(conf.default_take_name)
    
    def sequences_comboBox_changed(self, index):
        """called when the sequences_comboBox index has changed
        """
        logger.debug("sequences_comboBox changed")
        
        # get the cached sequence instance
        try:
            seq = self.sequences_comboBox.sequences[index]
        except IndexError:
            logger.debug("there is no sequences cached in sequence_comboBox")
            return
        
        # update the shots_listWidget
        shots = db.query(Shot).filter(Shot.sequence==seq).all()
        
        # add their names to the list
        self.shots_listWidget.clear()
        self.shots_listWidget.addItems([shot.code for shot in shots])
        
        # set the shots cache
        self.shots_listWidget.shots = shots
        
        # set the list to the first shot
        list_item = self.shots_listWidget.item(0)
        
        if list_item is not None:
            self.shots_listWidget.setCurrentItem(list_item)
            
            # call shots update
#            self.asset_changed(list_item.text())
            
#            # enable the asset_description_edit_pushButton
#            self.shot_description_edit_pushButton.setEnabled(True)
#        else:
#            self.shot_description_edit_pushButton.setEnabled(False)
    
    def asset_changed(self, asset_name):
        """updates the asset related fields with the current asset information
        """
        
        proj = self.get_current_project()
        
        asset = \
            db.query(Asset).\
            filter(Asset.project==proj).\
            filter_by(name=asset_name).\
            first()
        
        if asset is None:
            return
        
#        # set the description
#        if asset.description is not None:
#            self.asset_description_textEdit.setText(asset.description)
#        else:
#            self.asset_description_textEdit.setText("")
        
        # update the version data
        # Types
        # get all the types for this asset
        types = map(
            lambda x: x[0],
            db.query(distinct(VersionType.name)).
            join(Version).
            filter(Version.version_of==asset).
            all()
        )
        
        # add the types to the version types list
        self.version_types_comboBox.clear()
        self.version_types_comboBox.addItems(types)
        
        # select the first one
        self.version_types_comboBox.setCurrentIndex(0)
    
    def shot_changed(self, shot_name):
        """updates the shot related fields with the current shot information
        """
        
        proj = self.get_current_project()
        
        # get the shot from the index
        index = self.shots_listWidget.currentIndex().row()
        shot = self.shots_listWidget.shots[index]
        
#        # set the description
#        if shot.description is not None:
#            self.shot_description_textEdit.setText(shot.description)
#        else:
#            self.shot_description_textEdit.setText("")
        
        # update the version data
        # Types
        # get all the types for this asset
        types = map(
            lambda x: x[0],
            db.query(distinct(VersionType.name)).
            join(Version).
            filter(Version.version_of==shot).
            all()
        )
        
        # add the types to the version types list
        self.version_types_comboBox.clear()
        self.version_types_comboBox.addItems(types)

        # select the first one
        self.version_types_comboBox.setCurrentIndex(0)
    
    def version_types_comboBox_changed(self, index):
        """runs when the asset version types comboBox has changed
        """
        
        # get all the takes for this type
        proj = self.get_current_project()
        
        versionable = None
        if self.tabWidget.currentIndex() == 0:
            
            try:
                asset_name = self.assets_listWidget.currentItem().text()
            except AttributeError:
                asset_name = None
            
            versionable = \
                db.query(Asset).\
                filter(Asset.project==proj).\
                filter_by(name=asset_name).\
                first()
            
            if asset_name is not None:
                logger.debug("updating take list for asset: %s" % versionable.name)
            else:
                logger.debug("updating take list for no asset")
        else:
            index = self.shots_listWidget.currentIndex().row()
            versionable = self.shots_listWidget.shots[index]
            
            logger.debug("updating take list for shot: %s" % versionable.code)
        
        # version type name
        version_type_name = self.version_types_comboBox.currentText()
        
        logger.debug("version_type_name: %s" % version_type_name)
        
        # Takes
        # get all the takes of the current asset
        takes = map(
            lambda x: x[0],
            db.query(distinct(Version.take_name)).
            join(VersionType).
            filter(VersionType.name==version_type_name).
            filter(Version.version_of==versionable).
            all()
        )
        
        self.takes_comboBox.clear()
        
        if len(takes) == 0:
            # append the default take
            takes.append(conf.default_take_name)
        
        self.takes_comboBox.addItems(takes)
        self.takes_comboBox.setCurrentIndex(0)
    
    def takes_comboBox_changed(self, index):
        """runs when the takes_comboBox has changed
        """
        
        proj = self.get_current_project()
        
        versionable = None
        if self.tabWidget.currentIndex() == 0:
            
            try:
                asset_name = self.assets_listWidget.currentItem().text()
            except AttributeError:
                # no asset
                # just return
                asset_name = None
            
            versionable = db.query(Asset).\
                filter(Asset.project==proj).\
                filter(Asset.name==asset_name).\
                first()
            
            if versionable is not None:
                logger.debug("updating take list for asset: %s" % versionable.name)
            else:
                logger.debug("updating take list for no asset")
        else:
            index = self.shots_listWidget.currentIndex().row()
            versionable = self.shots_listWidget.shots[index]
            
            logger.debug("updating take list for shot: %s" % versionable.code)
        
        # version type name
        version_type_name = self.version_types_comboBox.currentText()
        
        logger.debug("version_type_name: %s" % version_type_name)
        
        # take name
        take_name = self.takes_comboBox.currentText()
        
        logger.debug("take_name: %s" % take_name)
        
        # query the Versions of this type and take
        versions = db.query(Version).join(VersionType).\
            filter(VersionType.name==version_type_name).\
            filter(Version.version_of==versionable).\
            filter(Version.take_name==take_name).\
            order_by(Version.version_number).all()
        
        #        print versions
        self.previous_versions_tableWidget.clear()
        self.previous_versions_tableWidget.setRowCount(len(versions))
        
        self.previous_versions_tableWidget.setHorizontalHeaderLabels(
            self.previous_versions_tableWidget.labels
        )
        
        # update the previous versions list
        for i, vers in enumerate(versions):
        # TODO: add the Version instance to the tableWidget
        
        #            assert isinstance(vers, Version)
        
        #            # --------------------------------
        #            # base_name
        #            item = QtGui.QTableWidgetItem(vers.base_name)
        #            # align to left and vertical center
        #            item.setTextAlignment(0x0001 | 0x0080)
        #            self.previous_versions_tableWidget.setItem(i, 0, item)
        #            
        #            # ------------------------------------
        #            # type_name
        #            item = QtGui.QTableWidgetItem(vers.type.name)
        #            # align to center and vertical center
        #            item.setTextAlignment(0x0001 | 0x0080)
        #            self.previous_versions_tableWidget.setItem(i, 1, item)
        #            # ------------------------------------
        #            
        #            # ------------------------------------
        #            # take_name
        #            item = QtGui.QTableWidgetItem(vers.take_name)
        #            # align to center and vertical center
        #            item.setTextAlignment(0x0001 | 0x0080)
        #            self.previous_versions_tableWidget.setItem(i, 2, item)            
        #            # ------------------------------------
        
            # ------------------------------------
            # version_number
            item = QtGui.QTableWidgetItem(str(vers.version_number))
            # align to center and vertical center
            item.setTextAlignment(0x0004 | 0x0080)
            self.previous_versions_tableWidget.setItem(i, 0, item)
            # ------------------------------------
        
            # ------------------------------------
            # user.name
            item = QtGui.QTableWidgetItem(vers.created_by.name)
            # align to left and vertical center
            item.setTextAlignment(0x0001 | 0x0080)
            self.previous_versions_tableWidget.setItem(i, 1, item)
            # ------------------------------------
        
            # ------------------------------------
            # note
            item = QtGui.QTableWidgetItem(vers.note)
            # align to left and vertical center
            item.setTextAlignment(0x0001 | 0x0080)
            self.previous_versions_tableWidget.setItem(i, 2, item)
            # ------------------------------------
        
            # ------------------------------------
            # filesize
            item = QtGui.QTableWidgetItem("")
            # align to left and vertical center
            item.setTextAlignment(0x0001 | 0x0080)
            self.previous_versions_tableWidget.setItem(i, 3, item)
            # ------------------------------------
        
            # ------------------------------------
            # full_path
            item = QtGui.QTableWidgetItem(vers.full_path)
            # align to center and vertical center
            item.setTextAlignment(0x0001 | 0x0080)
            self.previous_versions_tableWidget.setItem(i, 4, item)
            # ------------------------------------
        
        # resize the first column
        self.previous_versions_tableWidget.resizeColumnToContents(0)
        self.previous_versions_tableWidget.resizeColumnToContents(1)
        self.previous_versions_tableWidget.resizeColumnToContents(2)
        self.previous_versions_tableWidget.resizeColumnToContents(3)
        self.previous_versions_tableWidget.resizeColumnToContents(4)
#        self.previous_versions_tableWidget.resizeColumnToContents(5)
#        self.previous_versions_tableWidget.resizeColumnToContents(6)
#        self.previous_versions_tableWidget.resizeColumnToContents(7)
        
        # add the versions to the widget
        self.previous_versions_tableWidget.versions = versions
    
    def asset_description_edit_pushButton_clicked(self):
        """checks the asset_description_edit_pushButton
        """

        button = self.asset_description_edit_pushButton
        text_field = self.asset_description_textEdit
        
        # check or uncheck
        if button.text() != u"Done":
            # change the text to "Done"
            button.setText(u"Done")
            
            # make the text field read-write
            text_field.setReadOnly(False)
            
            # to discourage edits
            # disable the assets_listWidget
            self.assets_listWidget.setEnabled(False)
            
            # and the projects_comboBox
            self.projects_comboBox.setEnabled(False)
            
            # and the create_asset_pushButton
            self.create_asset_pushButton.setEnabled(False)
            
            # and the shots_tab
            self.shots_tab.setEnabled(False)
            
            # and the new_version_groupBox
            self.new_version_groupBox.setEnabled(False)
            
            # and the previous_versions_groupBox
            self.previous_versions_groupBox.setEnabled(False)
            
        else:
            asset_name = self.assets_listWidget.currentItem().text()
            
            # change the text to "Edit"
            button.setText("Edit")
            button.setStyleSheet("")
            text_field.setReadOnly(True)
            
            proj = self.get_current_project()
            asset = \
                db.query(Asset).\
                filter(Asset.project==proj).\
                filter_by(name=asset_name).\
                first()
            
            # update the asset description
            logger.debug("asset description of %s changed to %s" % (
                    asset,
                    self.asset_description_textEdit.toPlainText()
                )
            )
            
            # only issue an update if the description has changed
            new_description = self.asset_description_textEdit.toPlainText()
            
            if asset.description != new_description:
                asset.description = new_description
                asset.save()

            # re-enable assets_listWidget
            self.assets_listWidget.setEnabled(True)

            # and the projects_comboBox
            self.projects_comboBox.setEnabled(True)

            # and the create_asset_pushButton
            self.create_asset_pushButton.setEnabled(True)

            # and the shots_tab
            self.shots_tab.setEnabled(True)
            
            # and the new_version_groupBox
            self.new_version_groupBox.setEnabled(True)
            
            # and the previous_versions_groupBox
            self.previous_versions_groupBox.setEnabled(True)
    
    def shot_description_edit_pushButton_clicked(self):
        """checks the shot_description_edit_pushButton
        """
        # TODO: organize the actions, first do what needs to be done and then update the interface
        
        button = self.shot_description_edit_pushButton
        text_field = self.shot_description_textEdit
        list_widget = self.shots_listWidget
        tab = self.assets_tab
        
        # check or uncheck
        if button.text() != u"Done":
            # change the text to "Done"
            button.setText(u"Done")
            
            # make the text field read-write
            text_field.setReadOnly(False)
            
            # to discourage edits
            # disable the assets_listWidget
            list_widget.setEnabled(False)
            
            # and the projects_comboBox
            self.projects_comboBox.setEnabled(False)
            
            # and the sequences_comboBox
            self.sequences_comboBox.setEnabled(False)
            
            # and the create_shot_pushButton
            self.create_shot_pushButton.setEnabled(False)
            
            # and the assets_tab
            tab.setEnabled(False)
            
            # and the new_version_groupBox
            self.new_version_groupBox.setEnabled(False)
            
            # and the previous_versions_groupBox
            self.previous_versions_groupBox.setEnabled(False)
        else:
            # change the text to "Edit"
            button.setText("Edit")
            button.setStyleSheet("")
            text_field.setReadOnly(True)
            
            index = self.shots_listWidget.currentIndex().row()
            shot = self.shots_listWidget.shots[index]
            
            # update the shot description
            logger.debug("shot description of %s changed to '%s'" % (
                    shot,
                    self.shot_description_textEdit.toPlainText()
                )
            )
            
            # only issue an update if the description has changed
            new_description = self.shot_description_textEdit.toPlainText()
            
            if shot.description != new_description:
                shot.description = new_description
                shot.save()
            
            # re-enable shots_listWidget
            list_widget.setEnabled(True)
            
            # and the projects_comboBox
            self.projects_comboBox.setEnabled(True)
            
            # and the create_asset_pushButton
            self.create_shot_pushButton.setEnabled(True)
            
            # and the sequences_comboBox
            self.sequences_comboBox.setEnabled(True)
            
            # and the shots_tab
            tab.setEnabled(True)
            
            # and the new_version_groupBox
            self.new_version_groupBox.setEnabled(True)
            
            # and the previous_versions_groupBox
            self.previous_versions_groupBox.setEnabled(True)
    
    def create_asset_pushButton_clicked(self):
        """
        """
        
        self.input_dialog = QtGui.QInputDialog(self)
        
#        print "self.input_dialog: %s " % self.input_dialog
        
        asset_name, ok = self.input_dialog.getText(
            self,
            "Enter new asset name",
            "Asset name:"
        )
        
        if not ok or asset_name == "":
            logger.debug("either canceled or the given asset_name is empty, "
                         "not creating a new asset")
            return
        
        proj = self.get_current_project()
        
        try:
            new_asset = Asset(proj, asset_name)
            new_asset.save()
        except (TypeError, ValueError, IntegrityError) as error:
            
            
            if isinstance(error, IntegrityError):
                # the transaction needs to be rollback
                db.session.rollback()
                error.message = "Asset.name or Asset.code is not unique"
            
            # pop up an Message Dialog to give the error message
            QtGui.QMessageBox.critical(
                self,
                "Error",
                error.message
            )
            
            return
        
        # update the assets by calling project_changed
        self.project_changed()
    
    def get_versionable(self):
        """returns the versionable from the UI, it is an asset or a shot
        depending on to the current tab
        """
        proj = self.get_current_project()
        
        versionable = None
        if self.tabWidget.currentIndex() == 0:
            asset_name = self.assets_listWidget.currentItem().text()
            versionable = \
                db.query(Asset).\
                filter(Asset.project==proj).\
                filter_by(name=asset_name).\
                first()

            logger.debug("updating take list for asset: %s" % versionable.name)
        
        else:
            index = self.shots_listWidget.currentIndex().row()
            versionable = self.shots_listWidget.shots[index]
            
            logger.debug("updating take list for shot: %s" % versionable.code)
        
        return versionable
    
    def get_version_type(self):
        """returns the VersionType instance by looking at the UI elements. It
        will return the correct VersionType by looking at if it is an Asset or
        a Shot and picking the name of the VersionType from the comboBox
        
        :returns: :class:`~oyProjectManager.core.models.VersionType`
        """
        
        project = self.get_current_project()
        if project is None:
            return None
        
        # get the versionable type
        versionable = self.get_versionable()
        
        type_for = versionable.__class__.__name__
        
        # get the version type name
        version_type_name = self.version_types_comboBox.currentText()
        
        # get the version type instance
        return db.query(VersionType).\
            filter(VersionType.type_for==type_for).\
            filter(VersionType.name==version_type_name).\
            first()
    
    def get_current_project(self):
        """Returns the currently selected project instance in the
        projects_comboBox
        :return: :class:`~oyProjectManager.core.models.Project` instance
        """
        
        index = self.projects_comboBox.currentIndex()
        
        try:
            return self.projects_comboBox.projects[index]
        except IndexError:
            return None
    
    def add_type(self, version_type):
        """adds new types to the version_types_comboBox
        """
        
        if not isinstance(version_type, VersionType):
            raise TypeError("please supply a "
                            "oyProjectManager.core.models.VersionType for the"
                            "type to be added to the version_type_comboBox")
        
        # check if the given type is suitable for the current versionable
        versionable = self.get_versionable()
        
        if versionable.__class__.__name__ != version_type.type_for:
            raise TypeError("The given version_type is not suitable for %s"
                            % self.tabWidget.tabText(
                self.tabWidget.currentIndex()
            ))
        
        index = self.version_types_comboBox.findText(version_type.name)
        
        if index == -1:
            self.version_types_comboBox.addItem(version_type.name)
            self.version_types_comboBox.setCurrentIndex(
                self.version_types_comboBox.count() - 1
            )
    
    def add_type_toolButton_clicked(self):
        """adds a new type for the currently selected Asset or Shot
        """
        proj = self.get_current_project()
        
        # get the versionable
        versionable = self.get_versionable()
        
        # get all the version types which doesn't have any version defined
        
        # get all the current types from the interface
        current_types = []
        for index in range(self.version_types_comboBox.count()):
            current_types.append(self.version_types_comboBox.itemText(index))
        
        # available types for Versionable in this environment
        available_types = map(
            lambda x: x[0],
            db.query(distinct(VersionType.name)).
            join(VersionTypeEnvironments).
            filter(VersionType.type_for==versionable.__class__.__name__).
            filter(VersionTypeEnvironments.environment_name==self.environment.name).
            filter(~ VersionType.name.in_(current_types)).
            all()
        )
        
        # create a QInputDialog with comboBox
        self.input_dialog = QtGui.QInputDialog(self)
        
        type_name, ok = self.input_dialog.getItem(
            self,
            "Choose a VersionType",
            "Available Version Types for %ss in %s" % 
                (versionable.__class__.__name__, self.environment.name),
            available_types,
            0,
            False
        )
        
        # if ok add the type name to the end of the types_comboBox and make
        # it the current selection
        if ok:
            # get the type
            vers_type = db.query(VersionType).filter_by(name=type_name).first()
            
            try:
                self.add_type(vers_type)
            except TypeError:
                # the given type doesn't exists
                # just return without doing anything
                return
    
    def add_take_toolButton_clicked(self):
        """runs when the add_take_toolButton clicked
        """
        
        # open up a QInputDialog and ask for a take name
        # anything is acceptable
        # because the validation will occur in the Version instance
        
        self.input_dialog = QtGui.QInputDialog(self)
        
        take_name, ok = self.input_dialog.getText(
            self,
            "Add Take Name",
            "New Take Name"
        )
        
        if ok:
            # add the given text to the takes_comboBox
            # if it is not empty
            if take_name != "":
                self.takes_comboBox.addItem(take_name)
                # set the take to the new one
                self.takes_comboBox.setCurrentIndex(
                    self.takes_comboBox.count() - 1
                )
    
    def get_new_version(self):
        """returns a :class:`~oyProjectManager.core.models.Version` instance
        from the UI by looking at the input fields
        
        :returns: :class:`~oyProjectManager.core.models.Version` instance
        """
        
        # create a new version
        versionable = self.get_versionable()
        version_type = self.get_version_type()
        take_name = self.takes_comboBox.currentText()
        user = self.get_user()
        
        note = self.note_textEdit.toPlainText()
        
        version = Version(
            versionable, versionable.code, version_type, user,
            take_name=take_name, note=note
        )
        
        return version
    
    def get_previous_version(self):
        """returns the :class:`~oyProjectManager.core.models.Version` instance
        from the UI by looking at the previous_versions_tableWidget
        """
        
        index = self.previous_versions_tableWidget.currentRow()
        version = self.previous_versions_tableWidget.versions[index]
        
        return version
    
    def get_user(self):
        """returns the current User instance from the interface by looking at
        the name of the user from the users comboBox
        
        :return: :class:`~oyProjectManager.core.models.User` instance
        """
        
        index = self.users_comboBox.currentIndex()
        return self.users_comboBox.users[index]
    
    def export_as_pushButton_clicked(self):
        """runs when the export_as_pushButton clicked
        """
        
        logger.debug("exporting the data as a new version")
        
        # get the new version
        new_version = self.get_new_version()
        
        # call the environments export_as method
        if self.environment is not None:
            self.environment.export_as(new_version)
    
    def save_as_pushButton_clicked(self):
        """runs when the save_as_pushButton clicked
        """
        
        logger.debug("saving the data as a new version")
        
        # get the new version
        try:
            new_version = self.get_new_version()
        except (TypeError, ValueError) as error:
            
            # pop up an Message Dialog to give the error message
            QtGui.QMessageBox.critical(
                self,
                "Error",
                error.message
            )
            
            return None
        
        # call the environments save_as method
        if self.environment is not None:
            self.environment.save_as(new_version)
        
        # save the new version to the database
        db.session.add(new_version)
        db.session.commit()
        
        # close the UI
        self.close()
    
    def open_pushButton_clicked(self):
        """runs when the open_pushButton clicked
        """
        
        # get the new version
        old_version = self.get_previous_version()

        logger.debug("opening version %s" % old_version)
        
        # call the environments open_ method
        if self.environment is not None:
            
            # environment can throw RuntimeError for unsaved changes
            
            try:
                self.environment.open_(old_version)
            except RuntimeError as e:
                # pop a dialog and ask if the user really wants to open the
                # file

                answer = QtGui.QMessageBox.question(
                    self,
                    'RuntimeError',
                    "There are <b>unsaved changes</b> in the current "
                    "scene<br><br>Do you really want to open the file?",
                    QtGui.QMessageBox.Yes,
                    QtGui.QMessageBox.No
                )
                
                envStatus = False
                
                if answer== QtGui.QMessageBox.Yes:
                    envStatus, to_update_list = \
                        self.environment.open_(old_version, True)
                else:
                    # no, just return
                    return
                
#                # check the to_update_list to update old versions
#                if len(to_update_list):
#                    # invoke the assetUpdater for this scene
#                    assetUpdaterMainDialog = version_updater.MainDialog(self.environment.name, self )
#                    assetUpdaterMainDialog.exec_()
                    
                self.environment.post_open(old_version)
        
        # close the dialog
        self.close()
    
    def reference_pushButton_clicked(self):
        """runs when the reference_pushButton clicked
        """
        
        # get the new version
        previous_version = self.get_previous_version()
        
        logger.debug("referencing version %s" % previous_version)
        
        # call the environments reference method
        if self.environment is not None:
            self.environment.reference(previous_version)
    
    def import_pushButton_clicked(self):
        """runs when the import_pushButton clicked
        """
        
        # get the previous version
        previous_version = self.get_previous_version()
        
        logger.debug("importing version %s" % previous_version)
        
        # call the environments import_ method
        if self.environment is not None:
            self.environment.import_(previous_version)
    
