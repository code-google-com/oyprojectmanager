# -*- coding: utf-8 -*-
# Copyright (c) 2009-2014, Erkan Ozgur Yilmaz
# 
# This module is part of oyProjectManager and is released under the BSD 2
# License: http://www.opensource.org/licenses/BSD-2-Clause


# create a logger
import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)

class CircularDependencyError(Exception):
    """Raised when there is circular dependencies between Versions
    """

    def __init__(self, value=""):
        super(CircularDependencyError, self).__init__(value)
        self.value = value

    def __str__(self):
        return repr(self.value)
