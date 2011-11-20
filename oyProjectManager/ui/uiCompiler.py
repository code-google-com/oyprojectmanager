# -*- coding: utf-8 -*-

import os

# fix running other python versions than the system python
os.environ["PATH"] = "/usr/bin:" + os.environ["PATH"] 

#from PyQt4 import uic
import subprocess
import oyProjectManager

global uicFile
global pyFile

uicFilePaths = []
pyFilePaths = []

path = os.path.dirname(oyProjectManager.__file__)
ui_path = os.path.join(path, "ui")

# assetManager3.ui
uicFilePaths.append(os.path.join(ui_path, "version_creator.ui"))
pyFilePaths.append(os.path.join(ui_path, "version_creator_UI.py"))

## assetManager.ui
#uicFilePaths.append(os.path.join(ui_path, "assetManager.ui"))
#pyFilePaths.append(os.path.join(ui_path, "assetManager_UI.py"))
#
## assetManager2.ui
#uicFilePaths.append(os.path.join(ui_path, "assetManager2.ui"))
#pyFilePaths.append(os.path.join(ui_path, "assetManager2_UI.py"))
#
## projectManager
#uicFilePaths.append(os.path.join(ui_path, "projectManager.ui"))
#pyFilePaths.append(os.path.join(ui_path, "projectManager_UI.py"))
#
## assetUpdater
#uicFilePaths.append(os.path.join(ui_path, "assetUpdater.ui"))
#pyFilePaths.append(os.path.join(ui_path, "assetUpdater_UI.py"))
#
## shotEditor
#uicFilePaths.append(os.path.join(ui_path, "shotEditor.ui"))
#pyFilePaths.append(os.path.join(ui_path, "shotEditor_UI.py"))
#
## projectSetter
#uicFilePaths.append(os.path.join(ui_path, "projectSetter.ui"))
#pyFilePaths.append(os.path.join(ui_path, "projectSetter_UI.py"))
#
## assetReplacer
#uicFilePaths.append(os.path.join(ui_path, "assetReplacer.ui"))
#pyFilePaths.append(os.path.join(ui_path, "assetReplacer_UI.py"))
#
## saveFields
#uicFilePaths.append(os.path.join(ui_path, "saveFields.ui"))
#pyFilePaths.append(os.path.join(ui_path, "saveFields_UI.py"))

for i,uicFilePath in enumerate(uicFilePaths):
    pyFilePath = pyFilePaths[i]
#    uicFile = file(uicFilePath)
#    pyFile  = file(pyFilePath,'w')
    
    # call the external pyside-uic tool
    
    print "compiling %s to %s" % (uicFilePath, pyFilePath)
#    uic.compileUi( uicFile, pyFile )
#    uicFile.close()
#    pyFile.close()
    
    subprocess.call(["pyside-uic", "-o", pyFilePath, uicFilePath])

print "finished compiling"
