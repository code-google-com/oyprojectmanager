# -*- coding: utf-8 -*-
# Copyright (c) 2009-2012, Erkan Ozgur Yilmaz
# 
# This module is part of oyProjectManager and is released under the BSD 2
# License: http://www.opensource.org/licenses/BSD-2-Clause

import os, sys

qt_module_key = "PREFERRED_QT_MODULE"
qt_module = "PyQt4"

if os.environ.has_key(qt_module_key):
    qt_module = os.environ[qt_module_key]

if qt_module == "PySide":
    from PySide import QtGui, QtCore
    from oyProjectManager.ui import version_updater_UI_pyside as version_updater_UI
elif qt_module == "PyQt4":
    import sip
    sip.setapi('QString', 2)
    sip.setapi('QVariant', 2)
    from PyQt4 import QtGui, QtCore
    from oyProjectManager.ui import version_updater_UI_pyqt4 as version_updater_UI

def UI(environment):
    """the UI to call the dialog by itself
    """
    global app
    global mainDialog
    
#    app = singletonQApplication.QApplication(sys.argv)

    self_quit = False
    if QtGui.QApplication.instance() is None:
        app = QtGui.QApplication(sys.argv)
        self_quit = True
    else:
        app = QtGui.QApplication.instance()

    mainDialog = MainDialog(environment)
    mainDialog.show()
    #app.setStyle('Plastique')
    app.exec_()
    
    if self_quit:
        app.connect(
            app,
            QtCore.SIGNAL("lastWindowClosed()"),
            app,
            QtCore.SLOT("quit()")
        )
    
    return mainDialog

class MainDialog(QtGui.QDialog, version_updater_UI.Ui_Dialog):
    """The main dialog of the version updater system
    
    The version_tuple list consist of a Version instance and a reference
    object.
    
    For Maya environment the reference object is the PyMel Reference node,
    for other environments reference object type will be as native as it can be
    """
    
    def __init__(self, environment=None, parent=None):
        super(MainDialog, self).__init__(parent)
        self.setupUi(self)
        
        # change the window title
        self.setWindowTitle(self.windowTitle())
        
        # center to the window
        self._centerWindow()
        
        self._horizontalLabels = [
            'Versionable',
            'Type',
            'Take',
            'Current',
            'Latest Published',
            'Do Update?'
        ]
        
        self.versions_tableWidget.setHorizontalHeaderLabels(
            self._horizontalLabels
        )
        self.versions_tableWidget.versions = []

        self.setup_signals()
        
        self._version_tuple_list = []
        self._num_of_versions = 0
        
        #self._tableItems = []
        
        # setup the environment
        self.environment = environment
        
        self._do_env_read()
        self._fill_UI()
    
    def setup_signals(self):
        """sets up the signals
        """
        # SIGNALS
        # cancel button
        QtCore.QObject.connect(
            self.cancel_pushButton,
            QtCore.SIGNAL("clicked()"),
            self.close
        )
        
        # select all button
        QtCore.QObject.connect(
            self.selectAll_pushButton,
            QtCore.SIGNAL("clicked()"),
            self._select_all_versions
        )
        
        # select none button
        QtCore.QObject.connect(
            self.selectNone_pushButton,
            QtCore.SIGNAL("clicked()"),
            self._select_no_version
        )
        
        # update button
        QtCore.QObject.connect(
            self.update_pushButton,
            QtCore.SIGNAL("clicked()"),
            self.update_versions
        )
    
    def _centerWindow(self):
        """centers the window to the screen
        """
        screen = QtGui.QDesktopWidget().screenGeometry()
        size =  self.geometry()
        self.move(
            (screen.width()-size.width()) * 0.5,
            (screen.height()-size.height()) * 0.5
        )
    
    def get_version_tuple_from_environment(self):
        """gets the references from environment
        
        returns a tuple consist of an asset and the environments representation
        of the asset
        """
        return self.environment.check_referenced_versions()
    
    def get_version_tuple_list(self):
        """returns the asset tuple list
        """
        return self._version_tuple_list
    
    def set_version_tuple_list(self, assetTupleList):
        """sets the asset tuple list
        """
        self._version_tuple_list = assetTupleList
        self._num_of_versions = len(self._version_tuple_list)
    
    version_tuple_list = property(get_version_tuple_list, set_version_tuple_list)
    
    def _fill_UI(self):
        """fills the UI with the asset data
        """
        # set the row count
        self.versions_tableWidget.setRowCount(self._num_of_versions)
        self.versions_tableWidget.versions = []
        
        unpublished_versions = []
        
        for i,version_info in enumerate(self._version_tuple_list):
            version = version_info[0]
            # TODO: there is a problem about unpublished versions
            latest_published_version = version.latest_published_version()
            if latest_published_version is None:
                # just skip this one or at least warn the user
                unpublished_versions.append(version)
                continue
            
            # ------------------------------------
            # the versionable name
            item = QtGui.QTableWidgetItem(version.base_name)
            # align to left and vertical center
            item.setTextAlignment(
                QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter
            )
            self.versions_tableWidget.setItem(i, 0, item)
            
            #-------------------------------------
            # type name
            item = QtGui.QTableWidgetItem(version.type.name)
            # align to horizontal and vertical center
            item.setTextAlignment(
                QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter
            )
            self.versions_tableWidget.setItem(i, 1, item)
            
            #-------------------------------------
            # take name
            item = QtGui.QTableWidgetItem(version.take_name)
            # align to horizontal and vertical center
            item.setTextAlignment(
                QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter
            )
            self.versions_tableWidget.setItem(i, 2, item)
            
            # ------------------------------------
            # current version
            current_version_number = str(version.version_number)
            item = QtGui.QTableWidgetItem(current_version_number)
            # align to horizontal and vertical center
            item.setTextAlignment(
                QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter
            )
            self.versions_tableWidget.setItem(i, 3, item)
            
            # ------------------------------------
            # latest version
            latest_published_version_number = \
                str(version.latest_published_version().version_number)
            item = \
                QtGui.QTableWidgetItem(latest_published_version_number)
            # align to horizontal and vertical center
            item.setTextAlignment(
                QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter
            )
            self.versions_tableWidget.setItem(i, 4, item)
            # ------------------------------------
            
            # ------------------------------------
            # do update ?
            item = QtGui.QTableWidgetItem('')
            item.setTextAlignment(
                QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter
            )
            try:
                # for PyQt
                item.setCheckState(QtCore.Qt.Unchecked)
            except AttributeError:
                # for PyCharm
                item.setCheckState(0)
            self.versions_tableWidget.setItem(i, 5, item)
            # ------------------------------------
            
            self.versions_tableWidget.versions.append(version)
        
        if len(unpublished_versions):
            QtGui.QMessageBox.warning(
                self,
                "Warning",
                "The following references have no published versions:\n\n" +
                "\n".join([vers.filename for vers in unpublished_versions]) +
                "\n\nPlease publish them and re-open the current file.",
                QtGui.QMessageBox.Ok
            )
    
    def _do_env_read(self):
        """gets the asset tuple from env
        """
        self._version_tuple_list = self.get_version_tuple_from_environment()
        self._num_of_versions = len(self._version_tuple_list)
    
    def _select_all_versions(self):
        """selects all the versions in the tableWidget
        """
        #for currentItems in self._tableItems:
        #    currentItem = currentItems[3]
        #    currentItem.setCheckState(2)
        for i in range(self.versions_tableWidget.rowCount()):
            item = self.versions_tableWidget.item(i, 5)
            item.setCheckState(2)
    
    def _select_no_version(self):
        """deselects all versions in the tableWidget
        """
        #for currentItems in self._tableItems:
        #    currentItem = currentItems[3]
        #    currentItem.setCheckState(0)
        for i in range(self.versions_tableWidget.rowCount()):
            item = self.versions_tableWidget.item(i, 5)
            item.setCheckState(0)
    
    def update_versions(self):
        """updates the versions if it is checked in the UI
        """
        # get the marked versions from UI first
        marked_versions = self.get_marked_versions()
        
        # send them back to environment
        self.environment.update_versions(marked_versions)
        
        # close the interface
        self.close()
    
    def get_marked_versions(self):
        """returns the assets as tuple again, if it is checked in the interface
        """
        marked_version_list = []
        
        # find the marked versions
        for i in range(self._num_of_versions):
            checkBox_tableItem = self.versions_tableWidget.item(i, 5)
            
            if checkBox_tableItem.checkState() == 2:
                # get the ith number of the asset
                marked_version_list.append(self._version_tuple_list[i])
        
        return marked_version_list
        
