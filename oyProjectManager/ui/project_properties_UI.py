# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/ozgur/Documents/development/oyProjectManager/oyProjectManager/ui/project_properties.ui'
#
# Created: Mon Jan  9 00:52:04 2012
#      by: pyside-uic 0.2.11 running on PySide 1.0.9
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(340, 175)
        self.verticalLayout = QtGui.QVBoxLayout(Dialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.gridLayout = QtGui.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.name_label = QtGui.QLabel(Dialog)
        self.name_label.setObjectName("name_label")
        self.gridLayout.addWidget(self.name_label, 0, 0, 1, 1)
        self.resolution_label = QtGui.QLabel(Dialog)
        self.resolution_label.setObjectName("resolution_label")
        self.gridLayout.addWidget(self.resolution_label, 2, 0, 1, 1)
        self.resolution_comboBox = QtGui.QComboBox(Dialog)
        self.resolution_comboBox.setObjectName("resolution_comboBox")
        self.gridLayout.addWidget(self.resolution_comboBox, 2, 1, 1, 1)
        self.fps_label = QtGui.QLabel(Dialog)
        self.fps_label.setObjectName("fps_label")
        self.gridLayout.addWidget(self.fps_label, 3, 0, 1, 1)
        self.fps_spinBox = QtGui.QSpinBox(Dialog)
        self.fps_spinBox.setObjectName("fps_spinBox")
        self.gridLayout.addWidget(self.fps_spinBox, 3, 1, 1, 1)
        self.name_lineEdit = QtGui.QLineEdit(Dialog)
        self.name_lineEdit.setObjectName("name_lineEdit")
        self.gridLayout.addWidget(self.name_lineEdit, 0, 1, 1, 1)
        self.code_label = QtGui.QLabel(Dialog)
        self.code_label.setObjectName("code_label")
        self.gridLayout.addWidget(self.code_label, 1, 0, 1, 1)
        self.code_lineEdit = QtGui.QLineEdit(Dialog)
        self.code_lineEdit.setObjectName("code_lineEdit")
        self.gridLayout.addWidget(self.code_lineEdit, 1, 1, 1, 1)
        self.active_checkBox = QtGui.QCheckBox(Dialog)
        self.active_checkBox.setObjectName("active_checkBox")
        self.gridLayout.addWidget(self.active_checkBox, 4, 1, 1, 1)
        self.verticalLayout.addLayout(self.gridLayout)
        self.buttonBox = QtGui.QDialogButtonBox(Dialog)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QtGui.QApplication.translate("Dialog", "Dialog", None, QtGui.QApplication.UnicodeUTF8))
        self.name_label.setText(QtGui.QApplication.translate("Dialog", "Name", None, QtGui.QApplication.UnicodeUTF8))
        self.resolution_label.setText(QtGui.QApplication.translate("Dialog", "Resolution", None, QtGui.QApplication.UnicodeUTF8))
        self.fps_label.setText(QtGui.QApplication.translate("Dialog", "Fps", None, QtGui.QApplication.UnicodeUTF8))
        self.code_label.setText(QtGui.QApplication.translate("Dialog", "Code", None, QtGui.QApplication.UnicodeUTF8))
        self.active_checkBox.setText(QtGui.QApplication.translate("Dialog", "Active", None, QtGui.QApplication.UnicodeUTF8))

