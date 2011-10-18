#-*- coding: utf-8 -*-

import os
import logging
logger = logging.getLogger(__name__)

class Config(object):
    """config abstraction
    
    Idea comes from Sphinx config
    
    Holds the default settings for the system.
    
    The system looks for these paths to get more config values:
        
        * conf.py under "~/.oyrc/" directory
        * conf.py under "$OYPROJECTMANAGER_PATH"
    
    Sample usage is::
    
        from oyProjectManager import config
        conf = config.Config()
        
        print conf.DATABASE_FILE_NAME
        # return .metadata.db or the user overrides
    
    """
    
    default_config_values = dict(
        DATABASE_FILE_NAME = ".metadata.db",
        
        SHOT_PREFIX = "SH",
        SHOT_PADDING = 3,
        
        REV_PREFIX = "r",
        REV_PADDING = 2,
        
        VER_PREFIX = "v",
        VER_PADDING = 3,
        
        FPS = 25,
        RESOLUTION_WIDTH = 1920,
        RESOLUTION_HEIGHT = 1080,
        RESOLUTION_PIXEL_ASPECT = 1.0,
        
        TAKE_NAME = "MAIN",
        
        USERS = [{"name": "Administrator", "initials": "adm"}],
        
        SERVERS = [
            {
                "name": "Default",
                "windows_path": "M:/JOBs",
                "linux_path": "/mnt/M/JOBs",
                "osx_path": "/Users/Shared/Servers/M/JOBs"
            }
        ],
        
        ENVIRONMENTS = [
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
            }
        ],
        
        STRUCTURE = """Sequences/
        {% for sequence in project.sequences %}
            {{sequence.code}}/Edit/Offline
            {{sequence.code}}/Edit/Sound
            {{sequence.code}}/References/Artworks
            {{sequence.code}}/References/Text/Scenario
            {{sequence.code}}/References/Photos_Images
            {{sequence.code}}/References/Videos
            {{sequence.code}}/References/Others
            {{sequence.code}}/Others
            {{sequence.code}}/Others/assets
            {{sequence.code}}/Others/clips
            {{sequence.code}}/Others/data
            {{sequence.code}}/Others/fur
            {{sequence.code}}/Others/fur/furAttrMap
            {{sequence.code}}/Others/fur/furEqualMap
            {{sequence.code}}/Others/fur/furFiles
            {{sequence.code}}/Others/fur/furImages
            {{sequence.code}}/Others/fur/furShadowMap
            {{sequence.code}}/Others/mel
            {{sequence.code}}/Others/particles
        {% endfor %}
        """,
        
        VERSION_TYPES = [
            {
                "name": "Animation",
                "code": "ANIM",
                "filename": "{{version.base_name}}_{{version.take_name}}_{{type.code}}_v{{'%03d'|format(version.version_number)}}_{{version.created_by.initials}}",
                "path": "{{sequence.code}}/Shots/{{version.base_name}}/{{type.code}}",
                "output_path": "{{version.path}}/OUTPUT/{{version.take_name}}",
                "extra_folders": "",
                "environments": ["Maya", "Houdini"],
                "type_for": "Shot"
            },
            {
                "name": "Camera",
                "code": "CAMERA",
                "filename": "{{version.base_name}}_{{version.take_name}}_{{type.code}}_v{{'%03d'|format(version.version_number)}}_{{version.created_by.initials}}",
                "path": "{{sequence.code}}/Shots/{{version.base_name}}/{{type.code}}",
                "output_path": "{{version.path}}/OUTPUT/{{version.take_name}}",
                "extra_folders": "",
                "environments": ["Maya", "Houdini"],
                "type_for": "Shot"
            },
            {
                "name": "Composition",
                "code": "COMP",
                "filename": "{{version.base_name}}_{{version.take_name}}_{{type.code}}_v{{'%03d'|format(version.version_number)}}_{{version.created_by.initials}}",
                "path": "{{sequence.code}}/Shots/{{version.base_name}}/{{type.code}}",
                "output_path": "{{version.path}}/OUTPUT/{{version.take_name}}",
                "extra_folders": "",
                "environments": ["Nuke"],
                "type_for": "Shot"
            },
            {
                "name": "Edit",
                "code": "EDIT",
                "filename": "{{version.base_name}}_{{version.take_name}}_{{type.code}}_v{{'%03d'|format(version.version_number)}}_{{version.created_by.initials}}",
                "path": "{{sequence.code}}/Shots/{{version.base_name}}/{{type.code}}",
                "output_path": "{{version.path}}/OUTPUT/{{version.take_name}}",
                "extra_folders": "",
                "environments": ["Nuke"],
                "type_for": "Shot"
            },
            {
                "name":"FX",
                "code": "FX",
                "filename": "{{version.base_name}}_{{version.take_name}}_{{type.code}}_v{{'%03d'|format(version.version_number)}}_{{version.created_by.initials}}",
                "path": "{{sequence.code}}/Shots/{{version.base_name}}/{{type.code}}",
                "output_path": "{{version.path}}/OUTPUT/{{version.take_name}}",
                "extra_folders": """{{version.path}}/anim
                        {{version.path}}/cache
                        {{version.path}}/exports
                        {{version.path}}/fx_scenes
                        {{version.path}}/maps
                        {{version.path}}/misc
                        {{version.path}}/obj
                        {{version.path}}/sim_in
                        {{version.path}}/sim_out""",
                "environments": ["Maya", "Houdini"],
                "type_for": "Shot"
            },
            {
                "name":"Model",
                "code": "MODEL",
                "filename": "{{version.base_name}}_{{version.take_name}}_{{type.code}}_v{{'%03d'|format(version.version_number)}}_{{version.created_by.initials}}",
                "path": "Assets/{{version.base_name}}/{{type.code}}",
                "output_path": "{{version.path}}/OUTPUT/{{version.take_name}}",
                "extra_folders": "",
                "environments": ["MAYA", "HOUDINI"],
                "type_for": "Asset"
            },
            {
                "name": "Other",
                "code": "OTHER",
                "filename": "{{version.base_name}}_{{version.take_name}}_{{type.code}}_v{{'%03d'|format(version.version_number)}}_{{version.created_by.initials}}",
                "path": "Others/{{version.base_name}}/{{type.code}}",
                "output_path": "{{version.path}}/OUTPUT/{{version.take_name}}",
                "extra_folders": "",
                "environments": ["Maya", "Houdini", "Nuke"],
                "type_for": "Asset, Shot"
            },
            {
                "name": "Previs",
                "code": "PREVIS",
                "filename": "{{version.base_name}}_{{version.take_name}}_{{type.code}}_v{{'%03d'|format(version.version_number)}}_{{version.created_by.initials}}",
                "path": "{{sequence.code}}/Shots/{{version.base_name}}/{{type.code}}",
                "output_path": "{{version.path}}/OUTPUT/{{version.take_name}}",
                "extra_folders": "",
                "environments": ["Maya", "Houdini"],
                "type_for": "Shot"
            },
            {
                "name": "Lighting",
                "code": "LIGHTING",
                "filename": "{{version.base_name}}_{{version.take_name}}_{{type.code}}_v{{'%03d'|format(version.version_number)}}_{{version.created_by.initials}}",
                "path": "{{sequence.code}}/Shots/{{version.base_name}}/{{type.code}}",
                "output_path": "{{version.path}}/OUTPUT/{{version.take_name}}",
                "extra_folders": "",
                "environments": ["Maya", "Houdini"],
                "type_for": "Shot"
            },
            {
                "name": "Rig",
                "code": "RIG",
                "filename": "{{version.base_name}}_{{version.take_name}}_{{type.code}}_v{{'%03d'|format(version.version_number)}}_{{version.created_by.initials}}",
                "path": "Assets/{{version.base_name}}/{{type.code}}",
                "output_path": "{{version.path}}/OUTPUT/{{version.take_name}}",
                "extra_folders": "",
                "environments": ["Maya", "Houdini"],
                "type_for": "Asset"
            },
            {
                "name": "Scene Assembly",
                "code": "SCNASS",
                "filename": "{{version.base_name}}_{{version.take_name}}_{{type.code}}_v{{'%03d'|format(version.version_number)}}_{{version.created_by.initials}}",
                "path":"{{sequence.code}}/Shots/{{version.base_name}}/{{type.code}}",
                "output_path": "{{version.path}}/OUTPUT/{{version.take_name}}",
                "extra_folders": "",
                "environments": ["Maya", "Houdini"],
                "type_for": "Shot"
            },
            {
                "name": "Matte Paint",
                "code": "MATTE",
                "filename": "{{version.base_name}}_{{version.take_name}}_{{type.code}}_v{{'%03d'|format(version.version_number)}}_{{version.created_by.initials}}",
                "path": "{{sequence.code}}/Shots/{{version.base_name}}/PAINTINGS/{{type.code}}",
                "output_path": "{{version.path}}/OUTPUT/{{version.take_name}}",
                "extra_folders": "",
                "environments": ["Photoshop"],
                "type_for": "Shot"
            },
            {
                "name": "Texture Paint",
                "code": "TEXTURE",
                "filename": "{{version.base_name}}_{{version.take_name}}_{{type.code}}_v{{'%03d'|format(version.version_number)}}_{{version.created_by.initials}}",
                "path": "Assets/{{version.base_name}}/PAINTINGS/{{type.code}}",
                "output_path": "{{version.path}}/OUTPUT/{{version.take_name}}",
                "extra_folders": "",
                "environments": ["Photoshop"],
                "type_for": "Asset",
            },
            {
                "name": "Illustration",
                "code": "ILLUSTRATION",
                "filename": "{{version.base_name}}_{{version.take_name}}_{{type.code}}_v{{'%03d'|format(version.version_number)}}_{{version.created_by.initials}}",
                "path": "Assets/{{version.base_name}}/PAINTINGS/{{type.code}}",
                "output_path": "{{version.path}}/OUTPUT/{{version.take_name}}",
                "extra_folders": "",
                "environments": ["Photoshop"],
                "type_for": "Asset"
            },
            {
                "name": "Shading",
                "code": "SHADING",
                "filename": "{{version.base_name}}_{{version.take_name}}_{{type.code}}_v{{'%03d'|format(version.version_number)}}_{{version.created_by.initials}}",
                "path": "Assets/{{version.base_name}}/{{type.code}}",
                "output_path": "{{version.path}}/OUTPUT/{{version.take_name}}",
                "extra_folders": "",
                "environments": ["Maya", "Houdini"],
                "type_for": "Asset"
            },
            {
                "name": "Tracking",
                "code": "TRACK",
                "filename": "{{version.base_name}}_{{version.take_name}}_{{type.code}}_v{{'%03d'|format(version.version_number)}}_{{version.created_by.initials}}",
                "path": "{{sequence.code}}/Shots/{{version.base_name}}/{{type.code}}",
                "output_path": "{{version.path}}/OUTPUT/{{version.take_name}}",
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
        # conf.py under .oyrc directory
        # conf.py under $OYPROJECTMANAGER_PATH
        
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
                    "conf.py"
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
                self.config_values.update(self.user_config)
            
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
