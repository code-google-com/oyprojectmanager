# -*- coding: utf-8 -*-



from PyQt4 import QtGui






########################################################################
class QApplication(QtGui.QApplication):
    """a singleton QApplication class
    """
    
    #----------------------------------------------------------------------
    def __new__(cls, *args):
        if cls.instance() is None:
            # create a QApplication
            return QtGui.QApplication(*args)
        
        # return the instance
        return cls.instance()
