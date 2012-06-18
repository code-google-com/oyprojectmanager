# -*- coding: utf-8 -*-
# Copyright (c) 2009-2012, Erkan Ozgur Yilmaz
# 
# This module is part of oyProjectManager and is released under the BSD 2
# License: http://www.opensource.org/licenses/BSD-2-Clause

import os
import sys
import logging
import datetime
from sqlalchemy.exc import IntegrityError

from sqlalchemy.sql.expression import distinct

import oyProjectManager
from oyProjectManager import config, db, utils
from oyProjectManager.core.models import (Asset, Project, Sequence, Repository,
                                          Version, VersionType, Shot, User,
                                          VersionTypeEnvironments)
from oyProjectManager.ui import version_updater, ui_utils

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
    from oyProjectManager.ui import version_creator_UI_pyside as version_creator_UI
    from oyProjectManager.ui import create_asset_dialog_UI_pyside as create_asset_dialog_UI
elif qt_module == "PyQt4":
    import sip
    sip.setapi('QString', 2)
    sip.setapi('QVariant', 2)
    from PyQt4 import QtGui, QtCore
    from oyProjectManager.ui import version_creator_UI_pyqt4 as version_creator_UI
    from oyProjectManager.ui import create_asset_dialog_UI_pyqt4 as create_asset_dialog_UI

def UI(environment):
    """the UI to call the dialog by itself
    """
    global app
    global mainDialog
    
#    app = singletonQApplication.QApplication()

    self_quit = False
    if QtGui.QApplication.instance() is None:
        try:
            app = QtGui.QApplication(sys.argv)
        except AttributeError: # sys.argv gives argv.error
            app = QtGui.QApplication([])
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

class MainDialog(QtGui.QDialog, version_creator_UI.Ui_Dialog):
    """The main asset version creation dialog for the system.
    
    This is the main interface that the users of the oyProjectManager will use
    to create a 
    
    :param environment: It is an object which supplies **methods** like
      ``open``, ``save``, ``export``,  ``import`` or ``reference``. The most
      basic way to do this is to pass an instance of a class which is derived
      from the :class:`~oyProjectManager.core.models.EnvironmentBase` which has
      all this methods but produces ``NotImplemented`` errors if the child
      class has not implemented these actions.
      
      The main duty of the Environment object is to introduce the host
      application (Maya, Houdini, Nuke, etc.) to oyProjectManager and let it to
      open, save, export, import or reference a file.
    
    :param parent: The parent ``PySide.QtCore.QObject`` of this interface. It
      is mainly useful if this interface is going to be attached to a parent
      UI, like the Maya or Nuke.
    """
    
    # TODO: add only active users to the interface
    
    def __init__(self, environment=None, parent=None):
        logger.debug("initializing the interface")
        
        super(MainDialog, self).__init__(parent)
        self.setupUi(self)
        
        # change the window title
        self.setWindowTitle(
            'Version Creator | ' + \
            'oyProjectManager v' + oyProjectManager.__version__
        )
        
        self.config = config.Config()
        self.repo = Repository()
        
        # setup the database
        if db.session is None:
            db.setup()
        
        self.environment = environment
        
        # create the project attribute in projects_comboBox
        # TODO: create an array of Project instances for each project_name in the comboBox
        #       but just fill them when the Project instance is created
        self.users_comboBox.users = []
        self.projects_comboBox.projects = []
        self.sequences_comboBox.sequences = []
        self.assets_tableWidget.assets = []
        self.shots_listWidget.shots = []
        self.input_dialog = None
        self.previous_versions_tableWidget.versions = []
        
        # set the asset_tableWidget.labels
        self.assets_tableWidget.labels = ['Type', 'Name']
        
        # set previous_versions_tableWidget.labels
        self.previous_versions_tableWidget.labels = [
            "Version",
            "User",
            "Status",
            "File Size",
            "Date",
            "Note",
            #"Path"
        ]
        
        # setup signals
        self._setup_signals()
        
        # setup defaults
        self._set_defaults()
        
        # center window
        self._center_window()
        
        logger.debug("finished initializing the interface")
    
    def _setup_signals(self):
        """sets up the signals
        """
        
        logger.debug("start setting up interface signals")
        
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
        
        # sequences_comboBox
        QtCore.QObject.connect(
            self.sequences_comboBox,
            QtCore.SIGNAL("currentIndexChanged(int)"),
            self.sequences_comboBox_changed
        )
        
        # assets_tableWidget
        QtCore.QObject.connect(
            self.assets_tableWidget,
            QtCore.SIGNAL(
                'currentItemChanged(QTableWidgetItem*,QTableWidgetItem*)'
            ),
            self.asset_changed
        )
        
        
        # shots_listWidget
        QtCore.QObject.connect(
            self.shots_listWidget,
            QtCore.SIGNAL("currentTextChanged(QString)"),
            self.shot_changed
        )
        
#        # asset_description_edit_pushButton
#        QtCore.QObject.connect(
#            self.asset_description_edit_pushButton,
#            QtCore.SIGNAL("clicked()"),
#            self.asset_description_edit_pushButton_clicked
#        )
#        
#        # shot_description_edit_pushButton
#        QtCore.QObject.connect(
#            self.shot_description_edit_pushButton,
#            QtCore.SIGNAL("clicked()"),
#            self.shot_description_edit_pushButton_clicked
#        )
        
        # types_comboBox
        QtCore.QObject.connect(
            self.version_types_listWidget,
            QtCore.SIGNAL("currentTextChanged(QString)"),
            self.version_types_listWidget_changed
        )
        
        # take_comboBox
        QtCore.QObject.connect(
            self.takes_listWidget,
            QtCore.SIGNAL("currentTextChanged(QString)"),
            self.takes_listWidget_changed
        )
        
        # add_type_toolButton
        QtCore.QObject.connect(
            self.add_type_toolButton,
            QtCore.SIGNAL("clicked()"),
            self.add_type_toolButton_clicked
        )
        
        # custom context menu for the assets_tableWidget
        self.assets_tableWidget.setContextMenuPolicy(
            QtCore.Qt.CustomContextMenu
        )
        
        QtCore.QObject.connect(
            self.assets_tableWidget,
            QtCore.SIGNAL("customContextMenuRequested(const QPoint&)"),
            self._show_assets_tableWidget_context_menu
        )
        
        # custom context menu for the previous_versions_tableWidget
        self.previous_versions_tableWidget.setContextMenuPolicy(
            QtCore.Qt.CustomContextMenu
        )
        
        QtCore.QObject.connect(
            self.previous_versions_tableWidget,
            QtCore.SIGNAL("customContextMenuRequested(const QPoint&)"),
            self._show_previous_versions_tableWidget_context_menu
        )
         
        # create_asset_pushButton
        QtCore.QObject.connect(
            self.create_asset_pushButton,
            QtCore.SIGNAL("clicked()"),
            self.create_asset_pushButton_clicked
        )

        # add_take_toolButton
        QtCore.QObject.connect(
            self.add_take_toolButton,
            QtCore.SIGNAL("clicked()"),
            self.add_take_toolButton_clicked
        )
        
        # export_as
        QtCore.QObject.connect(
            self.export_as_pushButton,
            QtCore.SIGNAL("clicked()"),
            self.export_as_pushButton_clicked
        )

        # save_as
        QtCore.QObject.connect(
            self.save_as_pushButton,
            QtCore.SIGNAL("clicked()"),
            self.save_as_pushButton_clicked
        )

        # open
        QtCore.QObject.connect(
            self.open_pushButton,
            QtCore.SIGNAL("clicked()"),
            self.open_pushButton_clicked
        )
        
        # add double clicking to previous_versions_tableWidget too
        QtCore.QObject.connect(
            self.previous_versions_tableWidget,
            QtCore.SIGNAL("cellDoubleClicked(int,int)"),
            self.open_pushButton_clicked
        )


        # reference
        QtCore.QObject.connect(
            self.reference_pushButton,
            QtCore.SIGNAL("clicked()"),
            self.reference_pushButton_clicked
        )

        # import
        QtCore.QObject.connect(
            self.import_pushButton,
            QtCore.SIGNAL("clicked()"),
            self.import_pushButton_clicked
        )
        
        # show_only_published_checkBox
        QtCore.QObject.connect(
            self.show_published_only_checkBox,
            QtCore.SIGNAL("stateChanged(int)"),
            self.update_previous_versions_tableWidget
        )
        
        # show_only_published_checkBox
        QtCore.QObject.connect(
            self.version_count_spinBox,
            QtCore.SIGNAL("valueChanged(int)"),
            self.update_previous_versions_tableWidget
        )
        
        # shot_info_update_pushButton 
        QtCore.QObject.connect(
            self.shot_info_update_pushButton,
            QtCore.SIGNAL("clicked()"),
            self.shot_info_update_pushButton_clicked
        )
        
        # upload_thumbnail_pushButton
        QtCore.QObject.connect(
            self.upload_thumbnail_pushButton,
            QtCore.SIGNAL("clicked()"),
            self.upload_thumbnail_pushButton_clicked
        )
        
        logger.debug("finished setting up interface signals")
    
    def _show_assets_tableWidget_context_menu(self, position):
        """the custom context menu for the assets_tableWidget
        """
        # convert the position to global screen position
        global_position = self.assets_tableWidget.mapToGlobal(position)
        
        # create the menu
        menu = QtGui.QMenu()
        menu.addAction("Rename Asset")
        
        selected_item = menu.exec_(global_position)
        
        if selected_item:
            # something is chosen
            if selected_item.text() == "Rename Asset":
                
                # show a dialog
                self.input_dialog = QtGui.QInputDialog(self)

                new_asset_name, ok = self.input_dialog.getText(
                    self,
                    "Rename Asset",
                    "New Asset Name"
                )
                
                if ok:
                    # if it is not empty
                    if new_asset_name != "":
                        # get the asset from the list
                        asset = self.get_versionable()
                        asset.name = new_asset_name
                        asset.code = new_asset_name
                        asset.save()
                        
                        # update assets_tableWidget
                        self.tabWidget_changed(0)

    def _show_previous_versions_tableWidget_context_menu(self, position):
        """the custom context menu for the pervious_versions_tableWidget
        """
        # convert the position to global screen position
        global_position = \
            self.previous_versions_tableWidget.mapToGlobal(position)
        
        item = self.previous_versions_tableWidget.itemAt(position)
        index = item.row()
        version = self.previous_versions_tableWidget.versions[index]
        
        # create the menu
        menu = QtGui.QMenu()
        
        #if not version.is_published:
        #    previous_versions_tableWidget_menu.addAction("Publish")
        
        #previous_versions_tableWidget_menu.addSeparator()
        
        # add statuses
        for status in conf.status_list_long_names:
            action = QtGui.QAction(status, menu)
            action.setCheckable(True)
            # set it checked if the status of the version is the current status
            if version.status == status:
                action.setChecked(True)
            
            menu.addAction(action)
        
        # add separator
        menu.addSeparator()
        
        # add Browse Outputs
        menu.addAction("Browse Outputs")
        
        selected_item = menu.exec_(global_position)
        
        if selected_item:
            #if selected_item.text() == "Publish":
            #    # publish the selected version
            #    if version:
            #        # publish it
            #        if not version.is_published:
            #            version.is_published = True
            #            version.save()
            #            # refresh the tableWidget
            #            self.update_previous_versions_tableWidget()
            #            return
            
            choice = selected_item.text()
            
            if choice in conf.status_list_long_names:
                # change the status of the version
                if version:
                    version.status = selected_item.text()
                    version.save()
                    # refresh the tableWidget
                    self.update_previous_versions_tableWidget()
                    return
            elif choice == 'Browse Outputs':
                path = os.path.expandvars(version.output_path)
                try:
                    utils.open_browser_in_location(path)
                except IOError:
                    QtGui.QMessageBox.critical(
                        self,
                        "Error",
                        "Path doesn't exists:\n" + path
                    ) 
    
    def rename_asset(self, asset, new_name):
        """Renames the asset with the given new name
        
        :param asset: The :class:`~oyProjectManager.core.models.Asset` instance
          to be renamed.
        
        :param new_name: The desired new name for the asset.
        """
        pass
    
    def _center_window(self):
        """centers the window to the screen
        """
        screen = QtGui.QDesktopWidget().screenGeometry()
        size =  self.geometry()
        self.move(
            (screen.width()-size.width()) * 0.5,
            (screen.height()-size.height()) * 0.5
        )
    
    def _set_defaults(self):
        """sets up the defaults for the interface
        """
        logger.debug("started setting up interface defaults")
        
        # clear the thumbnail area
        self.clear_thumbnail()
        
        # fill the statuses_comboBox
        self.statuses_comboBox.clear()
        self.statuses_comboBox.addItems(conf.status_list_long_names)
        
        # fill the projects
        projects = Project.query()\
            .filter(Project.active==True)\
            .order_by(Project.name)\
            .all()
        
        self.projects_comboBox.addItems(
            map(lambda x: x.name, projects)
        )
        self.projects_comboBox.projects = projects
        
        # fill the users
        users = User.query().all()
        self.users_comboBox.users = users
        self.users_comboBox.addItems(map(lambda x:x.name, users))
        
        # set the default user
        last_user_id = conf.last_user_id
        if last_user_id:
            logger.debug("last_user_id: %i" % last_user_id)
        else:
            logger.debug("no last user is set before")
        
        last_user = None
        if last_user_id is not None:
            last_user = User.query().filter(User.id==last_user_id).first()
        
        logger.debug("last_user: %s" % last_user)
        
        if last_user is not None:
            # select the user from the users_comboBox
            index = self.users_comboBox.findText(last_user.name)
            logger.debug("last_user index in users_comboBox: %i" % index)
            if index != -1:
                self.users_comboBox.setCurrentIndex(index)
        
        # add "Main" by default to the takes_listWidget
        self.takes_listWidget.addItem(conf.default_take_name)
        # select it
        item = self.takes_listWidget.item(0)
        self.takes_listWidget.setCurrentItem(item)
        
        # run the project changed item for the first time
        self.project_changed()
        
        if self.environment is not None:
            logger.debug("restoring the ui with the version from environment")
            
            # get the last version from the environment
            version_from_env = self.environment.get_last_version()
            
            logger.debug("version_from_env: %s" % version_from_env)
            
            self.restore_ui(version_from_env)
        
        logger.debug("finished setting up interface defaults")
    
    def restore_ui(self, version):
        """Restores the UI with the given Version instance
        
        :param version: :class:`~oyProjectManager.core.models.Version` instance
        """
        
        logger.debug("restoring ui with the given version: %s", version)
        
        # quit if version is None
        if version is None or not version.project.active:
            return
        
        # set the project
        index = self.projects_comboBox.findText(version.project.name)
        
        if index != -1:
            self.projects_comboBox.setCurrentIndex(index)
        else:
            return
        
        # set the versionable
        versionable = version.version_of
        
        # set the tab
        if isinstance(versionable, Asset):
            self.tabWidget.setCurrentIndex(0)
            
            # set the asset name
            items = self.assets_tableWidget.findItems(
                versionable.name,
                QtCore.Qt.MatchExactly
            )
            item = None
            if items:
                item = items[0]
            else:
                return
            
            logger.debug('*******************************')
            logger.debug('item: %s' % item)
            
            self.assets_tableWidget.setCurrentItem(item)
            
        else:
            self.tabWidget.setCurrentIndex(1)
            
            #the sequence
            index = self.sequences_comboBox.findText(versionable.sequence.name)
            
            if index != -1:
                self.sequences_comboBox.setCurrentIndex(index)
            else:
                return
            
            # the shot code
            items = self.shots_listWidget.findItems(
                versionable.code,
                QtCore.Qt.MatchExactly
            )
            item = None
            if items:
                item = items[0]
            else:
                return
            self.shots_listWidget.setCurrentItem(item)
        
        # version_type name
        type_name = version.type.name
        logger.debug('finding type with name: %s' % type_name)
        items = self.version_types_listWidget.findItems(
            type_name,
            QtCore.Qt.MatchExactly
        )
        
        if not items:
            logger.debug('no items found with: %s' % type_name)
            return
        
        self.version_types_listWidget.setCurrentItem(items[0])
        
        # take_name
        take_name = version.take_name
        logger.debug('finding take with name: %s' % take_name)
        items = self.takes_listWidget.findItems(
            take_name,
            QtCore.Qt.MatchExactly
        )
        self.takes_listWidget.setCurrentItem(items[0])
   
    def project_changed(self):
        """updates the assets list_widget and sequences_comboBox for the 
        """
        
        logger.debug("project_comboBox has changed in the UI")
        
        # call tabWidget_changed with the current index
        curr_tab_index = self.tabWidget.currentIndex()
        
        self.tabWidget_changed(curr_tab_index)
    
    def tabWidget_changed(self, index):
        """called when the tab widget is changed
        """
        
        proj = self.get_current_project()
        
        # clear the thumbnail area
        self.clear_thumbnail()
        
        # if assets is the current tab
        if index == 0:
            logger.debug("tabWidget index changed to asset")
            
            # TODO: don't update if the project is the same with the cached one
            
            # get all the assets of the project
            assets = Asset.query()\
                .filter(Asset.project==proj)\
                .order_by(Asset.type)\
                .order_by(Asset.name)\
                .all()
            
            # add the assets to the assets list
            self.assets_tableWidget.assets = assets
            
            # add their names to the list
            self.assets_tableWidget.clear()
            self.assets_tableWidget.setRowCount(len(assets))
            self.assets_tableWidget.setHorizontalHeaderLabels(
                self.assets_tableWidget.labels
            )
            
            for i, asset in enumerate(assets):
                # type
                item = QtGui.QTableWidgetItem(asset.type)
                # align to left and vertical center
                item.setTextAlignment(0x0001 | 0x0080)
                
                self.assets_tableWidget.setItem(i, 0, item)
                
                # name
                item = QtGui.QTableWidgetItem(asset.name)
                item.setTextAlignment(0x0001 | 0x0080)
                
                self.assets_tableWidget.setItem(i, 1, item)
            
            self.assets_tableWidget.resizeColumnsToContents()
            
            # set the list to the first asset
            table_item = self.assets_tableWidget.item(0, 0)
            
            if table_item is not None:
                self.assets_tableWidget.selectRow(0)
                
                # call asset update
                self.asset_changed()
                
#                # enable the asset_description_edit_pushButton
#                self.asset_description_edit_pushButton.setEnabled(True)
            else:
#                # disable the asset_description_edit_pushButton
#                self.asset_description_edit_pushButton.setEnabled(False)
                
                # clear the versions comboBox
                self.version_types_listWidget.clear()
                
                # set the take to default
                self.takes_listWidget.clear()
                self.takes_listWidget.addItem(conf.default_take_name)
                item = self.takes_listWidget.item(0)
                self.takes_listWidget.setCurrentItem(item)
                
        
        elif self.tabWidget.currentIndex() == 1:
            # TODO: don't update if the project is not changed from the last one
            
            logger.debug("tabWidget index changed to shots")
            
            # update the sequence comboBox
            seqs = Sequence.query().filter(Sequence.project==proj).all()
            
            self.sequences_comboBox.clear()
            self.sequences_comboBox.addItems([seq.name for seq in seqs])
            
            # attach the sequences to the sequences_comboBox
            self.sequences_comboBox.sequences = seqs
            
            if self.sequences_comboBox.count():
                self.sequences_comboBox.setCurrentIndex(0)
                self.sequences_comboBox_changed(0)
            else:
                # there is no sequence
                # clear the shots_listWidget
                self.shots_listWidget.clear()
                
                # clear the version comboBox
                self.version_types_listWidget.clear()
                
                # set the take to default
                self.takes_listWidget.clear()
                self.takes_listWidget.addItem(conf.default_take_name)
                item = self.takes_listWidget.item(0)
                self.takes_listWidget.setCurrentItem(item)
    
    def sequences_comboBox_changed(self, index):
        """called when the sequences_comboBox index has changed
        """
        logger.debug("sequences_comboBox changed")
        
        # get the cached sequence instance
        try:
            seq = self.sequences_comboBox.sequences[index]
        except IndexError:
            logger.debug("there is no sequences cached in sequence_comboBox")
            return
        
        # update the shots_listWidget
        shots = Shot.query().filter(Shot.sequence==seq).all()
        shots.sort(key=lambda x: utils.embedded_numbers(x.number))
        
        # add their names to the list
        self.shots_listWidget.clear()
        self.shots_listWidget.addItems([shot.code for shot in shots])
        
        # set the shots cache
        self.shots_listWidget.shots = shots
        
        # set the list to the first shot
        list_item = self.shots_listWidget.item(0)
        
        # clear the thumbnail area
        self.clear_thumbnail()
        
        if list_item is not None:
            self.shots_listWidget.setCurrentItem(list_item)
            
            # call shots update
#            self.asset_changed(list_item.text())
            
#            # enable the asset_description_edit_pushButton
#            self.shot_description_edit_pushButton.setEnabled(True)
#        else:
#            self.shot_description_edit_pushButton.setEnabled(False)
    
    def asset_changed(self):
        """updates the asset related fields with the current asset information
        """
        
        proj = self.get_current_project()
        
        #asset = \
        #    Asset.query().\
        #    filter(Asset.project==proj).\
        #    filter_by(name=asset_name).\
        #    first()
        asset = self.get_versionable()
        
        if asset is None:
            return
        
#        # set the description
#        if asset.description is not None:
#            self.asset_description_textEdit.setText(asset.description)
#        else:
#            self.asset_description_textEdit.setText("")
        
        # update the version data
        # Types
        # get all the types for this asset
        # available in this environment
        
        if self.environment is None:
            types = map(
                lambda x: x[0],
                db.query(distinct(VersionType.name))
                .join(Version)
                .filter(Version.version_of==asset)
                .all()
            )
        else:
            types = map(
                lambda x: x[0],
                db.query(distinct(VersionType.name))
                .join(VersionTypeEnvironments)
                .join(Version)
                .filter(VersionTypeEnvironments.environment_name==self.environment.name)
                .filter(Version.version_of==asset)
                .all()
            )
        
        # add the types to the version types list
        self.version_types_listWidget.clear()
        self.version_types_listWidget.addItems(types)
        
        # select the first one
        item = self.version_types_listWidget.item(0)
        self.version_types_listWidget.setCurrentItem(item)
        
        # update thumbnail
        self.update_thumbnail()

    def get_current_shot(self):
        """returns the current selected shot in the interface
        """
        # get the shot from the index
        index = self.shots_listWidget.currentIndex().row()
        shot = self.shots_listWidget.shots[index]
        return shot

    def shot_changed(self, shot_name):
        """updates the shot related fields with the current shot information
        """
        
        proj = self.get_current_project()
        shot = self.get_current_shot()
        
#        # set the description
#        if shot.description is not None:
#            self.shot_description_textEdit.setText(shot.description)
#        else:
#            self.shot_description_textEdit.setText("")
        
        # update the version data
        # frame info
        self.start_frame_spinBox.setValue(shot.start_frame)
        self.end_frame_spinBox.setValue(shot.end_frame)
        self.handle_at_start_spinBox.setValue(shot.handle_at_start)
        self.handle_at_end_spinBox.setValue(shot.handle_at_end)
        
        # Types
        # get all the types for this shot
        if self.environment is None:
            types = map(
                lambda x: x[0],
                db.query(distinct(VersionType.name)).
                join(Version).
                filter(Version.version_of==shot).
                all()
            )
        else:
            types = map(
                lambda x: x[0],
                db.query(distinct(VersionType.name))
                .join(VersionTypeEnvironments)
                .join(Version)
                .filter(VersionTypeEnvironments.environment_name==self.environment.name)
                .filter(Version.version_of==shot)
                .all()
            )
        
        # add the types to the version types list
        self.version_types_listWidget.clear()
        self.version_types_listWidget.addItems(types)

        # select the first one
        item = self.version_types_listWidget.item(0)
        self.version_types_listWidget.setCurrentItem(item)
#        setCurrentRow(0)
        
        # update thumbnail
        self.update_thumbnail()
    
    def shot_info_update_pushButton_clicked(self):
        """runs when the shot_info_update_pushButton is clicked
        """
        
        shot = self.get_current_shot()
        
        # get the info
        start_frame = self.start_frame_spinBox.value()
        end_frame = self.end_frame_spinBox.value()
        handle_at_start = self.handle_at_start_spinBox.value()
        handle_at_end = self.handle_at_end_spinBox.value()
        
        # now update the shot
        shot.start_frame = start_frame
        shot.end_frame = end_frame
        shot.handle_at_start = handle_at_start
        shot.handle_at_end = handle_at_end
    
    def version_types_listWidget_changed(self, index):
        """runs when the asset version types comboBox has changed
        """
        versionable = self.get_versionable()
        
        # version type name
        version_type_name = ""
        item = self.version_types_listWidget.currentItem()
        if item:
            version_type_name = item.text()
        
        if version_type_name != '':
            logger.debug("version_type_name: %s" % version_type_name)
        else:
            return
        
        # Takes
        # get all the takes of the current asset
        takes = map(
            lambda x: x[0],
            db.query(distinct(Version.take_name))
                .join(VersionType)
                .filter(VersionType.name==version_type_name)
                .filter(Version.version_of==versionable)
                .all()
        )
        
        self.takes_listWidget.clear()
        
        logger.debug("len(takes) from db: %s" % len(takes))
        
        if len(takes) == 0:
            # append the default take
            logger.debug("appending the default take name")
            self.takes_listWidget.addItem(conf.default_take_name)
        else:
            logger.debug("adding the takes from db")
            self.takes_listWidget.addItems(takes)
        
        logger.debug("setting the first element selected")
        item = self.takes_listWidget.item(0)
        self.takes_listWidget.setCurrentItem(item)
    
    def takes_listWidget_changed(self, index):
        """runs when the takes_listWidget has changed
        """
        
        # update the previous_versions_tableWidget
        self.update_previous_versions_tableWidget()
        
        # update the statuses_comboBox
        versionable = self.get_versionable()
        
        # version type name
        version_type_name = ""
        item = self.version_types_listWidget.currentItem()
        if item:
            version_type_name = item.text()
        
        # take name
        take_name = ""
        item = self.takes_listWidget.currentItem()
        if item:
            take_name = item.text()
        
        # query the Versions of this type and take
        query = Version.query().join(VersionType)\
            .filter(VersionType.name==version_type_name)\
            .filter(Version.version_of==versionable)\
            .filter(Version.take_name==take_name)
        
        ## get the published only
        #if self.show_published_only_checkBox.isChecked():
        #    query = query.filter(Version.is_published==True)
        
        version = query.order_by(Version.version_number.desc()).first()
        
        if version:
            status_index = conf.status_list.index(version.status)
            status_long_name = conf.status_list_long_names[status_index]
            index = self.statuses_comboBox.findText(status_long_name)
            if index != -1:
                self.statuses_comboBox.setCurrentIndex(index)
    
    def update_previous_versions_tableWidget(self):
        """updates the previous_versions_tableWidget
        """
        
        versionable = self.get_versionable()
        
        # version type name
        version_type_name = ""
        item = self.version_types_listWidget.currentItem()
        if item:
            version_type_name = item.text()
        
        if version_type_name != '':
            logger.debug("version_type_name: %s" % version_type_name)
        else:
            return
        
        # take name
        take_name = ""
        item = self.takes_listWidget.currentItem()
        if item:
            take_name = item.text()
        
        if take_name != '':
            logger.debug("take_name: %s" % take_name)
        else:
            return
        
        # query the Versions of this type and take
        query = Version.query().join(VersionType)\
            .filter(VersionType.name==version_type_name)\
            .filter(Version.version_of==versionable)\
            .filter(Version.take_name==take_name)
        
        # get the published only
        if self.show_published_only_checkBox.isChecked():
            query = query.filter(Version.is_published==True)
        
        # show how many
        count = self.version_count_spinBox.value()
        
        versions = query.order_by(Version.version_number.desc())\
            .limit(count).all()
        
        versions.reverse()
        
        # set the versions cache by adding them to the widget
        self.previous_versions_tableWidget.versions = versions
        
        self.previous_versions_tableWidget.clear()
        self.previous_versions_tableWidget.setRowCount(len(versions))
        
        self.previous_versions_tableWidget.setHorizontalHeaderLabels(
            self.previous_versions_tableWidget.labels
        )
        
        
        def set_font(item):
            """sets the font for the given item
            
            :param item: the a QTableWidgetItem
            """
            my_font = item.font()
            my_font.setBold(True)
            
            item.setFont(my_font)
           
            foreground = item.foreground()
            foreground.setColor(QtGui.QColor(0, 192, 0))
            item.setForeground(foreground)
        
        # update the previous versions list
        for i, vers in enumerate(versions):
           
            is_published = vers.is_published
            
            # ------------------------------------
            # version_number
            item = QtGui.QTableWidgetItem(str(vers.version_number))
            # align to center and vertical center
            item.setTextAlignment(0x0004 | 0x0080)
            
            if is_published:
                set_font(item)
            
            self.previous_versions_tableWidget.setItem(i, 0, item)
            # ------------------------------------
        
            # ------------------------------------
            # user.name
            item = QtGui.QTableWidgetItem(vers.created_by.name)
            # align to left and vertical center
            item.setTextAlignment(0x0001 | 0x0080)

            if is_published:
                set_font(item)
            
            self.previous_versions_tableWidget.setItem(i, 1, item)
            # ------------------------------------
            
            # ------------------------------------
            # status
            item = QtGui.QTableWidgetItem(vers.status)
            # align to left and vertical center
            item.setTextAlignment(0x0004 | 0x0080)
            
            #if is_published:
            #    set_font(item)
            
            # colorize the item
            index = conf.status_list.index(vers.status)
            bgcolor = conf.status_bg_colors[index]
            fgcolor = conf.status_fg_colors[index]
            
            bg = item.background()
            bg.setColor(QtGui.QColor(*bgcolor))
            item.setBackground(bg)
            
            fg = item.foreground()
            fg.setColor(QtGui.QColor(*fgcolor))

            try:
                item.setBackgroundColor(QtGui.QColor(*bgcolor))
            except AttributeError: # gives error with PySide
                pass
            
            self.previous_versions_tableWidget.setItem(i, 2, item)
            # ------------------------------------
 
        
            # ------------------------------------
            # filesize
            
            # get the file size
            #file_size_format = "%.2f MB"
            file_size = -1
            if os.path.exists(vers.full_path):
                file_size = float(os.path.getsize(vers.full_path))/1024/1024

            item = QtGui.QTableWidgetItem(conf.file_size_format % file_size)
            # align to left and vertical center
            item.setTextAlignment(0x0001 | 0x0080)

            if is_published:
                set_font(item)
            
            self.previous_versions_tableWidget.setItem(i, 3, item)
            # ------------------------------------
            
            # ------------------------------------
            # date
            
            # get the file date
            file_date = datetime.datetime.today()
            if os.path.exists(vers.full_path):
                file_date =  datetime.datetime.fromtimestamp(
                    os.path.getmtime(vers.full_path)
                )
            item = QtGui.QTableWidgetItem(
                file_date.strftime(conf.time_format)
            )
            
            # align to left and vertical center
            item.setTextAlignment(0x0001 | 0x0080)
            
            self.previous_versions_tableWidget.setItem(i, 4, item)
            # ------------------------------------
                        
            # ------------------------------------
            # note
            item = QtGui.QTableWidgetItem(vers.note)
            # align to left and vertical center
            item.setTextAlignment(0x0001 | 0x0080)

            if is_published:
                set_font(item)
            
            self.previous_versions_tableWidget.setItem(i, 5, item)
            # ------------------------------------
       
        # resize the first column
        self.previous_versions_tableWidget.resizeColumnsToContents()
   
    def create_asset_pushButton_clicked(self):
        """
        """
        
        dialog = create_asset_dialog(parent=self)
        dialog.exec_()
        
        ok = dialog.ok
        asset_name = dialog.asset_name_lineEdit.text()
        asset_type_name = dialog.asset_types_comboBox.currentText()
        
        logger.debug('new asset_name: %s' % asset_name)
        logger.debug('new asset_type_name: %s' % asset_type_name)
        
        if not ok:
            return
        elif asset_name == "" or asset_type_name == "":
            error_message = "The given Asset.name or Asset.type is " \
                            "empty!!!\n\nNot creating any new asset!"
            
            QtGui.QMessageBox.critical(self, 'Error', error_message)
            return
        
        proj = self.get_current_project()
        
        try:
            new_asset = Asset(proj, asset_name, type=asset_type_name)
            new_asset.save()
        except (TypeError, ValueError, IntegrityError) as e:
            if isinstance(e, IntegrityError):
                # the transaction needs to be rollback
                db.session.rollback()
                error_message = "Asset.name or Asset.code is not unique"
            
            # pop up an Message Dialog to give the error message
            QtGui.QMessageBox.critical(self, "Error", error_message)
            
            return
        
        # update the assets by calling project_changed
        self.project_changed()
    
    def get_versionable(self):
        """returns the versionable from the UI, it is an asset or a shot
        depending on to the current tab
        """
        proj = self.get_current_project()
        
        versionable = None
        if self.tabWidget.currentIndex() == 0:
            index = self.assets_tableWidget.currentRow()
#            logger.debug('assets_tableWidget.currentRow: %s' % index)
            
            if index != -1:
                versionable = self.assets_tableWidget.assets[index]
#                logger.debug("asset: %s" % versionable.name)
            
        else:
            index = self.shots_listWidget.currentIndex().row()
            
            if index != -1:
                versionable = self.shots_listWidget.shots[index]
#                logger.debug("shot: %s" % versionable.code)
        
        logger.debug('versionable: %s' % versionable)
        return versionable
    
    def get_version_type(self):
        """returns the VersionType instance by looking at the UI elements. It
        will return the correct VersionType by looking at if it is an Asset or
        a Shot and picking the name of the VersionType from the comboBox
        
        :returns: :class:`~oyProjectManager.core.models.VersionType`
        """
        
        project = self.get_current_project()
        if project is None:
            return None
        
        # get the versionable type
        versionable = self.get_versionable()
        
        type_for = versionable.__class__.__name__
        
        # get the version type name
        version_type_name = ""
        item = self.version_types_listWidget.currentItem()
        if item:
            version_type_name = item.text()
        
        # get the version type instance
        return VersionType.query()\
            .filter(VersionType.type_for==type_for)\
            .filter(VersionType.name==version_type_name)\
            .first()
    
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
    
    def add_type(self, version_type):
        """adds new types to the version_types_listWidget
        """
        
        if not isinstance(version_type, VersionType):
            raise TypeError("please supply a "
                            "oyProjectManager.core.models.VersionType for the"
                            "type to be added to the version_types_listWidget")
        
        # check if the given type is suitable for the current versionable
        versionable = self.get_versionable()
        
        if versionable.__class__.__name__ != version_type.type_for:
            raise TypeError("The given version_type is not suitable for %s"
                            % self.tabWidget.tabText(
                self.tabWidget.currentIndex()
            ))
        
        items = self.version_types_listWidget.findItems(
            version_type.name,
            QtCore.Qt.MatchExactly
        )
        
        if not len(items):
            self.version_types_listWidget.addItem(version_type.name)
            
            # select the last added type
            index = self.version_types_listWidget.count() - 1
            item = self.version_types_listWidget.item(index)
            self.version_types_listWidget.setCurrentItem(item)
    
    def add_type_toolButton_clicked(self):
        """adds a new type for the currently selected Asset or Shot
        """
        proj = self.get_current_project()
        
        # get the versionable
        versionable = self.get_versionable()
        
        # get all the version types which doesn't have any version defined
        
        # get all the current types from the interface
        current_types = []
        for index in range(self.version_types_listWidget.count()):
            current_types.append(
                self.version_types_listWidget.item(index).text()
            )
        
        # available types for Versionable in this environment
        # if there is an environment given
        if self.environment:
            available_types = map(
                lambda x: x[0],
                db.query(distinct(VersionType.name))
                .join(VersionTypeEnvironments)
                .filter(VersionType.type_for==versionable.__class__.__name__)
                .filter(VersionTypeEnvironments.environment_name==self.environment.name)
                .filter(~ VersionType.name.in_(current_types))
                .all()
            )
        else:
            # there is no environment
            # just return all VersionType names
            # TODO: create test for that case
            available_types = map(
                lambda x: x[0],
                db.query(distinct(VersionType.name))
                .filter(VersionType.type_for==versionable.__class__.__name__)
                .filter(~ VersionType.name.in_(current_types))
                .all()
            )

        
        # create a QInputDialog with comboBox
        self.input_dialog = QtGui.QInputDialog(self)
        
        if self.environment:
            type_name, ok = self.input_dialog.getItem(
                self,
                "Choose a VersionType",
                "Available Version Types for %ss in %s" % 
                    (versionable.__class__.__name__, self.environment.name),
                available_types,
                0,
                False
            )
        else:
            type_name, ok = self.input_dialog.getItem(
                self,
                "Choose a VersionType",
                "Available Version Types for %ss" % 
                    versionable.__class__.__name__,
                available_types,
                0,
                False
            )    
        
        # if ok add the type name to the end of the types_comboBox and make
        # it the current selection
        if ok:
            # get the type
            vers_type = VersionType.query().filter_by(name=type_name).first()
            
            try:
                self.add_type(vers_type)
            except TypeError:
                # the given type doesn't exists
                # just return without doing anything
                return
    
    def add_take_toolButton_clicked(self):
        """runs when the add_take_toolButton clicked
        """
        
        # open up a QInputDialog and ask for a take name
        # anything is acceptable
        # because the validation will occur in the Version instance
        
        self.input_dialog = QtGui.QInputDialog(self)
        
        take_name, ok = self.input_dialog.getText(
            self,
            "Add Take Name",
            "New Take Name"
        )
        
        if ok:
            # add the given text to the takes_listWidget
            # if it is not empty
            if take_name != "":
                item = self.takes_listWidget.addItem(take_name)
                # set the take to the new one
                self.takes_listWidget.setCurrentItem(item)
#                setCurrentRow(
#                    self.takes_listWidget.count() - 1,
#                    QtGui.QItemSelectionModel.Rows
#                )
    
    def get_new_version(self):
        """returns a :class:`~oyProjectManager.core.models.Version` instance
        from the UI by looking at the input fields
        
        :returns: :class:`~oyProjectManager.core.models.Version` instance
        """
        
        # create a new version
        versionable = self.get_versionable()
        version_type = self.get_version_type()
        take_name = self.takes_listWidget.currentItem().text()
        user = self.get_user()
        
        note = self.note_textEdit.toPlainText()
        
        published = self.publish_checkBox.isChecked()
        
        status = self.statuses_comboBox.currentText()
        
        version = Version(
            versionable,
            versionable.code,
            version_type,
            user,
            take_name=take_name,
            note=note,
            is_published=published,
            status=status
        )
        
        return version
    
    def get_previous_version(self):
        """returns the :class:`~oyProjectManager.core.models.Version` instance
        from the UI by looking at the previous_versions_tableWidget
        """
        
        index = self.previous_versions_tableWidget.currentRow()
        version = self.previous_versions_tableWidget.versions[index]
        
        return version
    
    def get_user(self):
        """returns the current User instance from the interface by looking at
        the name of the user from the users comboBox
        
        :return: :class:`~oyProjectManager.core.models.User` instance
        """
        
        index = self.users_comboBox.currentIndex()
        return self.users_comboBox.users[index]
    
    def export_as_pushButton_clicked(self):
        """runs when the export_as_pushButton clicked
        """
        
        logger.debug("exporting the data as a new version")
        
        # get the new version
        new_version = self.get_new_version()
        
        # call the environments export_as method
        if self.environment is not None:
            self.environment.export_as(new_version)
            
            # inform the user about what happened
            if logger.level != logging.DEBUG:
                QtGui.QMessageBox.information(
                    self,
                    "Export",
                    new_version.filename + "\n\n has been exported correctly!",
                    QtGui.QMessageBox.Ok
                )

    
    def save_as_pushButton_clicked(self):
        """runs when the save_as_pushButton clicked
        """
        
        logger.debug("saving the data as a new version")
        
        # get the new version
        try:
            new_version = self.get_new_version()
        except (TypeError, ValueError) as e:
            
            # pop up an Message Dialog to give the error message
            QtGui.QMessageBox.critical(self, "Error", e)
            
            return None
        
        # call the environments save_as method
        if self.environment is not None:
            self.environment.save_as(new_version)
        
        # save the new version to the database
        db.session.add(new_version)
        db.session.commit()
        
        
        # save the last user
        conf.last_user_id = new_version.created_by.id
        
        # close the UI
        self.close()
    
    def open_pushButton_clicked(self):
        """runs when the open_pushButton clicked
        """
        
        # get the new version
        old_version = self.get_previous_version()

        logger.debug("opening version %s" % old_version)
        
        # call the environments open_ method
        if self.environment is not None:
            
            to_update_list = []
            # environment can throw RuntimeError for unsaved changes
            try:
                envStatus, to_update_list = \
                    self.environment.open_(old_version)
            except RuntimeError as e:
                # pop a dialog and ask if the user really wants to open the
                # file

                answer = QtGui.QMessageBox.question(
                    self,
                    'RuntimeError',
                    "There are <b>unsaved changes</b> in the current "
                    "scene<br><br>Do you really want to open the file?",
                    QtGui.QMessageBox.Yes,
                    QtGui.QMessageBox.No
                )
                
                envStatus = False
                
                if answer== QtGui.QMessageBox.Yes:
                    envStatus, to_update_list = \
                        self.environment.open_(old_version, True)
                else:
                    # no, just return
                    return
            
            # check the to_update_list to update old versions
            if len(to_update_list):
                # invoke the assetUpdater for this scene
                version_updater_mainDialog = \
                    version_updater.MainDialog(self.environment, self)
                
                version_updater_mainDialog.exec_()
            
            self.environment.post_open(old_version)
        
        # close the dialog
        self.close()
    
    def reference_pushButton_clicked(self):
        """runs when the reference_pushButton clicked
        """
        
        # get the new version
        previous_version = self.get_previous_version()
        
        # allow only published versions to be referenced
        if not previous_version.is_published:
            QtGui.QMessageBox.critical(
                self,
                "Critical Error",
                "Referencing <b>un-published versions</b> are not allowed!\n"
                "Please reference a published version of the same Asset/Shot",
                QtGui.QMessageBox.Ok
            )
            return
        
        logger.debug("referencing version %s" % previous_version)
        
        # call the environments reference method
        if self.environment is not None:
            self.environment.reference(previous_version)
            
            # inform the user about what happened
            if logger.level != logging.DEBUG:
                QtGui.QMessageBox.information(
                    self,
                    "Reference",
                    previous_version.filename +\
                    "\n\n has been referenced correctly!",
                    QtGui.QMessageBox.Ok
                )

    def import_pushButton_clicked(self):
        """runs when the import_pushButton clicked
        """
        
        # get the previous version
        previous_version = self.get_previous_version()
        
        logger.debug("importing version %s" % previous_version)
        
        # call the environments import_ method
        if self.environment is not None:
            self.environment.import_(previous_version)

            # inform the user about what happened
            if logger.level != logging.DEBUG:
                QtGui.QMessageBox.information(
                    self,
                    "Import",
                    previous_version.filename +\
                    "\n\n has been imported correctly!",
                    QtGui.QMessageBox.Ok
                )
    
    def clear_thumbnail(self):
        """clears the thumbnail_graphicsView
        """
        ui_utils.clear_thumbnail(self.thumbnail_graphicsView)
    
    def update_thumbnail(self):
        """updates the thumbnail for the selected versionable
        """
        
        # get the current versionable
        versionable = self.get_versionable()
        ui_utils.update_gview_with_versionable_thumbnail(
            versionable,
            self.thumbnail_graphicsView
        )

    def upload_thumbnail_pushButton_clicked(self):
        """runs when the upload_thumbnail_pushButton is clicked
        """
        
        thumbnail_full_path = ui_utils.choose_thumbnail(self)
        
        # if the tumbnail_full_path is empty do not do anything
        if thumbnail_full_path == "":
            return
        
        # get the current versionable
        versionable = self.get_versionable()
        
        ui_utils.upload_thumbnail(versionable, thumbnail_full_path)
        
        # update the thumbnail
        self.update_thumbnail()
    
