from PyQt4 import uic, QtCore, QtGui

global uicFile
global pyFile

uicFile = None
pyFile = None

uicFile = file('/home/ozgur/maya/scripts/oy-maya-scripts/oyTools/oyProjectManager.ui')
pyFile  = file('/home/ozgur/maya/scripts/oy-maya-scripts/oyTools/oyProjectManagerUI.py','w')

uic.compileUi( uicFile, pyFile )

uicFile.close()
pyFile.close()
