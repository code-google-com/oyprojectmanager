# -*- coding: utf-8 -*-
# Copyright (c) 2009-2012, Erkan Ozgur Yilmaz
# 
# This module is part of oyProjectManager and is released under the BSD 2
# License: http://www.opensource.org/licenses/BSD-2-Clause

__version__ = "0.2.0"

import logging
logging.basicConfig(
    format='%(asctime)s:%(levelname)s:%(module)s:%(funcName)s:%(message)s',
    datefmt="%Y-%d-%m %H:%M:%S"
)

logging.info("Init oyProjectManager")

from oyProjectManager import config
conf = config.Config()
