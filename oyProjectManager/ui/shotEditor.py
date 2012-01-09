# -*- coding: utf-8 -*-
# Copyright (c) 2009-2012, Erkan Ozgur Yilmaz
# 
# This module is part of oyProjectManager and is released under the BSD 2
# License: http://www.opensource.org/licenses/BSD-2-Clause



import os, sys
from PyQt4 import QtGui, QtCore
import shotEditor_UI

from oyProjectManager import utils
from oyProjectManager.core.models import Project, Sequence, Repository
from oyProjectManager.ui import singletonQApplication
from oyProjectManager.environments import environmentFactory


def UI(environmentName=''):
    """the UI to call the dialog by itself
    """
    global app
    global mainDialog
    app = singletonQApplication.QApplication(sys.argv)
    mainDialog = MainDialog( environmentName )
    mainDialog.show()
    #app.setStyle('Plastique')
    app.exec_()
    app.connect(
        app,
        QtCore.SIGNAL("lastWindowClosed()"),
        app,
        QtCore.SLOT("quit()")
    )


class MainDialog(QtGui.QDialog, shotEditor_UI.Ui_Dialog):
    """the main dialog of a tool to edit shot ranges and descriptions for a
    project
    """
    
    
    
    
    def __init__(self, environmentName=None, parent=None):
        super(MainDialog,self).__init__(parent)
        self.setupUi(self)
        
        self.repo = Repository()
        
        self._envFactory = environmentFactory.EnvironmentFactory()
        self._environment = None
        self._createEnvironment( environmentName )
        
        # center to the window
        self._centerWindow()
        
        
        # create attributes to hold the project and sequence objects in the table
        setattr( self.shotData_tableWidget, 'project', None)
        setattr( self.shotData_tableWidget, 'sequence', None )
        
        # connect SIGNALs
        
        # server change --> update projects
        QtCore.QObject.connect(self.servers_comboBox, QtCore.SIGNAL("currentIndexChanged(int)"), self.updateProjects )
        
        # project change --> update sequences
        QtCore.QObject.connect(self.project_comboBox1, QtCore.SIGNAL("currentIndexChanged(int)"), self.updateSequences )
        
        # sequence change --> update shot table
        QtCore.QObject.connect(self.sequence_comboBox1, QtCore.SIGNAL("currentIndexChanged(int)"), self.updateShotDataTable )
        
        # shotDataTable change --> update self._newDataOnShotDataTable
        QtCore.QObject.connect(self.shotData_tableWidget, QtCore.SIGNAL("cellChanged(int,int)"), self._updateNewDataOnShotDataTable )
        
        # save button --> _saveShotData
        QtCore.QObject.connect( self.save_pushButton, QtCore.SIGNAL("clicked()"), self._saveShotData )
        
        # anyCell changed --> update duration
        QtCore.QObject.connect( self.shotData_tableWidget, QtCore.SIGNAL("cellChanged(int,int)"), self._updateDuration )
        
        # anyCell entered --> validate text
        QtCore.QObject.connect( self.shotData_tableWidget, QtCore.SIGNAL("cellChanged(int,int)"), self.validateText )
        
        # close button
        QtCore.QObject.connect( self.close_pushButton, QtCore.SIGNAL("clicked()"), self.close )
        
        self._newDataOnShotDataTable = bool(False)
        
        # add table cloumn labels
        self._horizontalLabels = [ 'Shot Name', 'Start Frame', 'End Frame', 'Duration', 'Description' ]
        self.shotData_tableWidget.setHorizontalHeaderLabels( self._horizontalLabels )
        
        self._tableItems = []
        self.shotCount = 0
        
        self.setDefaults()
        
        self.setSettingsFromEnvironment()
    
    
    
    
    def _centerWindow(self):
        """centers the window to the screen
        """
        screen = QtGui.QDesktopWidget().screenGeometry()
        size =  self.geometry()
        self.move((screen.width()-size.width())/2, (screen.height()-size.height())/2)
    
    
    
    
    def setDefaults(self):
        """sets the default values
        """
        
        # fill the server comboBox
        self.servers_comboBox.clear()
        self.servers_comboBox.addItem ( self.repo.server_path )
    
    
    
    
    # ENVIRONMENT PREPARATION
    
    
    def _createEnvironment(self, environmentName):
        """creates the environment object
        """
        self._environment = self._envFactory.create( environmentName=environmentName )
    
    
    
    def setSettingsFromEnvironment(self):
        """sets the data from environment
        """
        
        if self._environment != None:
            if self._environment.name != None and self._environment.name != '':
                fileName, path = self._environment.get_last_version()
                
                #print "fileName : ", fileName
                #print "path : ", path
                
                # update the interface
                projName, seqName = self.repo.get_project_and_sequence_name_from_file_path( path )
                
                # select them in the interface
                
                # project
                if projName is not None:
                    self.project_comboBox1.setCurrentIndex( self.project_comboBox1.findText( projName ) )
                
                # sequence
                if seqName is not None:
                    self.sequence_comboBox1.setCurrentIndex( self.sequence_comboBox1.findText( seqName ) )
    
    
    
    
    def updateProjects(self):
        """updates the projects combobox
        """
        
        projects = self.repo.valid_projects
        sortedProjects = sorted( projects )
        
        # clear all the items in the current combo boxes
        # and fill them with new data
        
        # try to keep the selections
        pText = self.project_comboBox1.currentText()
        
        self.project_comboBox1.clear()
        
        self.project_comboBox1.addItems( sortedProjects )
        
        pIndex = self.project_comboBox1.findText( pText )
        if pIndex != -1:
            self.project_comboBox1.setCurrentIndex( pIndex )
    
    
    
    
    def updateSequences(self):
        """updates the sequence combobox
        """
        
        
        #try to keep the current selections
        sText = self.sequence_comboBox1.currentText()
        
        # sequence_comboBox1
        projectObj = project.Project( unicode( self.project_comboBox1.currentText() ) )
        self.sequence_comboBox1.clear()
        self.sequence_comboBox1.addItems( sorted(projectObj.sequenceNames()) )
        
        # restore selections
        sIndex = self.sequence_comboBox1.findText( sText )
        if sIndex != -1:
            self.sequence_comboBox1.setCurrentIndex( sIndex )
    
    
    
    
    def updateShotDataTable(self):
        """updates the shot data table
        
        it warns the user to save or discard the changes in the current state
        if there are any changes 
        """
        
        if self._newDataOnShotDataTable:
            if self.askUserPermission():
                # save the current data before cleaning
                self._saveShotData()
            else:
                # zero the newDataOnShotDataTable attribute
                self._newDataOnShotDataTable = False
        
        # clear the current table
        self.shotData_tableWidget.clear()
        
        projName = str(self.getCurrentProjectName())
        seqName = str(self.getCurrentSequenceName())
        
        proj = project.Project( projName )
        seq = project.Sequence( proj, seqName )
        
        # set the project and sequence variables of the table
        self.shotData_tableWidget.project = proj
        self.shotData_tableWidget.sequence = seq
        
        # get the shot data
        shots = seq.shots
        
        self.shotCount = len(shots)
        
        # set the table row count
        self.shotData_tableWidget.setRowCount( self.shotCount )
        
        # clear previous tableItem cache
        self._tableItems = []
        
        # set the labels
        self.shotData_tableWidget.setHorizontalHeaderLabels( self._horizontalLabels )
        
        for i,shot in enumerate(shots):
            #assert(isinstance(shot, project.Shot) )
            
            name = shot.name
            startFrame = str( shot.startFrame )
            endFrame = str( shot.endFrame )
            duration = str( shot.duration )
            description = unicode( shot.description )
            
            # fill the fields
            
            # ------------------------------------
            # shot name
            shotName_tableWI = QtGui.QTableWidgetItem( name )
            # align to left and verticle center
            shotName_tableWI.setTextAlignment( 0x0004 | 0x0080  )
            self.shotData_tableWidget.setItem( i, 0, shotName_tableWI )
            # ------------------------------------
            
            
            # ------------------------------------
            # start frame
            startFrame_tableWI = QtGui.QTableWidgetItem( startFrame )
            # align to horizontal and vertical center
            startFrame_tableWI.setTextAlignment( 0x0004 | 0x0080  )
            self.shotData_tableWidget.setItem( i, 1, startFrame_tableWI )
            # ------------------------------------
            
            # ------------------------------------
            # end frame
            endFrame_tableWI = QtGui.QTableWidgetItem( endFrame )
            # align to horizontal and vertical center
            endFrame_tableWI.setTextAlignment( 0x0004 | 0x0080  )
            self.shotData_tableWidget.setItem( i, 2, endFrame_tableWI )
            # ------------------------------------
            
            # ------------------------------------
            # duration
            duration_tableWI = QtGui.QTableWidgetItem( duration )
            # align to horizontal and vertical center
            duration_tableWI.setTextAlignment( 0x0004 | 0x0080  )
            # disable for edits
            #duration_tableWI.setFlags( 0x01 )
            self.shotData_tableWidget.setItem( i, 3, duration_tableWI )
            # ------------------------------------
            
            # ------------------------------------
            # description
            description_tableWI = QtGui.QTableWidgetItem( description )
            # align to left and vertical center
            description_tableWI.setTextAlignment( 0x0001 | 0x0080  )
            self.shotData_tableWidget.setItem( i, 4, description_tableWI )
            # ------------------------------------
            
            # save table items
            self._tableItems.append( [shotName_tableWI, startFrame_tableWI, endFrame_tableWI, duration_tableWI, description_tableWI ] )
    
    
    
    
    def _updateNewDataOnShotDataTable(self):
        """updates the newDataOnShotDataTable
        """
        
        if self.isShotDataFilled():
            self._newDataOnShotDataTable = True
    
    
    
    
    def askUserPermission(self):
        """asks the user permission to discard the data
        """
        
        answer = QtGui.QMessageBox.question(self, 'RuntimeError', "Save changes?", QtGui.QMessageBox.Yes, QtGui.QMessageBox.No )
        
        if answer== QtGui.QMessageBox.Yes:
            # start saving of the data
            self._saveShotData()
            self._newDataOnShotDataTable = False
            return True
        
        return False
    
    
    
    
    def getCurrentProjectName(self):
        """returns the current project name
        """
        return self.project_comboBox1.currentText()
    
    
    
    
    def getCurrentSequenceName(self):
        """returns the current sequence name
        """
        return self.sequence_comboBox1.currentText()
    
    
    
    
    def _saveShotData(self):
        """saves the changes to the sequence
        """
        
        # gather the data
        # use the tableItems cache
        
        # get the current project and sequenceName
        # get the proejct and sequence from the table
        proj = self.shotData_tableWidget.project
        seq = self.shotData_tableWidget.sequence
        
        shots = seq.shots
        
        for i,item in enumerate(self._tableItems):
            # the table and the sequence settings should be in the same order
            # so don't try to find the shot name, just update the start and end
            # frames and the description
            
            #startFrameItem = item[1]
            #assert(isinstance(startFrameItem, QtGui.QTableWidgetItem))
            
            shotName = str(item[0].text())
            startFrame = str(item[1].text())
            endFrame = str(item[2].text())
            description = unicode(item[4].text())
            
            if startFrame != '':
                shots[i].startFrame = int(startFrame)
            
            if endFrame != '':
                shots[i].endFrame = int(endFrame)
            
            shots[i].description = description.strip()
        
        # save the sequence settings
        seq.save()
        
        self._newDataOnShotDataTable = False
    
    
    
    
    def _updateDuration(self, rowIndex, columnIndex):
        """updates the duration cell if any of the start or end frame cells
        changed
        """
        
        # first check if the table is filled properly or it is being filled
        # now
        if not self.isShotDataFilled():
            return
        
        if columnIndex == 1 or columnIndex == 2:
            # update the duration on that row
            # get the startFrame and endFrames
            startFrame = int( self._tableItems[ rowIndex ][1].text() )
            endFrame = int( self._tableItems[ rowIndex ][2].text() )
            
            # calculate duration
            duration = endFrame - startFrame + 1
            self._tableItems[ rowIndex ][3].setText( str(duration) )
    
    
    
    
    def validateText(self, rowIndex, columnIndex):
        """validates the text in the given cell
        """
        
        # first check if the table is filled properly or it is being filled
        # now
        if not self.isShotDataFilled():
            return
        
        item = self._tableItems[ rowIndex ][ columnIndex ]
        # get the text
        text = unicode( item.text() )
        
        # remove any invalid character
        text = utils.invalidCharacterRemover( text, utils.validTextChars )
        
        # set the text back
        item.setText( text )
    
    
    
    
    def isShotDataFilled(self):
        """returns true if the data filling process is ended
        """
        
        return len( self._tableItems ) == self.shotCount
