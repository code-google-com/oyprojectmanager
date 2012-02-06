# -*- coding: utf-8 -*-
# Copyright (c) 2009-2012, Erkan Ozgur Yilmaz
# 
# This module is part of oyProjectManager and is released under the BSD 2
# License: http://www.opensource.org/licenses/BSD-2-Clause

#from PySide import QtGui
import sip
sip.setapi('QString', 2)
sip.setapi('QVariant', 2)
from PyQt4 import QtGui

class QApplication(QtGui.QApplication):
    """a singleton QApplication class
    """
    
    def __new__(cls, *args):
        if cls.instance() is None:
            # create a QApplication
            return QtGui.QApplication(*args)
        
        # return the instance
        return cls.instance()
