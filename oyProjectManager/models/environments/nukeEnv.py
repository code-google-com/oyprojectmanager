# -*- coding: utf-8 -*-



import os
import platform
import nuke
import oyAuxiliaryFunctions as oyAux
from oyProjectManager.models import asset, project, abstractClasses, repository
from oyProjectManager import utils






########################################################################
class NukeEnvironment(abstractClasses.Environment):
    """the nuke environment class
    """
    
    
    
    #----------------------------------------------------------------------
    def __init__(self, asset=None, name='', extensions=None ):
        """nuke spesific init
        """
        # call the supers __init__
        super(NukeEnvironment, self).__init__(asset, name, extensions)
        
        # and add you own modifications to __init__
        # get the root node
        self._root = self.getRootNode()
        
        self._main_output_node_name = "MAIN_OUTPUT"
    
    
    
    #----------------------------------------------------------------------
    def getRootNode(self):
        """returns the root node of the current nuke session
        """
        
        return nuke.toNode("root")
    
    
    
    #----------------------------------------------------------------------
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
            # path already existsOSErro
            pass
        
        nuke.scriptSaveAs(fullPath)
        
        return True
    
    
    
    #----------------------------------------------------------------------
    def export(self):
        """the export action for nuke environment
        """
        
        # set the extension to 'nk'
        self._asset.extension = 'nk'
        
        fullPath = self._asset.fullPath
        
        # replace \\ with /
        fullPath = fullPath.replace('\\','/')
        
        nuke.nodeCopy( fullPath )
        
        return True
    
    
    
    #----------------------------------------------------------------------
    def open_(self, force=False):
        """the open action for nuke environment
        """
        
        fullPath = self._asset.fullPath
        
        # replace \\ with /
        fullPath = fullPath.replace('\\','/')
        
        nuke.scriptOpen(fullPath)
        
        # set the project_directory
        self.project_directory = self._asset.sequenceFullPath
        
        # TODO:
        # Check if the file paths are starting with a string matching one of the
        # OS'es project_directory path and replace them with a relative one
        # matching the current OS 
        
        # replace paths
        self.replace_file_path()
        
        return True
    
    
    
    #----------------------------------------------------------------------
    def import_(self):
        """the import action for nuke environment
        """
        
        fullPath = self._asset.fullPath
        
        # replace \\ with /
        fullPath = fullPath.replace('\\','/')
        
        nuke.nodePaste( fullPath )
        return True
    
    
    
    #----------------------------------------------------------------------
    def getPathVariables(self):
        """gets the file name from nuke
        """
        
        fullPath = path = fileName = None
        fullPath = self._root.knob('name').value()
        
        
        if fullPath != None and fullPath != '':
            # for winodws replace the path seperator
            if os.name == 'nt':
                fullPath = fullPath.replace('/','\\')
            
            fileName = os.path.basename( fullPath )
            path = os.path.dirname( fullPath )
        else:
            
            # use the last file from the recent file list
            fullPath = nuke.recentFile(1)
            
            # for winodws replace the path seperator
            if os.name == 'nt':
                fullPath = fullPath.replace('/','\\')
            
            fileName = os.path.basename( fullPath )
            path = os.path.dirname( fullPath )
            
        return fileName, path
    
    
    
    #----------------------------------------------------------------------
    def getFrameRange(self):
        """returns the current frame range
        """
        #self._root = self.getRootNode()
        startFrame = int(self._root.knob('first_frame').value())
        endFrame = int(self._root.knob('last_frame').value())
        return startFrame, endFrame
    
    
    
    #----------------------------------------------------------------------
    def setFrameRange(self, startFrame=1, endFrame=100):
        """sets the start and end frame range
        """
        #self._root = self.getRootNode()
        self._root.knob('first_frame').setValue(startFrame)
        self._root.knob('last_frame').setValue(endFrame)
    
    
    #----------------------------------------------------------------------
    def setTimeUnit(self, timeUnit='pal'):
        """sets the current time unit
        """
        
        # get the fps value of the given time unit
        repo = repository.Repository()
        
        try:
            fps = repo.time_units[timeUnit]
        except KeyError:
            # set it to pal by default
            fps = repo.time_units['pal']
        
        self._root.knob('fps').setValue(fps)
    
    
    
    #----------------------------------------------------------------------
    def getTimeUnit(self):
        """returns the current time unit
        """
        
        currentFps = int(self._root.knob('fps').getValue())
        
        repo = repository.Repository()
        time_units = repo.time_units
        
        # by default set it to pal
        timeUnit = 'pal'
        
        for timeUnitName, timeUnitFps in time_units.iteritems():
            if currentFps == timeUnitFps:
                timeUnit = timeUnitName
                break
        
        return timeUnit
    
    
    
    #----------------------------------------------------------------------
    def get_main_write_node(self):
        """Returns the main write node in the scene or None.
        """
        
        # list all the write nodes in the current file
        all_write_nodes = nuke.allNodes("Write")
        
        main_write_node = None
        
        for write_node in all_write_nodes:
            if write_node.name().startswith(self._main_output_node_name):
                main_write_node = write_node
                return main_write_node
        
        return None
    
    
    
    #----------------------------------------------------------------------
    def create_main_write_node(self):
        """creates the default write node if there is no one created before.
        """
        
        # list all the write nodes in the current file
        main_write_node = self.get_main_write_node()
        
        if main_write_node is None:
            # create one with correct output path
            main_write_node = nuke.nodes.Write()
            main_write_node.setName(self._main_output_node_name)
        
        # set the output path
        
        assert(isinstance(self._asset, asset.Asset))
        
        seq = self._asset.sequence
        assert(isinstance(seq, project.Sequence))
        
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
        platform_system = platform.system()
        
        format_id = 7
        if platform_system == "Darwin":
            format_id = 6
            # check the nuke version for nuke 6.2 and below
            if (nuke.NUKE_VERSION_MAJOR + nuke.NUKE_VERSION_MINOR/10.0) < 6.3:
                format_id = 8
        
        main_write_node["file_type"].setValue(format_id)
        main_write_node["channels"].setValue("rgb")
    
    
    
    #----------------------------------------------------------------------
    def replace_file_path(self):
        """replaces file paths with environment variable scripts
        """
        
        repo = repository.Repository()
        
        # TODO:
        # check if the project_directory is still the same
        # if it is do the regular replacement
        # but if it is not then expand all the paths to absolute paths
        
        
        # convert the given path to tcl environment script
        def repPath(path):
            #return path.replace(repo.server_path, env_str)
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
    
    
    
    #----------------------------------------------------------------------
    def project_directory():
        def fget(self):
            #return self._project_directory
            root = self.getRootNode()
            return root["project_directory"].getValue()
        
        def fset(self, project_directory_in):
            
            project_directory_in = project_directory_in.replace("\\", "/")
            
            root = self.getRootNode()
            root["project_directory"].setValue(project_directory_in)
        
        doc = """The project directory.
        
        Set it to the project root, and set all your paths relative to this
        directory.
        """
        
        return locals()
    
    project_directory = property(**project_directory())
    
