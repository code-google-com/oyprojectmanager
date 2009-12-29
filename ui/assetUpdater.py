import os, sys
import oyAuxiliaryFunctions as oyAux
from PyQt4 import QtGui, QtCore
import assetUpdater_UI

import oyProjectManager
from oyProjectManager.dataModels import assetModel, projectModel, repositoryModel
from oyProjectManager.ui import singletonQapplication


__version__ = "9.12.26"



#----------------------------------------------------------------------
def UI( environmentName=None, parent=None ):
    """the UI
    """
    global app
    global mainWindow
    app = singletonQapplication.QApplication(sys.argv)
    mainWindow = MainWindow( environmentName, parent )
    mainWindow.show()
    app.setStyle('Plastique')
    app.exec_()
    app.connect(app, QtCore.SIGNAL("lastWindowClosed()"), app, QtCore.SLOT("quit()"))






#######################################################################
class MainWindow(QtGui.QMainWindow, assetUpdater_UI.Ui_MainWindow):
    """the main dialog of the asset updater system
    
    the assetTuple list consist of an asset object and a reference object
    
    for Maya environment the reference object is the PyMel Reference node,
    for other environments reference object type will be as native as it can be
    """
    
    
    
    #----------------------------------------------------------------------
    def __init__(self, environmentName=None, parent=None):
        QtGui.QMainWindow.__init__(self, parent)
        self.setupUi(self)
        
        # change the window title
        self.setWindowTitle( self.windowTitle() + ' v' + __version__ )
        
        # center to the window
        self._centerWindow()
        
        self._horizontalLabels = [ 'Asset Name', 'Current', 'Last', 'Do Update?' ]
        self.assetList_tableWidget.setHorizontalHeaderLabels( self._horizontalLabels )
        
        # ------------------------------------------------------------
        # SIGNALS
        # ------------------------------------------------------------
        
        # cancel button
        QtCore.QObject.connect( self.cancel_pushButton, QtCore.SIGNAL("clicked()"), self.close )
        
        # select all button
        QtCore.QObject.connect( self.selectAll_pushButton, QtCore.SIGNAL("clicked()"), self._selectAllAssets )
        
        # select none button
        QtCore.QObject.connect( self.selectNone_pushButton, QtCore.SIGNAL("clicked()"), self._selectNoAsset )
        
        # update button
        QtCore.QObject.connect( self.update_pushButton, QtCore.SIGNAL("clicked()"), self.updateAssets )
        
        # ------------------------------------------------------------
        
        self._assetTupleList = []
        self._numOfAssets = 0
        
        self._tableItems = []
        
        
        # ------------------------------------------------------------
        # setup the environment
        # ------------------------------------------------------------
        self._environmentName = environmentName
        self._environment = None
        
        self.setEnvironmentName( self._environmentName )
        
        ## ---------------
        ## debug
        ## show the assets in the interface
        #self._testDataFill()
        ## ---------------
        self._doEnvRead()
        self._fillUI()
    
    
    
    #----------------------------------------------------------------------
    def _centerWindow(self):
        """centers the window to the screen
        """
        screen = QtGui.QDesktopWidget().screenGeometry()
        size =  self.geometry()
        self.move((screen.width()-size.width())/2, (screen.height()-size.height())/2)
    
    
    
    #----------------------------------------------------------------------
    def getAssetTupleListFromEnvironment(self):
        """gets the references from environment
        
        returns a tuple consist of an asset and the environments representation
        of the asset
        """
        return self._environment.checkReferenceVersions()
    
    
    #----------------------------------------------------------------------
    def getAssetTupleList(self):
        """returns the asset tuple list
        """
        return self._assetTupleList
    
    
    
    #----------------------------------------------------------------------
    def setAssetTupleList(self, assetTupleList):
        """sets the asset tuple list
        """
        self._assetTupleList = assetTupleList
        self._numOfAssets = len( self._assetTupleList )
    
    assetTupleList = property( getAssetTupleList, setAssetTupleList )
    
    
    
    #----------------------------------------------------------------------
    def getEnvironmentName(self):
        """returns the environment name
        """
        return self._environmentName
    
    
    
    #----------------------------------------------------------------------
    def setEnvironmentName(self, environmentName):
        """sets the environment name
        """
        self._environmentName = environmentName
        
        if self._environmentName == 'MAYA':
            from oyProjectManager.environments import mayaEnv
            self.setEnvironment( mayaEnv.MayaEnvironment() )
        
        elif self._environmentName == 'HOUDINI':
            from oyProjectManager.environments import houdiniEnv
            self.setEnvironment( houdiniEnv.HoudiniEnvironment() )
        
        elif self._environmentName == 'NUKE':
            from oyProjectManager.environments import nukeEnv
            self.setEnvironment(  nukeEnv.NukeEnvironment() )
    
    environmentName = property( getEnvironmentName, setEnvironmentName )
    
    
    
    #----------------------------------------------------------------------
    def getEnvironment(self):
        """returns the environment object
        """
        return self._environment
    
    
    
    #----------------------------------------------------------------------
    def setEnvironment(self, environment):
        """sets the environment
        """
        self._environment = environment
    
    environment = property( getEnvironment, setEnvironment )
    
    
    
    ##----------------------------------------------------------------------
    #def _testDataFill(self):
        #"""creates some test data to test the interface
        #"""
        
        ## create a project a sequence and get some assets
        #assetCount = 10
        
        #repo = repositoryModel.Repository()
        #proj = projectModel.Project( 'ETI_TOPKEK' )
        #seq = projectModel.Sequence( proj, '_CHARACTER_SETUP_' )
        
        #assetFileNames = seq.getAllAssetFileNamesForType('RIG')
        
        ## fill the data
        #self._assetTupleList = []
        #for i in range(assetCount):
            #self._assetTupleList.append( (assetModel.Asset( proj, seq, assetFileNames[i] ), None) )
    
    
    
    #----------------------------------------------------------------------
    def _fillUI(self):
        """fills the UI with the asset data
        """
        
        # set the row count
        self.assetList_tableWidget.setRowCount( self._numOfAssets)
        
        for i,assetTuple in enumerate(self._assetTupleList):
            #assert(isinstance(asset, assetModel.Asset) )
            
            asset = assetTuple[0]
            
            # ------------------------------------
            # the critique name
            assetName_tableWI = QtGui.QTableWidgetItem( asset._getCritiqueName() )
            # align to left
            assetName_tableWI.setTextAlignment( 0x0001 | 0x0080  )
            self.assetList_tableWidget.setItem( i, 0, assetName_tableWI )
            # ------------------------------------
            
            
            # ------------------------------------
            # current version
            currentVersionNumber = str(asset.getVersionNumber() )
            currentVersion_tableWI = QtGui.QTableWidgetItem( currentVersionNumber )
            # align to center
            currentVersion_tableWI.setTextAlignment( 0x0004 | 0x0080  )
            self.assetList_tableWidget.setItem( i, 1, currentVersion_tableWI )
            # ------------------------------------
            
            
            # ------------------------------------
            # last version
            lastVersionNumber = str( asset.getLatestVersion2()[1] )
            lastVersion_tableWI = QtGui.QTableWidgetItem( lastVersionNumber )
            # align to center
            lastVersion_tableWI.setTextAlignment( 0x0004 | 0x0080 )
            self.assetList_tableWidget.setItem( i, 2, lastVersion_tableWI )
            # ------------------------------------
            
            
            # ------------------------------------
            # do update ?
            checkBox_tableWI = QtGui.QTableWidgetItem('')
            #checkBox_tableWI.setCheckState( 16 )
            checkBox_tableWI.setCheckState( 0 )
            self.assetList_tableWidget.setItem( i, 3, checkBox_tableWI )
            # ------------------------------------
            
            self._tableItems.append( [assetName_tableWI, currentVersion_tableWI, lastVersion_tableWI, checkBox_tableWI] )
    
    
    
    #----------------------------------------------------------------------
    def _doEnvRead(self):
        """gets the asset tuple from env
        """
        self._assetTupleList = self.getAssetTupleListFromEnvironment()
        self._numOfAssets = len( self._assetTupleList )
    
    
    
    #----------------------------------------------------------------------
    def _selectAllAssets(self):
        """selects all the assets in the tableWidget
        """
        
        for currentItems in self._tableItems:
            currentItem = currentItems[3]
            currentItem.setCheckState( 2 )
    
    
    #----------------------------------------------------------------------
    def _selectNoAsset(self):
        """deselects all assets in the tableWidget
        """
        
        for currentItems in self._tableItems:
            currentItem = currentItems[3]
            currentItem.setCheckState( 0 )
        
    
    
    
    #----------------------------------------------------------------------
    def updateAssets(self):
        """updates the assets if it is checked in the
        """
        
        # get the marked assets from UI first
        markedAssets = self.getMarkedAssets()
        
        # send them back to environment
        self._environment.updateAssets( markedAssets )
        
        # close the interface
        self.close()
    
    
    
    #----------------------------------------------------------------------
    def getMarkedAssets(self):
        """returns the assets as tuple again, if it is checked in the interface
        """
        
        markedAssetList = []
        
        # find the marked assets
        for i in range(self._numOfAssets):
            checkBox_tableItem = self._tableItems[i][3]
            assert(isinstance(checkBox_tableItem, QtGui.QTableWidgetItem))
            
            if checkBox_tableItem.checkState() == 2:
                # get the ith number of the asset
                markedAssetList.append( self._assetTupleList[i] )
        
        return markedAssetList
        