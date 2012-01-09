# -*- coding: utf-8 -*-
# Copyright (c) 2009-2012, Erkan Ozgur Yilmaz
# 
# This module is part of oyProjectManager and is released under the BSD 2
# License: http://www.opensource.org/licenses/BSD-2-Clause

import sys

from PySide import QtGui, QtCore

import oyProjectManager
from oyProjectManager import db
from oyProjectManager.ui import project_properties
import project_manager_UI
from oyProjectManager.core.models import Project, Sequence, Shot

def UI():
    """the UI to call the dialog by itself
    """
    global app
    global mainDialog
    
    self_quit = False
    if QtGui.QApplication.instance() is None:
        app = QtGui.QApplication(*sys.argv)
        self_quit = True
    else:
        app = QtGui.QApplication.instance()

    mainDialog = MainDialog()
    mainDialog.show()
    #app.setStyle('Plastique')
    app.exec_()

    if self_quit:
        app.connect(
            app,
            QtCore.SIGNAL("lastWindowClosed()"),
            app,
            QtCore.SLOT("quit()")
        )

    return mainDialog


class MainDialog(QtGui.QDialog, project_manager_UI.Ui_dialog):
    """the main dialog of the system
    """
    
    def __init__(self, parent=None):
        super(MainDialog, self).__init__(parent)
        self.setupUi(self)
        
        # change the window title
        self.setWindowTitle(
            self.windowTitle() + ' | ' + \
            'oyProjectManager v' + oyProjectManager.__version__
        )
        
        # center to the window
        self._center_window()
        
        # create cache attributes
        self.projects_comboBox.projects = []
        self.sequences_comboBox.sequences = []
        self.shots_comboBox.shots = []

        # setup the database
        if db.session is None:
            db.setup()
        
        self._setup_signals()
        self._set_defaults()
    
    def _center_window(self):
        """centers the window to the screen
        """
        screen = QtGui.QDesktopWidget().screenGeometry()
        size =  self.geometry()
        self.move(
            (screen.width()-size.width()) * 0.5,
            (screen.height()-size.height()) * 0.5
        )
    
    def _setup_signals(self):
        """sets up the signals
        """

        # close button
        QtCore.QObject.connect(
            self.close_pushButton,
            QtCore.SIGNAL("clicked()"),
            self.close
        )

        # project_comboBox
        QtCore.QObject.connect(
            self.projects_comboBox,
            QtCore.SIGNAL("currentIndexChanged(int)"),
            self.projects_changed
        )
        
        # sequences_comboBox
        QtCore.QObject.connect(
            self.sequences_comboBox,
            QtCore.SIGNAL("currentIndexChanged(int)"),
            self.sequences_changed
        )

        # new_project_pushButton
        QtCore.QObject.connect(
            self.new_project_pushButton,
            QtCore.SIGNAL("clicked()"),
            self.new_project_pushButton_clicked
        )

        # edit_project_pushButton
        QtCore.QObject.connect(
            self.edit_project_pushButton,
            QtCore.SIGNAL("clicked()"),
            self.edit_project_pushButton_clicked
        )

        # new_sequence_pushButton
        QtCore.QObject.connect(
            self.new_sequence_pushButton,
            QtCore.SIGNAL("clicked()"),
            self.new_sequence_pushButton_clicked
        )
        
        # new_shots_pushButton
        QtCore.QObject.connect(
            self.new_shots_pushButton,
            QtCore.SIGNAL("clicked()"),
            self.new_shots_pushButton_clicked
        )

    def _set_defaults(self):
        """sets the default values for the interface
        """
        
        # update projects
        self.update_project_comboBox()
        
        # select first project
        self.projects_comboBox.setCurrentIndex(0)
        
    def update_project_comboBox(self):
        """Updates the projects_comboBox
        """
        
        # fill projects
        projects = db.query(Project)\
            .order_by(Project.name.asc())\
            .all()

        # cache the projects
        self.projects_comboBox.projects = projects
        
        self.projects_comboBox.clear()
        self.projects_comboBox.addItems(map(lambda x: x.name, projects))
    
    def projects_changed(self):
        """runs when the projects comboBox changed
        """
        self.update_sequences_comboBox()
    
    def update_sequences_comboBox(self):
        """updates the sequences_comboBox according to the current project
        """
        project = self.get_current_project()
        sequences = db.query(Sequence)\
            .filter(Sequence.project==project)\
            .order_by(Sequence.name.asc())\
            .all()
        self.sequences_comboBox.sequences = sequences
        self.sequences_comboBox.clear()
        self.sequences_comboBox.addItems(map(lambda x: x.name, sequences))
    
    def get_current_project(self):
        """Returns the currently selected
        :class:`~oyProjectManager.core.models.Project` instance from the UI
        
        :return: :class:`~oyProjectManager.core.models.Project`
        """
        
        index = self.projects_comboBox.currentIndex()
        
        if index != -1:
            return self.projects_comboBox.projects[index]
        
        return None
    
    def sequences_changed(self):
        """runs when sequence_comboBox has changed
        """
        
        # update shots
        self.update_shots_comboBox()
    
    def update_shots_comboBox(self):
        """updates the shots_comboBox
        """
        
        sequence = self.get_current_sequence()
        shots = db.query(Shot)\
            .filter(Shot.sequence==sequence)\
            .order_by(Shot.code.asc())\
            .all()
        
        self.shots_comboBox.shots = shots
        self.shots_comboBox.clear()
        self.shots_comboBox.addItems(
            sorted(map(lambda x: x.code, shots))
        )
    
    def get_current_sequence(self):
        """Returns the currently selected
        :class:`~oyProjectManager.core.models.Sequence` instance from the UI
        
        :return: :class:`~oyProjectManager.core.models.Sequence`
        """
        
        index = self.sequences_comboBox.currentIndex()
        if index != -1:
            return self.sequences_comboBox.sequences[index]
        
        return None

    def new_project_pushButton_clicked(self):
        """runs when new_project_pushButton is clicked
        """

        # just call the project_properties dialog
        proj_pro_dialog = project_properties.MainDialog(self)
        proj_pro_dialog.exec_()

        new_project = proj_pro_dialog.project

        if new_project is not None:
            # update projects_comboBox
            self.update_project_comboBox()

            # set it to the new project
            index = self.projects_comboBox.findText(new_project.name)
            self.projects_comboBox.setCurrentIndex(index)

    def edit_project_pushButton_clicked(self):
        """runs when edit_project_pushButton is clicked
        """
        
        # get the project from UI
        project = self.get_current_project()
        
        # just call the project_properties dialog
        proj_pro_dialog = project_properties.MainDialog(self, project)
        proj_pro_dialog.exec_()

        # update projects_comboBox
        self.update_project_comboBox()

        # set it to the project
        index = self.projects_comboBox.findText(project.name)
        self.projects_comboBox.setCurrentIndex(index)

    def new_sequence_pushButton_clicked(self):
        """runs when new_sequence_pushButton is clicked
        """
        
        project = self.get_current_project()
        
        if project is None:
            return
        
        dialog = QtGui.QInputDialog()
        
        new_sequence_name, ok = dialog.getText(
            self,
            "Add Sequence",
            "New Sequence Name"
        )
        
        if ok:
            if new_sequence_name != "":
                new_sequence = Sequence(project, new_sequence_name)
                new_sequence.save()
                new_sequence.create()
                
                # update sequence_comboBox
                self.update_sequences_comboBox()

                # set it to the new project
                index = self.sequences_comboBox.findText(new_sequence.name)
                self.sequences_comboBox.setCurrentIndex(index)
    
    def new_shots_pushButton_clicked(self):
        """runs when new_shots_pushButton clicked
        """
        
        sequence = self.get_current_sequence()
        
        if sequence is None:
            return
        
        assert isinstance(sequence, Sequence)
        
        dialog = QtGui.QInputDialog()
        
        shot_template, ok = dialog.getText(
            self,
            "Add Shots",
            "Shot Template"
        )
        
        if ok:
            if shot_template != "":
                sequence.add_shots(shot_template)
                
                # update the shots_comboBox
                self.update_shots_comboBox()
