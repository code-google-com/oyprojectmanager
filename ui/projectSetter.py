from PyQt4 import QtGui, QtCore
from oyProjectManager.ui import singletonQApplication, projectSetter_UI
from oyProjectManager.models import project, repository
from oyProjectManager.models.environments import environmentFactory
import sys



__version__ = '10.6.17'



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
        
        envFactory = environmentFactory.EnvironmentFactory()
        #environment = environmentFactory.EnvironmentFactory.create( None, environmentName )
        environment = envFactory.create( None, environmentName )
        environment.setProject( projectName, sequenceName )



def UI(environmentName=None):
    """the UI to call the dialog by itself
    """
    global app
    global mainDialog
    app = singletonQApplication.QApplication(sys.argv)
    mainDialog = MainDialog( environmentName )

    #app.setStyle('Plastique')
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
        
        self._repo = repository.Repository()
        
        self._envFactory = environmentFactory.EnvironmentFactory()
        
        self._environment = self._envFactory.create( None, environmentName )
        
        # SIGNALS
        QtCore.QObject.connect( self.project_comboBox, QtCore.SIGNAL("currentIndexChanged(int)"), self.updateSequenceList )
        
        # fill the fields with default values
        self.setDefaults()
    
    
    
    #----------------------------------------------------------------------
    def setDefaults(self):
        """fills the default values
        """
        
        # update servers and projects
        self.updateServerList()
        self.updateProjectList()
        
        # get the current project
        # get it from the environment
        fileName, filePath = self._environment.getPathVariables()
        
        currentProjectName, currentSequenceName = self._repo.getProjectAndSequenceNameFromFilePath( filePath )
        
        if currentProjectName is not None:
            self.project_comboBox.setCurrentIndex( self.project_comboBox.findText(currentProjectName) )
        
        # update the sequence list
        self.updateSequenceList()
        
        # set the sequence
        if currentSequenceName is not None:
            self.sequence_comboBox.setCurrentIndex( self.sequence_comboBox.findText(currentSequenceName) )
    
    
    
    #----------------------------------------------------------------------
    def updateServerList(self):
        """updates the server list
        """
        # get the server from database object
        servers = self._repo.projectsFullPath
        
        # fill the server comboBoxes
        self.server_comboBox.clear()
        self.server_comboBox.addItem( servers )
    
    
    
    #----------------------------------------------------------------------
    def updateProjectList(self):
        """updates the project list
        """
        
        # get the valid projects
        projects = self._repo.validProjects
        
        self.project_comboBox.clear()
        self.project_comboBox.addItems( sorted(projects) )
    
    
    
    #----------------------------------------------------------------------
    def updateSequenceList(self):
        """updates the sequence list whenever requested
        """
        currentProjectName = self.getCurrentProjectName()
        
        # create the project object
        currentProject = project.Project( currentProjectName )
        
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
    