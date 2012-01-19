# -*- coding: utf-8 -*-
# Copyright (c) 2009-2012, Erkan Ozgur Yilmaz
# 
# This module is part of oyProjectManager and is released under the BSD 2
# License: http://www.opensource.org/licenses/BSD-2-Clause

import sys
import os
import logging
from sqlalchemy.exc import IntegrityError

from sqlalchemy.sql.expression import distinct


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
    from oyProjectManager.ui import version_creator_UI_pyside as version_creator_UI
elif qt_module == "PyQt4":
    import sip
    sip.setapi('QString', 2)
    sip.setapi('QVariant', 2)
    from PyQt4 import QtGui, QtCore
    from oyProjectManager.ui import version_creator_UI_pyqt4 as version_creator_UI

def UI(environment):
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
        
#        super(QtGui.QDialog, self).__init__(parent)
        super(MainDialog, self).__init__(parent)
        self.setupUi(self)
        
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
        self.shots_listWidget.shots = []
        self.input_dialog = None
        self.previous_versions_tableWidget.versions = []
        
        # set previous_versions_tableWidget.labels
        self.previous_versions_tableWidget.labels = [
            "Version",
            "User",
            "File Size",
            "Note",
            "Path"
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
        
        # assets_listWidget
        QtCore.QObject.connect(
            self.assets_listWidget,
            QtCore.SIGNAL("currentTextChanged(QString)"),
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
            self.version_types_comboBox,
            QtCore.SIGNAL("currentIndexChanged(int)"),
            self.version_types_comboBox_changed
        )
        
        # take_comboBox
        QtCore.QObject.connect(
            self.takes_comboBox,
            QtCore.SIGNAL("currentIndexChanged(int)"),
            self.takes_comboBox_changed
        )
        
        # add_type_toolButton
        QtCore.QObject.connect(
            self.add_type_toolButton,
            QtCore.SIGNAL("clicked()"),
            self.add_type_toolButton_clicked
        )
        
        # custom context menu for the assets_listWidget
        self.assets_listWidget.setContextMenuPolicy(
            QtCore.Qt.CustomContextMenu
        )
        
        QtCore.QObject.connect(
            self.assets_listWidget,
            QtCore.SIGNAL("customContextMenuRequested(const QPoint&)"),
            self._show_assets_listWidget_context_menu
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
        
        logger.debug("finished setting up interface signals")
    
    def _show_assets_listWidget_context_menu(self, position):
        """the custom context menu for the assets_listWidget
        """
#        print "this has been run"
        # convert the position to global screen position
        global_position = self.assets_listWidget.mapToGlobal(position)
        
        # create the menu
        self.assets_listWidget_menu = QtGui.QMenu()
        self.assets_listWidget_menu.addAction("Rename Asset")
        #self.asset_description_menu.addAction("Delete Asset")
        
        selected_item = self.assets_listWidget_menu.exec_(global_position)
        
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
                        
                        # update assets_listWidget
                        self.tabWidget_changed(0)
                
    
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
        
        # fill the projects
        projects = db.query(Project).all()
        self.projects_comboBox.addItems(
            map(lambda x: x.name, projects)
        )
        self.projects_comboBox.projects = projects
        
        # fill the users
#        self.users_comboBox.addItems([user.name for user in self.config.users])
        users = db.query(User).all()
        self.users_comboBox.users = users
        self.users_comboBox.addItems(map(lambda x:x.name, users))
        
        # set the default user
        last_user_id = conf.last_user_id
        last_user = None
        if last_user_id is not None:
            last_user = db.query(User).filter(User.id==last_user_id).first()
        
        if last_user is not None:
            # select the user from the users_comboBox
            index = self.users_comboBox.findText(last_user.name)
            if index != -1:
                self.users_comboBox.setCurrentIndex(index)
        
        # add "Main" by default to the takes_comboBox
        self.takes_comboBox.addItem(conf.default_take_name)
        
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
        if version is None:
            return
        
        # set the project
        index = self.projects_comboBox.findText(version.project.name)
        self.projects_comboBox.setCurrentIndex(index)
        
        # set the versionable
        versionable = version.version_of
        
        # set the tab
        if isinstance(versionable, Asset):
            self.tabWidget.setCurrentIndex(0)
            
            # set the asset name
            items = self.assets_listWidget.findItems(
                versionable.name,
                QtCore.Qt.MatchExactly
            )
            self.assets_listWidget.setCurrentItem(items[0])
            
        else:
            self.tabWidget.setCurrentIndex(1)
            
            #the sequence
            index = self.sequences_comboBox.findText(versionable.sequence.name)
            self.sequences_comboBox.setCurrentIndex(index)
            
            # the shot code
            items = self.shots_listWidget.findItems(
                versionable.code,
                QtCore.Qt.MatchExactly
            )
            self.shots_listWidget.setCurrentItem(items[0])
            
        
        # version_type name
        type_name = version.type.name
        index = self.version_types_comboBox.findText(type_name)
        self.version_types_comboBox.setCurrentIndex(index)
        
        # take_name
        take_name = version.take_name
        index = self.takes_comboBox.findText(take_name)
        self.takes_comboBox.setCurrentIndex(index)
    
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
        
        # if assets is the current tab
        if index == 0:
            logger.debug("tabWidget index changed to asset")
            
            # TODO: don't update if the project is the same with the cached one
            
            # get all the assets of the project
            assets = db.query(Asset).filter(Asset.project==proj).all()
            
            # add their names to the list
            self.assets_listWidget.clear()
            self.assets_listWidget.addItems([asset.name for asset in assets])
            
            # set the list to the first asset
            list_item = self.assets_listWidget.item(0)
            
            if list_item is not None:
            #            list_item.setSelected(True)
                self.assets_listWidget.setCurrentItem(list_item)
    
                # call asset update
                self.asset_changed(list_item.text())
                
#                # enable the asset_description_edit_pushButton
#                self.asset_description_edit_pushButton.setEnabled(True)
            else:
#                # disable the asset_description_edit_pushButton
#                self.asset_description_edit_pushButton.setEnabled(False)
                
                # clear the versions comboBox
                self.version_types_comboBox.clear()
                
                # set the take to default
                self.takes_comboBox.clear()
                self.takes_comboBox.addItem(conf.default_take_name)
        
        elif self.tabWidget.currentIndex() == 1:
            # TODO: don't update if the project is not changed from the last one
            
            logger.debug("tabWidget index changed to shots")
            
            # update the sequence comboBox
            seqs = db.query(Sequence).filter(Sequence.project==proj).all()
            
            self.sequences_comboBox.clear()
            self.sequences_comboBox.addItems([seq.name for seq in seqs])
            
            # attach the sequences to the sequences_comboBox
            self.sequences_comboBox.sequences = seqs
            
            if self.sequences_comboBox.count():
                self.sequences_comboBox.setCurrentIndex(0)
                self.sequences_comboBox_changed(0)
            else:
                # there is no sequence
                # clear the version comboBox
                self.version_types_comboBox.clear()
                
                # set the take to default
                self.takes_comboBox.clear()
                self.takes_comboBox.addItem(conf.default_take_name)
    
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
        shots = db.query(Shot).filter(Shot.sequence==seq).all()
        
        # add their names to the list
        self.shots_listWidget.clear()
        self.shots_listWidget.addItems([shot.code for shot in shots])
        
        # set the shots cache
        self.shots_listWidget.shots = shots
        
        # set the list to the first shot
        list_item = self.shots_listWidget.item(0)
        
        if list_item is not None:
            self.shots_listWidget.setCurrentItem(list_item)
            
            # call shots update
#            self.asset_changed(list_item.text())
            
#            # enable the asset_description_edit_pushButton
#            self.shot_description_edit_pushButton.setEnabled(True)
#        else:
#            self.shot_description_edit_pushButton.setEnabled(False)
    
    def asset_changed(self, asset_name):
        """updates the asset related fields with the current asset information
        """
        
        proj = self.get_current_project()
        
        asset = \
            db.query(Asset).\
            filter(Asset.project==proj).\
            filter_by(name=asset_name).\
            first()
        
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
        self.version_types_comboBox.clear()
        self.version_types_comboBox.addItems(types)
        
        # select the first one
        self.version_types_comboBox.setCurrentIndex(0)
    
    def shot_changed(self, shot_name):
        """updates the shot related fields with the current shot information
        """
        
        proj = self.get_current_project()
        
        # get the shot from the index
        index = self.shots_listWidget.currentIndex().row()
        shot = self.shots_listWidget.shots[index]
        
#        # set the description
#        if shot.description is not None:
#            self.shot_description_textEdit.setText(shot.description)
#        else:
#            self.shot_description_textEdit.setText("")
        
        # update the version data
        # Types
        # get all the types for this asset
        types = map(
            lambda x: x[0],
            db.query(distinct(VersionType.name)).
            join(Version).
            filter(Version.version_of==shot).
            all()
        )
        
        # add the types to the version types list
        self.version_types_comboBox.clear()
        self.version_types_comboBox.addItems(types)

        # select the first one
        self.version_types_comboBox.setCurrentIndex(0)
    
    def version_types_comboBox_changed(self, index):
        """runs when the asset version types comboBox has changed
        """
        
        # get all the takes for this type
        proj = self.get_current_project()
        
        versionable = None
        if self.tabWidget.currentIndex() == 0:
            
            try:
                asset_name = self.assets_listWidget.currentItem().text()
            except AttributeError:
                asset_name = None
            
            versionable = \
                db.query(Asset)\
                .filter(Asset.project==proj)\
                .filter_by(name=asset_name)\
                .first()
            
            if asset_name is not None:
                logger.debug("updating take list for asset: %s" % versionable.name)
            else:
                logger.debug("updating take list for no asset")
        else:
            index = self.shots_listWidget.currentIndex().row()
            versionable = self.shots_listWidget.shots[index]
            
            logger.debug("updating take list for shot: %s" % versionable.code)
        
        # version type name
        version_type_name = self.version_types_comboBox.currentText()
        
        logger.debug("version_type_name: %s" % version_type_name)
        
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
        
        self.takes_comboBox.clear()
        
        if len(takes) == 0:
            # append the default take
            takes.append(conf.default_take_name)
        
        self.takes_comboBox.addItems(takes)
        self.takes_comboBox.setCurrentIndex(0)
    
    def takes_comboBox_changed(self, index):
        """runs when the takes_comboBox has changed
        """
        
        # just update the previous_versions_tableWidget
        self.update_previous_versions_tableWidget()
    
    def update_previous_versions_tableWidget(self):
        """updates the previous_versions_tableWidget
        """
        
        proj = self.get_current_project()
        
        versionable = None
        if self.tabWidget.currentIndex() == 0:
            
            try:
                asset_name = self.assets_listWidget.currentItem().text()
            except AttributeError:
                # no asset
                # just return
                asset_name = None
            
            versionable = db.query(Asset)\
                .filter(Asset.project==proj)\
                .filter(Asset.name==asset_name)\
                .first()
            
            if versionable is not None:
                logger.debug("updating take list for asset: %s" % versionable.name)
            else:
                logger.debug("updating take list for no asset")
        else:
            index = self.shots_listWidget.currentIndex().row()
            versionable = self.shots_listWidget.shots[index]
            
            logger.debug("updating take list for shot: %s" % versionable.code)
        
        # version type name
        version_type_name = self.version_types_comboBox.currentText()
        
        logger.debug("version_type_name: %s" % version_type_name)
        
        # take name
        take_name = self.takes_comboBox.currentText()
        
        logger.debug("take_name: %s" % take_name)
        
        # query the Versions of this type and take
        query = db.query(Version).join(VersionType)\
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
        
#        versions =
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
            
            item.setTextColor(QtGui.QColor(0, 192, 0))
        
        # update the previous versions list
        for i, vers in enumerate(versions):
        # TODO: add the Version instance to the tableWidget
        
        #            assert isinstance(vers, Version)
        
        #            # --------------------------------
        #            # base_name
        #            item = QtGui.QTableWidgetItem(vers.base_name)
        #            # align to left and vertical center
        #            item.setTextAlignment(0x0001 | 0x0080)
        #            self.previous_versions_tableWidget.setItem(i, 0, item)
        #            
        #            # ------------------------------------
        #            # type_name
        #            item = QtGui.QTableWidgetItem(vers.type.name)
        #            # align to center and vertical center
        #            item.setTextAlignment(0x0001 | 0x0080)
        #            self.previous_versions_tableWidget.setItem(i, 1, item)
        #            # ------------------------------------
        #            
        #            # ------------------------------------
        #            # take_name
        #            item = QtGui.QTableWidgetItem(vers.take_name)
        #            # align to center and vertical center
        #            item.setTextAlignment(0x0001 | 0x0080)
        #            self.previous_versions_tableWidget.setItem(i, 2, item)            
        #            # ------------------------------------
            
            is_published = vers.is_published
            
            # ------------------------------------
            # version_number
            item = QtGui.QTableWidgetItem(str(vers.version_number))
            # align to center and vertical center
            item.setTextAlignment(0x0004 | 0x0080)
            
            if is_published:
                set_font(item)
            
#            item.setFont(font_weight)
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
            # filesize
            item = QtGui.QTableWidgetItem("")
            # align to left and vertical center
            item.setTextAlignment(0x0001 | 0x0080)

            if is_published:
                set_font(item)
            
            self.previous_versions_tableWidget.setItem(i, 2, item)
            # ------------------------------------

            # ------------------------------------
            # note
            item = QtGui.QTableWidgetItem(vers.note)
            # align to left and vertical center
            item.setTextAlignment(0x0001 | 0x0080)

            if is_published:
                set_font(item)
            
            self.previous_versions_tableWidget.setItem(i, 3, item)
            # ------------------------------------

            # ------------------------------------
            # full_path
            item = QtGui.QTableWidgetItem(vers.full_path)
            # align to center and vertical center
            item.setTextAlignment(0x0001 | 0x0080)

            if is_published:
                set_font(item)
            
            self.previous_versions_tableWidget.setItem(i, 4, item)
            # ------------------------------------
        
        # resize the first column
        self.previous_versions_tableWidget.resizeColumnToContents(0)
        self.previous_versions_tableWidget.resizeColumnToContents(1)
        self.previous_versions_tableWidget.resizeColumnToContents(2)
        self.previous_versions_tableWidget.resizeColumnToContents(3)
        self.previous_versions_tableWidget.resizeColumnToContents(4)
#        self.previous_versions_tableWidget.resizeColumnToContents(5)
#        self.previous_versions_tableWidget.resizeColumnToContents(6)
#        self.previous_versions_tableWidget.resizeColumnToContents(7)
    
    def asset_description_edit_pushButton_clicked(self):
        """checks the asset_description_edit_pushButton
        """

        button = self.asset_description_edit_pushButton
        text_field = self.asset_description_textEdit
        
        # check or uncheck
        if button.text() != u"Done":
            # change the text to "Done"
            button.setText(u"Done")
            
            # make the text field read-write
            text_field.setReadOnly(False)
            
            # to discourage edits
            # disable the assets_listWidget
            self.assets_listWidget.setEnabled(False)
            
            # and the projects_comboBox
            self.projects_comboBox.setEnabled(False)
            
            # and the create_asset_pushButton
            self.create_asset_pushButton.setEnabled(False)
            
            # and the shots_tab
            self.shots_tab.setEnabled(False)
            
            # and the new_version_groupBox
            self.new_version_groupBox.setEnabled(False)
            
            # and the previous_versions_groupBox
            self.previous_versions_groupBox.setEnabled(False)
            
        else:
            asset_name = self.assets_listWidget.currentItem().text()
            
            # change the text to "Edit"
            button.setText("Edit")
            button.setStyleSheet("")
            text_field.setReadOnly(True)
            
            proj = self.get_current_project()
            asset = \
                db.query(Asset)\
                .filter(Asset.project==proj)\
                .filter_by(name=asset_name)\
                .first()
            
            # update the asset description
            logger.debug("asset description of %s changed to %s" % (
                    asset,
                    self.asset_description_textEdit.toPlainText()
                )
            )
            
            # only issue an update if the description has changed
            new_description = self.asset_description_textEdit.toPlainText()
            
            if asset.description != new_description:
                asset.description = new_description
                asset.save()

            # re-enable assets_listWidget
            self.assets_listWidget.setEnabled(True)

            # and the projects_comboBox
            self.projects_comboBox.setEnabled(True)

            # and the create_asset_pushButton
            self.create_asset_pushButton.setEnabled(True)

            # and the shots_tab
            self.shots_tab.setEnabled(True)
            
            # and the new_version_groupBox
            self.new_version_groupBox.setEnabled(True)
            
            # and the previous_versions_groupBox
            self.previous_versions_groupBox.setEnabled(True)
    
    def shot_description_edit_pushButton_clicked(self):
        """checks the shot_description_edit_pushButton
        """
        # TODO: organize the actions, first do what needs to be done and then update the interface
        
        button = self.shot_description_edit_pushButton
        text_field = self.shot_description_textEdit
        list_widget = self.shots_listWidget
        tab = self.assets_tab
        
        # check or uncheck
        if button.text() != u"Done":
            # change the text to "Done"
            button.setText(u"Done")
            
            # make the text field read-write
            text_field.setReadOnly(False)
            
            # to discourage edits
            # disable the assets_listWidget
            list_widget.setEnabled(False)
            
            # and the projects_comboBox
            self.projects_comboBox.setEnabled(False)
            
            # and the sequences_comboBox
            self.sequences_comboBox.setEnabled(False)
            
            # and the create_shot_pushButton
            self.create_shot_pushButton.setEnabled(False)
            
            # and the assets_tab
            tab.setEnabled(False)
            
            # and the new_version_groupBox
            self.new_version_groupBox.setEnabled(False)
            
            # and the previous_versions_groupBox
            self.previous_versions_groupBox.setEnabled(False)
        else:
            # change the text to "Edit"
            button.setText("Edit")
            button.setStyleSheet("")
            text_field.setReadOnly(True)
            
            index = self.shots_listWidget.currentIndex().row()
            shot = self.shots_listWidget.shots[index]
            
            # update the shot description
            logger.debug("shot description of %s changed to '%s'" % (
                    shot,
                    self.shot_description_textEdit.toPlainText()
                )
            )
            
            # only issue an update if the description has changed
            new_description = self.shot_description_textEdit.toPlainText()
            
            if shot.description != new_description:
                shot.description = new_description
                shot.save()
            
            # re-enable shots_listWidget
            list_widget.setEnabled(True)
            
            # and the projects_comboBox
            self.projects_comboBox.setEnabled(True)
            
            # and the create_asset_pushButton
            self.create_shot_pushButton.setEnabled(True)
            
            # and the sequences_comboBox
            self.sequences_comboBox.setEnabled(True)
            
            # and the shots_tab
            tab.setEnabled(True)
            
            # and the new_version_groupBox
            self.new_version_groupBox.setEnabled(True)
            
            # and the previous_versions_groupBox
            self.previous_versions_groupBox.setEnabled(True)
    
    def create_asset_pushButton_clicked(self):
        """
        """
        
        self.input_dialog = QtGui.QInputDialog(self)
        
#        print "self.input_dialog: %s " % self.input_dialog
        
        asset_name, ok = self.input_dialog.getText(
            self,
            "Enter new asset name",
            "Asset name:"
        )
        
        if not ok or asset_name == "":
            logger.debug("either canceled or the given asset_name is empty, "
                         "not creating a new asset")
            return
        
        proj = self.get_current_project()
        
        try:
            new_asset = Asset(proj, asset_name)
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
            asset_name = self.assets_listWidget.currentItem().text()
            versionable = \
                db.query(Asset)\
                .filter(Asset.project==proj)\
                .filter_by(name=asset_name)\
                .first()

            logger.debug("updating take list for asset: %s" % versionable.name)
        
        else:
            index = self.shots_listWidget.currentIndex().row()
            versionable = self.shots_listWidget.shots[index]
            
            logger.debug("updating take list for shot: %s" % versionable.code)
        
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
        version_type_name = self.version_types_comboBox.currentText()
        
        # get the version type instance
        return db.query(VersionType)\
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
        """adds new types to the version_types_comboBox
        """
        
        if not isinstance(version_type, VersionType):
            raise TypeError("please supply a "
                            "oyProjectManager.core.models.VersionType for the"
                            "type to be added to the version_type_comboBox")
        
        # check if the given type is suitable for the current versionable
        versionable = self.get_versionable()
        
        if versionable.__class__.__name__ != version_type.type_for:
            raise TypeError("The given version_type is not suitable for %s"
                            % self.tabWidget.tabText(
                self.tabWidget.currentIndex()
            ))
        
        index = self.version_types_comboBox.findText(version_type.name)
        
        if index == -1:
            self.version_types_comboBox.addItem(version_type.name)
            self.version_types_comboBox.setCurrentIndex(
                self.version_types_comboBox.count() - 1
            )
    
    def add_type_toolButton_clicked(self):
        """adds a new type for the currently selected Asset or Shot
        """
        proj = self.get_current_project()
        
        # get the versionable
        versionable = self.get_versionable()
        
        # get all the version types which doesn't have any version defined
        
        # get all the current types from the interface
        current_types = []
        for index in range(self.version_types_comboBox.count()):
            current_types.append(self.version_types_comboBox.itemText(index))
        
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
        
        type_name, ok = self.input_dialog.getItem(
            self,
            "Choose a VersionType",
            "Available Version Types for %ss in %s" % 
                (versionable.__class__.__name__, self.environment.name),
            available_types,
            0,
            False
        )
        
        # if ok add the type name to the end of the types_comboBox and make
        # it the current selection
        if ok:
            # get the type
            vers_type = db.query(VersionType).filter_by(name=type_name).first()
            
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
            # add the given text to the takes_comboBox
            # if it is not empty
            if take_name != "":
                self.takes_comboBox.addItem(take_name)
                # set the take to the new one
                self.takes_comboBox.setCurrentIndex(
                    self.takes_comboBox.count() - 1
                )
    
    def get_new_version(self):
        """returns a :class:`~oyProjectManager.core.models.Version` instance
        from the UI by looking at the input fields
        
        :returns: :class:`~oyProjectManager.core.models.Version` instance
        """
        
        # create a new version
        versionable = self.get_versionable()
        version_type = self.get_version_type()
        take_name = self.takes_comboBox.currentText()
        user = self.get_user()
        
        note = self.note_textEdit.toPlainText()
        
        published = self.publish_checkBox.isChecked()
        
        version = Version(
            versionable, versionable.code, version_type, user,
            take_name=take_name, note=note, is_published=published
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
        conf.last_user_id = new_version.created_by_id
        
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
            
            # environment can throw RuntimeError for unsaved changes
            
            try:
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
                
#                # check the to_update_list to update old versions
#                if len(to_update_list):
#                    # invoke the assetUpdater for this scene
#                    assetUpdaterMainDialog = version_updater.MainDialog(self.environment.name, self )
#                    assetUpdaterMainDialog.exec_()
                    
                self.environment.post_open(old_version)
        
        # close the dialog
        self.close()
    
    def reference_pushButton_clicked(self):
        """runs when the reference_pushButton clicked
        """
        
        # get the new version
        previous_version = self.get_previous_version()
        
        logger.debug("referencing version %s" % previous_version)
        
        # call the environments reference method
        if self.environment is not None:
            self.environment.reference(previous_version)
    
    def import_pushButton_clicked(self):
        """runs when the import_pushButton clicked
        """
        
        # get the previous version
        previous_version = self.get_previous_version()
        
        logger.debug("importing version %s" % previous_version)
        
        # call the environments import_ method
        if self.environment is not None:
            self.environment.import_(previous_version)
    
