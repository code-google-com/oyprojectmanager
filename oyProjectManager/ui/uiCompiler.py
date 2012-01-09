# -*- coding: utf-8 -*-
# Copyright (c) 2009-2012, Erkan Ozgur Yilmaz
# 
# This module is part of oyProjectManager and is released under the BSD 2
# License: http://www.opensource.org/licenses/BSD-2-Clause

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

# version_creator
uicFilePaths.append(os.path.join(ui_path, "version_creator.ui"))
pyFilePaths.append(os.path.join(ui_path, "version_creator_UI.py"))

# project_manager
uicFilePaths.append(os.path.join(ui_path, "project_manager.ui"))
pyFilePaths.append(os.path.join(ui_path, "project_manager_UI.py"))

# project_properties
uicFilePaths.append(os.path.join(ui_path, "project_properties.ui"))
pyFilePaths.append(os.path.join(ui_path, "project_properties_UI.py"))

# assetUpdater
#uicFilePaths.append(os.path.join(ui_path, "version_updater.ui"))
#pyFilePaths.append(os.path.join(ui_path, "version_updater_UI.py"))
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
