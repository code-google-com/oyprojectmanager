# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/eoyilmaz/Documents/development/oyProjectManager/oyProjectManager/ui/version_replacer.ui'
#
# Created: Sat Oct 20 20:42:57 2012
#      by: PyQt4 UI code generator 4.9.3
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
        Dialog.resize(1043, 414)
        self.horizontalLayout_5 = QtGui.QHBoxLayout(Dialog)
        self.horizontalLayout_5.setObjectName(_fromUtf8("horizontalLayout_5"))
        self.verticalWidget = QtGui.QWidget(Dialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(3)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.verticalWidget.sizePolicy().hasHeightForWidth())
        self.verticalWidget.setSizePolicy(sizePolicy)
        self.verticalWidget.setMinimumSize(QtCore.QSize(10, 0))
        self.verticalWidget.setObjectName(_fromUtf8("verticalWidget"))
        self.verticalLayout = QtGui.QVBoxLayout(self.verticalWidget)
        self.verticalLayout.setMargin(0)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.label = QtGui.QLabel(self.verticalWidget)
        self.label.setObjectName(_fromUtf8("label"))
        self.verticalLayout.addWidget(self.label)
        self.assetList_tableWidget = QtGui.QTableWidget(self.verticalWidget)
        self.assetList_tableWidget.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        self.assetList_tableWidget.setAlternatingRowColors(True)
        self.assetList_tableWidget.setCornerButtonEnabled(False)
        self.assetList_tableWidget.setColumnCount(2)
        self.assetList_tableWidget.setObjectName(_fromUtf8("assetList_tableWidget"))
        self.assetList_tableWidget.setRowCount(0)
        self.assetList_tableWidget.horizontalHeader().setStretchLastSection(True)
        self.verticalLayout.addWidget(self.assetList_tableWidget)
        self.horizontalLayout_5.addWidget(self.verticalWidget)
        self.verticalWidget1 = QtGui.QWidget(Dialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(2)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.verticalWidget1.sizePolicy().hasHeightForWidth())
        self.verticalWidget1.setSizePolicy(sizePolicy)
        self.verticalWidget1.setObjectName(_fromUtf8("verticalWidget1"))
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.verticalWidget1)
        self.verticalLayout_2.setMargin(0)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.gridWidget1 = QtGui.QWidget(self.verticalWidget1)
        self.gridWidget1.setObjectName(_fromUtf8("gridWidget1"))
        self.gridLayout1 = QtGui.QGridLayout(self.gridWidget1)
        self.gridLayout1.setMargin(0)
        self.gridLayout1.setObjectName(_fromUtf8("gridLayout1"))
        self.sequence_label = QtGui.QLabel(self.gridWidget1)
        self.sequence_label.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.sequence_label.setObjectName(_fromUtf8("sequence_label"))
        self.gridLayout1.addWidget(self.sequence_label, 1, 0, 1, 1)
        self.assetType_label1 = QtGui.QLabel(self.gridWidget1)
        self.assetType_label1.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.assetType_label1.setObjectName(_fromUtf8("assetType_label1"))
        self.gridLayout1.addWidget(self.assetType_label1, 3, 0, 1, 1)
        self.assetType_comboBox1 = QtGui.QComboBox(self.gridWidget1)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.assetType_comboBox1.sizePolicy().hasHeightForWidth())
        self.assetType_comboBox1.setSizePolicy(sizePolicy)
        self.assetType_comboBox1.setObjectName(_fromUtf8("assetType_comboBox1"))
        self.gridLayout1.addWidget(self.assetType_comboBox1, 3, 1, 1, 1)
        self.line_4 = QtGui.QFrame(self.gridWidget1)
        self.line_4.setFrameShape(QtGui.QFrame.HLine)
        self.line_4.setFrameShadow(QtGui.QFrame.Sunken)
        self.line_4.setObjectName(_fromUtf8("line_4"))
        self.gridLayout1.addWidget(self.line_4, 6, 0, 1, 2)
        self.project_comboBox = QtGui.QComboBox(self.gridWidget1)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.project_comboBox.sizePolicy().hasHeightForWidth())
        self.project_comboBox.setSizePolicy(sizePolicy)
        self.project_comboBox.setEditable(False)
        self.project_comboBox.setObjectName(_fromUtf8("project_comboBox"))
        self.gridLayout1.addWidget(self.project_comboBox, 0, 1, 1, 1)
        self.subName_label = QtGui.QLabel(self.gridWidget1)
        self.subName_label.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.subName_label.setObjectName(_fromUtf8("subName_label"))
        self.gridLayout1.addWidget(self.subName_label, 7, 0, 1, 1)
        self.baseName_label = QtGui.QLabel(self.gridWidget1)
        self.baseName_label.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.baseName_label.setObjectName(_fromUtf8("baseName_label"))
        self.gridLayout1.addWidget(self.baseName_label, 5, 0, 1, 1)
        self.sequence_comboBox = QtGui.QComboBox(self.gridWidget1)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.sequence_comboBox.sizePolicy().hasHeightForWidth())
        self.sequence_comboBox.setSizePolicy(sizePolicy)
        self.sequence_comboBox.setEditable(False)
        self.sequence_comboBox.setObjectName(_fromUtf8("sequence_comboBox"))
        self.gridLayout1.addWidget(self.sequence_comboBox, 1, 1, 1, 1)
        self.project_label = QtGui.QLabel(self.gridWidget1)
        self.project_label.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.project_label.setObjectName(_fromUtf8("project_label"))
        self.gridLayout1.addWidget(self.project_label, 0, 0, 1, 1)
        self.line_2 = QtGui.QFrame(self.gridWidget1)
        self.line_2.setFrameShape(QtGui.QFrame.HLine)
        self.line_2.setFrameShadow(QtGui.QFrame.Sunken)
        self.line_2.setObjectName(_fromUtf8("line_2"))
        self.gridLayout1.addWidget(self.line_2, 2, 0, 1, 2)
        self.line_3 = QtGui.QFrame(self.gridWidget1)
        self.line_3.setFrameShape(QtGui.QFrame.HLine)
        self.line_3.setFrameShadow(QtGui.QFrame.Sunken)
        self.line_3.setObjectName(_fromUtf8("line_3"))
        self.gridLayout1.addWidget(self.line_3, 4, 0, 1, 2)
        self.baseName_comboBox = QtGui.QComboBox(self.gridWidget1)
        self.baseName_comboBox.setEnabled(True)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.baseName_comboBox.sizePolicy().hasHeightForWidth())
        self.baseName_comboBox.setSizePolicy(sizePolicy)
        self.baseName_comboBox.setObjectName(_fromUtf8("baseName_comboBox"))
        self.gridLayout1.addWidget(self.baseName_comboBox, 5, 1, 1, 1)
        self.subName_comboBox = QtGui.QComboBox(self.gridWidget1)
        self.subName_comboBox.setEnabled(True)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.subName_comboBox.sizePolicy().hasHeightForWidth())
        self.subName_comboBox.setSizePolicy(sizePolicy)
        self.subName_comboBox.setObjectName(_fromUtf8("subName_comboBox"))
        self.gridLayout1.addWidget(self.subName_comboBox, 7, 1, 1, 1)
        self.assetFile_label = QtGui.QLabel(self.gridWidget1)
        self.assetFile_label.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.assetFile_label.setObjectName(_fromUtf8("assetFile_label"))
        self.gridLayout1.addWidget(self.assetFile_label, 9, 0, 1, 1)
        self.assetFile_comboBox = QtGui.QComboBox(self.gridWidget1)
        self.assetFile_comboBox.setEnabled(True)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.assetFile_comboBox.sizePolicy().hasHeightForWidth())
        self.assetFile_comboBox.setSizePolicy(sizePolicy)
        self.assetFile_comboBox.setObjectName(_fromUtf8("assetFile_comboBox"))
        self.gridLayout1.addWidget(self.assetFile_comboBox, 9, 1, 1, 1)
        self.line_5 = QtGui.QFrame(self.gridWidget1)
        self.line_5.setFrameShape(QtGui.QFrame.HLine)
        self.line_5.setFrameShadow(QtGui.QFrame.Sunken)
        self.line_5.setObjectName(_fromUtf8("line_5"))
        self.gridLayout1.addWidget(self.line_5, 8, 0, 1, 2)
        self.verticalLayout_2.addWidget(self.gridWidget1)
        self.removeReplacement_pushButton = QtGui.QPushButton(self.verticalWidget1)
        self.removeReplacement_pushButton.setObjectName(_fromUtf8("removeReplacement_pushButton"))
        self.verticalLayout_2.addWidget(self.removeReplacement_pushButton)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout_2.addItem(spacerItem)
        self.horizontalWidget = QtGui.QWidget(self.verticalWidget1)
        self.horizontalWidget.setObjectName(_fromUtf8("horizontalWidget"))
        self.horizontalLayout = QtGui.QHBoxLayout(self.horizontalWidget)
        self.horizontalLayout.setMargin(0)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        spacerItem1 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem1)
        self.replace_pushButton = QtGui.QPushButton(self.horizontalWidget)
        self.replace_pushButton.setObjectName(_fromUtf8("replace_pushButton"))
        self.horizontalLayout.addWidget(self.replace_pushButton)
        self.cancel_pushButton = QtGui.QPushButton(self.horizontalWidget)
        self.cancel_pushButton.setObjectName(_fromUtf8("cancel_pushButton"))
        self.horizontalLayout.addWidget(self.cancel_pushButton)
        self.verticalLayout_2.addWidget(self.horizontalWidget)
        self.horizontalLayout_5.addWidget(self.verticalWidget1)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QtGui.QApplication.translate("Dialog", "Version Replacer", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("Dialog", "Please check the Versions that needs to be replaced", None, QtGui.QApplication.UnicodeUTF8))
        self.sequence_label.setText(QtGui.QApplication.translate("Dialog", "Sequence", None, QtGui.QApplication.UnicodeUTF8))
        self.assetType_label1.setText(QtGui.QApplication.translate("Dialog", "Version Type", None, QtGui.QApplication.UnicodeUTF8))
        self.assetType_comboBox1.setToolTip(QtGui.QApplication.translate("Dialog", "Select an asset type", None, QtGui.QApplication.UnicodeUTF8))
        self.assetType_comboBox1.setStatusTip(QtGui.QApplication.translate("Dialog", "Select an asset type", None, QtGui.QApplication.UnicodeUTF8))
        self.assetType_comboBox1.setWhatsThis(QtGui.QApplication.translate("Dialog", "Asset Type:\n"
"\n"
"Assets has types that lets you distinguish their purpose of existance. This comboBox lists the asset types that the sequence and the current host environment (MAYA, NUKE etc.) can support.", None, QtGui.QApplication.UnicodeUTF8))
        self.project_comboBox.setToolTip(QtGui.QApplication.translate("Dialog", "Select a Project", None, QtGui.QApplication.UnicodeUTF8))
        self.project_comboBox.setStatusTip(QtGui.QApplication.translate("Dialog", "Select a Project", None, QtGui.QApplication.UnicodeUTF8))
        self.project_comboBox.setWhatsThis(QtGui.QApplication.translate("Dialog", "Project:\n"
"\n"
"A project is a collection of sequences. So projects can only contain sequences. This comboBox lists the current projects on the server. If you select one it will update the available sequences for that project...", None, QtGui.QApplication.UnicodeUTF8))
        self.subName_label.setText(QtGui.QApplication.translate("Dialog", "Take Name", None, QtGui.QApplication.UnicodeUTF8))
        self.baseName_label.setText(QtGui.QApplication.translate("Dialog", "Base Name", None, QtGui.QApplication.UnicodeUTF8))
        self.sequence_comboBox.setToolTip(QtGui.QApplication.translate("Dialog", "Select a Sequence", None, QtGui.QApplication.UnicodeUTF8))
        self.sequence_comboBox.setStatusTip(QtGui.QApplication.translate("Dialog", "Select a Sequence", None, QtGui.QApplication.UnicodeUTF8))
        self.sequence_comboBox.setWhatsThis(QtGui.QApplication.translate("Dialog", "Sequence:\n"
"\n"
"Sequences are collections of folders. Each folder has a special meaning and can may contain one type of asset file. Every sequence has its own settings. So while one sequence supports some features, others may not...", None, QtGui.QApplication.UnicodeUTF8))
        self.project_label.setText(QtGui.QApplication.translate("Dialog", "Project", None, QtGui.QApplication.UnicodeUTF8))
        self.baseName_comboBox.setToolTip(QtGui.QApplication.translate("Dialog", "if the type is a shot dependent type this will be activated", None, QtGui.QApplication.UnicodeUTF8))
        self.baseName_comboBox.setStatusTip(QtGui.QApplication.translate("Dialog", "if the type is a shot dependent type this will be activated", None, QtGui.QApplication.UnicodeUTF8))
        self.baseName_comboBox.setWhatsThis(QtGui.QApplication.translate("Dialog", "Shot:\n"
"\n"
"If an asset is shot dependent, its base name is a shot string (SH001, SH010 etc. ). So, shot and base name comboBoxes are actually showing the base name of the asset, but it lets the user to separate the shot dependent asset types from shot independent types.", None, QtGui.QApplication.UnicodeUTF8))
        self.subName_comboBox.setToolTip(QtGui.QApplication.translate("Dialog", "if the type is a shot dependent type this will be activated", None, QtGui.QApplication.UnicodeUTF8))
        self.subName_comboBox.setStatusTip(QtGui.QApplication.translate("Dialog", "if the type is a shot dependent type this will be activated", None, QtGui.QApplication.UnicodeUTF8))
        self.subName_comboBox.setWhatsThis(QtGui.QApplication.translate("Dialog", "Shot:\n"
"\n"
"If an asset is shot dependent, its base name is a shot string (SH001, SH010 etc. ). So, shot and base name comboBoxes are actually showing the base name of the asset, but it lets the user to separate the shot dependent asset types from shot independent types.", None, QtGui.QApplication.UnicodeUTF8))
        self.assetFile_label.setText(QtGui.QApplication.translate("Dialog", "Asset File", None, QtGui.QApplication.UnicodeUTF8))
        self.assetFile_comboBox.setToolTip(QtGui.QApplication.translate("Dialog", "if the type is a shot dependent type this will be activated", None, QtGui.QApplication.UnicodeUTF8))
        self.assetFile_comboBox.setStatusTip(QtGui.QApplication.translate("Dialog", "if the type is a shot dependent type this will be activated", None, QtGui.QApplication.UnicodeUTF8))
        self.assetFile_comboBox.setWhatsThis(QtGui.QApplication.translate("Dialog", "Shot:\n"
"\n"
"If an asset is shot dependent, its base name is a shot string (SH001, SH010 etc. ). So, shot and base name comboBoxes are actually showing the base name of the asset, but it lets the user to separate the shot dependent asset types from shot independent types.", None, QtGui.QApplication.UnicodeUTF8))
        self.removeReplacement_pushButton.setText(QtGui.QApplication.translate("Dialog", "Remove Replacement", None, QtGui.QApplication.UnicodeUTF8))
        self.replace_pushButton.setText(QtGui.QApplication.translate("Dialog", "Replace", None, QtGui.QApplication.UnicodeUTF8))
        self.cancel_pushButton.setText(QtGui.QApplication.translate("Dialog", "Cancel", None, QtGui.QApplication.UnicodeUTF8))

