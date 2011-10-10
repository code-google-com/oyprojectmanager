#-*- coding: utf-8 -*-


DATABASE_FILE_NAME = ".metadata.db"

SHOT_PREFIX = "SH"
SHOT_PADDING = 3

REV_PREFIX = "r"
REV_PADDING = 2
VER_PREFIX = "v"
VER_PADDING = 3

TIME_UNIT = "pal"

# Default Project Structure

SHOT_DEPENDENT_FOLDERS = [
    "SHOTS/{{assetBaseName}}/ANIMATIONS",
    "SHOTS/{{assetBaseName}}/CAMERAS",
    "SHOTS/{{assetBaseName}}/COMP",
    "SHOTS/{{assetBaseName}}/FX",
    "SHOTS/{{assetBaseName}}/EDIT/ONLINE",
    "SHOTS/{{assetBaseName}}/PREVIS",
    "SHOTS/{{assetBaseName}}/RENDERED_IMAGES",
    "SHOTS/{{assetBaseName}}/LIGHTING",
    "SHOTS/{{assetBaseName}}/SCENE_ASSEMBLY",
    "SHOTS/{{assetBaseName}}/MATCH_MOVE"
]

SHOT_INDEPENDENT_FOLDERS = [
    "PAINTINGS/ILLUSTRATION",
    "PAINTINGS/ILLUSTRATION/CHARACTER_DESIGNS",
    "PAINTINGS/MATTE_PAINT",
    "PAINTINGS/TEXTURES",
    "EDIT/OFFLINE",
    "EDIT/ONLINE/WHOLE_SEQUENCE",
    "EDIT/SOUND",
    "EDIT/ANIMATIC_STORYBOARD",
    "EDIT/MAKING_OF",
    "OTHERS",
    "OTHERS/assets",
    "OTHERS/clips",
    "OTHERS/data",
    "OTHERS/fur",
    "OTHERS/fur/furAttrMap",
    "OTHERS/fur/furEqualMap",
    "OTHERS/fur/furFiles",
    "OTHERS/fur/furImages",
    "OTHERS/fur/furShadowMap",
    "OTHERS/mel",
    "OTHERS/particles",
    "REFERENCES",
    "REFERENCES/ARTWORKS",
    "REFERENCES/TEXT",
    "REFERENCES/TEXT/SCENARIO",
    "REFERENCES/PHOTOS",
    "REFERENCES/STORYBOARD"
]


ASSET_TYPES = [
    {
        "name": "ANIM",
        "path": "SHOTS/{{assetBaseName}}/{{assetTypeName}}",
        "shotDependent": True,
        "environments": "MAYA,HOUDINI",
        "output_path": \
            "SHOTS/{{assetBaseName}}/{{assetTypeName}}/OUTPUT/{{assetSubName}}"
    },
    {
        "name": "CAMERA",
        "path": "SHOTS/{{assetBaseName}}/{{assetTypeName}}",
        "shotDependent": True,
        "environments": "MAYA,HOUDINI",
        "output_path": \
            "SHOTS/{{assetBaseName}}/{{assetTypeName}}/OUTPUT/{{assetSubName}}"
    },
    {
        "name": "COMP",
        "path": "SHOTS/{{assetBaseName}}/{{assetTypeName}}",
        "shotDependent": True,
        "environments": "NUKE",
        "output_path": \
            "SHOTS/{{assetBaseName}}/{{assetTypeName}}/OUTPUT/{{assetSubName}}",
    },
    {
        "name": "EDIT",
        "path": "SHOTS/{{assetBaseName}}/{{assetTypeName}}",
        "shotDependent":True,
        "environments": "NUKE",
        "output_path": \
            "ASSETS/{{assetBaseName}}/{{assetTypeName}}/OUTPUT/{{assetSubName}}"
    },
    {
        "name":"FX",
        "path": "SHOTS/{{assetBaseName}}/{{assetTypeName}}",
        "shotDependent": True,
        "environments": "MAYA,HOUDINI",
        "output_path": \
            "SHOTS/{{assetBaseName}}/{{assetTypeName}}/OUTPUT/{{assetSubName}}"
    },
    {
        "name":"MODEL",
        "path": "ASSETS/{{assetBaseName}}/{{assetTypeName}}",
        "shotDependent": False,
        "environments": "MAYA,HOUDINI",
        "output_path": \
            "ASSETS/{{assetBaseName}}/{{assetTypeName}}/OUTPUT/{{assetSubName}}"
    },
    {
        "name": "OTHER",
        "path": "OTHERS/{{assetBaseName}}/{{assetTypeName}}",
        "shotDependent": False,
        "environments": "MAYA,HOUDINI,NUKE",
        "output_path": \
            "OTHERS/{{assetBaseName}}/{{assetTypeName}}/OUTPUT/{{assetSubName}}"
    },
    {
        "name":"PREVIS",
        "path": "SHOTS/{{assetBaseName}}/{{assetTypeName}}",
        "shotDependent": True,
        "environments": "MAYA,HOUDINI",
        "output_path": \
            "SHOTS/{{assetBaseName}}/{{assetTypeName}}/OUTPUT/{{assetSubName}}"
    },
    {
        "name": "LIGHTING",
        "path": "SHOTS/{{assetBaseName}}/{{assetTypeName}}",
        "shotDependent": True,
        "environments": "MAYA,HOUDINI",
        "output_path": \
            "SHOTS/{{assetBaseName}}/{{assetTypeName}}/OUTPUT/{{assetSubName}}"
    },
    {
        "name": "RIG",
        "path": "ASSETS/{{assetBaseName}}/{{assetTypeName}}",
        "shotDependent": "0",
        "environments": "MAYA,HOUDINI",
        "output_path": \
            "ASSETS/{{assetBaseName}}/{{assetTypeName}}/OUTPUT/{{assetSubName}}"
    },
    {
        "name": "SCENE_ASSEMBLY",
        "path":"SHOTS/{{assetBaseName}}/{{assetTypeName}}",
        "shotDependent": "1",
        "environments": "MAYA,HOUDINI",
        "output_path": \
            "SHOTS/{{assetBaseName}}/{{assetTypeName}}/OUTPUT/{{assetSubName}}"
    },
    {
        "name": "MATTE",
        "path": "SHOTS/{{assetBaseName}}/PAINTINGS/{{assetTypeName}}",
        "shotDependent": False,
        "environments": "PHOTOSHOP",
        "output_path": \
            "ASSETS/{{assetBaseName}}/{{assetTypeName}}/OUTPUT/{{assetSubName}}"
    },
    {
        "name": "TEXTURE",
        "path": "ASSETS/{{assetBaseName}}/PAINTINGS/{{assetTypeName}}",
        "shotDependent": "0",
        "environments": "PHOTOSHOP",
        "output_path": \
            "ASSETS/{{assetBaseName}}/{{assetTypeName}}/OUTPUT/{{assetSubName}}"
    },
    {
        "name": "ILLUSTRATION",
        "path": "ASSETS/{{assetBaseName}}/PAINTINGS/{{assetTypeName}}",
        "shotDependent": False,
        "environments": "PHOTOSHOP",
        "output_path": \
            "ASSETS/{{assetBaseName}}/{{assetTypeName}}/OUTPUT/{{assetSubName}}"
    },
    {
        "name": "SHADING",
        "path": "ASSETS/{{assetBaseName}}/{{assetTypeName}}",
        "shotDependent": False,
        "environments": "MAYA,HOUDINI",
        "output_path": \
            "ASSETS/{{assetBaseName}}/{{assetTypeName}}/OUTPUT/{{assetSubName}}"
    },
    {
        "name": "TRACKING",
        "path": "SHOTS/{{assetBaseName}}/{{assetTypeName}}",
        "shotDependent": True,
        "environments": "3DEQUALIZER",
        "output_path": \
            "SHOTS/{{assetBaseName}}/{{assetTypeName}}/OUTPUT/{{assetSubName}}"
    }
]
