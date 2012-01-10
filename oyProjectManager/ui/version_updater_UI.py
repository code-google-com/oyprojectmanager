# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/ozgur/Documents/development/oyProjectManager/oyProjectManager/ui/version_updater.ui'
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
        Dialog.setWindowModality(QtCore.Qt.ApplicationModal)
        Dialog.resize(437, 442)
        Dialog.setWindowTitle(QtGui.QApplication.translate("Dialog", "Asset Updater", None, QtGui.QApplication.UnicodeUTF8))
        self.verticalLayout = QtGui.QVBoxLayout(Dialog)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.label = QtGui.QLabel(Dialog)
        self.label.setText(QtGui.QApplication.translate("Dialog", "Please check the Assets that needs to be updated", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setObjectName(_fromUtf8("label"))
        self.verticalLayout.addWidget(self.label)
        self.assetList_tableWidget = QtGui.QTableWidget(Dialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(self.assetList_tableWidget.sizePolicy().hasHeightForWidth())
        self.assetList_tableWidget.setSizePolicy(sizePolicy)
        self.assetList_tableWidget.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        self.assetList_tableWidget.setAlternatingRowColors(True)
        self.assetList_tableWidget.setCornerButtonEnabled(False)
        self.assetList_tableWidget.setColumnCount(4)
        self.assetList_tableWidget.setObjectName(_fromUtf8("assetList_tableWidget"))
        self.assetList_tableWidget.setRowCount(0)
        self.assetList_tableWidget.horizontalHeader().setVisible(True)
        self.assetList_tableWidget.horizontalHeader().setStretchLastSection(True)
        self.verticalLayout.addWidget(self.assetList_tableWidget)
        self.horizontalWidget = QtGui.QWidget(Dialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.horizontalWidget.sizePolicy().hasHeightForWidth())
        self.horizontalWidget.setSizePolicy(sizePolicy)
        self.horizontalWidget.setObjectName(_fromUtf8("horizontalWidget"))
        self.horizontalLayout = QtGui.QHBoxLayout(self.horizontalWidget)
        self.horizontalLayout.setMargin(0)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.selectNone_pushButton = QtGui.QPushButton(self.horizontalWidget)
        self.selectNone_pushButton.setText(QtGui.QApplication.translate("Dialog", "Select None", None, QtGui.QApplication.UnicodeUTF8))
        self.selectNone_pushButton.setObjectName(_fromUtf8("selectNone_pushButton"))
        self.horizontalLayout.addWidget(self.selectNone_pushButton)
        self.selectAll_pushButton = QtGui.QPushButton(self.horizontalWidget)
        self.selectAll_pushButton.setText(QtGui.QApplication.translate("Dialog", "Select All", None, QtGui.QApplication.UnicodeUTF8))
        self.selectAll_pushButton.setObjectName(_fromUtf8("selectAll_pushButton"))
        self.horizontalLayout.addWidget(self.selectAll_pushButton)
        self.update_pushButton = QtGui.QPushButton(self.horizontalWidget)
        self.update_pushButton.setText(QtGui.QApplication.translate("Dialog", "Update", None, QtGui.QApplication.UnicodeUTF8))
        self.update_pushButton.setObjectName(_fromUtf8("update_pushButton"))
        self.horizontalLayout.addWidget(self.update_pushButton)
        self.cancel_pushButton = QtGui.QPushButton(self.horizontalWidget)
        self.cancel_pushButton.setText(QtGui.QApplication.translate("Dialog", "Cancel", None, QtGui.QApplication.UnicodeUTF8))
        self.cancel_pushButton.setObjectName(_fromUtf8("cancel_pushButton"))
        self.horizontalLayout.addWidget(self.cancel_pushButton)
        self.verticalLayout.addWidget(self.horizontalWidget)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        pass

