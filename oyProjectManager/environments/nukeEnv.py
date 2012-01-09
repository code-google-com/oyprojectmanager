# -*- coding: utf-8 -*-
# Copyright (c) 2009-2012, Erkan Ozgur Yilmaz
# 
# This module is part of oyProjectManager and is released under the BSD 2
# License: http://www.opensource.org/licenses/BSD-2-Clause

import os
import nukeEnv
from oyProjectManager.core.models import Asset, Sequence, Repository, EnvironmentBase
from oyProjectManager import utils


class Nuke(EnvironmentBase):
    """the nuke environment class
    """
    
    def __init__(self, asset=None, name='', extensions=None ):
        """nuke specific init
        """
        # call the supers __init__
        super(Nuke, self).__init__(asset, name, extensions)
        
        # and add you own modifications to __init__
        # get the root node
        self._root = self.getRootNode()
        
        self._main_output_node_name = "MAIN_OUTPUT"
    
    
    def getRootNode(self):
        """returns the root node of the current nuke session
        """
        return nukeEnv.toNode("root")
    
    def save(self):
        """"the save action for nuke environment
        
        uses Nukes own python binding
        """
        
        # set the extension to 'nk'
        self._asset.extension = 'nk'
        
        fullPath = self._asset.fullPath
        fullPath = fullPath.replace('\\','/')
        
        # set project_directory
        self.project_directory = self._asset.sequenceFullPath
        
        # create the main write node
        self.create_main_write_node()
        
        # replace read and write node paths
        self.replace_file_path()
        
        # create the path before saving
        try:
            os.makedirs(os.path.dirname(fullPath))
        except OSError:
            # path already exists OSError
            pass
        
        nukeEnv.scriptSaveAs(fullPath)
        
        return True
    
    def export(self, asset):
        """the export action for nuke environment
        """
        # set the extension to 'nk'
        asset.extension = 'nk'
        
        fullPath = asset.fullPath
        
        # replace \\ with /
        fullPath = fullPath.replace('\\','/')
        
        nukeEnv.nodeCopy(fullPath)
        
        return True
    
    def open_(self, force=False):
        """the open action for nuke environment
        """
        
        fullPath = self._asset.fullPath
        
        # replace \\ with /
        fullPath = fullPath.replace('\\','/')
        
        nukeEnv.scriptOpen(fullPath)
        
        # set the project_directory
        self.project_directory = self._asset.sequenceFullPath
        
        # TODO: file paths in different OS'es should be replaced with the current one
        # Check if the file paths are starting with a string matching one of the
        # OS'es project_directory path and replace them with a relative one
        # matching the current OS 
        
        # replace paths
        self.replace_file_path()
        
        return True
    
    def import_(self, asset):
        """the import action for nuke environment
        """
        fullPath = asset.fullPath
        
        # replace \\ with /
        fullPath = fullPath.replace('\\','/')
        
        nukeEnv.nodePaste( fullPath )
        
        return True
    
    def get_last_version(self):
        """gets the file name from nuke
        """
        
        fullPath = path = fileName = None
        fullPath = self._root.knob('name').value()
        
        
        if fullPath is not None and fullPath != '':
            # for windows replace the path separator
            if os.name == 'nt':
                fullPath = fullPath.replace('/','\\')
            
            fileName = os.path.basename( fullPath )
            path = os.path.dirname( fullPath )
        else:
            
            # use the last file from the recent file list
            fullPath = nukeEnv.recentFile(1)
            
            # for windows replace the path separator
            if os.name == 'nt':
                fullPath = fullPath.replace('/','\\')
            
            fileName = os.path.basename( fullPath )
            path = os.path.dirname( fullPath )
        
        return fileName, path
    
    def getFrameRange(self):
        """returns the current frame range
        """
        #self._root = self.getRootNode()
        startFrame = int(self._root.knob('first_frame').value())
        endFrame = int(self._root.knob('last_frame').value())
        return startFrame, endFrame
    
    def setFrameRange(self, startFrame=1, endFrame=100):
        """sets the start and end frame range
        """
        #self._root = self.getRootNode()
        self._root.knob('first_frame').setValue(startFrame)
        self._root.knob('last_frame').setValue(endFrame)
    
    def setTimeUnit(self, timeUnit='pal'):
        """sets the current time unit
        """
        # get the fps value of the given time unit
        repo = Repository()
        
        try:
            fps = repo.time_units[timeUnit]
        except KeyError:
            # set it to pal by default
            fps = repo.time_units['pal']
        
        self._root.knob('fps').setValue(fps)
    
    def getTimeUnit(self):
        """returns the current time unit
        """
        currentFps = int(self._root.knob('fps').getValue())
        
        repo = Repository()
        time_units = repo.time_units
        
        # by default set it to pal
        timeUnit = 'pal'
        
        for timeUnitName, timeUnitFps in time_units.iteritems():
            if currentFps == timeUnitFps:
                timeUnit = timeUnitName
                break
        
        return timeUnit
    
    def get_main_write_node(self):
        """Returns the main write node in the scene or None.
        """
        # list all the write nodes in the current file
        all_write_nodes = nukeEnv.allNodes("Write")
        
        for write_node in all_write_nodes:
            if write_node.name().startswith(self._main_output_node_name):
                main_write_node = write_node
                return main_write_node
        
        return None
    
    def create_main_write_node(self):
        """creates the default write node if there is no one created before.
        """
        
        # list all the write nodes in the current file
        main_write_node = self.get_main_write_node()
        
        if main_write_node is None:
            # create one with correct output path
            main_write_node = nukeEnv.nodes.Write()
            main_write_node.setName(self._main_output_node_name)
        
        # set the output path
        
        assert(isinstance(self._asset, Asset))
        
        seq = self._asset.sequence
        assert(isinstance(seq, Sequence))
        
        output_file_name = self._asset.baseName + "_" + \
                           self._asset.subName + "_" + \
                           "OUTPUT_" + \
                           self._asset.revisionString + "_" + \
                           self._asset.versionString + "_" + \
                           self._asset.userInitials + ".###.jpg"
        
        # check if it is a stereo comp
        # if it is enable seperate view rendering
        
        
        output_file_full_path = os.path.join(
            seq.fullPath,
            self._asset.output_path,
            output_file_name
        )
        
        output_file_full_path = \
            output_file_full_path.replace("\\", "/")
        
        main_write_node["file"].setValue(output_file_full_path)
        
        # create the path
        try:
            os.makedirs(os.path.dirname(output_file_full_path))
        except OSError:
            # path already exists
            pass
        
        # set the default output file type to jpeg
        format_id = 7
        if os.name != "nt":
            # check the nuke version for nuke 6.2 and below
            if (nukeEnv.NUKE_VERSION_MAJOR + nukeEnv.NUKE_VERSION_MINOR/10.0) < 6.3:
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
        allNodes = nukeEnv.allNodes()
        
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
        
        root = self.getRootNode()
        
        # TODO: root node gets lost, fix it
        # there is a bug in Nuke, the root node get lost time to time find 
        # the source and fix it.
        if root is None:
            # there is a bug about Nuke,
            # sometimes it losses the root node, while it shouldn't
            # I can't find the source
            # so instead of using the root node,
            # just return the sequence.fullpath
            
            return self.asset.sequence.fullPath
        
        return root["project_directory"].getValue()
    
    @project_directory.setter
    def project_directory(self, project_directory_in):
        
        project_directory_in = project_directory_in.replace("\\", "/")
        
        root = self.getRootNode()
        root["project_directory"].setValue(project_directory_in)
