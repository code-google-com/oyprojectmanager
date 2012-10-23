# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/eoyilmaz/Documents/development/oyProjectManager/oyProjectManager/ui/shot_editor.ui'
#
# Created: Fri Jun  8 17:40:15 2012
#      by: pyside-uic 0.2.13 running on PySide 1.1.0
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(381, 399)
        self.verticalLayout = QtGui.QVBoxLayout(Dialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.label = QtGui.QLabel(Dialog)
        self.label.setObjectName("label")
        self.horizontalLayout_2.addWidget(self.label)
        self.shot_name_label = QtGui.QLabel(Dialog)
        self.shot_name_label.setObjectName("shot_name_label")
        self.horizontalLayout_2.addWidget(self.shot_name_label)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.gridLayout = QtGui.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.frame_range_label = QtGui.QLabel(Dialog)
        self.frame_range_label.setObjectName("frame_range_label")
        self.gridLayout.addWidget(self.frame_range_label, 0, 0, 1, 1)
        self.start_frame_spinBox = QtGui.QSpinBox(Dialog)
        self.start_frame_spinBox.setMaximum(9999)
        self.start_frame_spinBox.setObjectName("start_frame_spinBox")
        self.gridLayout.addWidget(self.start_frame_spinBox, 0, 1, 1, 1)
        self.end_frame_spinBox = QtGui.QSpinBox(Dialog)
        self.end_frame_spinBox.setMaximum(9999)
        self.end_frame_spinBox.setObjectName("end_frame_spinBox")
        self.gridLayout.addWidget(self.end_frame_spinBox, 0, 2, 1, 1)
        self.handle_at_start_spinBox = QtGui.QSpinBox(Dialog)
        self.handle_at_start_spinBox.setMaximum(9999)
        self.handle_at_start_spinBox.setObjectName("handle_at_start_spinBox")
        self.gridLayout.addWidget(self.handle_at_start_spinBox, 1, 1, 1, 1)
        self.handle_at_end_spinBox = QtGui.QSpinBox(Dialog)
        self.handle_at_end_spinBox.setMaximum(9999)
        self.handle_at_end_spinBox.setObjectName("handle_at_end_spinBox")
        self.gridLayout.addWidget(self.handle_at_end_spinBox, 1, 2, 1, 1)
        self.handles_label = QtGui.QLabel(Dialog)
        self.handles_label.setObjectName("handles_label")
        self.gridLayout.addWidget(self.handles_label, 1, 0, 1, 1)
        self.verticalLayout.addLayout(self.gridLayout)
        self.upload_thumbnail_pushButton = QtGui.QPushButton(Dialog)
        self.upload_thumbnail_pushButton.setObjectName("upload_thumbnail_pushButton")
        self.verticalLayout.addWidget(self.upload_thumbnail_pushButton)
        self.thumbnail_graphicsView = QtGui.QGraphicsView(Dialog)
        self.thumbnail_graphicsView.setObjectName("thumbnail_graphicsView")
        self.verticalLayout.addWidget(self.thumbnail_graphicsView)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        spacerItem1 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem1)
        self.buttonBox = QtGui.QDialogButtonBox(Dialog)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.horizontalLayout.addWidget(self.buttonBox)
        self.verticalLayout.addLayout(self.horizontalLayout)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QtGui.QApplication.translate("Dialog", "Dialog", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("Dialog", "Editing Shot:", None, QtGui.QApplication.UnicodeUTF8))
        self.shot_name_label.setText(QtGui.QApplication.translate("Dialog", "TextLabel", None, QtGui.QApplication.UnicodeUTF8))
        self.frame_range_label.setText(QtGui.QApplication.translate("Dialog", "Range", None, QtGui.QApplication.UnicodeUTF8))
        self.handles_label.setText(QtGui.QApplication.translate("Dialog", "Handles", None, QtGui.QApplication.UnicodeUTF8))
        self.upload_thumbnail_pushButton.setText(QtGui.QApplication.translate("Dialog", "Upload Thumbnail...", None, QtGui.QApplication.UnicodeUTF8))

