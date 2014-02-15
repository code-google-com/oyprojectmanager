# -*- coding: utf-8 -*-
# Copyright (c) 2009-2014, Erkan Ozgur Yilmaz
# 
# This module is part of oyProjectManager and is released under the BSD 2
# License: http://www.opensource.org/licenses/BSD-2-Clause

import os
import sys
import logging
import datetime
from sqlalchemy.exc import IntegrityError

from sqlalchemy.sql.expression import distinct


from oyProjectManager import config, db, utils
from oyProjectManager.models.asset import Asset
from oyProjectManager.models.auth import User
from oyProjectManager.models.project import Project
from oyProjectManager.models.repository import Repository
from oyProjectManager.models.sequence import Sequence
from oyProjectManager.models.shot import Shot
from oyProjectManager.models.version import Version, VersionType, VersionTypeEnvironments
from oyProjectManager.ui import ui_utils

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
    from oyProjectManager.ui import shot_editor_UI_pyside as shot_editor_UI, ui_utils
elif qt_module == "PyQt4":
    import sip
    sip.setapi('QString', 2)
    sip.setapi('QVariant', 2)
    from PyQt4 import QtGui, QtCore
    from oyProjectManager.ui import shot_editor_UI_pyqt4 as shot_editor_UI

def UI():
    """the UI to call the dialog by itself
    """
    global app
    global mainDialog
    
    self_quit = False
    if QtGui.QApplication.instance() is None:
        app = QtGui.QApplication(sys.argv)
        self_quit = True
    else:
        app = QtGui.QApplication.instance()
    
    mainDialog = MainDialog()
    mainDialog.show()
    app.exec_()

    if self_quit:
        app.connect(
            app,
            QtCore.SIGNAL("lastWindowClosed()"),
            app,
            QtCore.SLOT("quit()")
        )

    return mainDialog

class MainDialog(QtGui.QDialog, shot_editor_UI.Ui_Dialog):
    """the shot editor dialog of the system
    """
    
    def __init__(self, shot=None, parent=None):
        super(MainDialog, self).__init__(parent)
        self.setupUi(self)
        
        self.shot = shot
        
        self.setup_signals()
        self.setup_defaults()
    
    def setup_signals(self):
        """set up the signals
        """
        
        # button box
        QtCore.QObject.connect(
            self.buttonBox,
            QtCore.SIGNAL('accepted()'),
            self.dialog_accepted
        )
        
        QtCore.QObject.connect(
            self.buttonBox,
            QtCore.SIGNAL('rejected()'),
            self.dialog_rejected
        )
        
        # upload_thumbnail_button
        QtCore.QObject.connect(
            self.upload_thumbnail_pushButton,
            QtCore.SIGNAL('clicked()'),
            self.upload_thumbnail
        )
        
    def setup_defaults(self):
        """set up default values
        """
        
        if not self.shot:
            # set the label to "N/A"
            self.shot_name_label.setText('N/A')
            return
        
        self.shot_name_label.setText(self.shot.code)
        self.start_frame_spinBox.setValue(self.shot.start_frame)
        self.end_frame_spinBox.setValue(self.shot.end_frame)
        self.handle_at_start_spinBox.setValue(self.shot.handle_at_start)
        self.handle_at_end_spinBox.setValue(self.shot.handle_at_end)
        ui_utils.update_gview_with_versionable_thumbnail(
            self.shot,
            self.thumbnail_graphicsView
        )
    
    def upload_thumbnail(self):
        """uploads the thumbnail for the given shot
        """
        
        thumbnail_full_path = ui_utils.choose_thumbnail(self)
        
        if thumbnail_full_path == '':
            # do nothing
            return
        
        if not self.shot:
            # again do nothing
            return
        
        #ui_utils.upload_thumbnail(self.shot, thumbnail_full_path)
        #ui_utils.update_gview_with_versionable_thumbnail(
        #    self.shot,
        #    self.thumbnail_graphicsView
        #)
        ui_utils.update_gview_with_image_file(
            thumbnail_full_path,
            self.thumbnail_graphicsView
        )
    
    def dialog_accepted(self):
        """runs when the OK button is clicked
        """
        
        if self.shot:
            # update shot info
            self.shot.start_frame = self.start_frame_spinBox.value()
            self.shot.end_frame = self.end_frame_spinBox.value()
            self.shot.handle_at_start = self.handle_at_start_spinBox.value()
            self.shot.handle_at_end = self.handle_at_end_spinBox.value()
            
            # thumbnail
            # render the current gView QPixmap to a file
            ui_utils.render_image_from_gview(
                self.thumbnail_graphicsView,
                self.shot.thumbnail_full_path
            )
            self.shot.save()
        
        # close the dialog
        self.close()
    
    def dialog_rejected(self):
        """runs when the Cancel button is clicked
        """
        # just close the dialog
        self.close()
