from PyQt4 import uic, QtCore, QtGui

version = '10.1.11'

global uicFile
global pyFile

uicFilePaths = []
pyFilePaths = []

#uicFilePaths.append( '/home/ozgur/maya/scripts/oy-maya-scripts/oyTools/oyProjectManager/ui/assetManager.ui' )
#pyFilePaths.append( '/home/ozgur/maya/scripts/oy-maya-scripts/oyTools/oyProjectManager/ui/assetManager_UI.py' )

#uicFilePaths.append( '/home/ozgur/maya/scripts/oy-maya-scripts/oyTools/oyProjectManager/ui/projectManager.ui' )
#pyFilePaths.append( '/home/ozgur/maya/scripts/oy-maya-scripts/oyTools/oyProjectManager/ui/projectManager_UI.py' )

#uicFilePaths.append( '/home/ozgur/maya/scripts/oy-maya-scripts/oyTools/oyProjectManager/ui/assetUpdater.ui' )
#pyFilePaths.append( '/home/ozgur/maya/scripts/oy-maya-scripts/oyTools/oyProjectManager/ui/assetUpdater_UI.py' )

#uicFilePaths.append( '/home/ozgur/maya/scripts/oy-maya-scripts/oyTools/oyProjectManager/ui/shotEditor.ui' )
#pyFilePaths.append( '/home/ozgur/maya/scripts/oy-maya-scripts/oyTools/oyProjectManager/ui/shotEditor_UI.py' )

#uicFilePaths.append( '/home/ozgur/maya/scripts/oy-maya-scripts/oyTools/oyProjectManager/ui/projectSetter.ui' )
#pyFilePaths.append( '/home/ozgur/maya/scripts/oy-maya-scripts/oyTools/oyProjectManager/ui/projectSetter_UI.py' )



for i,uicFilePath in enumerate(uicFilePaths):
    uicFile = file( uicFilePath)
    pyFile  = file( pyFilePaths[i],'w')
    uic.compileUi( uicFile, pyFile )
    uicFile.close()
    pyFile.close()
