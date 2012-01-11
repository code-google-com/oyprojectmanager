# -*- coding: utf-8 -*-
# Copyright (c) 2009-2012, Erkan Ozgur Yilmaz
# 
# This module is part of oyProjectManager and is released under the BSD 2
# License: http://www.opensource.org/licenses/BSD-2-Clause

import os
import platform

import nuke
from oyProjectManager.core.models import EnvironmentBase
from oyProjectManager import utils


class Nuke(EnvironmentBase):
    """the nuke environment class
    """
    
    name = "Nuke"
    
    def __init__(self, version=None, name='', extensions=None):
        """nuke specific init
        """
#        # call the supers __init__
#        super(Nuke, self).__init__(asset, name, extensions)
        
        # and add you own modifications to __init__
        # get the root node
        self._root = self.get_root_node()
        
        self._main_output_node_name = "MAIN_OUTPUT"
    
    
    def get_root_node(self):
        """returns the root node of the current nuke session
        """
        return nuke.toNode("root")
    
    def save_as(self, version):
        """"the save action for nuke environment
        
        uses Nukes own python binding
        """
        
        # set the extension to '.nk'
        version.extension = '.nk'
        
        # set project_directory
        self.project_directory = os.path.dirname(version.path)
        
        # create the main write node
        self.create_main_write_node(version)
        
        # replace read and write node paths
        self.replace_file_path()
        
        # create the path before saving
        try:
            os.makedirs(version.path)
        except OSError:
            # path already exists OSError
            pass
        
        nuke.scriptSaveAs(version.full_path)
        
        return True
    
    def export_as(self, version):
        """the export action for nuke environment
        """
        # set the extension to '.nk'
        version.extension = '.nk'
        nuke.nodeCopy(version.fullPath)
        return True
    
    def open_(self, version, force=False):
        """the open action for nuke environment
        """
        nuke.scriptOpen(version.full_path)
        
        # set the project_directory
        self.project_directory = os.path.dirname(version.path)
        
        # TODO: file paths in different OS'es should be replaced with the current one
        # Check if the file paths are starting with a string matching one of the
        # OS'es project_directory path and replace them with a relative one
        # matching the current OS 
        
        # replace paths
        self.replace_file_path()
        
        return True
    
    def import_(self, version):
        """the import action for nuke environment
        """
        nuke.nodePaste(version.full_path)
        return True

    def get_current_version(self):
        """Finds the Version instance from the current open file.
        
        If it can't find any then returns None.
        
        :return: :class:`~oyProjectManager.core.models.Version`
        """
        full_path = self._root.knob('name').value()
        return self.get_version_from_full_path(full_path)
    
    def get_version_from_recent_files(self):
        """It will try to create a
        :class:`~oyProjectManager.core.models.Version` instance by looking at
        the recent files list.
        
        It will return None if it can not find one.
        
        :return: :class:`~oyProjectManager.core.models.Version`
        """
        # use the last file from the recent file list
        i = 1
        while True:
            try:
                full_path = nuke.recentFile(i)
            except RuntimeError:
                # no recent file anymore just return None
                return None
            i += 1
            
            version = self.get_version_from_full_path(full_path)
            if version is not None:
                return version
    
    def get_version_from_project_dir(self):
        """Tries to find a Version from the current project directory
        
        :return: :class:`~oyProjectManager.core.models.Version`
        """
        versions = self.get_versions_from_path(self.project_directory)
        version = None
        
        if len(versions):
            version = versions[0]
        
        return version
    
    def get_last_version(self):
        """gets the file name from nuke
        """
        version = self.get_current_version()
        
        # read the recent file list
        if version is None:
            version = self.get_version_from_recent_files()

        # get the latest possible Version instance by using the workspace path
        if version is None:
            version = self.get_version_from_project_dir()

        return version
    
    def get_frame_range(self):
        """returns the current frame range
        """
        #self._root = self.get_root_node()
        startFrame = int(self._root.knob('first_frame').value())
        endFrame = int(self._root.knob('last_frame').value())
        return startFrame, endFrame
    
    def set_frame_range(self, start_frame=1, end_frame=100,
                        adjust_frame_range=False):
        """sets the start and end frame range
        """
        self._root.knob('first_frame').setValue(start_frame)
        self._root.knob('last_frame').setValue(end_frame)
    
    def set_fps(self, fps=25):
        """sets the current fps
        """
        self._root.knob('fps').setValue(fps)
    
    def get_fps(self):
        """returns the current fps
        """
        return int(self._root.knob('fps').getValue())
    
    def get_main_write_node(self):
        """Returns the main write node in the scene or None.
        """
        # list all the write nodes in the current file
        all_write_nodes = nuke.allNodes("Write")
        
        for write_node in all_write_nodes:
            if write_node.name().startswith(self._main_output_node_name):
                main_write_node = write_node
                return main_write_node
        
        return None
    
    def create_main_write_node(self, version):
        """creates the default write node if there is no one created before.
        """
        
        # list all the write nodes in the current file
        main_write_node = self.get_main_write_node()
        
        if main_write_node is None:
            # create one with correct output path
            main_write_node = nuke.nodes.Write()
            main_write_node.setName(self._main_output_node_name)
        
        # set the output path
        output_file_name = version.project.code
        
        if version.type.type_for == "Shot":
            output_file_name += "_" + version.version_of.sequence.code + "_"
        
        output_file_name += \
            version.base_name + "_" + \
            version.take_name + "_" + \
            "Output_" + \
            "v%03d" % version.version_number + "_" + \
            version.created_by.initials + ".###.jpg"
        
        # check if it is a stereo comp
        # if it is enable separate view rendering
        
        output_file_full_path = os.path.join(
            version.output_path,
            output_file_name
        ).replace("\\", "/")
        
        main_write_node["file"].setValue(output_file_full_path)
        
        # create the path
        try:
            os.makedirs(os.path.dirname(output_file_full_path))
        except OSError:
            # path already exists
            pass
        
        # set the default output file type to jpeg
        platform_system = platform.system()
        
        format_id = 7
        if platform_system == "Darwin":
            format_id = 6
            # check the nuke version for nuke 6.2 and below
            if (nuke.NUKE_VERSION_MAJOR + nuke.NUKE_VERSION_MINOR/10.0) < 6.3:
                format_id = 8
        
        main_write_node["file_type"].setValue(format_id)
        main_write_node["channels"].setValue("rgb")
    
    def replace_file_path(self):
        """replaces file paths with environment variable scripts
        """
        
        # TODO: replace file paths if project_directory changes
        # check if the project_directory is still the same
        # if it is do the regular replacement
        # but if it is not then expand all the paths to absolute paths
        
        # convert the given path to tcl environment script
        def repPath(path):
            return utils.relpath(self.project_directory, path, "/", "..")
        
        # get all read nodes
        allNodes = nuke.allNodes()
        
        readNodes = [node for node in allNodes if node.Class() == "Read"]
        writeNodes = [node for node in allNodes if node.Class() == "Write"]
        readGeoNodes = [node for node in allNodes if node.Class() == "ReadGeo"]
        readGeo2Nodes = [node for node in allNodes if node.Class() == "ReadGeo2"]
        writeGeoNodes = [node for node in allNodes if node.Class() == "WriteGeo"]
        
        def nodeRep(nodes):
            [node["file"].setValue(
                repPath(
                    os.path.expandvars(
                        os.path.expanduser(
                            node["file"].getValue()
                        )
                    )
                )
            ) for node in nodes]
        
        nodeRep(readNodes)        
        # the fucking windows is complaining about back-slashes again
        # in the write nodes so the write nodes are going to be absolute
        # path
        if os.name != "nt":
            nodeRep(writeNodes)
        nodeRep(readGeoNodes)
        nodeRep(readGeo2Nodes)
        nodeRep(writeGeoNodes)
    
    @property
    def project_directory(self):
        """The project directory.
        
        Set it to the project root, and set all your paths relative to this
        directory.
        """
        
        root = self.get_root_node()
        
        # TODO: root node gets lost, fix it
        # there is a bug in Nuke, the root node get lost time to time find 
        # the source and fix it.
#        if root is None:
#            # there is a bug about Nuke,
#            # sometimes it losses the root node, while it shouldn't
#            # I can't find the source
#            # so instead of using the root node,
#            # just return the os.path.dirname(version.path)
#            
#            return os.path.dirname(self.version.path)
        
        return root["project_directory"].getValue()
    
    @project_directory.setter
    def project_directory(self, project_directory_in):
        
        project_directory_in = project_directory_in.replace("\\", "/")
        
        root = self.get_root_node()
        root["project_directory"].setValue(project_directory_in)
