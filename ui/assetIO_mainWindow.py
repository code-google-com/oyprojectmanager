import os, sys
import oyAuxiliaryFunctions as oyAux
from PyQt4 import QtGui, QtCore
import assetIO_mainWindowUI

from oyProjectManager.dataModels import assetModel, projectModel
#from oyProjectManager.environments import maya, nuke, photoshop, houdini
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
class MainWindow(QtGui.QMainWindow, assetIO_mainWindowUI.Ui_MainWindow):
    """the main dialog of the system
    """
    
    
    
    #----------------------------------------------------------------------
    def __init__(self, environment=None, fileName=None, path=None):
        QtGui.QDialog.__init__(self)
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
        
        
        # close button
        QtCore.QObject.connect(self.cancel_button1, QtCore.SIGNAL("clicked()"), self.close )
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
        QtCore.QObject.connect(self.assetType_comboBox1, QtCore.SIGNAL("currentIndexChanged(int)"), self.updateShotDependentFieldsInSave )
        QtCore.QObject.connect(self.assetType_comboBox2, QtCore.SIGNAL("currentIndexChanged(int)"), self.updateShotDependentFieldsInOpen )
        
        # type change ---> fill baseName comboBox
        QtCore.QObject.connect(self.assetType_comboBox1, QtCore.SIGNAL("currentIndexChanged(int)"), self.updateBaseNameFieldInSave )
        QtCore.QObject.connect(self.assetType_comboBox2, QtCore.SIGNAL("currentIndexChanged(int)"), self.updateBaseNameFieldInOpen )
        
        # shotName or baseName change ---> fill subName comboBox
        QtCore.QObject.connect(self.shot_comboBox1, QtCore.SIGNAL("currentIndexChanged(int)"), self.updateSubNameFieldInSave )
        QtCore.QObject.connect(self.shot_comboBox2, QtCore.SIGNAL("currentIndexChanged(int)"), self.updateSubNameFieldInOpen )
        QtCore.QObject.connect(self.baseName_comboBox1, QtCore.SIGNAL("currentIndexChanged(int)"), self.updateSubNameFieldInSave )
        QtCore.QObject.connect(self.baseName_comboBox2, QtCore.SIGNAL("currentIndexChanged(int)"), self.updateSubNameFieldInOpen )
        
        # subName change ---> fille assets_listWidget2 update ( OPEN TAB only )
        QtCore.QObject.connect(self.subName_comboBox2, QtCore.SIGNAL("currentIndexChanged(int)"), self.updateAssetsListWidget )
        QtCore.QObject.connect(self.baseName_comboBox2, QtCore.SIGNAL("currentIndexChanged(int)"), self.updateAssetsListWidget )
        QtCore.QObject.connect(self.shot_comboBox2, QtCore.SIGNAL("currentIndexChanged(int)"), self.updateAssetsListWidget )
        QtCore.QObject.connect(self.assetType_comboBox2, QtCore.SIGNAL("currentIndexChanged(int)"), self.updateAssetsListWidget )
        
        # get latest revision --> revision
        QtCore.QObject.connect(self.revision_pushButton, QtCore.SIGNAL("clicked()"), self.updateRevisionToLatest )
        
        # get latest version --> version
        QtCore.QObject.connect(self.version_pushButton, QtCore.SIGNAL("clicked()"), self.updateVersionToLatest )
        
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
        
        if lastUser != '' and lastUser != None:
            userIndex = self.user_comboBox1.findText(lastUser) 
        else:
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
            self.baseName_comboBox1.setCurrentIndex( self.baseName_comboBox1.findText(baseName) )
        
        if not currentSequence._noSubNameField: # remove this block when the support for old version becomes obsolute
            # sub Name
            self.subName_comboBox1.setCurrentIndex( self.subName_comboBox1.findText(subName) )
        
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
        
        projectsList = self._db.getProjects()
        projectsList.sort()
        
        self.server_comboBox.clear()
        self.project_comboBox.clear()
        self.server_comboBox.addItem( serverPath )
        self.project_comboBox.addItems( projectsList )
    
    
    
    #----------------------------------------------------------------------
    def updateSequenceList(self, *arg):
        """updates the sequence according to selected project
        """
        
        #print "assetIO -> updateSequenceList"
        
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
        
        # SAVE ASSET TAB
        # clear and update the comboBoxes
        # try to keep the same item in the list
        lastSelectedItem = self.assetType_comboBox1.currentText()
        self.assetType_comboBox1.clear()
        self.assetType_comboBox1.addItems( assetTypeNames )
        # reselect the last selected item
        
        if lastSelectedItem != "":
            self.assetType_comboBox1.setCurrentIndex( self.assetType_comboBox1.findText( lastSelectedItem ) )
        
        # OPEN ASSET TAB
        lastSelectedItem = self.assetType_comboBox2.currentText()
        self.assetType_comboBox2.clear()
        self.assetType_comboBox2.addItems( assetTypeNames )
        #reselect the last seelected item
        if lastSelectedItem != "":
            self.assetType_comboBox2.setCurrentIndex( self.assetType_comboBox2.findText( lastSelectedItem ) )
    
    
    
    #----------------------------------------------------------------------
    def updateShotList(self):
        """
        """
        
        self._updateSequenceObject()
        currentSequence = self._sequence
        
        # get shot list
        shotList = currentSequence.getShotList()
        
        # clear and update the list
        self.shot_comboBox1.clear()
        self.shot_comboBox1.addItems( shotList )
        
        self.shot_comboBox2.clear()
        self.shot_comboBox2.addItems( shotList )
    
    
    
    #----------------------------------------------------------------------
    def updateBaseNameFieldInSave(self):
        """updates the baseName fields with current asset baseNames for selected
        type, if the type is not shot dependent
        """
        
        #print "assetIO -> updateBaseNameFieldInSave"
        
        # if the current selected type is not shot dependent
        # get all the assets of that type and get their baseNames

        self._updateSequenceObject()
        currentSequence = self._sequence
        
        currentTypeName = self.getCurrentAssetTypeInSave()
        
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
        comboBox.addItems( baseNamesList )    
    
    
    
    #----------------------------------------------------------------------
    def updateBaseNameFieldInOpen(self):
        """updates the baseName fields with current asset baseNames for selected
        type, if the type is not shot dependent
        """
        
        #print "assetIO -> updateBaseNameFieldInOpen"
        
        # if the current selected type is not shot dependent
        # get all the assets of that type and get their baseNames
        self._updateProjectObject()
        self._updateSequenceObject()
        currentProject = self._project
        currentSequence = self._sequence
        
        currentTypeName = self.getCurrentAssetTypeInOpen()
        
        if currentTypeName == None:
            return
        
        comboBox = self.baseName_comboBox2
        
        currentType = currentSequence.getAssetTypeWithName( currentTypeName )
        
        if currentType == None or currentType.isShotDependent():
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
        
        # add the list
        comboBox.addItems( baseNamesList )
    
    
    
    #----------------------------------------------------------------------
    def updateSubNameFieldInSave(self):
        """updates the subName fields with current asset subNames for selected
        baseName, if the type is not shot dependent
        """
        
        # if the current selected type is not shot dependent
        # get all the assets of that type and get their baseNames
        self._updateSequenceObject()
        currentSequence = self._sequence
        
        # if the current sequence doesn't support subName field just return
        if currentSequence._noSubNameField:
            return
        
        currentAssetTypeName = self.getCurrentAssetTypeInSave()
        
        assetTypeObj = currentSequence.getAssetTypeWithName( currentAssetTypeName )
        
        if assetTypeObj == None:
            return
        
        if assetTypeObj.isShotDependent():
            currentBaseName = currentSequence.convertToShotString( self.getCurrentShotStringInSave() )
        else:
            currentBaseName = self.getCurrentBaseNameInSave()
        
        self._updateSubNameField( currentSequence, currentAssetTypeName, currentBaseName, self.subName_comboBox1 )
    
    
    
    #----------------------------------------------------------------------
    def updateSubNameFieldInOpen(self):
        """updates the subName fields with current asset subNames for selected
        baseName, if the type is not shot dependent
        """
        
        # if the current selected type is not shot dependent
        # get all the assets of that type and get their baseNames
        self._updateSequenceObject()
        currentSequence = self._sequence
        
        # if the current sequence doesn't support subName field just return
        if currentSequence._noSubNameField:
            return
        
        currentAssetTypeName = self.getCurrentAssetTypeInOpen()
        
        assetTypeObj = currentSequence.getAssetTypeWithName( currentAssetTypeName )
        
        if assetTypeObj == None:
            return
        
        if assetTypeObj.isShotDependent():
            currentBaseName = currentSequence.convertToShotString( self.getCurrentShotStringInOpen() )
        else:
            currentBaseName = self.getCurrentBaseNameInOpen()
        
        self._updateSubNameField( currentSequence, currentAssetTypeName, currentBaseName, self.subName_comboBox2 )
    
    
    
    #----------------------------------------------------------------------
    def _updateSubNameField(self, currentSequence, currentTypeName, currentBaseName, comboBox):
        """
        """
        
        #print "assetIO -> _updateSubNameField"
        
        if currentTypeName == None or currentBaseName == None:
            return
        
        currentType = currentSequence.getAssetTypeWithName( currentTypeName )
        
        if currentType == None:
            # do nothing
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
        comboBox.addItems( subNamesList )
    
    
    
    #----------------------------------------------------------------------
    def updateShotDependentFields(self):
        """updates shot dependent fields like the shotList and basName
        """
        
        self._updateSequenceObject()
        currentSequence = self._sequence
        
        # get selected asset type name
        assetTypeName1 = self.getCurrentAssetTypeInSave()
        assetTypeName2 = self.getCurrentAssetTypeInOpen()
        
        assetType1 = currentSequence.getAssetTypeWithName( assetTypeName1 )
        assetType2 = currentSequence.getAssetTypeWithName( assetTypeName2 )
        
        if assetType1 != None:
            # enable the shot if the asset type is shot dependent
            isShotDependent = assetType1.isShotDependent() 
            self.shot_comboBox1.setEnabled( isShotDependent )
            self.baseName_comboBox1.setEnabled( not isShotDependent )
        
        # ----- update OPEN ASSET FIELDS -------
        if assetType2 != None:
            isShotDependent = assetType2.isShotDependent()
            self.shot_comboBox2.setEnabled( isShotDependent )
            self.baseName_comboBox2.setEnabled( not isShotDependent )
    
    
    
    #----------------------------------------------------------------------
    def updateShotDependentFieldsInSave(self):
        """updates shot dependent fields like the shotList and baseName
        """
        
        self._updateSequenceObject()
        currentSequence = self._sequence
        
        # get selected asset type name
        assetTypeName = self.getCurrentAssetTypeInSave()
        
        assetType = currentSequence.getAssetTypeWithName( assetTypeName )
        
        if assetType == None:
            return
        
        # enable the shot if the asset type is shot dependent
        isShotDependent = assetType.isShotDependent() 
        self.shot_comboBox1.setEnabled( isShotDependent )
        self.baseName_comboBox1.setEnabled( not isShotDependent )
    
    
    
    #----------------------------------------------------------------------
    def updateShotDependentFieldsInOpen(self):
        """updates shot dependent fields like the shotList and baseName
        """
        
        self._updateSequenceObject()
        currentSequence = self._sequence
        
        # get selected asset type name
        assetTypeName = self.getCurrentAssetTypeInOpen()
        
        assetType = currentSequence.getAssetTypeWithName( assetTypeName )
        
        if assetType == None:
            return
        
        # enable the shot if the asset type is shot dependent
        isShotDependent = assetType.isShotDependent() 
        self.shot_comboBox2.setEnabled( isShotDependent )
        self.baseName_comboBox2.setEnabled( not isShotDependent )
    
    
    
    #----------------------------------------------------------------------
    def updateAssetsListWidget(self):
        """fills the assets listWidget with assets
        """
        
        #print "assetIO -> updateAssetsListWidget"
        
        self._updateProjectObject()
        self._updateSequenceObject()
        
        currentProject = self._project
        currentSequence = self._sequence
        
        typeName = self.getCurrentAssetTypeInOpen()
        
        if typeName == '' or typeName == None:
            return
        
        # if the type is shot dependent get the shot number
        # if it is not use the baseName
        if currentSequence.getAssetTypeWithName( typeName ).isShotDependent():
            baseName = currentSequence.convertToShotString( self.getCurrentShotStringInOpen() )
        else:
            baseName = self.getCurrentBaseNameInOpen()
        
        
        if not currentSequence.noSubNameField():
            subName = self.getCurrentSubNameInOpen()
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
        self.assets_listWidget2.clear()
        
        if len(allVersionsList) > 0:
            self.assets_listWidget2.addItems( sorted(allVersionsList) )
    
    
    
    #----------------------------------------------------------------------
    def getCurrentProjectName(self):
        """returns the current project name
        """
        return unicode( self.project_comboBox.currentText() )
    
    
    
    def getCurrentSequenceName(self):
        """returns the current sequence name
        """
        return unicode( self.sequence_comboBox.currentText() )
    
    
    
    ##----------------------------------------------------------------------
    #def getCurrentAssetType(self):
        #"""returns the current assetType from the UI
        #"""
        
        #return unicode( self.assetType_comboBox1.currentText() ), unicode( self.assetType_comboBox2.currentText() )
    
    
    
    #----------------------------------------------------------------------
    def getCurrentAssetTypeInSave(self):
        """returns the current assetType from the UI
        """
        return unicode( self.assetType_comboBox1.currentText() )
    
    
    
    #----------------------------------------------------------------------
    def getCurrentAssetTypeInOpen(self):
        """returns the current assetType from the UI
        """
        return unicode( self.assetType_comboBox2.currentText() )
    
    
    
    #----------------------------------------------------------------------
    def getCurrentShotStringInSave(self):
        """returns the current shot string from the UI
        """
        
        return unicode( self.shot_comboBox1.currentText() )
    
    
    
    #----------------------------------------------------------------------
    def getCurrentShotStringInOpen(self):
        """returns the current shot string from the UI
        """
        
        return unicode( self.shot_comboBox2.currentText() )
    
    
    
    #----------------------------------------------------------------------
    def getCurrentBaseNameInSave(self):
        """returns the current baseName from the UI
        """
        
        return unicode( self.baseName_comboBox1.currentText() )
    
    
    
    #----------------------------------------------------------------------
    def getCurrentBaseNameInOpen(self):
        """returns the current baseName from the UI
        """
        
        return unicode( self.baseName_comboBox2.currentText() )
    
    
    
    #----------------------------------------------------------------------
    def getCurrentSubNameInSave(self):
        """returns the current subName from the UI
        """
        
        return unicode( self.subName_comboBox1.currentText() )
    
    
    
    #----------------------------------------------------------------------
    def getCurrentSubNameInOpen(self):
        """returns the current subName from the UI
        """
        
        return unicode( self.subName_comboBox2.currentText() )
    
    
    
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
        
        maxRevAsset, maxRevNumber = asset.getLatestRevision()
        
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
        
        maxVerAsset, maxVerNumber = asset.getLatestVersion()
        
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
        
        assetObj = assetModel.Asset( self._project, self._sequence )
        
        # gather information
        typeName = self.getCurrentAssetTypeInSave()
        
        assetTypeObj = self._sequence.getAssetTypeWithName(typeName)
        
        if assetTypeObj == None:
            return
        
        isShotDependent = assetTypeObj.isShotDependent()
        if isShotDependent:
            baseName = self._sequence.convertToShotString( self.getCurrentShotStringInSave() )
        else:
            baseName = self.getCurrentBaseNameInSave()
        
        subName = self.getCurrentSubNameInSave()
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
        
        assetFileName = self.assets_listWidget2.currentItem().text()
        
        assetObject = assetModel.Asset( self._project, self._sequence, assetFileName )
        
        return assetObject
    
    
    
    #----------------------------------------------------------------------
    def getFileNameFromSaveFields(self):
        """returns the file name from the fields
        """
        # get the asset object from fields
        assetObject = self.getAssetObjectFromSaveFields()
        
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
        self.subName_comboBox2.setEnabled(not currentSequence._noSubNameField)
    
    
    
    #----------------------------------------------------------------------
    def _updateProjectObject(self):
        """updates the project object if it is changed
        it is introduced to take advantege of the cache system
        """
        
        currentProjectName = self.getCurrentProjectName()
        
        #assert(isinstance(self._project,Project))
        
        if self._project == None or (self._project.getName() != currentProjectName and (currentProjectName != "" or currentProjectName != None ) ):
            self._project = projectModel.Project( currentProjectName )
    
    
    
    #----------------------------------------------------------------------
    def _updateSequenceObject(self):
        """updates the sequence object if it is not
        """
        
        currentSequenceName = self.getCurrentSequenceName()
        
        #assert(isinstance(self._sequence,Sequence))
        
        if self._sequence == None or (self._sequence.getName() != currentSequenceName and (currentSequenceName != "" or currentSequenceName != None ) ):
            self._updateProjectObject()
            newSeq = projectModel.Sequence( self._project, currentSequenceName )
            if newSeq._exists:
                self._sequence = newSeq
    
    
    
    #----------------------------------------------------------------------
    # ENVIRONMENT PREPARATION
    #----------------------------------------------------------------------
    def getSettingsFromEnvironment(self):
        """gets the data from environment
        """
        if self.environment == 'MAYA':
            from oyProjectManager import maya
            self.fileName, self.path = maya.getPathVariables()
        
        if self.environment != None:
            # update the interface
            self.fillFieldsFromFileInfo()
    
    
    
    #----------------------------------------------------------------------
    # SAVE & OPEN & IMPORT & REFERENCE ACTIONS FOR ENVIRONMENTS
    #----------------------------------------------------------------------
    
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
        
        # get the asset object
        assetObject = self.getAssetObjectFromSaveFields()
        
        # check the file conditions
        
        verStatus = self.checkOutputFileVersion( assetObject )
        revStatus = self.checkOutputFileRevision( assetObject )
        overwriteStatus = self.checkOutputFileOverwrite( assetObject )
        
        if verStatus and revStatus and overwriteStatus:
            # everything is ok now save in the host application
            if self.environment == 'MAYA':
                from oyProjectManager.environments import maya
                envStatus = maya.save( assetObject )
            
            
            # if everything worked fine close the interface
            if envStatus:
                # set the last user variable
                self._db.setLastUser( assetObject.getUserInitials() )
                
                self.close()
    
    
    
    #----------------------------------------------------------------------
    def exportAsset(self):
        """prepares the data and sends the asset object to the function
        specially written for the host environment to open the asset file
        """
        
        # get the asset object
        assetObject = self.getAssetObjectFromSaveFields()
        
        # check the file conditions
        
        verStatus = self.checkOutputFileVersion( assetObject )
        revStatus = self.checkOutputFileRevision( assetObject )
        overwriteStatus = self.checkOutputFileOverwrite( assetObject )
        
        
        if verStatus and revStatus and overwriteStatus:
            # everything is ok now save in the host application
            if self.environment == 'MAYA':
                from oyProjectManager.environments import maya
                envStatus = maya.export( assetObject )
            
            # if everything worked fine close the interface
            if envStatus:
                # do not set the last user variable
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
        
        # open the asset in the environment
        if exists:
            if self.environment == 'MAYA':
                from oyProjectManager.environments import maya
                try:
                    envStatus = maya.open_( assetObject )
                except RuntimeError:
                    answer = QtGui.QMessageBox.question(self, 'File Error', "unsaved changes\nforce open ?", QtGui.QMessageBox.Yes, QtGui.QMessageBox.No )
                    
                    if answer== QtGui.QMessageBox.Yes:
                        envStatus = maya.open_( assetObject, True )
            
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
        
        # open the asset in the environment
        if exists:
            if self.environment == 'MAYA':
                from oyProjectManager.environments import maya
                envStatus = maya.import_( assetObject )
            
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
        
        # open the asset in the environment
        if exists:
            if self.environment == 'MAYA':
                from oyProjectManager.environments import maya
                envStatus = maya.reference( assetObject )
            
            if envStatus:
                self.close()
        
        else:
            # warn the user for non existing asset files
            answer = QtGui.QMessageBox.question(self, 'File Error', assetObject.getFullPath() + "\n\nAsset doesn't exist !!!", QtGui.QMessageBox.Ok )
    
    