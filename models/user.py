__version__ = "10.6.6"



########################################################################
class User(object):
    """a class for managing users
    """
    
    
    
    #----------------------------------------------------------------------
    def __init__(self, name='', initials=''):
        self._name = name
        self._initials = initials
        self._type = '' # userType object
        pass
    
    
    #----------------------------------------------------------------------
    def name():
        def fget(self):
            return self._name
        
        def fset(self, name):
            self._name = name
        
        return locals()
    
    name = property( **name() )
    
    
    #----------------------------------------------------------------------
    def initials():
        def fget(self):
            return self._initials
        
        def fset(self, initials):
            self._initials = initials
        
        return locals()
    
    initials = property( **initials() )






########################################################################
class UserType(object):
    """a class for managing user types
    """
    
    #----------------------------------------------------------------------
    def __init__(self):
        pass
        
        
    
    