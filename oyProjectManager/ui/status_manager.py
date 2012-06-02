# -*- coding: utf-8 -*-
# Copyright (c) 2009-2012, Erkan Ozgur Yilmaz
# 
# This module is part of oyProjectManager and is released under the BSD 2
# License: http://www.opensource.org/licenses/BSD-2-Clause

import os
import sys
import logging
from sqlalchemy.sql.expression import distinct, func

from oyProjectManager import config, db
from oyProjectManager.core.models import (Asset, Project, Sequence, Repository,
                                          Version, VersionType, Shot, User,
                                          VersionTypeEnvironments)

logger = logging.getLogger('beaker.container')
logger.setLevel(logging.WARNING)

# create a logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)

conf = config.Config()

qt_module_key = "PREFERRED_QT_MODULE"
qt_module = "PyQt4"

if os.environ.has_key(qt_module_key):
    qt_module = os.environ[qt_module_key]

if qt_module == "PySide":
    from PySide import QtGui, QtCore
    from oyProjectManager.ui import status_manager_UI_pyside as status_manager_UI
elif qt_module == "PyQt4":
    import sip
    sip.setapi('QString', 2)
    sip.setapi('QVariant', 2)
    from PyQt4 import QtGui, QtCore
    from oyProjectManager.ui import status_manager_UI_pyqt4 as status_manager_UI

def UI():
    """the UI to call the dialog by itself
    """
    global app
    global mainDialog
    
#    app = singletonQApplication.QApplication()

    self_quit = False
    if QtGui.QApplication.instance() is None:
        app = QtGui.QApplication(sys.argv)
        self_quit = True
    else:
        app = QtGui.QApplication.instance()
    
    mainDialog = MainDialog()
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

class MainDialog(QtGui.QDialog, status_manager_UI.Ui_Dialog):
    """Lets the users to view the status of the assets and shots in one place
    """
    
    def __init__(self, parent=None):
        super(MainDialog, self).__init__(parent)
        self.setupUi(self)
        
        # setup the database
        if db.session is None:
            db.setup()
        
        # data attributes
        self.projects_comboBox.projects = []
        
        self.setup_signals()
        self.setup_defaults()
    
    def setup_signals(self):
        """sets the signals up
        """
        
        # close button
        QtCore.QObject.connect(
            self.close_pushButton,
            QtCore.SIGNAL("clicked()"),
            self.close
        )
        
        # projects_comboBox
        QtCore.QObject.connect(
            self.projects_comboBox,
            QtCore.SIGNAL("currentIndexChanged(int)"),
            self.project_changed
        )
        
        # tabWidget
        QtCore.QObject.connect(
            self.tabWidget,
            QtCore.SIGNAL("currentChanged(int)"),
            self.tabWidget_changed
        )
        
        # TODO: add a right mouse context menu to the items on the list
    
    def setup_defaults(self):
        """sets the defaults
        """
        # fill the projects
        projects = db.query(Project)\
            .filter(Project.active==True)\
            .order_by(Project.name)\
            .all()
        
        self.projects_comboBox.addItems(
            map(lambda x: x.name, projects)
        )
        self.projects_comboBox.projects = projects
        self.projects_comboBox.setCurrentIndex(0)
        
        self.fill_assets_tableWidget()
    
    def get_current_project(self):
        """Returns the currently selected project instance in the
        projects_comboBox
        :return: :class:`~oyProjectManager.core.models.Project` instance
        """
        index = self.projects_comboBox.currentIndex()
        try:
            return self.projects_comboBox.projects[index]
        except IndexError:
            return None
    
    def project_changed(self):
        """runs when selection in projects_comboBox changed
        """
        self.tabWidget_changed()
    
    def tabWidget_changed(self):
        
        if self.tabWidget.currentIndex == 0: # update assets
            # update the assets_tableWidget
            self.fill_asset_tableWidget()
        else:
            # update the shots_tableWidget
            self.fill_shots_tableWidget()
    
    def fill_assets_tableWidget(self):
        """fills the asset_tableWidget
        """
        asset_vtypes = db.query(VersionType)\
            .filter(VersionType.type_for=='Asset')\
            .order_by(VersionType.name)\
            .all()
        
        asset_vtype_codes = map(lambda x: x.code, asset_vtypes)
        
        labels = ['Type', 'Name']
        labels.extend(map(lambda x: x.code, asset_vtypes))
        
        logger.debug('asset_tableWidget.labels: %s' % labels)
        
        self.assets_tableWidget.setColumnCount(len(labels))
        self.assets_tableWidget.setHorizontalHeaderLabels(labels)
        
        # get the project
        project = self.get_current_project()
        
        if project is None:
            return
        
        # get all the assets for the project
        assets = db.query(Asset)\
            .filter(Asset.project==project)\
            .order_by(Asset.type)\
            .all()
        
        # feed the assets to the list
        self.assets_tableWidget.setRowCount(len(assets))
        
        row = 0
        for asset in assets:
            # add the asset type to the first column
            column = 0
            item = QtGui.QTableWidgetItem(asset.type)
            item.setTextAlignment(0x0004 | 0x0080)
            self.assets_tableWidget.setItem(row, column, item)
            
            # add the asset name to the second column
            column += 1
            item = QtGui.QTableWidgetItem(asset.name)
            item.setTextAlignment(0x0004 | 0x0080)
            self.assets_tableWidget.setItem(row, column, item)
            
            #for type_code in type_codes:
            for type_code in asset_vtype_codes:
                column += 1
                # just consider the MAIN take
                
                # get the latest version of that type and take
                version = db.query(Version)\
                    .join(VersionType)\
                    .filter(Version.version_of==asset)\
                    .filter(Version.type_id==VersionType.id)\
                    .filter(VersionType.code==type_code)\
                    .filter(Version.take_name==conf.default_take_name)\
                    .order_by(Version.version_number.desc())\
                    .first()
                
                if version:
                    # mark the status of that type in that take
                    item = QtGui.QTableWidgetItem(version.status)
                    item.setTextAlignment(0x0004 | 0x0080)
                    
                    # set the color according to status
                    index = conf.status_list.index(version.status)
                    bgcolor = conf.status_bg_colors[index]
                    fgcolor = conf.status_fg_colors[index]
                    
                    bg = item.background()
                    bg.setColor(QtGui.QColor(*bgcolor))
                    item.setBackground(bg)
                    
                    fg = item.foreground()
                    fg.setColor(QtGui.QColor(*fgcolor))
                    item.setForeground(fg)
                    
                    item.setBackgroundColor(QtGui.QColor(*bgcolor))
                    
                else:
                    # set the background color to black
                    item = QtGui.QTableWidgetItem('N/A')
                    bg = item.background()
                    bg.setColor(QtGui.QColor(0, 0, 0))
                    item.setBackground(bg)
                    
                    item.setBackgroundColor(QtGui.QColor(0, 0, 0))
                
                self.assets_tableWidget.setItem(row, column, item)

            row += 1

        self.assets_tableWidget.resizeColumnsToContents()

    def fill_shots_tableWidget(self):
        """fills the shots_tableWidget
        """
        shot_vtypes = db.query(VersionType)\
            .filter(VersionType.type_for=='Shot')\
            .order_by(VersionType.name)\
            .all()
        
        shot_vtype_codes = map(lambda x: x.code, shot_vtypes)
        
        labels = ['Sequence', 'Number']
        labels.extend(map(lambda x: x.code, shot_vtypes))
        
        #logger.debug('shot_tableWidget.labels: %s' % labels)
        
        self.shots_tableWidget.setColumnCount(len(labels))
        self.shots_tableWidget.setHorizontalHeaderLabels(labels)
        
        # get the project
        project = self.get_current_project()
        
        if project is None:
            return
        
        # get all the shots for the sequence
        
        sequences = db.query(Sequence)\
            .filter(Sequence.project==project)\
            .order_by(Sequence.name)\
            .all()
        
        shot_count = db.query(func.count(Shot.id))\
            .join(Sequence)\
            .filter(Sequence.id==Shot.sequence_id)\
            .filter(Sequence.project==project)\
            .all()[0][0]
        
        # set the row count for all shots in that sequence
        self.shots_tableWidget.setRowCount(shot_count)
        
        row = 0
        for sequence in sequences:    
            shots = db.query(Shot)\
                .filter(Shot.sequence==sequence)\
                .order_by(Shot.number)\
                .all()
            
            #logger.debug('shots of sequence %s is %s' % (sequence.name, shots))
            
            # feed the shots to the list
            
            for shot in shots:
                # add the seq name to the first column
                column = 0
                item = QtGui.QTableWidgetItem(sequence.name)
                item.setTextAlignment(0x0004 | 0x0080)
                self.shots_tableWidget.setItem(row, column, item)
                
                # add the shot code to the second column
                column += 1
                item = QtGui.QTableWidgetItem(shot.code)
                item.setTextAlignment(0x0004 | 0x0080)
                self.shots_tableWidget.setItem(row, column, item)
                
                for type_code in shot_vtype_codes:
                    column += 1
                    # just consider the MAIN take
                    
                    # get the latest version of that type and take
                    version = db.query(Version)\
                        .join(VersionType)\
                        .filter(Version.version_of==shot)\
                        .filter(Version.type_id==VersionType.id)\
                        .filter(VersionType.code==type_code)\
                        .filter(Version.take_name==conf.default_take_name)\
                        .order_by(Version.version_number.desc())\
                        .first()
                    
                    if version:
                        status = version.status
                        # mark the status of that type in that take
                        item = QtGui.QTableWidgetItem(version.status)
                        item.setTextAlignment(0x0004 | 0x0080)
                        
                        # set the color according to status
                        index = conf.status_list.index(version.status)
                        bgcolor = conf.status_bg_colors[index]
                        fgcolor = conf.status_fg_colors[index]
                        
                        bg = item.background()
                        bg.setColor(QtGui.QColor(*bgcolor))
                        item.setBackground(bg)
                        
                        fg = item.foreground()
                        fg.setColor(QtGui.QColor(*fgcolor))
                        item.setForeground(fg)
                        
                        item.setBackgroundColor(QtGui.QColor(*bgcolor))
                        
                    else:
                        # set the background color to black
                        item = QtGui.QTableWidgetItem('N/A')
                        bg = item.background()
                        bg.setColor(QtGui.QColor(0, 0, 0))
                        item.setBackground(bg)
                        
                        item.setBackgroundColor(QtGui.QColor(0, 0, 0))
                    
                    self.shots_tableWidget.setItem(row, column, item)
                
                row += 1

        self.shots_tableWidget.resizeColumnsToContents()
