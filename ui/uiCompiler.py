from PyQt4 import uic, QtCore, QtGui

global uicFile
global pyFile

uicFile = None
pyFile = None

uicFile = file('/home/ozgur/maya/scripts/oy-maya-scripts/oyTools/oyProjectManager/ui/assetIO_mainWindow.ui')
pyFile  = file('/home/ozgur/maya/scripts/oy-maya-scripts/oyTools/oyProjectManager/ui/assetIO_mainWindowUI.py','w')
uic.compileUi( uicFile, pyFile )
uicFile.close()
pyFile.close()

uicFile = file('/home/ozgur/maya/scripts/oy-maya-scripts/oyTools/oyProjectManager/ui/projectManagement_mainWindow.ui')
pyFile  = file('/home/ozgur/maya/scripts/oy-maya-scripts/oyTools/oyProjectManager/ui/projectManagement_mainWindowUI.py','w')
uic.compileUi( uicFile, pyFile )
uicFile.close()
pyFile.close()


