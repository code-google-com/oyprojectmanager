# -*- coding: utf-8 -*-
# Copyright (c) 2009-2012, Erkan Ozgur Yilmaz
# 
# This module is part of oyProjectManager and is released under the BSD 2
# License: http://www.opensource.org/licenses/BSD-2-Clause

import os
import logging

logger = logging.getLogger(__name__)

class Config(object):
    """Config abstraction
    
    Idea is coming from Sphinx config.
    
    Holds system wide configuration variables. See
    `configuring oyProjectManager`_ for more detail.
    
    .. _configuring oyProjectManager: ../configure.html
    """
    
    default_config_values = dict(
        
        database_url = "sqlite:///$OYPROJECTMANAGER_PATH/project_manager.db",
        
        status_list = [
            'WTS',
            'WIP',
            'REV',
            'APP',
            'CMP'
        ],
        
        status_list_long_names = [
            'Waiting To Start',
            'Work In Progress',
            'For Review',
            'Approved',
            'Completed'
        ],
        
        status_bg_colors = [
            (192,  80,  77), #WTS
            (255, 192,   0), #WIP
            ( 89, 141, 213), #REV
            (155, 187,  89), #APP
            (155, 187,  89), #CMP
        ],
        
        status_fg_colors = [
            (255, 255, 255), #WTS
            (  0,   0,   0), #WIP
            (  0,   0,   0), #REV
            (  0,   0,   0), #APP
            (  0,   0,   0), #CMP
        ],
        
        sequence_format = "%h%p%t %R",
        
        shot_number_prefix = "SH",
        shot_number_padding = 3,
        
        rev_number_prefix = "r",
        rev_number_padding = 2,
        
        ver_number_prefix = "v",
        ver_number_padding = 3,
        
        default_fps = 25,
        
        default_asset_type_name = "Generic",
        default_take_name = "MAIN",
        
        users_data = [{"name": "Administrator", "initials": "adm"}],
        
        # just use one repository for now
        repository_env_key = "REPO",
        
        repository = {
            "name": "Default",
            "windows_path": "~/Projects",
            "linux_path": "~/Projects",
            "osx_path": "~/Projects"
        },


        file_size_format = "%.2f MB",
        time_format = '%d.%m.%Y %H:%M',

        environments = [
            {
                "name":"Maya",
                "extensions":["ma", "mb"]
            },
            {
                "name":"Houdini",
                "extensions":["hip"]
            },
            {
                "name":"Nuke",
                "extensions": ["nk"],
            },
            {
                "name":"Photoshop",
                "extensions": ["psd", "pdd"],
                "export_extensions": ["tif", "tga", "bmp", "jpg", "iff"],
            },
            {
                "name":"3DEqualizer",
                "extensions": ["3te"]
            },
            {
                "name":"Fusion",
                "extensions": ["comp"]
            }
        ],
        
        resolution_presets = {
            "PC Video": [640, 480, 1.0],
            "NTSC": [720, 486, 0.91],
            "NTSC 16:9": [720, 486, 1.21],
            "PAL": [720, 576, 1.067],
            "PAL 16:9": [720, 576, 1.46],
            "HD 720": [1280, 720, 1.0],
            "HD 1080": [1920, 1080, 1.0],
            "1K Super 35": [1024, 778, 1.0],
            "2K Super 35": [2048, 1556, 1.0],
            "4K Super 35": [4096, 3112, 1.0],
            "A4 Portrait": [2480, 3508, 1.0],
            "A4 Landscape": [3508, 2480, 1.0],
            "A3 Portrait": [3508, 4960, 1.0],
            "A3 Landscape": [4960, 3508, 1.0],
            "A2 Portrait": [4960, 7016, 1.0],
            "A2 Landscape": [7016, 4960, 1.0],
            "50x70cm Poster Portrait": [5905, 8268, 1.0],
            "50x70cm Poster Landscape": [8268, 5905, 1.0],
            "70x100cm Poster Portrait": [8268, 11810, 1.0],
            "70x100cm Poster Landscape": [11810, 8268, 1.0],
            "1k Square": [1024, 1024, 1.0],
            "2k Square": [2048, 2048, 1.0],
            "3k Square": [3072, 3072, 1.0],
            "4k Square": [4096, 4096, 1.0],
        },
        
        default_resolution_preset = "HD 1080",
        
        project_structure = """{% for sequence in project.sequences %}
            {% set seq_path = project.full_path + '/Sequences/' + sequence.code %}
            {{seq_path}}/Edit/Offline
            {{seq_path}}/Edit/Sound
            {{seq_path}}/References/Artworks
            {{seq_path}}/References/Text/Scenario
            {{seq_path}}/References/Photos_Images
            {{seq_path}}/References/Videos
            {{seq_path}}/References/Others
            {% for shot in sequence.shots %}
                {{seq_path}}/Shots/{{shot.code}}
                {{seq_path}}/Shots/{{shot.code}}/Plate
                {{seq_path}}/Shots/{{shot.code}}/Ref
                {{seq_path}}/Shots/{{shot.code}}/Texture
            {% endfor %}
        {% endfor %}
        """,
        
        asset_thumbnail_path = "{{project.code}}/Assets/{{asset.type}}/{{asset.code}}/Thumbnail",
        asset_thumbnail_filename = "{{asset.code}}_thumbnail.{{extension}}",
        
        shot_thumbnail_path = "{{project.code}}/Sequences/{{sequence.code}}/Shots/{{shot.code}}/Thumbnail",
        shot_thumbnail_filename = "{{shot.code}}_thumbnail.{{extension}}",
        
        thumbnail_format = "jpg",
        thumbnail_quality = 70,
        thumbnail_size = [320, 180],
        
        version_types = [
            {
                "name": "Animation",
                "code": "Anim",
                "path": "{{project.code}}/Sequences/{{sequence.code}}/Shots/{{version.base_name}}/{{type.code}}",
                "filename": "{{version.base_name}}_{{version.take_name}}_{{type.code}}_v{{'%03d'|format(version.version_number)}}_{{version.created_by.initials}}{{version.extension}}",
                "output_path": "{{version._path}}/Output/{{version.take_name}}",
                "extra_folders": "",
                "environments": ["Maya", "Houdini"],
                "type_for": "Shot"
            },
            {
                "name": "Camera",
                "code": "Cam",
                "path": "{{project.code}}/Sequences/{{sequence.code}}/Shots/{{version.base_name}}/{{type.code}}",
                "filename": "{{version.base_name}}_{{version.take_name}}_{{type.code}}_v{{'%03d'|format(version.version_number)}}_{{version.created_by.initials}}{{version.extension}}",
                "output_path": "{{version._path}}/Output/{{version.take_name}}",
                "extra_folders": "",
                "environments": ["Maya", "Houdini"],
                "type_for": "Shot"
            },
            {
                "name": "Composition",
                "code": "Comp",
                "path": "{{project.code}}/Sequences/{{sequence.code}}/Shots/{{version.base_name}}/{{type.code}}",
                "filename": "{{version.base_name}}_{{version.take_name}}_{{type.code}}_v{{'%03d'|format(version.version_number)}}_{{version.created_by.initials}}{{version.extension}}",
                "output_path": "{{version._path}}/Output/{{version.take_name}}",
                "extra_folders": "",
                "environments": ["Nuke", "Fusion"],
                "type_for": "Shot"
            },
#            {
#                "name": "Edit",
#                "code": "Edit",
#                "path": "{{project.code}}/Sequences/{{sequence.code}}/Shots/{{version.base_name}}/{{type.code}}",
#                "filename": "{{version.base_name}}_{{version.take_name}}_{{type.code}}_v{{'%03d'|format(version.version_number)}}_{{version.created_by.initials}}{{version.extension}}",
#                "output_path": "{{version._path}}/Output/{{version.take_name}}",
#                "extra_folders": "",
#                "environments": ["Nuke", "Fusion"],
#                "type_for": "Shot"
#            },
            {
                "name":"FX",
                "code": "FX",
                "path": "{{project.code}}/Sequences/{{sequence.code}}/Shots/{{version.base_name}}/{{type.code}}",
                "filename": "{{version.base_name}}_{{version.take_name}}_{{type.code}}_v{{'%03d'|format(version.version_number)}}_{{version.created_by.initials}}{{version.extension}}",
                "output_path": "{{version._path}}/Output/{{version.take_name}}",
                "extra_folders": """{{version.path}}/anim
                        {{version.path}}/cache
                        {{version.path}}/exports""",
                "environments": ["Maya", "Houdini"],
                "type_for": "Shot"
            },
            {
                "name":"Model",
                "code": "Model",
                "path": "{{project.code}}/Assets/{{asset.type}}/{{version.base_name}}/{{type.code}}",
                "filename": "{{version.base_name}}_{{version.take_name}}_{{type.code}}_v{{'%03d'|format(version.version_number)}}_{{version.created_by.initials}}{{version.extension}}",
                "output_path": "{{version._path}}/Output/{{version.take_name}}",
                "extra_folders": "",
                "environments": ["Maya", "Houdini"],
                "type_for": "Asset"
            },
            {
                "name": "Other",
                "code": "Other",
                "path": "{{project.code}}/Assets/{{asset.type}}/{{version.base_name}}/{{type.code}}",
                "filename": "{{version.base_name}}_{{version.take_name}}_{{type.code}}_v{{'%03d'|format(version.version_number)}}_{{version.created_by.initials}}{{version.extension}}",
                "output_path": "{{version._path}}/Output/{{version.take_name}}",
                "extra_folders": "",
                "environments": ["Maya", "Houdini", "Nuke", "Fusion", "Photoshop"],
                "type_for": "Asset"
            },
            {
                "name": "Previs",
                "code": "Previs",
                "path": "{{project.code}}/Sequences/{{sequence.code}}/Shots/{{version.base_name}}/{{type.code}}",
                "filename": "{{version.base_name}}_{{version.take_name}}_{{type.code}}_v{{'%03d'|format(version.version_number)}}_{{version.created_by.initials}}{{version.extension}}",
                "output_path": "{{version._path}}/Output/{{version.take_name}}",
                "extra_folders": "",
                "environments": ["Maya", "Houdini"],
                "type_for": "Shot"
            },
            {
                "name": "Lighting",
                "code": "Lighting",
                "path": "{{project.code}}/Sequences/{{sequence.code}}/Shots/{{version.base_name}}/{{type.code}}",
                "filename": "{{version.base_name}}_{{version.take_name}}_{{type.code}}_v{{'%03d'|format(version.version_number)}}_{{version.created_by.initials}}{{version.extension}}",
                "output_path": "{{version._path}}/Output/{{version.take_name}}",
                "extra_folders": "",
                "environments": ["Maya", "Houdini"],
                "type_for": "Shot"
            },
            {
                "name": "Rig",
                "code": "Rig",
                "path": "{{project.code}}/Assets/{{asset.type}}/{{version.base_name}}/{{type.code}}",
                "filename": "{{version.base_name}}_{{version.take_name}}_{{type.code}}_v{{'%03d'|format(version.version_number)}}_{{version.created_by.initials}}{{version.extension}}",
                "output_path": "{{version._path}}/Output/{{version.take_name}}",
                "extra_folders": "",
                "environments": ["Maya", "Houdini"],
                "type_for": "Asset"
            },
            {
                "name": "Roto",
                "code": "Roto",
                "path": "{{project.code}}/Sequences/{{sequence.code}}/Shots/{{version.base_name}}/{{type.code}}",
                "filename": "{{version.base_name}}_{{version.take_name}}_{{type.code}}_v{{'%03d'|format(version.version_number)}}_{{version.created_by.initials}}{{version.extension}}",
                "output_path": "{{version._path}}/Output/{{version.take_name}}",
                "extra_folders": "",
                "environments": ["Nuke", "Fusion"],
                "type_for": "Shot"
            },
            {
                "name": "Layout",
                "code": "Layout",
                "path":"{{project.code}}/Sequences/{{sequence.code}}/Shots/{{version.base_name}}/{{type.code}}",
                "filename": "{{version.base_name}}_{{version.take_name}}_{{type.code}}_v{{'%03d'|format(version.version_number)}}_{{version.created_by.initials}}{{version.extension}}",
                "output_path": "{{version._path}}/Output/{{version.take_name}}",
                "extra_folders": "",
                "environments": ["Maya", "Houdini"],
                "type_for": "Shot"
            },
            {
                "name": "Matte",
                "code": "Matte",
                "path": "{{project.code}}/Sequences/{{sequence.code}}/Shots/{{version.base_name}}/{{type.code}}",
                "filename": "{{version.base_name}}_{{version.take_name}}_{{type.code}}_v{{'%03d'|format(version.version_number)}}_{{version.created_by.initials}}{{version.extension}}",
                "output_path": "{{version._path}}/Output/{{version.take_name}}",
                "extra_folders": "",
                "environments": ["Photoshop"],
                "type_for": "Shot"
            },
            {
                "name": "Texture",
                "code": "Texture",
                "path": "{{project.code}}/Assets/{{asset.type}}/{{version.base_name}}/{{type.code}}",
                "filename": "{{version.base_name}}_{{version.take_name}}_{{type.code}}_v{{'%03d'|format(version.version_number)}}_{{version.created_by.initials}}{{version.extension}}",
                "output_path": "{{version._path}}/Output/{{version.take_name}}",
                "extra_folders": "",
                "environments": ["Photoshop", "Nuke", "Fusion"],
                "type_for": "Asset",
            },
            {
                "name": "Illustration",
                "code": "Illust",
                "path": "{{project.code}}/Assets/{{asset.type}}/{{version.base_name}}/{{type.code}}",
                "filename": "{{version.base_name}}_{{version.take_name}}_{{type.code}}_v{{'%03d'|format(version.version_number)}}_{{version.created_by.initials}}{{version.extension}}",
                "output_path": "{{version._path}}/Output/{{version.take_name}}",
                "extra_folders": "",
                "environments": ["Photoshop"],
                "type_for": "Asset"
            },
            {
                "name": "Look Development",
                "code": "LookDev",
                "path": "{{project.code}}/Assets/{{asset.type}}/{{version.base_name}}/{{type.code}}",
                "filename": "{{version.base_name}}_{{version.take_name}}_{{type.code}}_v{{'%03d'|format(version.version_number)}}_{{version.created_by.initials}}{{version.extension}}",
                "output_path": "{{version._path}}/Output/{{version.take_name}}",
                "extra_folders": "",
                "environments": ["Maya", "Houdini"],
                "type_for": "Asset"
            },
            {
                "name": "Match Move",
                "code": "MM",
                "path": "{{project.code}}/Sequences/{{sequence.code}}/Shots/{{version.base_name}}/{{type.code}}",
                "filename": "{{version.base_name}}_{{version.take_name}}_{{type.code}}_v{{'%03d'|format(version.version_number)}}_{{version.created_by.initials}}{{version.extension}}",
                "output_path": "{{version._path}}/Output/{{version.take_name}}",
                "extra_folders": "",
                "environments": ["3DEqualizer"],
                "type_for": "Shot"
            }
        ]
    )
    
    def __init__(self):
        
        self.config_values = Config.default_config_values.copy()
        self.user_config = {}
        
        # the priority order is
        # oyProjectManager.config
        # config.py under .oyrc directory
        # config.py under $OYPROJECTMANAGER_PATH
        
        self._parse_settings()
    
    def _parse_settings(self):
        # for now just use $OYPROJECTMANAGER_PATH
        ENV_KEY = "OYPROJECTMANAGER_PATH"
        
        # try to get the environment variable
        if not os.environ.has_key(ENV_KEY):
            # don't do anything
            logger.debug("no environment key found for user settings")
        else:
            logger.debug("environment key found")
            
            resolved_path = os.path.expanduser(
                os.path.join(
                    os.environ[ENV_KEY],
                    "config.py"
                )
            )
            
            # using `while` is not safe to expand variables
            # do the expansion for 5 times which is complex enough
            # and I don't (hopefully) expect anybody to use
            # more than 5 level deep environment variables
            resolved_path = os.path.expandvars(
                os.path.expandvars(
                    os.path.expandvars(
                        os.path.expandvars(
                            resolved_path
                        )
                    )
                )
            )
            
            try:
                try:
                    logger.debug("importing user config")
                    execfile(resolved_path, self.user_config)
                except SyntaxError, err:
                    raise RuntimeError("There is a syntax error in your "
                                       "configuration file: " + str(err))
                
                # append the data to the current settings
                logger.debug("updating system config")
                for key in self.user_config:
                    if key in self.config_values:
                        self.config_values[key] = self.user_config[key]
            
            except IOError:
                logger.warning("The $OYPROJETMANAGER_PATH:" + resolved_path + \
                               " doesn't exists! skipping user config")
    
    def __getattr__(self, name):
        return self.config_values[name]
    
    def __getitem__(self, name):
        return getattr(self, name)
    
    def __setitem__(self, name, value):
        return setattr(self, name, value)
    
    def __delitem__(self, name):
        delattr(self, name)
    
    def __contains__(self, name):
        return name in self.config_values
    
    @property
    def last_user_id(self):
        """returns the last user id
        
        It is not very much related with the config.py and user settings, but
        it seems the most appropriate place is this one to get information from
        individual users.
        
        This should work fairly fast, because it uses the local filesystem not
        the network thus the fileserver.
        """
        # TODO: This should be replaced with beaker.session
        
        file_name = 'last_user_id'
        file_path = os.path.expanduser("~/.oypmrc/")
        file_full_path = os.path.join(file_path, file_name)
        
        last_user_id = None
        
        try:
            last_user_file = open(file_full_path)
        except IOError:
            pass
        else:
            last_user_id = int(last_user_file.readline().strip())
            last_user_file.close()
        
        return last_user_id
        
    @last_user_id.setter
    def last_user_id(self, user_id):
        """sets the user id for the last user
        """
        if not isinstance(user_id, int):
            raise RuntimeWarning("user_id for last_user_id should be an int")
            return
        
        file_name = 'last_user_id'
        file_path = os.path.expanduser("~/.oypmrc/")
        file_full_path = os.path.join(file_path, file_name)
        
        logger.debug("saving user id to %s" % file_full_path)
        
        # create the folder first
        try:
            os.makedirs(file_path)
        except OSError:
            # already created
            pass
        
        try:
            last_user_file = open(file_full_path, 'w')
        except IOError as e:
            pass
        else:
            last_user_file.write(str(user_id))
            last_user_file.close()
