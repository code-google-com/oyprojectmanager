# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/ozgur/maya/scripts/oy-maya-scripts/oyTools/oyProjectManager/ui/assetManager.ui'
#
# Created: Sat Oct 10 11:45:04 2009
#      by: PyQt4 UI code generator 4.4.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.setWindowModality(QtCore.Qt.ApplicationModal)
        MainWindow.resize(656, 513)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(MainWindow.sizePolicy().hasHeightForWidth())
        MainWindow.setSizePolicy(sizePolicy)
        self.centralwidget = QtGui.QWidget(MainWindow)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(self.centralwidget.sizePolicy().hasHeightForWidth())
        self.centralwidget.setSizePolicy(sizePolicy)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout = QtGui.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName("verticalLayout")
        self.main_horizontalWidget = QtGui.QWidget(self.centralwidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(self.main_horizontalWidget.sizePolicy().hasHeightForWidth())
        self.main_horizontalWidget.setSizePolicy(sizePolicy)
        self.main_horizontalWidget.setObjectName("main_horizontalWidget")
        self.main_horizontalLayout = QtGui.QHBoxLayout(self.main_horizontalWidget)
        self.main_horizontalLayout.setMargin(6)
        self.main_horizontalLayout.setObjectName("main_horizontalLayout")
        self.verticalWidget1 = QtGui.QWidget(self.main_horizontalWidget)
        self.verticalWidget1.setObjectName("verticalWidget1")
        self.verticalLayout1 = QtGui.QVBoxLayout(self.verticalWidget1)
        self.verticalLayout1.setObjectName("verticalLayout1")
        self.gridWidget1 = QtGui.QWidget(self.verticalWidget1)
        self.gridWidget1.setObjectName("gridWidget1")
        self.gridLayout1 = QtGui.QGridLayout(self.gridWidget1)
        self.gridLayout1.setObjectName("gridLayout1")
        self.server_label = QtGui.QLabel(self.gridWidget1)
        self.server_label.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.server_label.setObjectName("server_label")
        self.gridLayout1.addWidget(self.server_label, 0, 0, 1, 1)
        self.server_comboBox = QtGui.QComboBox(self.gridWidget1)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.server_comboBox.sizePolicy().hasHeightForWidth())
        self.server_comboBox.setSizePolicy(sizePolicy)
        self.server_comboBox.setEditable(False)
        self.server_comboBox.setObjectName("server_comboBox")
        self.gridLayout1.addWidget(self.server_comboBox, 0, 1, 1, 1)
        self.project_label = QtGui.QLabel(self.gridWidget1)
        self.project_label.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.project_label.setObjectName("project_label")
        self.gridLayout1.addWidget(self.project_label, 2, 0, 1, 1)
        self.project_comboBox = QtGui.QComboBox(self.gridWidget1)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.project_comboBox.sizePolicy().hasHeightForWidth())
        self.project_comboBox.setSizePolicy(sizePolicy)
        self.project_comboBox.setEditable(False)
        self.project_comboBox.setObjectName("project_comboBox")
        self.gridLayout1.addWidget(self.project_comboBox, 2, 1, 1, 1)
        self.sequence_label = QtGui.QLabel(self.gridWidget1)
        self.sequence_label.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.sequence_label.setObjectName("sequence_label")
        self.gridLayout1.addWidget(self.sequence_label, 3, 0, 1, 1)
        self.sequence_comboBox = QtGui.QComboBox(self.gridWidget1)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.sequence_comboBox.sizePolicy().hasHeightForWidth())
        self.sequence_comboBox.setSizePolicy(sizePolicy)
        self.sequence_comboBox.setEditable(False)
        self.sequence_comboBox.setObjectName("sequence_comboBox")
        self.gridLayout1.addWidget(self.sequence_comboBox, 3, 1, 1, 1)
        self.assetType_label1 = QtGui.QLabel(self.gridWidget1)
        self.assetType_label1.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.assetType_label1.setObjectName("assetType_label1")
        self.gridLayout1.addWidget(self.assetType_label1, 6, 0, 1, 1)
        self.assetType_comboBox1 = QtGui.QComboBox(self.gridWidget1)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.assetType_comboBox1.sizePolicy().hasHeightForWidth())
        self.assetType_comboBox1.setSizePolicy(sizePolicy)
        self.assetType_comboBox1.setObjectName("assetType_comboBox1")
        self.gridLayout1.addWidget(self.assetType_comboBox1, 6, 1, 1, 1)
        self.shot_label1 = QtGui.QLabel(self.gridWidget1)
        self.shot_label1.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.shot_label1.setObjectName("shot_label1")
        self.gridLayout1.addWidget(self.shot_label1, 7, 0, 1, 1)
        self.shot_comboBox1 = QtGui.QComboBox(self.gridWidget1)
        self.shot_comboBox1.setEnabled(True)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.shot_comboBox1.sizePolicy().hasHeightForWidth())
        self.shot_comboBox1.setSizePolicy(sizePolicy)
        self.shot_comboBox1.setObjectName("shot_comboBox1")
        self.gridLayout1.addWidget(self.shot_comboBox1, 7, 1, 1, 1)
        self.baseName_label1 = QtGui.QLabel(self.gridWidget1)
        self.baseName_label1.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.baseName_label1.setObjectName("baseName_label1")
        self.gridLayout1.addWidget(self.baseName_label1, 8, 0, 1, 1)
        self.baseName_comboBox1 = QtGui.QComboBox(self.gridWidget1)
        self.baseName_comboBox1.setEnabled(True)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.baseName_comboBox1.sizePolicy().hasHeightForWidth())
        self.baseName_comboBox1.setSizePolicy(sizePolicy)
        self.baseName_comboBox1.setEditable(True)
        self.baseName_comboBox1.setObjectName("baseName_comboBox1")
        self.gridLayout1.addWidget(self.baseName_comboBox1, 8, 1, 1, 1)
        self.subName_label1 = QtGui.QLabel(self.gridWidget1)
        self.subName_label1.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.subName_label1.setObjectName("subName_label1")
        self.gridLayout1.addWidget(self.subName_label1, 9, 0, 1, 1)
        self.subName_comboBox1 = QtGui.QComboBox(self.gridWidget1)
        self.subName_comboBox1.setEnabled(True)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.subName_comboBox1.sizePolicy().hasHeightForWidth())
        self.subName_comboBox1.setSizePolicy(sizePolicy)
        self.subName_comboBox1.setEditable(True)
        self.subName_comboBox1.setObjectName("subName_comboBox1")
        self.gridLayout1.addWidget(self.subName_comboBox1, 9, 1, 1, 1)
        self.line = QtGui.QFrame(self.gridWidget1)
        self.line.setFrameShape(QtGui.QFrame.HLine)
        self.line.setFrameShadow(QtGui.QFrame.Sunken)
        self.line.setObjectName("line")
        self.gridLayout1.addWidget(self.line, 1, 0, 1, 2)
        self.line_2 = QtGui.QFrame(self.gridWidget1)
        self.line_2.setFrameShape(QtGui.QFrame.HLine)
        self.line_2.setFrameShadow(QtGui.QFrame.Sunken)
        self.line_2.setObjectName("line_2")
        self.gridLayout1.addWidget(self.line_2, 4, 0, 1, 2)
        self.revision_label1 = QtGui.QLabel(self.gridWidget1)
        self.revision_label1.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.revision_label1.setObjectName("revision_label1")
        self.gridLayout1.addWidget(self.revision_label1, 10, 0, 1, 1)
        self.revision_horizontalWidget = QtGui.QWidget(self.gridWidget1)
        self.revision_horizontalWidget.setObjectName("revision_horizontalWidget")
        self.revision_horizontalLayout = QtGui.QHBoxLayout(self.revision_horizontalWidget)
        self.revision_horizontalLayout.setMargin(0)
        self.revision_horizontalLayout.setObjectName("revision_horizontalLayout")
        self.revision_spinBox = QtGui.QSpinBox(self.revision_horizontalWidget)
        self.revision_spinBox.setMinimumSize(QtCore.QSize(50, 0))
        self.revision_spinBox.setObjectName("revision_spinBox")
        self.revision_horizontalLayout.addWidget(self.revision_spinBox)
        self.revision_pushButton = QtGui.QPushButton(self.revision_horizontalWidget)
        self.revision_pushButton.setMinimumSize(QtCore.QSize(111, 0))
        self.revision_pushButton.setObjectName("revision_pushButton")
        self.revision_horizontalLayout.addWidget(self.revision_pushButton)
        self.gridLayout1.addWidget(self.revision_horizontalWidget, 10, 1, 1, 1)
        self.version_label1 = QtGui.QLabel(self.gridWidget1)
        self.version_label1.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.version_label1.setObjectName("version_label1")
        self.gridLayout1.addWidget(self.version_label1, 11, 0, 1, 1)
        self.version_horizontalWidget = QtGui.QWidget(self.gridWidget1)
        self.version_horizontalWidget.setObjectName("version_horizontalWidget")
        self.version_horizontalLayout = QtGui.QHBoxLayout(self.version_horizontalWidget)
        self.version_horizontalLayout.setMargin(0)
        self.version_horizontalLayout.setObjectName("version_horizontalLayout")
        self.version_spinBox = QtGui.QSpinBox(self.version_horizontalWidget)
        self.version_spinBox.setMinimumSize(QtCore.QSize(50, 0))
        self.version_spinBox.setMinimum(1)
        self.version_spinBox.setMaximum(99999999)
        self.version_spinBox.setObjectName("version_spinBox")
        self.version_horizontalLayout.addWidget(self.version_spinBox)
        self.version_pushButton = QtGui.QPushButton(self.version_horizontalWidget)
        self.version_pushButton.setMinimumSize(QtCore.QSize(111, 0))
        self.version_pushButton.setObjectName("version_pushButton")
        self.version_horizontalLayout.addWidget(self.version_pushButton)
        self.gridLayout1.addWidget(self.version_horizontalWidget, 11, 1, 1, 1)
        self.user_label1 = QtGui.QLabel(self.gridWidget1)
        self.user_label1.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.user_label1.setObjectName("user_label1")
        self.gridLayout1.addWidget(self.user_label1, 12, 0, 1, 1)
        self.user_comboBox1 = QtGui.QComboBox(self.gridWidget1)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.user_comboBox1.sizePolicy().hasHeightForWidth())
        self.user_comboBox1.setSizePolicy(sizePolicy)
        self.user_comboBox1.setObjectName("user_comboBox1")
        self.gridLayout1.addWidget(self.user_comboBox1, 12, 1, 1, 1)
        self.note_label1 = QtGui.QLabel(self.gridWidget1)
        self.note_label1.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.note_label1.setObjectName("note_label1")
        self.gridLayout1.addWidget(self.note_label1, 13, 0, 1, 1)
        self.note_lineEdit1 = QtGui.QLineEdit(self.gridWidget1)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.note_lineEdit1.sizePolicy().hasHeightForWidth())
        self.note_lineEdit1.setSizePolicy(sizePolicy)
        self.note_lineEdit1.setObjectName("note_lineEdit1")
        self.gridLayout1.addWidget(self.note_lineEdit1, 13, 1, 1, 1)
        self.verticalLayout1.addWidget(self.gridWidget1)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout1.addItem(spacerItem)
        self.saveButtons_horizontalWidget = QtGui.QWidget(self.verticalWidget1)
        self.saveButtons_horizontalWidget.setObjectName("saveButtons_horizontalWidget")
        self.saveCanel_horizontalLayout = QtGui.QHBoxLayout(self.saveButtons_horizontalWidget)
        self.saveCanel_horizontalLayout.setObjectName("saveCanel_horizontalLayout")
        self.save_button = QtGui.QPushButton(self.saveButtons_horizontalWidget)
        self.save_button.setObjectName("save_button")
        self.saveCanel_horizontalLayout.addWidget(self.save_button)
        self.export_button = QtGui.QPushButton(self.saveButtons_horizontalWidget)
        self.export_button.setObjectName("export_button")
        self.saveCanel_horizontalLayout.addWidget(self.export_button)
        self.verticalLayout1.addWidget(self.saveButtons_horizontalWidget)
        self.main_horizontalLayout.addWidget(self.verticalWidget1)
        self.verticalWidget2 = QtGui.QWidget(self.main_horizontalWidget)
        self.verticalWidget2.setObjectName("verticalWidget2")
        self.verticalLayout2 = QtGui.QVBoxLayout(self.verticalWidget2)
        self.verticalLayout2.setMargin(6)
        self.verticalLayout2.setObjectName("verticalLayout2")
        self.assets_listWidget1 = QtGui.QListWidget(self.verticalWidget2)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(self.assets_listWidget1.sizePolicy().hasHeightForWidth())
        self.assets_listWidget1.setSizePolicy(sizePolicy)
        self.assets_listWidget1.setObjectName("assets_listWidget1")
        self.verticalLayout2.addWidget(self.assets_listWidget1)
        self.openButtons_horizontalWidget = QtGui.QWidget(self.verticalWidget2)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.openButtons_horizontalWidget.sizePolicy().hasHeightForWidth())
        self.openButtons_horizontalWidget.setSizePolicy(sizePolicy)
        self.openButtons_horizontalWidget.setObjectName("openButtons_horizontalWidget")
        self.openButtons_horizontalLayout = QtGui.QHBoxLayout(self.openButtons_horizontalWidget)
        self.openButtons_horizontalLayout.setObjectName("openButtons_horizontalLayout")
        self.open_button = QtGui.QPushButton(self.openButtons_horizontalWidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.open_button.sizePolicy().hasHeightForWidth())
        self.open_button.setSizePolicy(sizePolicy)
        self.open_button.setObjectName("open_button")
        self.openButtons_horizontalLayout.addWidget(self.open_button)
        self.reference_button = QtGui.QPushButton(self.openButtons_horizontalWidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.reference_button.sizePolicy().hasHeightForWidth())
        self.reference_button.setSizePolicy(sizePolicy)
        self.reference_button.setObjectName("reference_button")
        self.openButtons_horizontalLayout.addWidget(self.reference_button)
        self.import_button = QtGui.QPushButton(self.openButtons_horizontalWidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.import_button.sizePolicy().hasHeightForWidth())
        self.import_button.setSizePolicy(sizePolicy)
        self.import_button.setObjectName("import_button")
        self.openButtons_horizontalLayout.addWidget(self.import_button)
        self.cancel_button2 = QtGui.QPushButton(self.openButtons_horizontalWidget)
        self.cancel_button2.setObjectName("cancel_button2")
        self.openButtons_horizontalLayout.addWidget(self.cancel_button2)
        self.verticalLayout2.addWidget(self.openButtons_horizontalWidget)
        self.main_horizontalLayout.addWidget(self.verticalWidget2)
        self.verticalLayout.addWidget(self.main_horizontalWidget)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtGui.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 656, 23))
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.MinimumExpanding, QtGui.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.menubar.sizePolicy().hasHeightForWidth())
        self.menubar.setSizePolicy(sizePolicy)
        self.menubar.setObjectName("menubar")
        self.menuFile = QtGui.QMenu(self.menubar)
        self.menuFile.setObjectName("menuFile")
        self.menuHelp = QtGui.QMenu(self.menubar)
        self.menuHelp.setObjectName("menuHelp")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtGui.QStatusBar(MainWindow)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.statusbar.sizePolicy().hasHeightForWidth())
        self.statusbar.setSizePolicy(sizePolicy)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.actionOpen_Settings = QtGui.QAction(MainWindow)
        self.actionOpen_Settings.setObjectName("actionOpen_Settings")
        self.actionAbout = QtGui.QAction(MainWindow)
        self.actionAbout.setObjectName("actionAbout")
        self.actionSave_Asset = QtGui.QAction(MainWindow)
        self.actionSave_Asset.setObjectName("actionSave_Asset")
        self.actionSave_Settings = QtGui.QAction(MainWindow)
        self.actionSave_Settings.setObjectName("actionSave_Settings")
        self.actionExit = QtGui.QAction(MainWindow)
        self.actionExit.setObjectName("actionExit")
        self.menuFile.addAction(self.actionOpen_Settings)
        self.menuFile.addAction(self.actionSave_Asset)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionSave_Settings)
        self.menuFile.addAction(self.actionExit)
        self.menuHelp.addAction(self.actionAbout)
        self.menuHelp.addSeparator()
        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuHelp.menuAction())

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)
        MainWindow.setTabOrder(self.server_comboBox, self.project_comboBox)
        MainWindow.setTabOrder(self.project_comboBox, self.sequence_comboBox)
        MainWindow.setTabOrder(self.sequence_comboBox, self.revision_pushButton)
        MainWindow.setTabOrder(self.revision_pushButton, self.version_spinBox)
        MainWindow.setTabOrder(self.version_spinBox, self.version_pushButton)
        MainWindow.setTabOrder(self.version_pushButton, self.save_button)
        MainWindow.setTabOrder(self.save_button, self.export_button)
        MainWindow.setTabOrder(self.export_button, self.open_button)
        MainWindow.setTabOrder(self.open_button, self.reference_button)
        MainWindow.setTabOrder(self.reference_button, self.import_button)
        MainWindow.setTabOrder(self.import_button, self.cancel_button2)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QtGui.QApplication.translate("MainWindow", "Asset Manager", None, QtGui.QApplication.UnicodeUTF8))
        self.server_label.setText(QtGui.QApplication.translate("MainWindow", "Server", None, QtGui.QApplication.UnicodeUTF8))
        self.server_comboBox.setToolTip(QtGui.QApplication.translate("MainWindow", "Select a Server", None, QtGui.QApplication.UnicodeUTF8))
        self.server_comboBox.setStatusTip(QtGui.QApplication.translate("MainWindow", "Select a Server", None, QtGui.QApplication.UnicodeUTF8))
        self.server_comboBox.setWhatsThis(QtGui.QApplication.translate("MainWindow", "Server:\n"
"\n"
"Servers are the places that the main project folders are saved. For now there is only one supported server. In the future that can be expanded to multiple servers...", None, QtGui.QApplication.UnicodeUTF8))
        self.project_label.setText(QtGui.QApplication.translate("MainWindow", "Project", None, QtGui.QApplication.UnicodeUTF8))
        self.project_comboBox.setToolTip(QtGui.QApplication.translate("MainWindow", "Select a Project", None, QtGui.QApplication.UnicodeUTF8))
        self.project_comboBox.setStatusTip(QtGui.QApplication.translate("MainWindow", "Select a Project", None, QtGui.QApplication.UnicodeUTF8))
        self.project_comboBox.setWhatsThis(QtGui.QApplication.translate("MainWindow", "Project:\n"
"\n"
"A project is a collection of sequences. So projects can only contain sequences. This comboBox lists the current projects on the server. If you select one it will update the available sequences for that project...", None, QtGui.QApplication.UnicodeUTF8))
        self.sequence_label.setText(QtGui.QApplication.translate("MainWindow", "Sequence", None, QtGui.QApplication.UnicodeUTF8))
        self.sequence_comboBox.setToolTip(QtGui.QApplication.translate("MainWindow", "Select a Sequence", None, QtGui.QApplication.UnicodeUTF8))
        self.sequence_comboBox.setStatusTip(QtGui.QApplication.translate("MainWindow", "Select a Sequence", None, QtGui.QApplication.UnicodeUTF8))
        self.sequence_comboBox.setWhatsThis(QtGui.QApplication.translate("MainWindow", "Sequence:\n"
"\n"
"Sequences are collections of folders. Each folder has a special meaning and can may contain one type of asset file. Every sequence has its own settings. So while one sequence supports some features, others may not...", None, QtGui.QApplication.UnicodeUTF8))
        self.assetType_label1.setText(QtGui.QApplication.translate("MainWindow", "Asset Type", None, QtGui.QApplication.UnicodeUTF8))
        self.assetType_comboBox1.setToolTip(QtGui.QApplication.translate("MainWindow", "Select an asset type", None, QtGui.QApplication.UnicodeUTF8))
        self.assetType_comboBox1.setStatusTip(QtGui.QApplication.translate("MainWindow", "Select an asset type", None, QtGui.QApplication.UnicodeUTF8))
        self.assetType_comboBox1.setWhatsThis(QtGui.QApplication.translate("MainWindow", "Asset Type:\n"
"\n"
"Assets has types that lets you distinguish their purpose of existance. This comboBox lists the asset types that the sequence and the current host environment (MAYA, NUKE etc.) can support.", None, QtGui.QApplication.UnicodeUTF8))
        self.shot_label1.setText(QtGui.QApplication.translate("MainWindow", "Shot", None, QtGui.QApplication.UnicodeUTF8))
        self.shot_comboBox1.setToolTip(QtGui.QApplication.translate("MainWindow", "if the type is a shot dependent type this will be activated", None, QtGui.QApplication.UnicodeUTF8))
        self.shot_comboBox1.setStatusTip(QtGui.QApplication.translate("MainWindow", "if the type is a shot dependent type this will be activated", None, QtGui.QApplication.UnicodeUTF8))
        self.shot_comboBox1.setWhatsThis(QtGui.QApplication.translate("MainWindow", "Shot:\n"
"\n"
"If an asset is shot dependent, its base name is a shot string (SH001, SH010 etc. ). So, shot and base name comboBoxes are actually showing the base name of the asset, but it lets the user to separate the shot dependent asset types from shot independent types.", None, QtGui.QApplication.UnicodeUTF8))
        self.baseName_label1.setText(QtGui.QApplication.translate("MainWindow", "Base Name", None, QtGui.QApplication.UnicodeUTF8))
        self.baseName_comboBox1.setToolTip(QtGui.QApplication.translate("MainWindow", "for shot independent types enter or select a baseName", None, QtGui.QApplication.UnicodeUTF8))
        self.baseName_comboBox1.setStatusTip(QtGui.QApplication.translate("MainWindow", "for shot independent types enter or select a baseName", None, QtGui.QApplication.UnicodeUTF8))
        self.baseName_comboBox1.setWhatsThis(QtGui.QApplication.translate("MainWindow", "Base Name:\n"
"\n"
"This shows the base name of an asset", None, QtGui.QApplication.UnicodeUTF8))
        self.subName_label1.setText(QtGui.QApplication.translate("MainWindow", "Sub Name", None, QtGui.QApplication.UnicodeUTF8))
        self.subName_comboBox1.setToolTip(QtGui.QApplication.translate("MainWindow", "if the project supports SubName field, you can enter or select a subName", None, QtGui.QApplication.UnicodeUTF8))
        self.subName_comboBox1.setStatusTip(QtGui.QApplication.translate("MainWindow", "if the project supports SubName field, you can enter or select a subName", None, QtGui.QApplication.UnicodeUTF8))
        self.subName_comboBox1.setWhatsThis(QtGui.QApplication.translate("MainWindow", "Sub Name:\n"
"\n"
"Sub name field is introduced with this new version. Its main purpose is to let the users work on the same shot dependent assets togather. By default the field will be set to MAIN...", None, QtGui.QApplication.UnicodeUTF8))
        self.revision_label1.setText(QtGui.QApplication.translate("MainWindow", "Revision", None, QtGui.QApplication.UnicodeUTF8))
        self.revision_spinBox.setToolTip(QtGui.QApplication.translate("MainWindow", "increase it when the asset needs a revision", None, QtGui.QApplication.UnicodeUTF8))
        self.revision_spinBox.setStatusTip(QtGui.QApplication.translate("MainWindow", "increase it when the asset needs a revision", None, QtGui.QApplication.UnicodeUTF8))
        self.revision_spinBox.setWhatsThis(QtGui.QApplication.translate("MainWindow", "Revision Number:\n"
"\n"
"Revision numbers represents the milestones in the development of this asset. Generally it is increased when something big is changed in the asset.", None, QtGui.QApplication.UnicodeUTF8))
        self.revision_pushButton.setToolTip(QtGui.QApplication.translate("MainWindow", "gets the latest revision number", None, QtGui.QApplication.UnicodeUTF8))
        self.revision_pushButton.setStatusTip(QtGui.QApplication.translate("MainWindow", "gets the latest revision number", None, QtGui.QApplication.UnicodeUTF8))
        self.revision_pushButton.setText(QtGui.QApplication.translate("MainWindow", "Lastest Revision", None, QtGui.QApplication.UnicodeUTF8))
        self.version_label1.setText(QtGui.QApplication.translate("MainWindow", "Version", None, QtGui.QApplication.UnicodeUTF8))
        self.version_spinBox.setToolTip(QtGui.QApplication.translate("MainWindow", "it is automatically increased by 1", None, QtGui.QApplication.UnicodeUTF8))
        self.version_spinBox.setStatusTip(QtGui.QApplication.translate("MainWindow", "it is automatically increased by 1", None, QtGui.QApplication.UnicodeUTF8))
        self.version_spinBox.setWhatsThis(QtGui.QApplication.translate("MainWindow", "Version Number:\n"
"\n"
"Any incarnation of an asset should be have different version numbers.", None, QtGui.QApplication.UnicodeUTF8))
        self.version_pushButton.setToolTip(QtGui.QApplication.translate("MainWindow", "gets the latest version number", None, QtGui.QApplication.UnicodeUTF8))
        self.version_pushButton.setStatusTip(QtGui.QApplication.translate("MainWindow", "gets the latest version number", None, QtGui.QApplication.UnicodeUTF8))
        self.version_pushButton.setText(QtGui.QApplication.translate("MainWindow", "Latest Version", None, QtGui.QApplication.UnicodeUTF8))
        self.user_label1.setText(QtGui.QApplication.translate("MainWindow", "User", None, QtGui.QApplication.UnicodeUTF8))
        self.user_comboBox1.setToolTip(QtGui.QApplication.translate("MainWindow", "select your user initials", None, QtGui.QApplication.UnicodeUTF8))
        self.user_comboBox1.setStatusTip(QtGui.QApplication.translate("MainWindow", "select your user initials", None, QtGui.QApplication.UnicodeUTF8))
        self.user_comboBox1.setWhatsThis(QtGui.QApplication.translate("MainWindow", "User Initials:\n"
"\n"
"Select your user initials from the list, so anybody can understand who created this version of the asset...", None, QtGui.QApplication.UnicodeUTF8))
        self.note_label1.setText(QtGui.QApplication.translate("MainWindow", "Note", None, QtGui.QApplication.UnicodeUTF8))
        self.note_lineEdit1.setToolTip(QtGui.QApplication.translate("MainWindow", "it is a limited field, try to keep it brief", None, QtGui.QApplication.UnicodeUTF8))
        self.note_lineEdit1.setStatusTip(QtGui.QApplication.translate("MainWindow", "it is a limited field, try to keep it brief", None, QtGui.QApplication.UnicodeUTF8))
        self.note_lineEdit1.setWhatsThis(QtGui.QApplication.translate("MainWindow", "Note:\n"
"\n"
"You can use this field to leave little but important messages here... It is limited with 30 characters...", None, QtGui.QApplication.UnicodeUTF8))
        self.save_button.setToolTip(QtGui.QApplication.translate("MainWindow", "Saves the asset to the server", None, QtGui.QApplication.UnicodeUTF8))
        self.save_button.setStatusTip(QtGui.QApplication.translate("MainWindow", "Saves the asset to the server", None, QtGui.QApplication.UnicodeUTF8))
        self.save_button.setWhatsThis(QtGui.QApplication.translate("MainWindow", "Save:\n"
"\n"
"Saves the asset to the server", None, QtGui.QApplication.UnicodeUTF8))
        self.save_button.setText(QtGui.QApplication.translate("MainWindow", "Save", None, QtGui.QApplication.UnicodeUTF8))
        self.export_button.setToolTip(QtGui.QApplication.translate("MainWindow", "Exports the Selected items as a new asset", None, QtGui.QApplication.UnicodeUTF8))
        self.export_button.setStatusTip(QtGui.QApplication.translate("MainWindow", "Exports the Selected items as a new asset", None, QtGui.QApplication.UnicodeUTF8))
        self.export_button.setWhatsThis(QtGui.QApplication.translate("MainWindow", "Export:\n"
"\n"
"Exports the selected content to the server as an asset", None, QtGui.QApplication.UnicodeUTF8))
        self.export_button.setText(QtGui.QApplication.translate("MainWindow", "Export", None, QtGui.QApplication.UnicodeUTF8))
        self.assets_listWidget1.setToolTip(QtGui.QApplication.translate("MainWindow", "Lists all the versions of the current asset", None, QtGui.QApplication.UnicodeUTF8))
        self.assets_listWidget1.setStatusTip(QtGui.QApplication.translate("MainWindow", "Lists all the versions of the current asset", None, QtGui.QApplication.UnicodeUTF8))
        self.assets_listWidget1.setWhatsThis(QtGui.QApplication.translate("MainWindow", "Asset List:\n"
"\n"
"All versions of the currently selected asset will be listed here...", None, QtGui.QApplication.UnicodeUTF8))
        self.open_button.setToolTip(QtGui.QApplication.translate("MainWindow", "Opens the selected asset", None, QtGui.QApplication.UnicodeUTF8))
        self.open_button.setStatusTip(QtGui.QApplication.translate("MainWindow", "Opens the selected asset", None, QtGui.QApplication.UnicodeUTF8))
        self.open_button.setWhatsThis(QtGui.QApplication.translate("MainWindow", "Open:\n"
"\n"
"Opens the current selected asset in the host application", None, QtGui.QApplication.UnicodeUTF8))
        self.open_button.setText(QtGui.QApplication.translate("MainWindow", "Open", None, QtGui.QApplication.UnicodeUTF8))
        self.reference_button.setToolTip(QtGui.QApplication.translate("MainWindow", "References the asset tho the current scene (Maya only)", None, QtGui.QApplication.UnicodeUTF8))
        self.reference_button.setStatusTip(QtGui.QApplication.translate("MainWindow", "References the asset tho the current scene (Maya only)", None, QtGui.QApplication.UnicodeUTF8))
        self.reference_button.setWhatsThis(QtGui.QApplication.translate("MainWindow", "Reference:\n"
"\n"
"References the asset to the current environment in the host application. For now just MAYA supports referencing, but in near future NUKE will have too...", None, QtGui.QApplication.UnicodeUTF8))
        self.reference_button.setText(QtGui.QApplication.translate("MainWindow", "Reference", None, QtGui.QApplication.UnicodeUTF8))
        self.import_button.setToolTip(QtGui.QApplication.translate("MainWindow", "Imports the contents to the current scene", None, QtGui.QApplication.UnicodeUTF8))
        self.import_button.setStatusTip(QtGui.QApplication.translate("MainWindow", "Imports the contents to the current scene", None, QtGui.QApplication.UnicodeUTF8))
        self.import_button.setWhatsThis(QtGui.QApplication.translate("MainWindow", "Import:\n"
"\n"
"Imports the content of the selected asset to the current environment in the host application...", None, QtGui.QApplication.UnicodeUTF8))
        self.import_button.setText(QtGui.QApplication.translate("MainWindow", "Import", None, QtGui.QApplication.UnicodeUTF8))
        self.cancel_button2.setToolTip(QtGui.QApplication.translate("MainWindow", "Quits without doing anything", None, QtGui.QApplication.UnicodeUTF8))
        self.cancel_button2.setStatusTip(QtGui.QApplication.translate("MainWindow", "Quits without doing anything", None, QtGui.QApplication.UnicodeUTF8))
        self.cancel_button2.setWhatsThis(QtGui.QApplication.translate("MainWindow", "Cancel:\n"
"\n"
"Just quits the application without doing anything", None, QtGui.QApplication.UnicodeUTF8))
        self.cancel_button2.setText(QtGui.QApplication.translate("MainWindow", "Cancel", None, QtGui.QApplication.UnicodeUTF8))
        self.menuFile.setTitle(QtGui.QApplication.translate("MainWindow", "File", None, QtGui.QApplication.UnicodeUTF8))
        self.menuHelp.setTitle(QtGui.QApplication.translate("MainWindow", "Help", None, QtGui.QApplication.UnicodeUTF8))
        self.actionOpen_Settings.setText(QtGui.QApplication.translate("MainWindow", "Open Asset", None, QtGui.QApplication.UnicodeUTF8))
        self.actionAbout.setText(QtGui.QApplication.translate("MainWindow", "About oyProjectManager", None, QtGui.QApplication.UnicodeUTF8))
        self.actionSave_Asset.setText(QtGui.QApplication.translate("MainWindow", "Save Asset", None, QtGui.QApplication.UnicodeUTF8))
        self.actionSave_Settings.setText(QtGui.QApplication.translate("MainWindow", "Save Settings", None, QtGui.QApplication.UnicodeUTF8))
        self.actionExit.setText(QtGui.QApplication.translate("MainWindow", "Quit", None, QtGui.QApplication.UnicodeUTF8))

