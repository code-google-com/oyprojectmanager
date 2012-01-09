# -*- coding: utf-8 -*-
# Copyright (c) 2009-2012, Erkan Ozgur Yilmaz
# 
# This module is part of oyProjectManager and is released under the BSD 2
# License: http://www.opensource.org/licenses/BSD-2-Clause

import os
import hou
import re
from oyProjectManager.core.models import Asset, Project, Sequence, Repository, EnvironmentBase
from oyProjectManager import utils


class Houdini(EnvironmentBase):
    """the houdini environment class
    """
    
    def save(self):
        """the save action for houdini environment
        """
        
        # set the extension to hip
        self._asset.extension = 'hip'
        
        # create the folder if it doesn't exists
        utils.createFolder( self._asset.path )
        
        # houdini uses / instead of \ under windows
        # lets fix it
        
        fullPath = self._asset.fullPath
        fullPath = fullPath.replace('\\','/')
        
        # *************************************************************
        # trying to set the render file name while the file has not been
        # saved before creates an error
        # so save the file two times if it is not saved before
        
        ## check if the HIP environment variable has some data
        #if os.environ["HIP"] == os.environ["HOME"]:
        # save the file to create a meaningful HIP variable
        hou.hipFile.save(file_name=str(fullPath))

        # set the environment variables
        self.setEnvironmentVariables()
        
        # set the render file name
        self.setRenderFileName()
        
        # houdini accepts only strings as file name, no unicode support as I
        # see
        hou.hipFile.save(file_name=str(fullPath))
        
        # set the environment variables
        self.setEnvironmentVariables()
        
        return True
    
    
    
    
    def open_(self, force=False):
        """the open action for houdini environment
        """
        
        if hou.hipFile.hasUnsavedChanges() and not force:
            raise RuntimeError
        
        fullPath = self._asset.fullPath
        fullPath = fullPath.replace('\\','/')
        
        hou.hipFile.load(file_name=str(fullPath), suppress_save_prompt=True)
        
        # set the environment variables
        self.setEnvironmentVariables()
        
        return True
    
    
    
    
    def import_(self):
        """the import action for houdini environment
        """
        
        fullPath = self._asset.fullPath
        fullPath = fullPath.replace('\\','/')
        
        hou.hipFile.merge( str(fullPath) )
        
        return True
    
    
    
    
    def get_last_version(self):
        """gets the file name from houdini environment
        """
        
        foundValidAsset = False
        readRecentFile = True
        fileName = path = None
        
        repo = Repository()
        
        fullPath = hou.hipFile.name()
        
        # unfix windows path
        if os.name == 'nt':
            fullPath = fullPath.replace('/','\\')
        
        
        if fullPath != 'untitled.hip':
            fileName = os.path.basename( fullPath )
            path = os.path.dirname( fullPath )
            
            # try to create an asset with that info
            projName, seqName = repo.get_project_and_sequence_name_from_file_path( fullPath )
            
            if not projName is None and not seqName is None: 
                proj = Project(projName)
                seq = Sequence(proj, seqName)
            
            
                testAsset = Asset(proj, seq, fileName)
            
                if testAsset.isValidAsset:
                    fileName = testAsset.fileName
                    path = testAsset.path
                    readRecentFile = False
            else:
                # no good file name
                readRecentFile = True
        
        if readRecentFile:
            # there is no file oppend yet use the first valid file
            # from the recent files list
            
            recentFiles = self.getRecentFileList()
            
            # unfix the windows paths from / to \\
            if os.name == 'nt':
                recentFiles = [recentFile.replace('/','\\') for recentFile in recentFiles]
            
            for i in range(len(recentFiles)-1,0,-1):
                
                fileName = os.path.basename( recentFiles[i] )
                projName, seqName = repo.get_project_and_sequence_name_from_file_path( recentFiles[i] )
                
                if projName != None and seqName != None:
                    
                    proj = Project( projName )
                    seq = Sequence( proj, seqName )
                    
                    testAsset = Asset( proj, seq, fileName )
                    
                    if testAsset.isValidAsset:
                        path = testAsset.path
                        foundValidAsset = True
                        break
        
        return fileName, path
    
    
    
    
    def setEnvironmentVariables(self):
        """sets the environment variables according to the given assetObject
        """
        # set the $JOB variable to the sequence root
        repo = repository.Repository()
        #repo_env_key = "$" + repo.repository_path_env_key
        
        #asset_path = str(self._asset.fullpath).replace("\\", "/")
        sequence_path = str(self._asset.sequenceFullPath).replace('\\','/')
        
        # convert the sequence path to a self.repository_path_env_key relative 
        sequence_path = repo.relative_path(sequence_path)
        
        # update the environment variables
        os.environ.update({"JOB": str(sequence_path)})
        
        # also set it using hscript, hou is a little bit problematic
        hou.hscript("set -g JOB = '" + str(sequence_path) + "'")
        hou.allowEnvironmentVariableToOverwriteVariable("JOB", True)
        #hou.hscript(
        #    "set -g " + repo.repository_path_env_key + " = '" + \
        #    str(os.environ[repo.repository_path_env_key]) + "'"
        #)
    
    
    
    
    def getRecentFileList(self):
        """returns the recent HIP files list from the houdini
        """
        
        # use a FileHistory object
        fHist = FileHistory()
        
        # get the hip files list
        recentHipFiles = fHist.getRecentFiles('HIP')
        
        return recentHipFiles
    
    
    
    
    def getFrameRange(self):
        """returns the frame range of the
        """
        # use the hscript commands to get the frame range
        timeInfo = hou.hscript('tset')[0].split('\n')
        
        pattern = r'[-0-9\.]+'
        
        startFrame = int( hou.timeToFrame( float( re.search( pattern, timeInfo[2] ).group(0) ) ) )
        duration = int( re.search( pattern, timeInfo[0] ).group(0) )
        endFrame = startFrame + duration - 1
        
        return startFrame, endFrame
    
    
    
    
    def setFrameRange(self, startFrame=1, endFrame=100):
        """sets the frame range
        """
        
        # --------------------------------------------
        # set the timeline
        currFrame = hou.frame()
        if currFrame < startFrame:
            hou.setFrame( startFrame )
        elif currFrame > endFrame:
            hou.setFrame( endFrame )
        
        # for now use hscript, the python version is not implemented yet
        hou.hscript('tset `('+ str(startFrame) +'-1)/$FPS` `'+ str(endFrame)+'/$FPS`')
        
        # --------------------------------------------
        # Set the render nodes frame ranges if any
        # get the out nodes
        outNodes = self.getOutputNodes()
        
        for outNode in outNodes:
            outNode.setParms( {'trange':0,'f1':startFrame,'f2':endFrame,'f3':1})
    
    
    
    
    def getOutputNodes(self):
        """returns the rop nodes in the scene
        """
        ropContext = hou.node('/out')
        
        # get the children
        outNodes = ropContext.children()
        
        exclude_node_types = [
            hou.nodeType(hou.nodeTypeCategories()["Driver"], "wedge")
        ]
        
        # remove nodes in type in exclude_node_types list
        new_out_nodes = [node for node in outNodes
                         if node.type() not in exclude_node_types]
        
        return new_out_nodes
    
    
    
    
    def getTimeUnit(self):
        """returns the current time unit
        """
        
        repo = repository.Repository()
        time_units = repo.time_units
        
        currentFps = int(hou.fps())
        
        timeUnit = 'pal'
        
        for timeUnitName, timeUnitFps in time_units.iteritems():
            if currentFps == timeUnitFps:
                timeUnit = timeUnitName
                break
        
        return timeUnit
    
    
    
    
    def setRenderFileName(self):
        """sets the render file name
        """
        # M:/JOBs/PRENSESIN_UYKUSU/SC_008/_RENDERED_IMAGES_/_SHOTS_/SH008/MasalKusu/`$OS`/SH008_MasalKusu_`$OS`_v006_oy.$F4.exr
        # $REPO/PRENSESIN_UYKUSU/SC_008/_RENDERED_IMAGES_/_SHOTS_/SH008/MasalKusu/`$OS`/SH008_MasalKusu_`$OS`_v006_oy.$F4.exr
        seq = self._asset.sequence
        renderOutputFolder = self._asset.output_path # RENDERED_IMAGES/{{assetBaseName}}/{{assetSubName}}
        assetBaseName = self._asset.baseName
        assetSubName = self._asset.subName
        versionString = self._asset.versionString
        userInitials = self._asset.userInitials
        
        #outputFileName = renderOutputFolder + "/" + assetBaseName + "/" + \
        #               assetSubName + "/`$OS`/" + assetBaseName + "_" + \
        #               assetSubName + "_`$OS`_" + versionString + "_" + \
        #               userInitials + ".$F4.exr"
       
        outputFileName = os.path.join(
                             renderOutputFolder, "`$OS`",
                             assetBaseName + "_" + assetSubName + "_`$OS`_" + \
                             versionString + "_" + userInitials + ".$F4.exr"
                         )
        
        outputFileName = outputFileName.replace('\\','/')
        
        # compute a $JOB relative file path
        # which is much safer if the file is going to be render in multiple oses
        # $HIP = the current asset path
        # $JOB = the current sequence path
        #hip = self._asset.path
        #hip = hou.getenv("HIP")
        job = hou.getenv("JOB")
        # eliminate environment vars
        while "$" in job:
            job = os.path.expandvars(job)
        
        #hip_relative_output_file_path = "$HIP/" + utils.relpath(hip, outputFileName, "/", "..")
        job_relative_output_file_path = "$JOB/" + utils.relpath(job, outputFileName, "/", "..")
        
        outputNodes = self.getOutputNodes()
        for outputNode in outputNodes:
            # get only the ifd nodes for now
            if outputNode.type().name() == 'ifd':
                # set the file name
                #outputNode.setParms({'vm_picture': str(outputFileName)})
                outputNode.setParms({'vm_picture': str(job_relative_output_file_path)})
                
                # set the compression to zips (zip, single scanline)
                outputNode.setParms({"vm_image_exr_compression": "zips"})
                
                # also create the folders
                outputFileFullPath = outputNode.evalParm('vm_picture')
                outputFilePath = os.path.dirname(outputFileFullPath)
                
                print "outputFileFullPath: ", outputFileFullPath 
                
                utils.createFolder(
                    os.path.expandvars(
                        os.path.expandvars(outputFilePath)
                    )
                )
    
    
    
    
    def setTimeUnit(self, timeUnit='pal'):
        """sets the time unit of the environment
        """
        
        repo = repository.Repository()
        
        try:
            timeUnitFps = float(repo.time_units[timeUnit])
        except KeyError:
            # set it to pal by default
            timeUnit='pal'
            timeUnitFps = float(repo.time_units[timeUnit])
        
        # keep the current start and end time of the time range
        startFrame, endFrame = self.getFrameRange()
        hou.setFps(timeUnitFps)
        
        self.setFrameRange(startFrame, endFrame)
    
    
    
    
    def replace_paths(self):
        """replaces all the paths in all the path related nodes
        """
        
        # get all the nodes and their childs and
        # try to get string and file path parameters
        # and replace them if they contain absolute paths
        pass







class FileHistory( abstractClasses.Singleton ):
    """a houdini recent file history parser
    
    holds the data in a dictionary, where the keys are the file types and the
    values are string list of recent file paths of that type
    """
    
    
    def __init__(self):
        self._historyFileName = 'file.history'
        
        self._historyFilePath = ''
        
        if os.name == 'nt':
            # under windows the HIH is useless
            # interpret the HIH from POSE environment variable
            
            self._historyFilePath = os.path.dirname( os.getenv('POSE') )
        else:
            self._historyFilePath = os.getenv('HIH')
        
        self._historyFileFullPath = os.path.join( self._historyFilePath, self._historyFileName )
        
        self._buffer =  []
        
        self._history = dict()
        
        self._read()
        self._parse()
    
    
    
    
    def _read(self):
        """reads the history file to a buffer
        """
        try:
            historyFile = open( self._historyFileFullPath )
        except IOError:
            self._buffer = []
            return
        
        self._buffer = historyFile.readlines()
        
        # strip all the lines
        self._buffer = [ line.strip() for line in self._buffer ]
        
        historyFile.close()
    
    
    
    
    def _parse(self):
        """parses the data in self._buffer
        """
        
        self._history = dict()
        
        bufferList = self._buffer
        
        keyName = ''
        pathList = []
        
        lenBuffer = len(bufferList)
        
        for i in range(lenBuffer):
            
            # try to find a '{'
            if bufferList[i] == '{':
                # create a key with the previous line
                keyName = bufferList[i-1]
                pathList = []
                
                # starting from the next line
                for j in range(i+1, lenBuffer ):
                    
                    # add all the lines to the pathList until you find a '}'
                    currentElement = bufferList[j]
                    if  currentElement != '}':
                        pathList.append( currentElement )
                    else:
                        # set i to j+1 and let it continue
                        i = j + 1
                        break
                
                # append the key and data to the dictionary
                self._history[ keyName ] = pathList
    
    
    
    
    def getRecentFiles(self, typeName=''):
        """returns the file list of the given file type
        """
        
        if typeName == '' or typeName == None:
            return []
        else:
            if self._history.has_key( typeName ):
                return self._history[ typeName ]
            else:
                return []
