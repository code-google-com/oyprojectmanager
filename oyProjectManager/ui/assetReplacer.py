# -*- coding: utf-8 -*-
# Copyright (c) 2009-2012, Erkan Ozgur Yilmaz
# 
# This module is part of oyProjectManager and is released under the BSD 2
# License: http://www.opensource.org/licenses/BSD-2-Clause

import os, sys
from PyQt4 import QtGui, QtCore
import assetReplacer_UI

import oyProjectManager
from oyProjectManager import utils
from oyProjectManager.core.models import Asset, Project, Sequence, Repository
from oyProjectManager.environments import environmentFactory
from oyProjectManager.ui import singletonQApplication



#----------------------------------------------------------------------
def UI( environmentName=None ):
    """the UI to call the dialog by itself
    """
    
    global app
    global mainDialog
    app = singletonQApplication.QApplication(sys.argv)
    mainDialog = MainDialog( environmentName )
    mainDialog.show()
    app.exec_()
    app.connect(app, QtCore.SIGNAL("lastWindowClosed()"), app, QtCore.SLOT("quit()"))






########################################################################
class MainDialog(QtGui.QDialog, assetReplacer_UI.Ui_Dialog):
    """the main dialog of the script
    """
    
    
    
    #----------------------------------------------------------------------
    def __init__(self, environmentName=None, parent=None):
        # call the supers __init__
        super(MainDialog, self).__init__(parent)
        self.setupUi(self)
        
        # change the window title
        environmentTitle = ''
        if environmentName != None:
            enviornmentTitle = environmentName
        
        self._environmentFactory = environmentFactory.EnvironmentFactory()
        
        self.setWindowTitle( environmentTitle + ' | ' +
                             self.windowTitle() +  ' | ' +
                             'oyProjectManager v' + oyProjectManager.__version__ )
        
        # center to the window
        self._centerWindow()
        
        # ------------------------------------------------------------
        # SIGNALS
        # ------------------------------------------------------------
        self._horizontalLabels = [ 'Original Asset', 'Update To' ]
        
        self._numOfRefs = 0
        self._refDatas = []
        self._versionListBuffer = []

        
        self._project = None
        self._sequence = None
        self._asset = None
        
        self._assetsToReplaceList = []
        
        # create a repository object
        self._repo = repository.Repository()
        
        # create the environment object
        self._environment = self._environmentFactory.create( None, environmentName )
        
        #---------
        # SIGNALS
        #---------
        # cancel button
        QtCore.QObject.connect( self.cancel_pushButton,
                                QtCore.SIGNAL("clicked()"),
                                self.close )
        
        # project change ---> update sequence
        QtCore.QObject.connect( self.project_comboBox,
                                QtCore.SIGNAL("currentIndexChanged(int)"),
                                self._updateProjectObject )
        
        QtCore.QObject.connect( self.project_comboBox,
                                QtCore.SIGNAL("currentIndexChanged(int)"),
                                self.updateSequenceList )
        
        # sequence change ---> update _no_sub_name_field
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
        
        # type change ---> fill baseName comboBox and update subName
        QtCore.QObject.connect( self.assetType_comboBox1,
                                QtCore.SIGNAL("currentIndexChanged(int)"),
                                self.updateBaseNameField )
        
        # baseName change ---> full update subName
        QtCore.QObject.connect( self.baseName_comboBox,
                                QtCore.SIGNAL("currentIndexChanged(int)"),
                                self.updateSubNameField )
        
        # subName change ---> full update assetFile_comboBox
        QtCore.QObject.connect( self.project_comboBox,
                                QtCore.SIGNAL("currentIndexChanged(int)"),
                                self.fullUpdateAssetFilesComboBox )
        
        QtCore.QObject.connect( self.sequence_comboBox,
                                QtCore.SIGNAL("currentIndexChanged(int)"),
                                self.fullUpdateAssetFilesComboBox )
        
        QtCore.QObject.connect( self.assetType_comboBox1,
                                QtCore.SIGNAL("currentIndexChanged(int)"),
                                self.fullUpdateAssetFilesComboBox )
        
        QtCore.QObject.connect( self.baseName_comboBox,
                                QtCore.SIGNAL("currentIndexChanged(int)"),
                                self.fullUpdateAssetFilesComboBox )
        
        QtCore.QObject.connect( self.subName_comboBox,
                                QtCore.SIGNAL("currentIndexChanged(int)"),
                                self.fullUpdateAssetFilesComboBox )
        
        # replace button ---> do replace
        QtCore.QObject.connect( self.replace_pushButton,
                                QtCore.SIGNAL("clicked()"),
                                self.replaceAssets )
        
        # remove replacement button --> remove replacement
        QtCore.QObject.connect( self.removeReplacement_pushButton,
                                QtCore.SIGNAL("clicked()"),
                                self.removeReplacement )
        
        # assetList ---> double click update all fields
        QtCore.QObject.connect( self.assetList_tableWidget,
                                QtCore.SIGNAL("cellDoubleClicked(int,int)"),
                                self.updateComboBoxesForAsset )
        
        self._fillUI()
        self.update_project_list()
        
        if self._numOfRefs > 0:
            # just act like the first asset has been double clicked
            self.updateComboBoxesForAsset(0,0)
        
        
        ## add a popup menu
        #self._popupMenu = QtGui.QMenu( self )#.assetList_tableWidget )
        #self._popupMenu.addSeparator()
        
        #QtCore.QObject.connect( self.assetList_tableWidget,
                                #QtCore.SIGNAL("itemClicked(QTableWidgetItem*)"),
                                #self._popupMenu.show )
        ##self._popupMenu.show()
    
    
    
    #----------------------------------------------------------------------
    def _centerWindow(self):
        """centers the window to the screen
        """
        
        screen = QtGui.QDesktopWidget().screenGeometry()
        size =  self.geometry()
        self.move((screen.width()-size.width())/2, (screen.height()-size.height())/2)
    
    
    
    ##----------------------------------------------------------------------
    #def _setEnvironment(self, environmentName):
        #"""sets the environment object from the environemnt name
        #"""
        #self._environment = self._environmentFactory.create( self._asset, environmentName )
    
    
    
    #----------------------------------------------------------------------
    def updateReferencedAssetsFromEnvironment(self):
        """gets the referenced assets from the environment
        """
        
        # get all the referenced assets from the environment
        self._refDatas = self._environment.getReferencedAssets()
        self._numOfRefs = len( self._refDatas )
    
    
    
    #----------------------------------------------------------------------
    def _fillUI(self):
        """fills the UI with values from environment
        """
        
        
        self.updateReferencedAssetsFromEnvironment()
        
        self.assetList_tableWidget.clear()
        self.assetList_tableWidget.setRowCount( self._numOfRefs )
        self.assetList_tableWidget.setHorizontalHeaderLabels( self._horizontalLabels )
        
        
        # fill the assetList tableWidget
        for i, refData in enumerate(self._refDatas):
            
            assetObj = refData[0]
            assert(isinstance(assetObj, Asset))
            
            #----------------
            # the referenced asset file
            assetName_tableWI = QtGui.QTableWidgetItem( assetObj.fileName )
            # align to left and vertical center
            assetName_tableWI.setTextAlignment( 0x0001 | 0x0080  )
            self.assetList_tableWidget.setItem( i, 0, assetName_tableWI )
            # ------------------------------------
            
            
            # append the reference object to the assetsToReplaceList
            self._assetsToReplaceList.append( [refData, False, None] )
        
        # resize the columns
        self.assetList_tableWidget.resizeColumnToContents(0)
        self.assetList_tableWidget.resizeColumnToContents(1)
        
        # set sub name to MAIN by default
        self.subName_comboBox.clear()
        self.subName_comboBox.addItem( "MAIN" )
    
    
    
    #----------------------------------------------------------------------
    def _updateProjectObject(self):
        """updates the project object if it is changed
        it is introduced to take advantege of the cache system
        """
        
        currentProjectName = self.getCurrentProjectName()
        
        if self._project == None or self._project.name != currentProjectName or (currentProjectName != "" or currentProjectName != None ):
            self._project = project.Project( currentProjectName )
    
    
    
    #----------------------------------------------------------------------
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
    
    
    
    #----------------------------------------------------------------------
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
    
    
    
    #----------------------------------------------------------------------
    def updateSequenceList(self, *arg):
        """updates the sequence according to selected project
        """
        
        self._updateProjectObject()
        currentProjet = self._project
        
        # create a project and ask the child sequences
        self.sequence_comboBox.clear()
        sequences = currentProjet.sequenceNames()
        
        self.sequence_comboBox.addItems( sequences )
        
        self._updateSequenceObject() # it is not needed but do it for now
    
    
    
    #----------------------------------------------------------------------
    def getCurrentProjectName(self):
        """returns the current project name
        """
        return unicode( self.project_comboBox.currentText() )
    
    
    
    #----------------------------------------------------------------------
    def getCurrentSequenceName(self):
        """returns the current sequence name
        """
        return unicode( self.sequence_comboBox.currentText() )
    
    
    
    #----------------------------------------------------------------------
    def updateForNoSubName(self):
        """this method will be removed in later version, it is written just to support
        old types of assets those have no subName field
        """
        
        # if the current sequence has no support for subName fields disable them
        self._updateSequenceObject()
        currentSequence = self._sequence
        
        self.subName_comboBox.setEnabled(not currentSequence._noSubNameField)
    
    
    
    #----------------------------------------------------------------------
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
        
        if currentType == None:
            # do nothing
            return
        
        if currentType.isShotDependent:
            baseNamesList = [ currentSequence.convertToShotString(shotNumber) for shotNumber in currentSequence.shotList ]
        else:
            # remove duplicates
            baseNamesList = sorted( currentSequence.getAssetBaseNamesForType( currentTypeName ) )
        
        # add them to the baseName combobox
        self.baseName_comboBox.clear()
        
        # add the list
        self.baseName_comboBox.addItems( baseNamesList )
    
    
    
    #----------------------------------------------------------------------
    def updateSubNameField(self):
        """updates the subName field with current asset subNames for selected
        baseName, if the type is not shot dependent
        """
        
        # if the current selected type is not shot dependent
        # get all the assets of that type and get their baseNames
        self._updateSequenceObject()
        currentSequence = self._sequence
        
        # if the current sequence doesn't support subName field just return
        if currentSequence.no_sub_name_field:
            self.subName_comboBox.clear()
            return
        
        currentAssetTypeName = self.getCurrentAssetType()
        
        assetTypeObj = currentSequence.getAssetTypeWithName( currentAssetTypeName )
        
        if assetTypeObj == None:
            # clear the current subName field and return
            self.subName_comboBox.clear()
            return
        
        currentBaseName = self.getCurrentBaseName()
        
        self.subName_comboBox.clear()
        
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
        self.subName_comboBox.addItems( sorted(subNamesList) )
    
    
    
    #----------------------------------------------------------------------
    def getCurrentAssetType(self):
        """returns the current assetType from the UI
        """
        return unicode( self.assetType_comboBox1.currentText() )
    
    
    #----------------------------------------------------------------------
    def getCurrentBaseName(self):
        """returns the current baseName from the UI
        """
        return unicode( self.baseName_comboBox.currentText() )
    
    
    
    #----------------------------------------------------------------------
    def getCurrentSubName(self):
        """returns the current subName from the UI
        """
        return unicode( self.subName_comboBox.currentText() )
    
    
    
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
    
    
    
    #----------------------------------------------------------------------
    def fullUpdateAssetFilesComboBox(self):
        """invokes a version list buffer update and a assets files comboBox update
        """
        self.updateVersionListBuffer()
        self.partialUpdateAssetFilesComboBox()
    
    
    
    #----------------------------------------------------------------------
    def partialUpdateAssetFilesComboBox(self):
        """just updates if the number of maximum displayable entry is changed
        """
        
        _buffer = []
        
        _buffer = self._versionListBuffer
        
        self.fillAssetFilesComboBox( _buffer )
    
    
    
    #----------------------------------------------------------------------
    def fillAssetFilesComboBox(self, assetFileNames):
        """fills the assets table widget with given assets
        """
        
        assetCount = len(assetFileNames)
        
        self.assetFile_comboBox.clear()
        
        data = []
        
        if assetCount == 0 :
            return
        
        self.assetFile_comboBox.addItems( assetFileNames )
    
    
    
    #----------------------------------------------------------------------
    def addAssetToReplaceList(self):
        """adds the asset to the replace list
        """
        
        # first get the selection index from the asset list table
        index = self.assetList_tableWidget.currentIndex().row()
        
        # add the asset from the asset file combo box
        assetFile = self.assetFile_comboBox.currentText()
        
        self._createAssetObjectFromOpenFields()
        
        # set the update to field
        tableItem = self.addItemToIndex( self.assetList_tableWidget, index, 1, assetFile )
        
        # add the data
        self._assetsToReplaceList[index][1] = True
        self._assetsToReplaceList[index][2] = self._asset
    
    
    
    #----------------------------------------------------------------------
    def addItemToIndex(self, tableWidget, rowIndex, columnIndex, itemText):
        """adds new item to given index
        """
        
        item = QtGui.QTableWidgetItem( itemText )
        tableWidget.setItem( rowIndex, columnIndex, item )
        
        return item
    
    
    
    #----------------------------------------------------------------------
    def _createAssetObjectFromOpenFields(self):
        """retriewes the file name from the open asset fields
        """
        assetFileName = unicode(self.assetFile_comboBox.currentText())
        self._asset = Asset( self._project, self._sequence, assetFileName )
        self._environment.asset = self._asset
    
    
    
    #----------------------------------------------------------------------
    def removeReplacement(self):
        """removes the selected replacement
        """
        
        # first get the selection index from the asset list table
        index = self.assetList_tableWidget.currentIndex().row()
        
        # set the update to field
        tableItem = self.addItemToIndex( self.assetList_tableWidget, index, 1, '' )
        
        # add the data
        self._assetsToReplaceList[index][1] = False
        self._assetsToReplaceList[index][2] = None
    
    
    #----------------------------------------------------------------------
    def replaceAssets(self):
        """does the replace action
        """
        
        # iterate over the _assetsToReplaceList
        for repData in self._assetsToReplaceList:
            if repData[1] == True:
                self._environment.replaceAssets( repData[0][1], repData[2].full_path )
        
        # close the interface
        self.close()
    
    
    
    #----------------------------------------------------------------------
    def updateComboBoxesForAsset(self, cellRowId, cellColoumnId):
        """updates the comboboxes according to double clicked cell
        """
        #print cellRowId, cellColoumnId
        if cellColoumnId == 0:
            assetObj = self._assetsToReplaceList[cellRowId][0][0]
            
            assert(isinstance(assetObj, Asset))
            
            projectName = assetObj.sequence.project.name
            sequenceName = assetObj.sequence.name
            baseName = assetObj.baseName
            subName = assetObj.subName
            typeName = assetObj.typeName
            fileName = assetObj.fileName
            
            # update the fields
            # project
            self.project_comboBox.setCurrentIndex( self.project_comboBox.findText( projectName ) )
            
            # sequence
            self.sequence_comboBox.setCurrentIndex( self.sequence_comboBox.findText( sequenceName ) )
            
            # typeName
            self.assetType_comboBox1.setCurrentIndex( self.assetType_comboBox1.findText( typeName ) )
            
            # baseName
            self.baseName_comboBox.setCurrentIndex( self.baseName_comboBox.findText( baseName ) )
            
            # subName
            self.subName_comboBox.setCurrentIndex( self.subName_comboBox.findText( subName ) )
            
            # assetFile
            self.assetFile_comboBox.setCurrentIndex( self.assetFile_comboBox.findText( fileName ) )
        elif cellColoumnId == 1:
            self.addAssetToReplaceList()
        
    
