# -*- coding: utf-8 -*-
# Copyright (c) 2009-2012, Erkan Ozgur Yilmaz
# 
# This module is part of oyProjectManager and is released under the BSD 2
# License: http://www.opensource.org/licenses/BSD-2-Clause

from PySide import QtGui, QtCore
import logging
from oyProjectManager import conf
from oyProjectManager.core.models import Project
from oyProjectManager.ui import project_properties_UI


logger = logging.getLogger(__name__)

class MainDialog(QtGui.QDialog, project_properties_UI.Ui_Dialog):
    """Dialog to edit project properties
    
    If a :class:`~oyProjectManager.core.models.Project` instance is also passed
    it will edit the given project.
    
    If no Project is passed then it will create and return a new one.
    """
    
    def __init__(self, parent=None, project=None):
        super(MainDialog, self).__init__(parent)
        self.setupUi(self)
        
        self.resolution_presets = conf.resolution_presets
        self.project = project
        
        self._setup_signals()
        self._setup_defaults()
        
        self.update_UI_from_project(self.project)
    
    def _setup_signals(self):
        """sets up signals
        """

        # cancel button
        QtCore.QObject.connect(
            self.buttonBox,
            QtCore.SIGNAL("rejected()"),
            self.close
        )
        
        # ok button
        QtCore.QObject.connect(
            self.buttonBox,
            QtCore.SIGNAL("accepted()"),
            self.button_box_ok_clicked
        )

    def set_resolution_to_default(self):
        # set the resolution to the default preset
        index = self.resolution_comboBox.findText(
            conf.default_resolution_preset
        )
        self.resolution_comboBox.setCurrentIndex(index)

    def _setup_defaults(self):
        """sets up the default values
        """
        
        self.resolution_comboBox.addItems(
            sorted(conf.resolution_presets.keys())
        )
        self.set_resolution_to_default()

        # set the fps to conf.default_fps
        self.fps_spinBox.setValue(conf.default_fps)
        
        # set active_checkBox to true
        self.active_checkBox.setChecked(True)
        
        # if a project is given don't let the user to try to change the code
        # attribute
        if self.project is not None:
            self.code_lineEdit.setEnabled(False)
    
    def update_UI_from_project(self, project):
        """Updates the UI with the info from the given project instance
        
        :param project: The :class:`~oyProjectManager.core.models.Project`
          instance which the UI data will be read from.
        """
        # if a project is given update the UI with the given project info
        
        if project is None:
            return
        
        self.name_lineEdit.setText(project.name)
        self.code_lineEdit.setText(project.code)
        self.fps_spinBox.setValue(project.fps)
        self.active_checkBox.setChecked(project.active)
        
        # set the resolution
        preset_key = None
        for key in conf.resolution_presets.keys():
            if conf.resolution_presets[key] == [project.width,
                                                project.height,
                                                project.pixel_aspect]:
                preset_key = key
                break
        
        if preset_key is not None:
            index = self.resolution_comboBox.findText(preset_key)
            self.resolution_comboBox.setCurrentIndex(index)
        else:
            # set it to custom
            self.resolution_comboBox.setCurrentIndex(
                self.resolution_comboBox.count()-1
            )
        
    
    def button_box_ok_clicked(self):
        """runs when the ok button clicked
        """
        
        # if there is no project given create a new one and return it
        
        # create_project
        # get the data from the input fields
        name = self.name_lineEdit.text()
        code = self.code_lineEdit.text()
        resolution_name = self.resolution_comboBox.currentText()
        resolution_data = conf.resolution_presets[resolution_name]
        fps = self.fps_spinBox.value()
        active = self.active_checkBox.isChecked()
        
        if self.project is None:
            logger.debug("no project is given creating new one")
            # create the project
            
            new_project = Project(name=name, code=code)
            new_project.fps = fps
            new_project.width = resolution_data[0]
            new_project.height = resolution_data[1]
            new_project.pixel_aspect = resolution_data[2]
            new_project.active = active
            
            new_project.create()
            
            self.project = new_project
        
        else:
            logger.debug("updating the given project")
            
            # update the project
            self.project.name = name
            self.project.fps = fps
            self.project.width = resolution_data[0]
            self.project.height = resolution_data[1]
            self.project.pixel_aspect = resolution_data[2]
            self.project.active = active
            self.project.save()
        
        # and close the dialog
        self.close()
    
