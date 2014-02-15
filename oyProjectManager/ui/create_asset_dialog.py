# -*- coding: utf-8 -*-
# Copyright (c) 2009-2014, Erkan Ozgur Yilmaz
# 
# This module is part of oyProjectManager and is released under the BSD 2
# License: http://www.opensource.org/licenses/BSD-2-Clause

import os
import logging
from sqlalchemy.sql.expression import distinct

import oyProjectManager
from oyProjectManager import config, db
from oyProjectManager.models.asset import Asset

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
    from oyProjectManager.ui import create_asset_dialog_UI_pyside as create_asset_dialog_UI
elif qt_module == "PyQt4":
    import sip
    sip.setapi('QString', 2)
    sip.setapi('QVariant', 2)
    from PyQt4 import QtGui, QtCore
    from oyProjectManager.ui import create_asset_dialog_UI_pyqt4 as create_asset_dialog_UI

class create_asset_dialog(QtGui.QDialog, create_asset_dialog_UI.Ui_create_asset):
    """Called upon asset creation
    """
    def __init__(self, parent=None):
        logger.debug('initializing create_asset_dialog')
        super(create_asset_dialog, self).__init__(parent)
        self.setupUi(self)
        self.ok = False
        
        self._setup_signals()
        self._setup_defaults()
    
    def _setup_signals(self):
        """setting up the signals
        """
        
        # buttonBox
        QtCore.QObject.connect(
            self.buttonBox,
            QtCore.SIGNAL('accepted()'),
            self.buttonBox_accepted
        )
        
        ## add_new_type_toolButton
        #QtCore.QObject.connect(
        #    self.add_new_type_toolButton,
        #    QtCore.SIGNAL('clicked()'),
        #    self.add_new_type_toolButton_clicked
        #)
    
    def _setup_defaults(self):
        """setting up the defaults
        """
        # fill the asset_types_comboBox with all the asset types from the db
        all_types = map(lambda x: x[0], db.query(distinct(Asset.type)).all())

        if conf.default_asset_type_name not in all_types:
            all_types.append(conf.default_asset_type_name)
        
        logger.debug('all_types: %s' % all_types)
         
        self.asset_types_comboBox.addItems(all_types)
    
    def buttonBox_accepted(self):
        """runs when the buttonbox.OK is clicked
        """
        # just close the dialog
        self.ok = True
        self.close()
    
    def buttonBox_rejected(self):
        """runs when the buttonbox.Cancel is clicked
        """
        self.ok = False
        self.close()
    
    #def add_new_type_toolButton_clicked(self):
    #    """runs when add_new_type_toolButton is clicked
    #    """
    #    logger.debug('add_new_type_toolButton is clicked')
    #    
    #    type_name, ok = QtGui.QInputDialog(self).getText(
    #        self,
    #        'Enter new asset type name',
    #        'Asset Type name:'
    #    )
    #    
    #    if ok:
    #        if type_name != '':
    #            index = self.asset_types_comboBox.findText(type_name)
    #            if index == -1:
    #                # add new type to the asset_type_ComboBox
    #                self.asset_types_comboBox.addItem(type_name)
    #                index = self.asset_types_comboBox.findText(type_name)
    #            
    #            self.asset_types_comboBox.setCurrentIndex(index)
