import os, sys, re
import oyAuxiliaryFunctions as oyAux
from PyQt4 import QtGui, QtCore
import projectManager_UI
import oyProjectManager
from oyProjectManager.dataModels import projectModel
from oyProjectManager.tools import rangeTools



__version__ = "9.10.10"


#----------------------------------------------------------------------
def UI():
    """the UI
    """
    global app
    global mainWindow
    app = QtGui.QApplication(sys.argv)
    mainWindow = MainWindow()
    returnValue = mainWindow.show()
    app.setStyle('Plastique')
    app.exec_()
    app.connect(app, QtCore.SIGNAL("lastWindowClosed()"), app, QtCore.SLOT("quit()"))






########################################################################
class MainWindow(QtGui.QMainWindow, projectManager_UI.Ui_MainWindow):
    """the main window of the system
    """
    
    
    
    #----------------------------------------------------------------------
    def __init__(self):
        #super(MainWindow).__init__(self)
        QtGui.QMainWindow.__init__(self)
        self.setupUi(self)
        
        # change the window title
        self.setWindowTitle( self.windowTitle() + ' v' + __version__ + ' | ' + 'oyProjectManager v' + oyProjectManager.__version__ )
        
        # center to the window
        self._centerWindow()
        
        # connect SIGNALs
        QtCore.QObject.connect(self.tabWidget, QtCore.SIGNAL("currentChanged(int)"), self.updateProjectLists )
        
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
        
        self.db = projectModel.Database()
        
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
        self.servers_comboBox.addItem ( self.db.getServerPath() )
    
    
    
    #----------------------------------------------------------------------
    def checkProjectName(self):
        """checks the project lineEdit1
        """
        
        text = unicode( self.project_lineEdit1.text() )
        #text = oyAux.file_name_conditioner( text )
        text = oyAux.stringConditioner( text, False, True, False, True, True, False )
        
        self.project_lineEdit1.setText( text )
    
    
    
    #----------------------------------------------------------------------
    def checkSequenceName(self):
        """checks the sequence lineEdit2
        """
        text = unicode( self.sequence_lineEdit2.text() )
        #text = oyAux.file_name_conditioner( text )
        text = oyAux.stringConditioner( text, False, True, False, True, True, False )
        
        self.sequence_lineEdit2.setText( text )
    
    
    
    #----------------------------------------------------------------------
    def checkShotRange(self):
        """checks both shotRange lineEdits
        """
        self.shotRange_lineEdit2.setText( rangeTools.RangeConverter.matchRange( unicode( self.shotRange_lineEdit2.text() ) ) )
        self.shotRange_lineEdit3.setText( rangeTools.RangeConverter.matchRange( unicode( self.shotRange_lineEdit3.text() ) ) )
    
    
    
    #----------------------------------------------------------------------
    def createProject(self):
        """creates the project
        """
        # get the project name from the project_lineEdit1
        projectName = unicode( self.project_lineEdit1.text() )
        
        # condition it
        projectName = oyAux.file_name_conditioner( projectName )
        
        # create the project
        proj = projectModel.Project( projectName )
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
        shotRange = unicode( self.shotRange_lineEdit2.text() )
        
        # create the sequence object
        newSeq = projectModel.Sequence( projectModel.Project( projectName ) , sequenceName )
        newSeq.addShots( shotRange )
        newSeq.create()
        
        # inform the user if it is created
        QtGui.QMessageBox.information( self, 'Sequence Created', sequenceName + '\n\nSequence is successfuly created' )
    
    
    
    #----------------------------------------------------------------------
    def addShots(self):
        """add shots button action
        """
        
        # create the sequence object
        projectName = unicode( self.project_comboBox3.currentText() )
        sequenceName = unicode( self.sequence_comboBox3.currentText() )
        seq = projectModel.Sequence( projectModel.Project(projectName), sequenceName )
        
        shotRange = unicode( self.shotRange_lineEdit3.text() )
        
        seq.addShots( shotRange )
        seq.createShots()
        
        # inform the user if it is created
        QtGui.QMessageBox.information( self, 'Shots Added', 'Shots are successfuly added!' )
    
    
    
    #----------------------------------------------------------------------
    def updateProjectLists(self):
        """updates the project comboBoxes
        """
        projects = self.db.getProjects()
        sortedProjects = sorted( projects )
        
        # clear all the items in the current combo boxes
        # and fill them with new data
        
        self.project_comboBox2.clear()
        self.project_comboBox3.clear()
        self.project_comboBox4.clear()
        
        self.project_comboBox2.addItems( sortedProjects )
        self.project_comboBox3.addItems( sortedProjects )
        self.project_comboBox4.addItems( sortedProjects )
    
    
    
    #----------------------------------------------------------------------
    def updateSequenceLists(self):
        """updates the sequence comboBoxes
        """
        # sequence_comboBox3
        project = projectModel.Project( unicode( self.project_comboBox3.currentText() ) )
        self.sequence_comboBox3.clear()
        self.sequence_comboBox3.addItems( sorted(project.getSequenceNames()) )
        
        # sequence_comboBox4
        project = projectModel.Project( unicode( self.project_comboBox4.currentText() ) )
        self.sequence_comboBox4.clear()
        self.sequence_comboBox4.addItems( sorted(project.getSequenceNames()) )
    
    
    
    #----------------------------------------------------------------------
    def updateShotLists(self):
        """updates the shot lists
        """
        
        # get the projectName
        projectName = unicode( self.project_comboBox4.currentText() )
        
        # get the sequenceName
        sequenceName = unicode( self.sequence_comboBox4.currentText() )
        
        project = projectModel.Project( projectName )
        sequence = projectModel.Sequence( project, sequenceName )
        
        shotList = sequence.getShotList()
        
        # remove the current items and update the list
        self.shotNumber_comboBox4.clear()
        self.shotNumber_comboBox4.addItems( shotList )
    
    
    