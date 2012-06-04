# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/eoyilmaz/Documents/development/oyProjectManager/oyProjectManager/ui/status_manager.ui'
#
# Created: Tue Jun  5 02:32:23 2012
#      by: PyQt4 UI code generator 4.9.1
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
        Dialog.resize(1081, 701)
        self.verticalLayout = QtGui.QVBoxLayout(Dialog)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.label = QtGui.QLabel(Dialog)
        self.label.setObjectName(_fromUtf8("label"))
        self.horizontalLayout.addWidget(self.label)
        self.projects_comboBox = QtGui.QComboBox(Dialog)
        self.projects_comboBox.setObjectName(_fromUtf8("projects_comboBox"))
        self.horizontalLayout.addWidget(self.projects_comboBox)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.label_2 = QtGui.QLabel(Dialog)
        self.label_2.setStyleSheet(_fromUtf8("color: red;"))
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.verticalLayout.addWidget(self.label_2)
        self.tabWidget = QtGui.QTabWidget(Dialog)
        self.tabWidget.setObjectName(_fromUtf8("tabWidget"))
        self.assets_tab = QtGui.QWidget()
        self.assets_tab.setObjectName(_fromUtf8("assets_tab"))
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.assets_tab)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.assets_tableWidget = QtGui.QTableWidget(self.assets_tab)
        self.assets_tableWidget.setAutoFillBackground(True)
        self.assets_tableWidget.setObjectName(_fromUtf8("assets_tableWidget"))
        self.assets_tableWidget.setColumnCount(2)
        self.assets_tableWidget.setRowCount(0)
        item = QtGui.QTableWidgetItem()
        self.assets_tableWidget.setHorizontalHeaderItem(0, item)
        item = QtGui.QTableWidgetItem()
        self.assets_tableWidget.setHorizontalHeaderItem(1, item)
        self.assets_tableWidget.horizontalHeader().setStretchLastSection(True)
        self.verticalLayout_2.addWidget(self.assets_tableWidget)
        self.tabWidget.addTab(self.assets_tab, _fromUtf8(""))
        self.shots_tab = QtGui.QWidget()
        self.shots_tab.setObjectName(_fromUtf8("shots_tab"))
        self.verticalLayout_3 = QtGui.QVBoxLayout(self.shots_tab)
        self.verticalLayout_3.setObjectName(_fromUtf8("verticalLayout_3"))
        self.shots_tableWidget = QtGui.QTableWidget(self.shots_tab)
        self.shots_tableWidget.setObjectName(_fromUtf8("shots_tableWidget"))
        self.shots_tableWidget.setColumnCount(2)
        self.shots_tableWidget.setRowCount(0)
        item = QtGui.QTableWidgetItem()
        self.shots_tableWidget.setHorizontalHeaderItem(0, item)
        item = QtGui.QTableWidgetItem()
        self.shots_tableWidget.setHorizontalHeaderItem(1, item)
        self.shots_tableWidget.horizontalHeader().setStretchLastSection(True)
        self.verticalLayout_3.addWidget(self.shots_tableWidget)
        self.tabWidget.addTab(self.shots_tab, _fromUtf8(""))
        self.verticalLayout.addWidget(self.tabWidget)
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setContentsMargins(-1, 10, -1, -1)
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        spacerItem1 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem1)
        self.close_pushButton = QtGui.QPushButton(Dialog)
        self.close_pushButton.setObjectName(_fromUtf8("close_pushButton"))
        self.horizontalLayout_2.addWidget(self.close_pushButton)
        self.verticalLayout.addLayout(self.horizontalLayout_2)

        self.retranslateUi(Dialog)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QtGui.QApplication.translate("Dialog", "Dialog", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("Dialog", "Project", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("Dialog", "Right Click to change Version status !!!", None, QtGui.QApplication.UnicodeUTF8))
        item = self.assets_tableWidget.horizontalHeaderItem(0)
        item.setText(QtGui.QApplication.translate("Dialog", "Name", None, QtGui.QApplication.UnicodeUTF8))
        item = self.assets_tableWidget.horizontalHeaderItem(1)
        item.setText(QtGui.QApplication.translate("Dialog", "Take", None, QtGui.QApplication.UnicodeUTF8))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.assets_tab), QtGui.QApplication.translate("Dialog", "Assets", None, QtGui.QApplication.UnicodeUTF8))
        item = self.shots_tableWidget.horizontalHeaderItem(0)
        item.setText(QtGui.QApplication.translate("Dialog", "Sequence", None, QtGui.QApplication.UnicodeUTF8))
        item = self.shots_tableWidget.horizontalHeaderItem(1)
        item.setText(QtGui.QApplication.translate("Dialog", "Number", None, QtGui.QApplication.UnicodeUTF8))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.shots_tab), QtGui.QApplication.translate("Dialog", "Shots", None, QtGui.QApplication.UnicodeUTF8))
        self.close_pushButton.setText(QtGui.QApplication.translate("Dialog", "Close", None, QtGui.QApplication.UnicodeUTF8))

