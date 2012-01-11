# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/ozgur/Documents/development/oyProjectManager/oyProjectManager/ui/project_properties.ui'
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

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName(_fromUtf8("Dialog"))
        Dialog.resize(340, 175)
        Dialog.setWindowTitle(QtGui.QApplication.translate("Dialog", "Dialog", None, QtGui.QApplication.UnicodeUTF8))
        self.verticalLayout = QtGui.QVBoxLayout(Dialog)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.gridLayout = QtGui.QGridLayout()
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.name_label = QtGui.QLabel(Dialog)
        self.name_label.setText(QtGui.QApplication.translate("Dialog", "Name", None, QtGui.QApplication.UnicodeUTF8))
        self.name_label.setObjectName(_fromUtf8("name_label"))
        self.gridLayout.addWidget(self.name_label, 0, 0, 1, 1)
        self.resolution_label = QtGui.QLabel(Dialog)
        self.resolution_label.setText(QtGui.QApplication.translate("Dialog", "Resolution", None, QtGui.QApplication.UnicodeUTF8))
        self.resolution_label.setObjectName(_fromUtf8("resolution_label"))
        self.gridLayout.addWidget(self.resolution_label, 2, 0, 1, 1)
        self.resolution_comboBox = QtGui.QComboBox(Dialog)
        self.resolution_comboBox.setObjectName(_fromUtf8("resolution_comboBox"))
        self.gridLayout.addWidget(self.resolution_comboBox, 2, 1, 1, 1)
        self.fps_label = QtGui.QLabel(Dialog)
        self.fps_label.setText(QtGui.QApplication.translate("Dialog", "Fps", None, QtGui.QApplication.UnicodeUTF8))
        self.fps_label.setObjectName(_fromUtf8("fps_label"))
        self.gridLayout.addWidget(self.fps_label, 3, 0, 1, 1)
        self.fps_spinBox = QtGui.QSpinBox(Dialog)
        self.fps_spinBox.setObjectName(_fromUtf8("fps_spinBox"))
        self.gridLayout.addWidget(self.fps_spinBox, 3, 1, 1, 1)
        self.name_lineEdit = QtGui.QLineEdit(Dialog)
        self.name_lineEdit.setObjectName(_fromUtf8("name_lineEdit"))
        self.gridLayout.addWidget(self.name_lineEdit, 0, 1, 1, 1)
        self.code_label = QtGui.QLabel(Dialog)
        self.code_label.setText(QtGui.QApplication.translate("Dialog", "Code", None, QtGui.QApplication.UnicodeUTF8))
        self.code_label.setObjectName(_fromUtf8("code_label"))
        self.gridLayout.addWidget(self.code_label, 1, 0, 1, 1)
        self.code_lineEdit = QtGui.QLineEdit(Dialog)
        self.code_lineEdit.setObjectName(_fromUtf8("code_lineEdit"))
        self.gridLayout.addWidget(self.code_lineEdit, 1, 1, 1, 1)
        self.active_checkBox = QtGui.QCheckBox(Dialog)
        self.active_checkBox.setText(QtGui.QApplication.translate("Dialog", "Active", None, QtGui.QApplication.UnicodeUTF8))
        self.active_checkBox.setObjectName(_fromUtf8("active_checkBox"))
        self.gridLayout.addWidget(self.active_checkBox, 4, 1, 1, 1)
        self.verticalLayout.addLayout(self.gridLayout)
        self.buttonBox = QtGui.QDialogButtonBox(Dialog)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        pass

