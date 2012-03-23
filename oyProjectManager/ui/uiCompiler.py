# -*- coding: utf-8 -*-
# Copyright (c) 2009-2012, Erkan Ozgur Yilmaz
# 
# This module is part of oyProjectManager and is released under the BSD 2
# License: http://www.opensource.org/licenses/BSD-2-Clause

import os

# fix running other python versions than the system python
os.environ["PATH"] = "/usr/bin:/usr/local/bin/:/usr/local/lib/python2.6/site-packages" + os.environ["PATH"] 

from PyQt4 import uic
import subprocess
import oyProjectManager

global uicFile
global pyFile

uicFilePaths = []
pyFilePaths_PyQt4 = []
pyFilePaths_PySide = []

path = os.path.dirname(oyProjectManager.__file__)
ui_path = os.path.join(path, "ui")

# version_creator
uicFilePaths.append(os.path.join(ui_path, "version_creator.ui"))
pyFilePaths_PyQt4.append(os.path.join(ui_path, "version_creator_UI_pyqt4.py"))
pyFilePaths_PySide.append(os.path.join(ui_path, "version_creator_UI_pyside.py"))

## project_manager
#uicFilePaths.append(os.path.join(ui_path, "project_manager.ui"))
#pyFilePaths_PyQt4.append(os.path.join(ui_path, "project_manager_UI_pyqt4.py"))
#pyFilePaths_PySide.append(os.path.join(ui_path, "project_manager_UI_pyside.py"))

# project_properties
#uicFilePaths.append(os.path.join(ui_path, "project_properties.ui"))
#pyFilePaths_PyQt4.append(os.path.join(ui_path, "project_properties_UI_pyqt4.py"))
#pyFilePaths_PySide.append(os.path.join(ui_path, "project_properties_UI_pyside.py"))

# assetUpdater
#uicFilePaths.append(os.path.join(ui_path, "version_updater.ui"))
#pyFilePaths_PyQt4.append(os.path.join(ui_path, "version_updater_UI_pyqt4.py"))
#pyFilePaths_PySide.append(os.path.join(ui_path, "version_updater_UI_pyside.py"))

## shotEditor
#uicFilePaths.append(os.path.join(ui_path, "shotEditor.ui"))
#pyFilePaths.append(os.path.join(ui_path, "shotEditor_UI_pyqt4.py"))
#pyFilePaths.append(os.path.join(ui_path, "shotEditor_UI_pyside.py"))
#
## projectSetter
#uicFilePaths.append(os.path.join(ui_path, "projectSetter.ui"))
#pyFilePaths.append(os.path.join(ui_path, "projectSetter_UI_pyqt4.py"))
#pyFilePaths.append(os.path.join(ui_path, "projectSetter_UI_pyside.py"))
#
## assetReplacer
#uicFilePaths.append(os.path.join(ui_path, "assetReplacer.ui"))
#pyFilePaths.append(os.path.join(ui_path, "assetReplacer_UI_pyqt4.py"))
#pyFilePaths.append(os.path.join(ui_path, "assetReplacer_UI_pyside.py"))


for i,uicFilePath in enumerate(uicFilePaths):
    
    pyFilePath_PyQt4 = pyFilePaths_PyQt4[i]
    pyFilePath_PySide = pyFilePaths_PySide[i]
    
    # with PySide
    # call the external pyside-uic tool
    print "compiling %s to %s for PySide" % (uicFilePath, pyFilePath_PySide)
    subprocess.call(["pyside-uic", "-o", pyFilePath_PySide, uicFilePath])
    
    # with PyQt4
    uicFile = file(uicFilePath)
    pyFile  = file(pyFilePath_PyQt4,'w')
    
    print "compiling %s to %s for PyQt4" % (uicFilePath, pyFilePath_PyQt4)
    
    uic.compileUi( uicFile, pyFile )
    uicFile.close()
    pyFile.close()    

print "finished compiling"
