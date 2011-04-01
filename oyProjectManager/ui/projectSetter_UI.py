# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/ozgur/maya/scripts/oy-maya-scripts/oyTools/oyProjectManager/ui/projectSetter.ui'
#
# Created: Thu Jun  3 09:26:08 2010
#      by: PyQt4 UI code generator 4.7.2
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.setWindowModality(QtCore.Qt.ApplicationModal)
        Dialog.resize(450, 134)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(Dialog.sizePolicy().hasHeightForWidth())
        Dialog.setSizePolicy(sizePolicy)
        Dialog.setModal(True)
        self.verticalLayout = QtGui.QVBoxLayout(Dialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.gridLayoutWidget = QtGui.QWidget(Dialog)
        self.gridLayoutWidget.setObjectName("gridLayoutWidget")
        self.gridLayout = QtGui.QGridLayout(self.gridLayoutWidget)
        self.gridLayout.setObjectName("gridLayout")
        self.server_label = QtGui.QLabel(self.gridLayoutWidget)
        self.server_label.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.server_label.setObjectName("server_label")
        self.gridLayout.addWidget(self.server_label, 0, 0, 1, 1)
        self.server_comboBox = QtGui.QComboBox(self.gridLayoutWidget)
        self.server_comboBox.setObjectName("server_comboBox")
        self.gridLayout.addWidget(self.server_comboBox, 0, 1, 1, 1)
        self.project_label = QtGui.QLabel(self.gridLayoutWidget)
        self.project_label.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.project_label.setObjectName("project_label")
        self.gridLayout.addWidget(self.project_label, 1, 0, 1, 1)
        self.project_comboBox = QtGui.QComboBox(self.gridLayoutWidget)
        self.project_comboBox.setObjectName("project_comboBox")
        self.gridLayout.addWidget(self.project_comboBox, 1, 1, 1, 1)
        self.sequence_label = QtGui.QLabel(self.gridLayoutWidget)
        self.sequence_label.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.sequence_label.setObjectName("sequence_label")
        self.gridLayout.addWidget(self.sequence_label, 2, 0, 1, 1)
        self.sequence_comboBox = QtGui.QComboBox(self.gridLayoutWidget)
        self.sequence_comboBox.setObjectName("sequence_comboBox")
        self.gridLayout.addWidget(self.sequence_comboBox, 2, 1, 1, 1)
        self.gridLayout.setColumnStretch(1, 1)
        self.verticalLayout.addWidget(self.gridLayoutWidget)
        self.buttonBox = QtGui.QDialogButtonBox(Dialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setCenterButtons(False)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(Dialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("accepted()"), Dialog.accept)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QtGui.QApplication.translate("Dialog", "oySetProject", None, QtGui.QApplication.UnicodeUTF8))
        self.server_label.setText(QtGui.QApplication.translate("Dialog", "Server", None, QtGui.QApplication.UnicodeUTF8))
        self.project_label.setText(QtGui.QApplication.translate("Dialog", "Project", None, QtGui.QApplication.UnicodeUTF8))
        self.sequence_label.setText(QtGui.QApplication.translate("Dialog", "Sequence", None, QtGui.QApplication.UnicodeUTF8))

