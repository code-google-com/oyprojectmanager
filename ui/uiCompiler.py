from PyQt4 import uic, QtCore, QtGui

global uicFile
global pyFile

uicFile = None
pyFile = None

uicFile = file('/home/ozgur/maya/scripts/oy-maya-scripts/oyTools/oyProjectManager/ui/assetManager.ui')
pyFile  = file('/home/ozgur/maya/scripts/oy-maya-scripts/oyTools/oyProjectManager/ui/assetManager_UI.py','w')
uic.compileUi( uicFile, pyFile )
uicFile.close()
pyFile.close()

#uicFile = file('/home/ozgur/maya/scripts/oy-maya-scripts/oyTools/oyProjectManager/ui/projectManager.ui')
#pyFile  = file('/home/ozgur/maya/scripts/oy-maya-scripts/oyTools/oyProjectManager/ui/projectManager_UI.py','w')
#uic.compileUi( uicFile, pyFile )
#uicFile.close()
#pyFile.close()


uicFile = file('/home/ozgur/maya/scripts/oy-maya-scripts/oyTools/oyProjectManager/ui/assetUpdater.ui')
pyFile  = file('/home/ozgur/maya/scripts/oy-maya-scripts/oyTools/oyProjectManager/ui/assetUpdater_UI.py','w')
uic.compileUi( uicFile, pyFile )
uicFile.close()
pyFile.close()
