# -*- coding: utf-8 -*-



import os, sys, re
import oyAuxiliaryFunctions as oyAux
from PyQt4 import QtGui, QtCore
import projectManager_UI

import oyProjectManager
from oyProjectManager.models import project, repository
from oyProjectManager import utils
from oyProjectManager.ui import singletonQApplication






#----------------------------------------------------------------------
def UI():
    """the UI to call the dialog by itself
    """
    global app
    global mainDialog
    #app = QtGui.QApplication( sys.argv )
    app = singletonQApplication.QApplication(sys.argv)
    mainDialog = MainDialog()
    mainDialog.show()
    #app.setStyle('Plastique')
    app.exec_()
    app.connect(app, QtCore.SIGNAL("lastWindowClosed()"), app, QtCore.SLOT("quit()"))






########################################################################
class MainDialog(QtGui.QDialog, projectManager_UI.Ui_Dialog):
    """the main dialog of the system
    """
    
    
    
    #----------------------------------------------------------------------
    def __init__(self, parent=None):
        super(MainDialog,self).__init__(parent)
        self.setupUi(self)
        
        # change the window title
        self.setWindowTitle( self.windowTitle() + ' | ' + 'oyProjectManager v' + oyProjectManager.__version__ )
        
        # center to the window
        self._centerWindow()
        
        # connect SIGNALs
        QtCore.QObject.connect(self.tabWidget, QtCore.SIGNAL("currentChanged(int)"), self.update_project_lists )
        
        QtCore.QObject.connect(self.project_comboBox3, QtCore.SIGNAL("currentIndexChanged(int)"), self.updateSequenceLists )
        QtCore.QObject.connect(self.project_comboBox4, QtCore.SIGNAL("currentIndexChanged(int)"), self.updateSequenceLists )
        QtCore.QObject.connect(self.sequence_comboBox4, QtCore.SIGNAL("currentIndexChanged(int)"), self.updateShotLists )
        
        QtCore.QObject.connect(self.project_lineEdit1, QtCore.SIGNAL("textChanged(QString)"), self.checkProjectName )
        QtCore.QObject.connect(self.sequence_lineEdit2, QtCore.SIGNAL("textChanged(QString)"), self.checkSequenceName )
        QtCore.QObject.connect(self.shotRange_lineEdit2, QtCore.SIGNAL("textChanged(QString)"), self.checkShotRange )
        QtCore.QObject.connect(self.shotRange_lineEdit3, QtCore.SIGNAL("textChanged(QString)"), self.checkShotRange )
        
        QtCore.QObject.connect(self.createProject_pushButton, QtCore.SIGNAL("clicked()"), self.createProject )
        QtCore.QObject.connect(self.createSequence_pushButton, QtCore.SIGNAL("clicked()"), self.createSequence )
        QtCore.QObject.connect(self.addShots_pushButton, QtCore.SIGNAL("clicked()"), self.addShots )
        
        QtCore.QObject.connect(self.addAlternativeShot_pushButton, QtCore.SIGNAL("clicked()"), self.addAlternativeShot )
        
        self.repo = repository.Repository()
        
        self._timeFpsDivider = ' - '
        
        # fill defaults
        self.setDefaults()
        
    
    
    
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
        
        # fill the server comboBox
        self.servers_comboBox.clear()
        self.servers_comboBox.addItem ( self.repo.server_path )
        
        
        # --------------------------------
        # fill fps comboBox
        # --------------------------------
        self.fps_comboBox.clear()
        
        time_units = self.repo.time_units
        fpsList = []
        for timeUnitName in time_units.keys():
            fpsList.append(
                timeUnitName + \
                self._timeFpsDivider + \
                str(time_units[timeUnitName])
            )
        
        fpsList = sorted(
            fpsList,
            None,
            lambda x: x.split(self._timeFpsDivider)[1]
        )
        
        self.fps_comboBox.addItems(fpsList)
        
        # by default select 25 / ugly patch
        self.fps_comboBox.setCurrentIndex(2)
    
    
    
    #----------------------------------------------------------------------
    def checkProjectName(self):
        """checks the project lineEdit1
        """
        
        text = unicode( self.project_lineEdit1.text() )
        #text = oyAux.file_name_conditioner( text )
        text = oyAux.invalidCharacterRemover(text, oyAux.validFileNameChars)
        text = oyAux.stringConditioner( text, False, True, False, True, True, False )
        
        self.project_lineEdit1.setText( text )
    
    
    
    #----------------------------------------------------------------------
    def checkSequenceName(self):
        """checks the sequence lineEdit2
        """
        text = unicode( self.sequence_lineEdit2.text() )
        #text = oyAux.file_name_conditioner( text )
        text = oyAux.invalidCharacterRemover(text, oyAux.validFileNameChars)
        text = oyAux.stringConditioner( text, False, True, False, True, True, False )
        
        self.sequence_lineEdit2.setText( text )
    
    
    
    #----------------------------------------------------------------------
    def checkShotRange(self):
        """checks both shotRange lineEdits
        """
        self.shotRange_lineEdit2.setText(
            utils.matchRange(
                unicode(self.shotRange_lineEdit2.text())
            )
        )
        
        self.shotRange_lineEdit3.setText(
            utils.matchRange(
                unicode(self.shotRange_lineEdit3.text())
            )
        )
    
    
    
    #----------------------------------------------------------------------
    def createProject(self):
        """creates the project
        """
        # get the project name from the project_lineEdit1
        projectName = unicode( self.project_lineEdit1.text() )
        
        # condition it
        projectName = oyAux.file_name_conditioner( projectName )
        
        # create the project
        proj = project.Project( projectName )
        proj.create()
        
        # inform the user if it is created
        QtGui.QMessageBox.information( self, 'Project Created', projectName + '\n\nProject is successfuly created !!!!' )
    
    
    
    #----------------------------------------------------------------------
    def createSequence(self):
        """creates the sequence
        """
        # get the project name from the project_comboBox2
        projectName = unicode( self.project_comboBox2.currentText() )
        
        # get the sequence name
        sequenceName = unicode( self.sequence_lineEdit2.text() )
        
        # condition them
        sequenceName = oyAux.file_name_conditioner( sequenceName )
        
        # get the shot range
        shotRange = unicode(self.shotRange_lineEdit2.text())
        
        # get the timeUnit name
        timeUnit = unicode( self.fps_comboBox.currentText().split( self._timeFpsDivider )[0] )
        
        # create the sequence object
        newSeq = project.Sequence( project.Project( projectName ) , sequenceName )
        newSeq.addShots(shotRange)
        newSeq.create()
        newSeq.timeUnit = timeUnit
        newSeq.saveSettings()
        
        # inform the user if it is created
        QtGui.QMessageBox.information( self, 'Sequence Created', sequenceName + '\n\nSequence is successfuly created' )
    
    
    
    #----------------------------------------------------------------------
    def addShots(self):
        """add shots button action
        """
        
        # create the sequence object
        projectName = unicode( self.project_comboBox3.currentText() )
        sequenceName = unicode( self.sequence_comboBox3.currentText() )
        seq = project.Sequence( project.Project(projectName), sequenceName )
        
        shotRange = unicode(self.shotRange_lineEdit3.text())
        
        seq.addShots(shotRange)
        seq.createShots()
        seq.saveSettings()
        
        # inform the user if it is created
        QtGui.QMessageBox.information( self, 'Shots Added', 'Shots are successfuly added!' )
    
    
    
    #----------------------------------------------------------------------
    def update_project_lists(self):
        """updates the project comboBoxes
        """
        projects = self.repo.projects
        sortedProjects = sorted( projects )
        
        # clear all the items in the current combo boxes
        # and fill them with new data
        
        # try to keep the selections
        p2Text = self.project_comboBox2.currentText()
        p3Text = self.project_comboBox3.currentText()
        p4Text = self.project_comboBox4.currentText()
        
        self.project_comboBox2.clear()
        self.project_comboBox3.clear()
        self.project_comboBox4.clear()
        
        self.project_comboBox2.addItems( sortedProjects )
        self.project_comboBox3.addItems( sortedProjects )
        self.project_comboBox4.addItems( sortedProjects )
        
        p2Index = self.project_comboBox2.findText( p2Text )
        if p2Index != -1:
            self.project_comboBox2.setCurrentIndex( p2Index )
        
        p3Index = self.project_comboBox3.findText( p3Text )
        if p3Index != -1:
            self.project_comboBox3.setCurrentIndex( p3Index )
        
        p4Index = self.project_comboBox4.findText( p4Text )
        if p4Index != -1:
            self.project_comboBox4.setCurrentIndex( p4Index )
        
    
    
    
    #----------------------------------------------------------------------
    def updateSequenceLists(self):
        """updates the sequence comboBoxes
        """
        #try to keep the current selections
        s3Text = self.sequence_comboBox3.currentText()
        s4Text = self.sequence_comboBox4.currentText()
        
        
        # sequence_comboBox3
        projectObj = project.Project( unicode( self.project_comboBox3.currentText() ) )
        sequenceNames = sorted( projectObj.sequenceNames() )
        
        self.sequence_comboBox3.clear()
        self.sequence_comboBox3.addItems( sequenceNames )
        
        # sequence_comboBox4
        projectObj = project.Project( unicode( self.project_comboBox4.currentText() ) )
        sequenceNames = sorted( projectObj.sequenceNames() )
        
        self.sequence_comboBox4.clear()
        self.sequence_comboBox4.addItems( sequenceNames )
        
        # restore selections
        s3Index = self.sequence_comboBox3.findText( s3Text )
        if s3Index != -1:
            self.sequence_comboBox3.setCurrentIndex( s3Index )
        
        s4Index = self.sequence_comboBox4.findText( s4Text )
        if s4Index != -1:
            self.sequence_comboBox4.setCurrentIndex( s4Index )
    
    
    
    #----------------------------------------------------------------------
    def updateShotLists(self):
        """updates the shot lists
        """
        
        # get the projectName
        projectName = unicode( self.project_comboBox4.currentText() )
        
        # get the sequenceName
        sequenceName = unicode( self.sequence_comboBox4.currentText() )
        
        projectObj = project.Project( projectName )
        sequenceObj = project.Sequence( projectObj, sequenceName )
        
        # try to keep the current selection
        s4Text = self.shotNumber_comboBox4.currentText()
        
        # remove the current items and update the list
        self.shotNumber_comboBox4.clear()
        self.shotNumber_comboBox4.addItems( sequenceObj.shotList )
        
        # restore selection
        s4Index = self.shotNumber_comboBox4.findText( s4Text )
        if s4Index != -1:
            self.shotNumber_comboBox4.setCurrentIndex( s4Index )
    
    
    
    #----------------------------------------------------------------------
    def addAlternativeShot(self):
        """adds an alternative to the given shot
        """
        
        # get the projectName
        projectName = unicode( self.project_comboBox4.currentText() )
        
        # get the sequenceName
        sequenceName = unicode( self.sequence_comboBox4.currentText() )
        
        # get the current shot number
        shotNumber = self.shotNumber_comboBox4.currentText()
        
        # create the project and sequence objects
        projectObj = project.Project( projectName )
        sequenceObj = project.Sequence( projectObj, sequenceName )
        
        # invoke sequence objects add alternate shot method with the given shot number
        alternativeShotName = sequenceObj.addAlternativeShot( shotNumber )
        
        #print "projectManager -> adding alternative shot to shot %s" % shotNumber
        
        # create and save
        sequenceObj.createShots()
        sequenceObj.saveSettings()
        
        # update the fields
        self.updateShotLists()
        
        # inform the user if it is created
        QtGui.QMessageBox.information( self, 'Alternative Shots Added', 'Alternative shot added:<br><br>%s' % alternativeShotName)
