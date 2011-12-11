# -*- coding: utf-8 -*-

import os
from pymel import versions
from pymel import core as pm
import maya.cmds as mc

from oyProjectManager import conf, db
from oyProjectManager.core.models import (Asset, Project, Sequence, Repository,
                                          EnvironmentBase, Version)
from oyProjectManager import utils


class Maya(EnvironmentBase):
    """the maya environment class
    """
    
    name = "Maya"
    
    time_to_fps = {
        u'sec': 1,
        u'2fps': 2,
        u'3fps': 3,
        u'4fps': 4,
        u'5fps': 5,
        u'6fps': 6,
        u'8fps': 8,
        u'10fps': 10,
        u'12fps': 12,
        u'game': 15,
        u'16fps': 16,
        u'20fps': 20,
        u'film': 24,
        u'pal': 25,
        u'ntsc': 30,
        u'40fps': 40,
        u'show': 48,
        u'palf': 50,
        u'ntscf': 60,
        u'75fps': 75,
        u'80fps': 80,
        u'100fps': 100,
        u'120fps': 120,
        u'125fps': 125,
        u'150fps': 150,
        u'200fps': 200,
        u'240fps': 240,
        u'250fps': 250,
        u'300fps': 300,
        u'375fps': 375,
        u'400fps': 400,
        u'500fps': 500,
        u'600fps': 600,
        u'750fps': 750,
        u'millisec': 1000,
        u'1200fps': 1200,
        u'1500fps': 1500,
        u'2000fps': 2000,
        u'3000fps': 3000,
        u'6000fps': 6000,
    }
    
    def save_as(self, version):
        """the save_as action for maya environment

        uses PyMel to save the file (not necessary but comfortable)
        """
        
        # set asset extension
        version.extension = '.ma'
        
        # create a workspace file at the parent folder of the current version
        workspace_path = os.path.dirname(version.path)
        
        self.create_workspace_file(workspace_path)
        pm.workspace.open(workspace_path)
        
        # set the render file name and version
        self.set_render_fileName(version)
        
        # set the playblast file name
        self.set_playblast_file_name(version)
        
        # create the folder if it doesn't exists
        utils.createFolder(version.path)
        
        # delete the unknown nodes
        unknownNodes = pm.ls(type='unknown')
        pm.delete(unknownNodes)
        
        # set the file paths for external resources
        self.replace_external_paths(version)
        
        # save the file
        pm.saveAs(
            version.fullpath,
            type='mayaAscii'
        )
        
        # append it to the recent file list
        self.appendToRecentFiles(
            version.fullpath
        )
        
        return True
    
    def export_as(self, version):
        """the export action for maya environment
        """
        
        # check if there is something selected
        if len(pm.ls(sl=True)) < 1:
            raise RuntimeError("There is nothing selected to export")
        
        # set the extension to ma by default
        version.extension = '.ma'
        
        # create the folder if it doesn't exists
        utils.createFolder(version.path)
        
        # export the file
        pm.exportSelected(version.fullPath, type='mayaAscii')
        
        return True
    
    def open_(self, version, force=False):
        """the open action for maya environment
        
        returns Version instances which are referenced in to the opened version
        and those need to be updated
        """
        
        # check for unsaved changes
        pm.openFile(version.fullPath, f=force, loadReferenceDepth='none')
        
        # set the project
        pm.workspace.open(
            os.path.dirname(
                version.path
            )
        )
        
        # set the playblast folder
        self.set_playblast_file_name(version)
        
        self.appendToRecentFiles(version.fullPath)
        
        # replace_external_paths
        self.replace_external_paths(version)
        
        # check the referenced assets for newer version
        toUpdateList = self.check_reference_versions()
        
        return True, toUpdateList
    
    def import_(self, asset):
        """the import action for maya environment
        """
        pm.importFile(asset.fullPath)
        
        return True
    
    def reference(self, asset):
        """the reference action for maya environment
        """
        
        # use the file name without extension as the namespace
        #nameSpace = self._asset.fileNameWithoutExtension
        nameSpace = asset.fileNameWithoutExtension
        
        repo = repository.Repository()
        
        #repository_relative_asset_fullpath = repo.relative_path(self._asset.fullpath)
        #print "asset.fullpath: ", asset.fullpath
        #print "self._asset.fullpath: ", self._asset.fullpath
        
        new_asset_fullpath = asset.fullPath
        if asset.fullPath.replace("\\", "/").startswith(
          self._asset.sequenceFullPath):
            new_asset_fullpath = utils.relpath(
                self._asset.sequenceFullPath.replace("\\", "/"),
                asset.fullPath.replace("\\", "/"), "/", ".."
            )
        
        # replace the path with environment variable
        new_asset_fullpath = repo.relative_path(new_asset_fullpath)
        
        #print "printing the new path"
        #print new_asset_fullpath
        
        pm.createReference(
            new_asset_fullpath,
            gl=True,
            loadReferenceDepth='all',
            namespace=nameSpace,
            options='v=0'
        )
        
        return True
    
    def getPathVariables(self):
        """gets the file name from maya environment
        """
        
        foundValidAsset = False
        readRecentFile = True
        fileName = path = None
        workspacePath = None
        
        repo = repository.Repository()

        # pm.env.sceneName() always uses "/"
        fullPath = pm.env.sceneName()
        
        #if os.name == 'nt':
        #    fullpath = fullpath.replace('/','\\')
        
        #print "the fullpath in maya is ", fullpath
        
        if fullPath != '':
            fileName = os.path.basename(fullPath)
            
            # try to create an asset with that info
            projName, seqName = repo.get_project_and_sequence_name_from_file_path(fullPath)

            #print "projName", projName
            #print "seqName", seqName

            if projName != None and seqName != None:
                proj = Project(projName)
                seq = Sequence(proj, seqName)

                testAsset = Asset(proj, seq, fileName)
                
                if testAsset.isValidAsset:
                    fileName = testAsset.fileName
                    path = testAsset.path
                    readRecentFile = False
            else:
                readRecentFile = True
        
        
        
        if readRecentFile:
            # read the fileName from recent files list
            # try to get the a valid asset file from starting the last recent file
            
            try:
                recentFiles = pm.optionVar['RecentFilesList']
            except KeyError:
                print "no recent files"
                recentFiles = None
            
            if recentFiles is not None:
                
                for i in range(len(recentFiles)-1, -1,-1):
                    
                    fileName = os.path.basename(recentFiles[i])
                    projName, seqName = repo.get_project_and_sequence_name_from_file_path( recentFiles[i] )
                    
                    if projName != None and seqName != None:
                        
                        proj = Project(projName)
                        seq = Sequence(proj, seqName)
                        
                        testAsset = Asset(proj, seq, fileName)
                        
                        if testAsset.isValidAsset and testAsset.exists:
                            path = testAsset.path
                            foundValidAsset = True
                            break
                        
            # get the workscape path
            workspacePath = self.getWorkspacePath()
            returnWorkspace = False
            
            if foundValidAsset:
                #print "found a valid asset with path", path
                # check if the recent files path matches the current workspace
                if not path.startswith( workspacePath ):
                    # use the workspacePath
                    returnWorkspace = True
            else:
                # just get the path from workspace and return an empty fileName
                returnWorkspace = True
                
            if returnWorkspace:
                fileName = None
                path = workspacePath
                
                
        return fileName, path
    
    def set_render_fileName(self, version):
        """sets the render file name
        """
        
        assert isinstance(version, Version)
        
        render_output_folder = version.type.output_path.replace("\\", "/")
        
        # image folder from the workspace.mel
        # {{project.full_path}}/Sequences/{{seqence.code}}/Shots/{{shot.code}}/.maya_files/RENDERED_IMAGES
        image_folder_from_ws = pm.workspace.fileRules['image'] 
        image_folder_from_ws_full_path = os.path.join(
            os.path.dirname(version.path),
            image_folder_from_ws
        ).replace("\\", "/")
        
        version_base_name = version.base_name
        version_take_name = version.take_name
        render_file_name = ''
        
        render_file_full_path = \
            render_output_folder + "/<Layer>/" + \
            version.base_name + "_" + version.take_name + \
            "_<Layer>_<RenderPass>_<Version>"
        
        # convert the render_file_full_path to a relative path to the
        # imageFolderFromWS_full_path
        
        print "imageFolderFromWS_full_path: %s" % image_folder_from_ws_full_path
        print "render_file_full_path: %s" % render_file_full_path
        
        render_file_rel_path = utils.relpath(
            image_folder_from_ws_full_path,
            render_file_full_path,
            sep="/"
        )
        
        if self.hasStereoCamera():
            # just add the <Camera> template variable to the file name
            render_file_rel_path += "_<Camera>"
        
        
        # SHOTS/ToonShading/TestTransition/incidence/ToonShading_TestTransition_incidence_MasterPass_v050.####.iff
        
        # defaultRenderGlobals
        dRG = pm.PyNode('defaultRenderGlobals')
        dRG.setAttr('imageFilePrefix', render_file_rel_path)
        dRG.setAttr('renderVersion', "%03d" % version.version_number )
        dRG.setAttr('animation', 1)
        dRG.setAttr('outFormatControl', 0 )
        dRG.setAttr('extensionPadding', 3 )
        dRG.setAttr('imageFormat', 7 ) # force the format to iff
        dRG.setAttr('pff', 1)
        
        self.set_output_file_format()
    
    def set_output_file_format(self):
        """sets the output file format
        """
        dRG = pm.PyNode('defaultRenderGlobals')
        
        # check if Mentalray is the current renderer
        if dRG.getAttr('currentRenderer') == 'mentalRay':
            # set the render output to OpenEXR with zip compression
            dRG.setAttr('imageFormat', 51)
            dRG.setAttr('imfkey','exr')
            # check the maya version and set it if maya version is equal or
            # greater than 2012
            import pymel
            try:
                if pymel.versions.current() >= pymel.versions.v2012:
                    mrG = pm.PyNode("mentalrayGlobals")
                    mrG.setAttr("imageCompression", 4)
            except AttributeError, pm.general.MayaNodeError:
                pass
            
            # if the renderer is not registered this causes a _objectError
            # and the frame buffer to 16bit half
            try:
                miDF = pm.PyNode('miDefaultFramebuffer')
                miDF.setAttr('datatype', 16)
            except TypeError, pm.general.MayaNodeError:
                # just don't do anything
                pass
        
        
        ## check all the render layers and try to get if any of them are using
        ## mayaSoftware as the renderer, and set the render output to iff if any
        #for renderLayer in pm.ls(type='renderLayer'):
            ## if the renderer is set to mayaSoftware (which is very rare)
            #if dRG.getAttr('currentRenderer') == 'mayaSoftware':
    
    def set_playblast_file_name(self, version):
        """sets the playblast file name
        """
        
        playblast_path = os.path.join(
            version.output_path,
            "Playblast"
        )
        
        playblast_full_path = os.path.join(
            playblast_path,
            version.filename
        ).replace('\\','/')
        
        # create the folder
        utils.mkdir(playblast_path)
        pm.optionVar['playblastFile'] = playblast_full_path
    
    def setProject(self, projectName, sequenceName ):
        """sets the project
        """
        repo = repository.Repository()
        
        mayaProjectPath = os.path.join(
            repo.server_path,
            projectName,
            sequenceName
        )
        
        pm.workspace.open(mayaProjectPath)
        
        proj = Project(projectName)
        seq = Sequence(proj, sequenceName)
        
        # set the current timeUnit to match with the environments
        self.setTimeUnit(seq.timeUnit)
    
    def getWorkspacePath(self):
        """returns the workspace path
        tries to fix the path separator for windows
        """
        
        path = pm.workspace.name
        
        if os.name == 'nt':
            path = path.replace('/','\\')
        
        return path
    
    def appendToRecentFiles(self, path):
        """appends the given path to the recent files list
        """
        
        # add the file to the recent file list
        try:
            recentFiles = pm.optionVar['RecentFilesList']
        except KeyError:
            # there is no recent files list so create one
            # normally it is Maya's job
            # but somehow it is not working for new installations
            recentFiles = pm.OptionVarList( [], 'RecentFilesList' )
            
        #assert(isinstance(recentFiles,pm.OptionVarList))
        recentFiles.appendVar( path )
    
    def check_reference_versions(self):
        """checks the referenced assets versions
        
        returns a list of Version instances and maya Reference objects in a
        tupple
        """
        
        # get all the valid version references
        version_tuple_list = self.get_referenced_versions()
        
        to_be_updated_list = []
        
        for version_tuple in version_tuple_list:
            
            version = version_tuple[0]
            
            if not version.is_latest_version():
                # add version to the update list
                to_be_updated_list.append(version_tuple)
            
        # sort the list according to fullpath
        return sorted(to_be_updated_list, None, lambda x: x[2])
    
    def get_referenced_versions(self):
        """Returns the versions those been referenced to the current scene
        
        Returns Version instances and the corresponding Reference instance as a
        tupple in a list, and a string showing the path of the Reference.
        Replaces all the relative paths to absolute paths.
        
        The returned tuple format is as follows:
        (Version, Reference, fullpath)
        """
        
        valid_versions = []
        
        # get all the references
        references = pm.listReferences()
        
        # create a repository object
#        repo = repository.Repository()
        
#        osName = os.name
        
        refs_and_paths = []
        # iterate over them to find valid assets
        for reference in references:
            # it is a dictionary
            temp_version_fullpath = reference.path
            
            temp_version_fullpath = \
                os.path.expandvars(
                    os.path.expanduser(
                        os.path.normpath(
                            temp_version_fullpath
                        )
                    )
                )
            
            refs_and_paths.append((reference, temp_version_fullpath))
        
        # sort them according to path
        # to make same paths together
        
        refs_and_paths = sorted(refs_and_paths, None, lambda x: x[1])
        
        prev_version = None
        prev_fullpath = ''
        
        for reference, fullpath in refs_and_paths:
            
            if fullpath == prev_fullpath:
                # directly append the asset to the list
                valid_versions.append(
                    (prev_version, reference, prev_fullpath)
                )
            else:
                # try to get a version with the given path
                temp_version = \
                    db.query(Version).filter(Version.fullpath==fullpath).first()
                
                if temp_version:
                    valid_versions.append((temp_version, reference, fullpath))
                    
                    prev_version = temp_version
                    prev_fullpath = fullpath
                    
        # return a sorted list
        return sorted(valid_versions, None, lambda x: x[2])
    
    def update_versions(self, version_tuple_list):
        """update versions to the latest version
        """
        
        previous_version_fullpath = ''
        
        for version_tuple in version_tuple_list:
            version = version_tuple[0]
            reference = version_tuple[1]
            version_fullpath =  version_tuple[2]
            
            if version_fullpath != previous_version_fullpath:
                latest_version = version.latest_version()
                previous_version_fullpath = version_fullpath
            
            reference.replaceWith(latest_version.fullpath)
    
    def get_frame_range(self):
        """returns the current playback frame range
        """
        start_frame = int(pm.playbackOptions(q=True, ast=True))
        end_frame = int(pm.playbackOptions(q=True, aet=True))
        return start_frame, end_frame
    
    def set_frame_range(self, start_frame=1, end_frame=100,
                        adjust_frame_range=False):
        """sets the start and end frame range
        """
        # set it in the playback
        pm.playbackOptions(ast=start_frame, aet=end_frame)
        
        if adjust_frame_range:
            pm.playbackOptions( min=start_frame, max=end_frame )
        
        # set in the render range
        dRG = pm.PyNode('defaultRenderGlobals')
        dRG.setAttr('startFrame', start_frame )
        dRG.setAttr('endFrame', end_frame )
    
    def get_fps(self):
        """returns the fps of the environment
        """
        
        # return directly from maya, it uses the same format
        return self.time_to_fps[pm.currentUnit(q=1, t=1)]
    
    def set_fps(self, fps=25):
        """sets the fps of the environment
        """
        
        # get the current time, current playback min and max (because maya
        # changes them, try to restore the limits)
        
        current_time = pm.currentTime(q=1)
        pMin = pm.playbackOptions(q=1, min=1)
        pMax = pm.playbackOptions(q=1, max=1)
        pAst = pm.playbackOptions(q=1, ast=1)
        pAet = pm.playbackOptions(q=1, aet=1)
        
        # set the time unit, do not change the keyframe times
        # use the timeUnit as it is
        time_unit = u"pal"
        
        # try to find a timeUnit for the given fps
        for key in self.time_to_fps:
            if self.time_to_fps[key] == fps:
                time_unit = key
                break
        
        pm.currentUnit(t=time_unit, ua=0)
        # to be sure
        pm.optionVar['workingUnitTime'] = time_unit
        
        # update the playback ranges
        pm.currentTime(current_time)
        pm.playbackOptions(ast=pAst, aet=pAet)
        pm.playbackOptions(min=pMin, max=pMax)

    def load_references(self):
        """loads all the references
        """
        
        # get all the references
        references = pm.listReferences()
        
        for reference in references:
            reference.load()
    
    def replace_versions(self, source_reference, target_file):
        """replaces the source reference with the target file
        
        the source_reference may should be in maya reference node
        """
        
        # get the reference node
        base_reference_node = source_reference.refNode
        
        # get the base namespace before replacing the reference
        previous_namespace = \
            self.getFullNamespaceFromNodeName(source_reference.nodes()[0])
        
        # if the source_reference has referenced files do a dirty edit
        # by applying all the edits to the referenced node (the old way of
        # replacing references )
        subReferences = self.getAllSubReferences(source_reference)
        print "subReferences count:", len(subReferences)
        
        if len(subReferences) > 0:
            # for all subReferences get the editString and apply it to the
            # replaced file with new namespace
            allEdits = []
            for subRef in subReferences:
                allEdits += subRef.getReferenceEdits(orn= base_reference_node)
            
            # replace the reference
            source_reference.replaceWith(target_file)
            
            # try to find the new namespace
            subReferences = self.getAllSubReferences(source_reference)
            newNS = self.getFullNamespaceFromNodeName(subReferences[0].nodes()[0]) # possible bug here, fix it later
            
            # replace the old namespace with the new namespace in all the edits
            allEdits = [ edit.replace( previous_namespace+":", newNS+":") for edit in allEdits ] 
            
            # apply all the edits
            for edit in allEdits:
                try:
                    pm.mel.eval( edit )
                except pm.MelError:
                    pass
            
        else:
            
            # replace the reference
            source_reference.replaceWith( target_file )
            
            # try to find the new namespace
            subReferences = self.getAllSubReferences( source_reference )
            newNS = self.getFullNamespaceFromNodeName( subReferences[0].nodes()[0] ) # possible bug here, fix it later
            
            
            #subReferences = source_reference.subReferences()
            #for subRefData in subReferences.iteritems():
                #refNode = subRefData[1]
                #newNS = self.getFullNamespaceFromNodeName( refNode.nodes()[0] )
            
            # if the new namespace is different than the previous one
            # also change the edit targets
            if previous_namespace != newNS:
                # debug
                print "prevNS", previous_namespace
                print "newNS ", newNS
                
                # get the new sub references
                for subRef in self.getAllSubReferences( source_reference ):
                    # for all the nodes in sub references
                    # change the edit targets with new namespace
                    for node in subRef.nodes():
                        # use the long name -- suggested by maya help
                        nodeNewName = node.longName()
                        nodeOldName = nodeNewName.replace( newNS+':', previous_namespace+':')
                        
                        pm.referenceEdit( base_reference_node, changeEditTarget=( nodeOldName, nodeNewName) )
                        #pm.referenceEdit( baseRefNode, orn=baseRefNode, changeEditTarget=( nodeOldName, nodeNewName) )
                        #pm.referenceEdit( subRef, orn=baseRefNode, changeEditTarget=( nodeOldName, nodeNewName ) )
                        #for aRefNode in pm.ls(type='reference'):
                            #if len(aRefNode.attr('sharedReference').listConnections(s=0,d=1)) == 0: # not a shared reference
                                #pm.referenceEdit( aRefNode, orn=baseRefNode, changeEditTarget=( nodeOldName, nodeNewName), scs=1, fld=1 )
                                ##pm.referenceEdit( aRefNode, applyFailedEdits=True )
                    #pm.referenceEdit( subRef, applyFailedEdits=True )
                    
                    
                # apply all the failed edits again
                pm.referenceEdit( base_reference_node, applyFailedEdits=True )
    
    def getAllSubReferences(self, ref):
        """returns the recursive sub references as a list of FileReference
        objects for the given file reference
        """
        
        allRefs = []
        subRefDict = ref.subReferences()
        
        if len(subRefDict) > 0:
            for subRefData in subRefDict.iteritems():
                
                # first convert the sub ref dictionary to a normal ref object
                subRef = subRefData[1]
                allRefs.append(subRef)
                allRefs += self.getAllSubReferences(subRef)
        
        return allRefs
    
    def getFullNamespaceFromNodeName(self, node):
        """dirty way of getting the namespace from node name
        """
        
        return ':'.join( (node.name().split(':'))[:-1] )
    
    def hasStereoCamera(self):
        """checks if the scene has a stereo camera setup
        returns True if any
        """
        
        # check if the stereoCameraRig plugin is loaded
        if pm.pluginInfo('stereoCamera', q=True, l=True):
            return len(pm.ls(type='stereoRigTransform')) > 0
        else:
            # return False because it is impossible without stereoCamera plugin
            # to have a stereoCamera rig
            return False
    
    def replace_external_paths(self, version):
        """replaces all the external paths
        
        replaces:
          references: to a path with $REPO env variable
          file and mentalrayTextures: to a relative path to the project path
                                      (the self._asset.sequenceFullPath)
        """
        
        # create a repository
        repo = Repository()
        
        repo_env_key = "$" + conf.repository_env_key
        
        # replace reference paths with $REPO
        for ref in pm.listReferences():
            #if ref.path.replace("\\", "/").\
            #    startswith(repo.server_path.replace("\\", "/")):
            if ref.unresolvedPath().replace("\\", "/").\
                startswith(repo.server_path.replace("\\", "/")):
                
                new_ref_path = ref.path.replace(
                    repo.server_path.replace("\\", "/"),
                    repo_env_key
                )
                
                print "replacing reference:", ref.path
                print "replacing with:", new_ref_path
                
                
                #new_ref_path = utils.relpath(
                #    self._asset.sequenceFullPath.replace("\\", "/"),
                #    ref.path,
                #    "/", ".."
                #)
                
                #print new_ref_path
                
                ref.replaceWith(new_ref_path)
            
        # texture files
        for image_file in pm.ls(type="file"):
            file_texture_path = image_file.getAttr("fileTextureName")
            file_texture_path = file_texture_path.replace("\\", "/")
            #print "clean path:", file_texture_path
            if file_texture_path.startswith(repo.server_path.replace("\\", "/")):
                #new_path = utils.relpath(
                #    self._asset.sequenceFullPath.replace("\\", "/"),
                #    file_texture_path,
                #    "/", ".."
                #)
                new_path = file_texture_path.replace(
                    repo.server_path, repo_env_key
                )
                
                #print "new_path: ", new_path
                image_file.setAttr(
                    "fileTextureName",
                #    file_texture_path.replace(repo.server_path, repo_env_key)
                    new_path
                )
        
        # replace mentalray textures
        for mr_texture in pm.ls(type="mentalrayTexture"):
            mr_texture_path =  mr_texture.getAttr("fileTextureName")
            
            if mr_texture_path is not None:
                if mr_texture_path.startswith(repo.server_path):
                    #mr_texture.setAttr(
                    #    "fileTextureName",
                    #    "/" + mr_texture_path.replace(repo.server_path, repo_env_key)
                    #)
                    new_path = utils.relpath(
#                        self._asset.sequenceFullPath.replace("\\", "/"),
                        os.path.join(
                            version.version_of.project.fullpath,
                            os.path.dirname(
                                version.path
                            )
                        ),
                        mr_texture_path.replace("\\", "/"),
                        "/", ".."
                    )
                    mr_texture.setAttr(
                        "fileTextureName",
                        new_path
                    )
    
    def create_workspace_file(self, path):
        """creates the workspace.mel at the given path
        """
        
        content = """//Maya 2012 Project Definition

workspace -fr "scene" ".maya_files/OTHERS/";
workspace -fr "mayaAscii" ".maya_files/OTHERS/";
workspace -fr "mayaBinary" ".maya_files/OTHERS/";

workspace -fr "movie" ".maya_files/OTHERS/data/";
workspace -fr "offlineEdit" ".maya_files/OHTERS/edits/";
workspace -fr "autoSave" ".maya_files/OTHERS/autosave/";

workspace -fr "3dPaintTextures" ".maya_files/PAINTINGS/TEXTURES/";
workspace -fr "textures" ".maya_files/PAINTINGS/TEXTURES/";

workspace -fr "particles" ".maya_files/OTHERS/particles/";
workspace -fr "renderScenes" ".maya_files/LIGHTING/";
workspace -fr "lights" ".maya_files/RENDERED_IMAGES/renderData/shaders/";

workspace -fr "diskCache" ".maya_files/OTHERS/data/";

workspace -fr "furShadowMap" ".maya_files/OTHERS/fur/furShadowMap/";
workspace -fr "furFiles" ".maya_files/OTHERS/fur/furFiles/";
workspace -fr "furAttrMap" ".maya_files/OTHERS/fur/furAttrMap/";
workspace -fr "furImages" ".maya_files/OTHERS/fur/furImages/";
workspace -fr "furEqualMap" ".maya_files/OTHERS/fur/furEqualMap/";

workspace -fr "image" ".maya_files/RENDERED_IMAGES/";
workspace -fr "images" ".maya_files/RENDERED_IMAGES/";
workspace -fr "mentalray" ".maya_files/RENDERED_IMAGES/renderData/mentalRay/";
workspace -fr "mentalRay" ".maya_files/RENDERED_IMAGES/renderData/mentalRay/";
workspace -fr "iprImages" ".maya_files/RENDERED_IMAGES/renderData/iprImages/";
workspace -fr "depth" ".maya_files/RENDERED_IMAGES/renderData/depth/";

workspace -fr "animImport" ".maya_files/OTHERS/data/";
workspace -fr "animExport" ".maya_files/OTHERS/data/";
workspace -fr "clips" ".maya_files/OTHERS/clips/";

workspace -fr "templates" ".maya_files/OTHERS/assets/";

workspace -fr "audio" ".maya_files/EDIT/SOUND/";

workspace -fr "sourceImages" ".maya_files/PAINTINGS/TEXTURES/";

workspace -fr "mel" ".maya_files/OTHERS/mel/";

workspace -fr "Adobe(R) Illustrator(R)" ".maya_files/OTHERS/data/";
workspace -fr "aliasWire" ".maya_files/OTHERS/data/";
workspace -fr "DAE_FBX" ".maya_files/OTHERS/data/";
workspace -fr "DAE_FBX export" ".maya_files/OTHERS/data/";
workspace -fr "DXF_FBX" ".maya_files/OTHERS/data/";
workspace -fr "DXF_FBX export" ".maya_files/OTHERS/data/";
workspace -fr "DXF" ".maya_files/OTHERS/data/";
workspace -fr "DXF export" ".maya_files/OTHERS/data/";
workspace -fr "EPS" ".maya_files/OTHERS/data/";
workspace -fr "FBX" ".maya_files/OTHERS/data/";
workspace -fr "FBX export" ".maya_files/OTHERS/data/";
workspace -fr "IGES" ".maya_files/OTHERS/data/";
workspace -fr "IGESexport" ".maya_files/OTHERS/data/";
workspace -fr "move" ".maya_files/OTHERS/data/";
workspace -fr "OBJ" ".maya_files/OTHERS/data/";
workspace -fr "OBJexport" ".maya_files/OTHERS/data/";
workspace -fr "RIBexport" ".maya_files/OTHERS/data/";
workspace -fr "RIB" ".maya_files/OTHERS/data/";
        """
        
        # check if there is a workspace.mel at the given path
        full_path = os.path.join(path, "workspace.mel")
        
        if not os.path.exists(path):
            os.makedirs(
                os.path.dirname(full_path)
            )
            workspace_file = file(full_path, "w")
            workspace_file.write(content)
            workspace_file.close()
