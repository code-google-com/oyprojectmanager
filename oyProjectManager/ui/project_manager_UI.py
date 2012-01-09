# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/ozgur/Documents/development/oyProjectManager/oyProjectManager/ui/project_manager.ui'
#
# Created: Mon Jan  9 00:52:04 2012
#      by: pyside-uic 0.2.11 running on PySide 1.0.9
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_dialog(object):
    def setupUi(self, dialog):
        dialog.setObjectName("dialog")
        dialog.resize(523, 148)
        self.verticalLayout = QtGui.QVBoxLayout(dialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.gridLayout = QtGui.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.projects_label = QtGui.QLabel(dialog)
        self.projects_label.setObjectName("projects_label")
        self.gridLayout.addWidget(self.projects_label, 0, 0, 1, 1)
        self.projects_comboBox = QtGui.QComboBox(dialog)
        self.projects_comboBox.setObjectName("projects_comboBox")
        self.gridLayout.addWidget(self.projects_comboBox, 0, 1, 1, 1)
        self.sequences_comboBox = QtGui.QComboBox(dialog)
        self.sequences_comboBox.setObjectName("sequences_comboBox")
        self.gridLayout.addWidget(self.sequences_comboBox, 1, 1, 1, 1)
        self.sequences_label = QtGui.QLabel(dialog)
        self.sequences_label.setObjectName("sequences_label")
        self.gridLayout.addWidget(self.sequences_label, 1, 0, 1, 1)
        self.shots_label = QtGui.QLabel(dialog)
        self.shots_label.setObjectName("shots_label")
        self.gridLayout.addWidget(self.shots_label, 2, 0, 1, 1)
        self.shots_comboBox = QtGui.QComboBox(dialog)
        self.shots_comboBox.setObjectName("shots_comboBox")
        self.gridLayout.addWidget(self.shots_comboBox, 2, 1, 1, 1)
        self.new_project_pushButton = QtGui.QPushButton(dialog)
        self.new_project_pushButton.setObjectName("new_project_pushButton")
        self.gridLayout.addWidget(self.new_project_pushButton, 0, 3, 1, 1)
        self.edit_project_pushButton = QtGui.QPushButton(dialog)
        self.edit_project_pushButton.setObjectName("edit_project_pushButton")
        self.gridLayout.addWidget(self.edit_project_pushButton, 0, 2, 1, 1)
        self.new_sequence_pushButton = QtGui.QPushButton(dialog)
        self.new_sequence_pushButton.setObjectName("new_sequence_pushButton")
        self.gridLayout.addWidget(self.new_sequence_pushButton, 1, 3, 1, 1)
        self.edit_sequence_pushButton = QtGui.QPushButton(dialog)
        self.edit_sequence_pushButton.setObjectName("edit_sequence_pushButton")
        self.gridLayout.addWidget(self.edit_sequence_pushButton, 1, 2, 1, 1)
        self.edit_shot_pushButton = QtGui.QPushButton(dialog)
        self.edit_shot_pushButton.setObjectName("edit_shot_pushButton")
        self.gridLayout.addWidget(self.edit_shot_pushButton, 2, 2, 1, 1)
        self.new_shots_pushButton = QtGui.QPushButton(dialog)
        self.new_shots_pushButton.setObjectName("new_shots_pushButton")
        self.gridLayout.addWidget(self.new_shots_pushButton, 2, 3, 1, 1)
        self.gridLayout.setColumnStretch(1, 1)
        self.verticalLayout.addLayout(self.gridLayout)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.close_pushButton = QtGui.QPushButton(dialog)
        self.close_pushButton.setObjectName("close_pushButton")
        self.horizontalLayout.addWidget(self.close_pushButton)
        self.verticalLayout.addLayout(self.horizontalLayout)

        self.retranslateUi(dialog)
        QtCore.QMetaObject.connectSlotsByName(dialog)

    def retranslateUi(self, dialog):
        dialog.setWindowTitle(QtGui.QApplication.translate("dialog", "Project Manager", None, QtGui.QApplication.UnicodeUTF8))
        self.projects_label.setText(QtGui.QApplication.translate("dialog", "Projects", None, QtGui.QApplication.UnicodeUTF8))
        self.sequences_label.setText(QtGui.QApplication.translate("dialog", "Sequences", None, QtGui.QApplication.UnicodeUTF8))
        self.shots_label.setText(QtGui.QApplication.translate("dialog", "Shots", None, QtGui.QApplication.UnicodeUTF8))
        self.new_project_pushButton.setText(QtGui.QApplication.translate("dialog", "New", None, QtGui.QApplication.UnicodeUTF8))
        self.edit_project_pushButton.setText(QtGui.QApplication.translate("dialog", "Edit", None, QtGui.QApplication.UnicodeUTF8))
        self.new_sequence_pushButton.setText(QtGui.QApplication.translate("dialog", "New", None, QtGui.QApplication.UnicodeUTF8))
        self.edit_sequence_pushButton.setText(QtGui.QApplication.translate("dialog", "Edit", None, QtGui.QApplication.UnicodeUTF8))
        self.edit_shot_pushButton.setText(QtGui.QApplication.translate("dialog", "Edit", None, QtGui.QApplication.UnicodeUTF8))
        self.new_shots_pushButton.setText(QtGui.QApplication.translate("dialog", "New", None, QtGui.QApplication.UnicodeUTF8))
        self.close_pushButton.setText(QtGui.QApplication.translate("dialog", "Close", None, QtGui.QApplication.UnicodeUTF8))

