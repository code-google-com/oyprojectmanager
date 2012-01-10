# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/ozgur/Documents/development/oyProjectManager/oyProjectManager/ui/project_manager.ui'
#
# Created: Tue Jan 10 14:43:53 2012
#      by: PyQt4 UI code generator 4.8.5
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_dialog(object):
    def setupUi(self, dialog):
        dialog.setObjectName(_fromUtf8("dialog"))
        dialog.resize(523, 148)
        dialog.setWindowTitle(QtGui.QApplication.translate("dialog", "Project Manager", None, QtGui.QApplication.UnicodeUTF8))
        self.verticalLayout = QtGui.QVBoxLayout(dialog)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.gridLayout = QtGui.QGridLayout()
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.projects_label = QtGui.QLabel(dialog)
        self.projects_label.setText(QtGui.QApplication.translate("dialog", "Projects", None, QtGui.QApplication.UnicodeUTF8))
        self.projects_label.setObjectName(_fromUtf8("projects_label"))
        self.gridLayout.addWidget(self.projects_label, 0, 0, 1, 1)
        self.projects_comboBox = QtGui.QComboBox(dialog)
        self.projects_comboBox.setObjectName(_fromUtf8("projects_comboBox"))
        self.gridLayout.addWidget(self.projects_comboBox, 0, 1, 1, 1)
        self.sequences_comboBox = QtGui.QComboBox(dialog)
        self.sequences_comboBox.setObjectName(_fromUtf8("sequences_comboBox"))
        self.gridLayout.addWidget(self.sequences_comboBox, 1, 1, 1, 1)
        self.sequences_label = QtGui.QLabel(dialog)
        self.sequences_label.setText(QtGui.QApplication.translate("dialog", "Sequences", None, QtGui.QApplication.UnicodeUTF8))
        self.sequences_label.setObjectName(_fromUtf8("sequences_label"))
        self.gridLayout.addWidget(self.sequences_label, 1, 0, 1, 1)
        self.shots_label = QtGui.QLabel(dialog)
        self.shots_label.setText(QtGui.QApplication.translate("dialog", "Shots", None, QtGui.QApplication.UnicodeUTF8))
        self.shots_label.setObjectName(_fromUtf8("shots_label"))
        self.gridLayout.addWidget(self.shots_label, 2, 0, 1, 1)
        self.shots_comboBox = QtGui.QComboBox(dialog)
        self.shots_comboBox.setObjectName(_fromUtf8("shots_comboBox"))
        self.gridLayout.addWidget(self.shots_comboBox, 2, 1, 1, 1)
        self.new_project_pushButton = QtGui.QPushButton(dialog)
        self.new_project_pushButton.setText(QtGui.QApplication.translate("dialog", "New", None, QtGui.QApplication.UnicodeUTF8))
        self.new_project_pushButton.setObjectName(_fromUtf8("new_project_pushButton"))
        self.gridLayout.addWidget(self.new_project_pushButton, 0, 3, 1, 1)
        self.edit_project_pushButton = QtGui.QPushButton(dialog)
        self.edit_project_pushButton.setText(QtGui.QApplication.translate("dialog", "Edit", None, QtGui.QApplication.UnicodeUTF8))
        self.edit_project_pushButton.setObjectName(_fromUtf8("edit_project_pushButton"))
        self.gridLayout.addWidget(self.edit_project_pushButton, 0, 2, 1, 1)
        self.new_sequence_pushButton = QtGui.QPushButton(dialog)
        self.new_sequence_pushButton.setText(QtGui.QApplication.translate("dialog", "New", None, QtGui.QApplication.UnicodeUTF8))
        self.new_sequence_pushButton.setObjectName(_fromUtf8("new_sequence_pushButton"))
        self.gridLayout.addWidget(self.new_sequence_pushButton, 1, 3, 1, 1)
        self.edit_sequence_pushButton = QtGui.QPushButton(dialog)
        self.edit_sequence_pushButton.setText(QtGui.QApplication.translate("dialog", "Edit", None, QtGui.QApplication.UnicodeUTF8))
        self.edit_sequence_pushButton.setObjectName(_fromUtf8("edit_sequence_pushButton"))
        self.gridLayout.addWidget(self.edit_sequence_pushButton, 1, 2, 1, 1)
        self.edit_shot_pushButton = QtGui.QPushButton(dialog)
        self.edit_shot_pushButton.setText(QtGui.QApplication.translate("dialog", "Edit", None, QtGui.QApplication.UnicodeUTF8))
        self.edit_shot_pushButton.setObjectName(_fromUtf8("edit_shot_pushButton"))
        self.gridLayout.addWidget(self.edit_shot_pushButton, 2, 2, 1, 1)
        self.new_shots_pushButton = QtGui.QPushButton(dialog)
        self.new_shots_pushButton.setText(QtGui.QApplication.translate("dialog", "New", None, QtGui.QApplication.UnicodeUTF8))
        self.new_shots_pushButton.setObjectName(_fromUtf8("new_shots_pushButton"))
        self.gridLayout.addWidget(self.new_shots_pushButton, 2, 3, 1, 1)
        self.gridLayout.setColumnStretch(1, 1)
        self.verticalLayout.addLayout(self.gridLayout)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.close_pushButton = QtGui.QPushButton(dialog)
        self.close_pushButton.setText(QtGui.QApplication.translate("dialog", "Close", None, QtGui.QApplication.UnicodeUTF8))
        self.close_pushButton.setObjectName(_fromUtf8("close_pushButton"))
        self.horizontalLayout.addWidget(self.close_pushButton)
        self.verticalLayout.addLayout(self.horizontalLayout)

        self.retranslateUi(dialog)
        QtCore.QMetaObject.connectSlotsByName(dialog)

    def retranslateUi(self, dialog):
        pass

