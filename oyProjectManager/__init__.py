# -*- coding: utf-8 -*-
# Copyright (c) 2009-2012, Erkan Ozgur Yilmaz
# 
# This module is part of oyProjectManager and is released under the BSD 2
# License: http://www.opensource.org/licenses/BSD-2-Clause

__version__ = "0.2.5.1"

import logging
logging.basicConfig(
    format='%(asctime)s:%(levelname)s:%(module)s:%(funcName)s:%(message)s',
    datefmt="%Y-%d-%m %H:%M:%S"
)

logging.info("Init oyProjectManager")

from oyProjectManager import config
conf = config.Config()

# TODO: Think about adding Task's and Type's as a replacement of VersionType
# or stating in a different form separate the VersionType in to two new class
# called Task and Type (as in Stalker)

# TODO: Add tests for deletion of Project, Sequence, Shot, Asset and other types 

from oyProjectManager.models.asset import Asset
from oyProjectManager.models.auth import Client, User
from oyProjectManager.models.entity import VersionableBase, EnvironmentBase
from oyProjectManager.models.errors import CircularDependencyError
from oyProjectManager.models.link import FileLink
from oyProjectManager.models.mixins import IOMixin
from oyProjectManager.models.project import Project
from oyProjectManager.models.repository import Repository
from oyProjectManager.models.sequence import Sequence
from oyProjectManager.models.shot import Shot
from oyProjectManager.models.version import (Version, VersionType,
                                             VersionTypeEnvironments,
                                             VersionStatusComparator,
                                             Version_References)
