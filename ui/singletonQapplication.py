
from PyQt4 import QtGui

########################################################################
class QApplication( QtGui.QApplication ):
    """a singleton QApplication class
    """
    
    #----------------------------------------------------------------------
    def __new__(cls, *args, **kwargs ):
        if cls.instance() == None:
            QtGui.QApplication(*args, **kwargs)
        
        return cls.instance()