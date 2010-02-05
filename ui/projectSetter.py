from PyQt4 import QtGui, QtCore
from oyProjectManager.ui import singletonQapplication, projectSetter_UI
from oyProjectManager.dataModels import projectModel, repositoryModel
from oyProjectManager.environments import environmentFactory
import sys
import pymel as pm



__version__ = '10.2.5'



def setProject(environmentName, insist=False):
    """a wrapper function to make it easy to set projects in all environments
    """
    
    accepted = False
    mainDialog = None
    
    while not accepted:
        accepted, mainDialog = UI(environmentName)
        if not insist:
            break
    
    if accepted:
        # create the environment object and let it set the project environment
        projectName = mainDialog.getCurrentProjectName()
        sequenceName = mainDialog.getCurrentSequenceName()
        
        environment = environmentFactory.EnvironmentFactory.create( None, environmentName )
        environment.setProject( projectName, sequenceName )



def UI(environmentName=None):
    """the UI to call the dialog by itself
    """
    global app
    global mainDialog
    app = singletonQapplication.QApplication(sys.argv)
    mainDialog = MainDialog( environmentName )

    app.setStyle('Plastique')
    app.connect(app, QtCore.SIGNAL("lastWindowClosed()"), app, QtCore.SLOT("quit()"))
    
    return mainDialog.exec_(), mainDialog






########################################################################
class MainDialog(QtGui.QDialog, projectSetter_UI.Ui_Dialog):
    """the main dialog
    """
    
    #----------------------------------------------------------------------
    def __init__(self, environmentName, parent=None ):
        super(MainDialog, self).__init__( parent )
        self.setupUi(self)
        
        self._repo = repositoryModel.Repository()
        
        self._environment = environmentFactory.EnvironmentFactory.create( None, environmentName )
        
        # SIGNALS
        QtCore.QObject.connect( self.project_comboBox, QtCore.SIGNAL("currentIndexChanged(int)"), self.updateSequenceList )
        
        # fill the fields with default values
        self.setDefaults()
    
    
    
    #----------------------------------------------------------------------
    def setDefaults(self):
        """fills the default values
        """
        
        # get the server from database object
        
        servers = self._repo.projectsFullPath
        
        projects = self._repo.projects
        
        # fill the server and projects comboBoxes
        
        self.server_comboBox.clear()
        self.server_comboBox.addItem( servers )
        
        self.project_comboBox.clear()
        self.project_comboBox.addItems( sorted(projects) )
        
        # get the current project
        #currentProjectPath = pm.workspace.name
        # get it from the environment
        #currentProjectPath = self._environment.getPathVariables()
        fileName, filePath = self._environment.getPathVariables()
        
        currentProjectName, currentSequenceName = self._repo.getProjectAndSequenceNameFromFilePath( filePath )
        
        self.project_comboBox.setCurrentIndex( self.project_comboBox.findText(currentProjectName) )
        
        # update the sequence list
        self.updateSequenceList()
        
        # set the sequence
        self.sequence_comboBox.setCurrentIndex( self.sequence_comboBox.findText(currentSequenceName) )
    
    
    
    #----------------------------------------------------------------------
    def updateSequenceList(self):
        """updates the sequence list whenever requested
        """
        currentProjectName = self.getCurrentProjectName()
        
        # create the project object
        currentProject = projectModel.Project( currentProjectName )
        
        seqList = currentProject.sequenceNames()
        
        self.sequence_comboBox.clear()
        self.sequence_comboBox.addItems( sorted(seqList) )
    
    
    
    #----------------------------------------------------------------------
    def getCurrentProjectName(self):
        """returns the current projectName
        """
        
        return unicode(self.project_comboBox.currentText())
    
    
    
    #----------------------------------------------------------------------
    def getCurrentSequenceName(self):
        """returns the current sequenceName
        """
        return unicode(self.sequence_comboBox.currentText())
    