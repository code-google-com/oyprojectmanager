#-*- coding: utf-8 -*-

from exceptions import Exception


class CircularDependencyError(Exception):
    """Raised when there is circular dependencies between Versions
    """

    def __init__(self, value=""):
        super(CircularDependencyError, self).__init__(value)
        self.value = value

    def __str__(self):
        return repr(self.value)
