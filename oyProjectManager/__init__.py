# -*- coding: utf-8 -*-
"""
oyProjectManager by Erkan Ozgur Yilmaz (c) 2009-2011

Description :
-------------
The oyProjectManager is created to manage our animation studios own projects,
within a predefined project structure. It is also a simple asset management
system. The main purpose of this system is to create projects, sequences and
to allow users to save their files in correct folders with correct names. So
anyone can find their files later on by using this system. But again it is not
a complete Production Asset Management System (look for `Stalker` if you are
searching for a complete ProdAM).

This system uses a per project based SQLite3 databases.

Another aim of this code is to prevent the user to use the OSes own file
manager (ie. Windows Explorer on Windows ) to define the name and placement of
the asset file. In normal circumstances the user is not allowed to define the
file name.

While working for a project, every time we create an asset the files can
generally be grouped with the purpose of that file. For example we create files
for models, animations, renders etc.. So it is easy to define a file name that
can specify the type of that asset version, and we can create a simple logic to
define the placement of the files, in a predefined folder structure. So this
project manager creates the folder structure and the file name whenever a user
uses this code while saving its asset.

Another advantage of oyProjectManager is, it gives a framework to the project
manager, to edit all the project and sequences with very simple Python scripts.
"""

__version__ = "0.2.0b1"

import logging
logging.basicConfig(
    format='%(asctime)s:%(levelname)s:%(module)s:%(funcName)s:%(message)s',
    datefmt="%Y-%d-%m %H:%M:%S"
)

logging.info("Init oyProjectManager")

from oyProjectManager import config
conf = config.Config()
