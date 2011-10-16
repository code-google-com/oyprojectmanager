#-*- coding: utf-8 -*-

DATABASE_FILE_NAME = ".metadata.db"

SHOT_PREFIX = "SH"
SHOT_PADDING = 3

REV_PREFIX = "r"
REV_PADDING = 2
VER_PREFIX = "v"
VER_PADDING = 3

FPS = 25
RESOLUTION_WIDTH = 1920
RESOLUTION_HEIGHT = 1080
RESOLUTION_PIXEL_ASPECT = 1.0

TAKE_NAME = "MAIN"

ENVIRONMENTS = ["MAYA", "HOUDINI", "NUKE", "PHOTOSHOP", "3DEQUALIZER"]

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
"""

VERSION_TYPES = [
    {
        "name": "Animation",
        "code": "ANIM",
        "filename": "{{version.base_name}}_{{version.take_name}}_{{type.code}}_v{{'%03d'|format(version.version_number)}}_{{version.created_by.initials}}",
        "path": "{{sequence.code}}/Shots/{{version.base_name}}/{{type.code}}",
        "output_path": "{{version.path}}/OUTPUT/{{version.take_name}}",
        "extra_folders": "",
        "environments": "MAYA,HOUDINI",
        "type_for": "Shot"
    },
    {
        "name": "Camera",
        "code": "CAMERA",
        "filename": "{{version.base_name}}_{{version.take_name}}_{{type.code}}_v{{'%03d'|format(version.version_number)}}_{{version.created_by.initials}}",
        "path": "{{sequence.code}}/Shots/{{version.base_name}}/{{type.code}}",
        "output_path": "{{version.path}}/OUTPUT/{{version.take_name}}",
        "extra_folders": "",
        "environments": "MAYA,HOUDINI",
        "type_for": "Shot"
    },
    {
        "name": "Composition",
        "code": "COMP",
        "filename": "{{version.base_name}}_{{version.take_name}}_{{type.code}}_v{{'%03d'|format(version.version_number)}}_{{version.created_by.initials}}",
        "path": "{{sequence.code}}/Shots/{{version.base_name}}/{{type.code}}",
        "output_path": "{{version.path}}/OUTPUT/{{version.take_name}}",
        "extra_folders": "",
        "environments": "NUKE",
        "type_for": "Shot"
    },
    {
        "name": "Edit",
        "code": "EDIT",
        "filename": "{{version.base_name}}_{{version.take_name}}_{{type.code}}_v{{'%03d'|format(version.version_number)}}_{{version.created_by.initials}}",
        "path": "{{sequence.code}}/Shots/{{version.base_name}}/{{type.code}}",
        "output_path": "{{version.path}}/OUTPUT/{{version.take_name}}",
        "extra_folders": "",
        "environments": "NUKE",
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
        "environments": "MAYA,HOUDINI",
        "type_for": "Shot"
    },
    {
        "name":"Model",
        "code": "MODEL",
        "filename": "{{version.base_name}}_{{version.take_name}}_{{type.code}}_v{{'%03d'|format(version.version_number)}}_{{version.created_by.initials}}",
        "path": "Assets/{{version.base_name}}/{{type.code}}",
        "output_path": "{{version.path}}/OUTPUT/{{version.take_name}}",
        "extra_folders": "",
        "environments": "MAYA,HOUDINI",
        "type_for": "Asset"
    },
    {
        "name": "Other",
        "code": "OTHER",
        "filename": "{{version.base_name}}_{{version.take_name}}_{{type.code}}_v{{'%03d'|format(version.version_number)}}_{{version.created_by.initials}}",
        "path": "Others/{{version.base_name}}/{{type.code}}",
        "output_path": "{{version.path}}/OUTPUT/{{version.take_name}}",
        "extra_folders": "",
        "environments": "MAYA,HOUDINI,NUKE",
        "type_for": "Asset, Shot"
    },
    {
        "name": "Previs",
        "code": "PREVIS",
        "filename": "{{version.base_name}}_{{version.take_name}}_{{type.code}}_v{{'%03d'|format(version.version_number)}}_{{version.created_by.initials}}",
        "path": "{{sequence.code}}/Shots/{{version.base_name}}/{{type.code}}",
        "output_path": "{{version.path}}/OUTPUT/{{version.take_name}}",
        "extra_folders": "",
        "environments": "MAYA,HOUDINI",
        "type_for": "Shot"
    },
    {
        "name": "Lighting",
        "code": "LIGHTING",
        "filename": "{{version.base_name}}_{{version.take_name}}_{{type.code}}_v{{'%03d'|format(version.version_number)}}_{{version.created_by.initials}}",
        "path": "{{sequence.code}}/Shots/{{version.base_name}}/{{type.code}}",
        "output_path": "{{version.path}}/OUTPUT/{{version.take_name}}",
        "extra_folders": "",
        "environments": "MAYA,HOUDINI",
        "type_for": "Shot"
    },
    {
        "name": "Rig",
        "code": "RIG",
        "filename": "{{version.base_name}}_{{version.take_name}}_{{type.code}}_v{{'%03d'|format(version.version_number)}}_{{version.created_by.initials}}",
        "path": "Assets/{{version.base_name}}/{{type.code}}",
        "output_path": "{{version.path}}/OUTPUT/{{version.take_name}}",
        "extra_folders": "",
        "environments": "MAYA,HOUDINI",
        "type_for": "Asset"
    },
    {
        "name": "Scene Assembly",
        "code": "SCNASS",
        "filename": "{{version.base_name}}_{{version.take_name}}_{{type.code}}_v{{'%03d'|format(version.version_number)}}_{{version.created_by.initials}}",
        "path":"{{sequence.code}}/Shots/{{version.base_name}}/{{type.code}}",
        "output_path": "{{version.path}}/OUTPUT/{{version.take_name}}",
        "extra_folders": "",
        "environments": "MAYA,HOUDINI",
        "type_for": "Shot"
    },
    {
        "name": "Matte Paint",
        "code": "MATTE",
        "filename": "{{version.base_name}}_{{version.take_name}}_{{type.code}}_v{{'%03d'|format(version.version_number)}}_{{version.created_by.initials}}",
        "path": "{{sequence.code}}/Shots/{{version.base_name}}/PAINTINGS/{{type.code}}",
        "output_path": "{{version.path}}/OUTPUT/{{version.take_name}}",
        "extra_folders": "",
        "environments": "PHOTOSHOP",
        "type_for": "Shot"
    },
    {
        "name": "Texture Paint",
        "code": "TEXTURE",
        "filename": "{{version.base_name}}_{{version.take_name}}_{{type.code}}_v{{'%03d'|format(version.version_number)}}_{{version.created_by.initials}}",
        "path": "Assets/{{version.base_name}}/PAINTINGS/{{type.code}}",
        "environments": "PHOTOSHOP",
        "extra_folders": "",
        "output_path": "{{version.path}}/OUTPUT/{{version.take_name}}",
        "type_for": "Asset"
    },
    {
        "name": "Illustration",
        "code": "ILLUSTRATION",
        "filename": "{{version.base_name}}_{{version.take_name}}_{{type.code}}_v{{'%03d'|format(version.version_number)}}_{{version.created_by.initials}}",
        "path": "Assets/{{version.base_name}}/PAINTINGS/{{type.code}}",
        "output_path": "{{version.path}}/OUTPUT/{{version.take_name}}",
        "extra_folders": "",
        "environments": "PHOTOSHOP",
        "type_for": "Asset"
    },
    {
        "name": "Shading",
        "code": "SHADING",
        "filename": "{{version.base_name}}_{{version.take_name}}_{{type.code}}_v{{'%03d'|format(version.version_number)}}_{{version.created_by.initials}}",
        "path": "Assets/{{version.base_name}}/{{type.code}}",
        "output_path": "{{version.path}}/OUTPUT/{{version.take_name}}",
        "extra_folders": "",
        "environments": "MAYA,HOUDINI",
        "type_for": "Asset"
    },
    {
        "name": "Tracking",
        "code": "TRACK",
        "filename": "{{version.base_name}}_{{version.take_name}}_{{type.code}}_v{{'%03d'|format(version.version_number)}}_{{version.created_by.initials}}",
        "path": "{{sequence.code}}/Shots/{{version.base_name}}/{{type.code}}",
        "output_path": "{{version.path}}/OUTPUT/{{version.take_name}}",
        "extra_folders": "",
        "environments": "3DEQUALIZER",
        "type_for": "Shot"
    }
]
