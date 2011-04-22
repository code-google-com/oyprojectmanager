# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/ozgur/maya/scripts/oy-maya-scripts/oyTools/oyProjectManager/ui/shotEditor.ui'
#
# Created: Thu Jun  3 09:26:08 2010
#      by: PyQt4 UI code generator 4.7.2
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.setWindowModality(QtCore.Qt.NonModal)
        Dialog.resize(714, 858)
        self.verticalLayout = QtGui.QVBoxLayout(Dialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.gridWidget = QtGui.QWidget(Dialog)
        self.gridWidget.setMinimumSize(QtCore.QSize(0, 100))
        self.gridWidget.setObjectName("gridWidget")
        self.gridLayout = QtGui.QGridLayout(self.gridWidget)
        self.gridLayout.setObjectName("gridLayout")
        self.project_label3 = QtGui.QLabel(self.gridWidget)
        self.project_label3.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.project_label3.setObjectName("project_label3")
        self.gridLayout.addWidget(self.project_label3, 1, 0, 1, 1)
        self.project_comboBox1 = QtGui.QComboBox(self.gridWidget)
        self.project_comboBox1.setObjectName("project_comboBox1")
        self.gridLayout.addWidget(self.project_comboBox1, 1, 1, 1, 1)
        self.sequence_label3 = QtGui.QLabel(self.gridWidget)
        self.sequence_label3.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.sequence_label3.setObjectName("sequence_label3")
        self.gridLayout.addWidget(self.sequence_label3, 2, 0, 1, 1)
        self.sequence_comboBox1 = QtGui.QComboBox(self.gridWidget)
        self.sequence_comboBox1.setObjectName("sequence_comboBox1")
        self.gridLayout.addWidget(self.sequence_comboBox1, 2, 1, 1, 1)
        self.servers_label = QtGui.QLabel(self.gridWidget)
        self.servers_label.setMinimumSize(QtCore.QSize(118, 0))
        self.servers_label.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.servers_label.setObjectName("servers_label")
        self.gridLayout.addWidget(self.servers_label, 0, 0, 1, 1)
        self.servers_comboBox = QtGui.QComboBox(self.gridWidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.servers_comboBox.sizePolicy().hasHeightForWidth())
        self.servers_comboBox.setSizePolicy(sizePolicy)
        self.servers_comboBox.setObjectName("servers_comboBox")
        self.gridLayout.addWidget(self.servers_comboBox, 0, 1, 1, 1)
        self.gridLayout.setColumnStretch(1, 1)
        self.verticalLayout.addWidget(self.gridWidget)
        self.shotData_tableWidget = QtGui.QTableWidget(Dialog)
        self.shotData_tableWidget.setEditTriggers(QtGui.QAbstractItemView.AnyKeyPressed|QtGui.QAbstractItemView.DoubleClicked)
        self.shotData_tableWidget.setAlternatingRowColors(True)
        self.shotData_tableWidget.setColumnCount(5)
        self.shotData_tableWidget.setObjectName("shotData_tableWidget")
        self.shotData_tableWidget.setColumnCount(5)
        self.shotData_tableWidget.setRowCount(0)
        self.shotData_tableWidget.horizontalHeader().setStretchLastSection(True)
        self.verticalLayout.addWidget(self.shotData_tableWidget)
        self.horizontalWidget = QtGui.QWidget(Dialog)
        self.horizontalWidget.setObjectName("horizontalWidget")
        self.horizontalLayout = QtGui.QHBoxLayout(self.horizontalWidget)
        self.horizontalLayout.setObjectName("horizontalLayout")
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.save_pushButton = QtGui.QPushButton(self.horizontalWidget)
        self.save_pushButton.setObjectName("save_pushButton")
        self.horizontalLayout.addWidget(self.save_pushButton)
        self.close_pushButton = QtGui.QPushButton(self.horizontalWidget)
        self.close_pushButton.setObjectName("close_pushButton")
        self.horizontalLayout.addWidget(self.close_pushButton)
        self.verticalLayout.addWidget(self.horizontalWidget)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QtGui.QApplication.translate("Dialog", "Shot Editor", None, QtGui.QApplication.UnicodeUTF8))
        self.project_label3.setText(QtGui.QApplication.translate("Dialog", "Project", None, QtGui.QApplication.UnicodeUTF8))
        self.sequence_label3.setText(QtGui.QApplication.translate("Dialog", "Sequence", None, QtGui.QApplication.UnicodeUTF8))
        self.servers_label.setText(QtGui.QApplication.translate("Dialog", "server", None, QtGui.QApplication.UnicodeUTF8))
        self.save_pushButton.setText(QtGui.QApplication.translate("Dialog", "Save", None, QtGui.QApplication.UnicodeUTF8))
        self.close_pushButton.setText(QtGui.QApplication.translate("Dialog", "Close", None, QtGui.QApplication.UnicodeUTF8))

