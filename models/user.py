__version__ = "10.1.28"



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
    def _getName(self):
        """returns the user name
        """
        return self._name
    
    
    
    #----------------------------------------------------------------------
    def _setName(self, name):
        """sets the user name
        """
        self._name = name
    
    name = property( _getName, _setName )
    
    
    #----------------------------------------------------------------------
    def _getInitials(self):
        """returns the user initials
        """
        return self._initials
    
    
    
    #----------------------------------------------------------------------
    def _setInitials(self, initials):
        """sets the user initials
        """
        self._initials = initials
    
    initials = property( _getInitials, _setInitials )






########################################################################
class UserType(object):
    """a class for managing user types
    """
    
    #----------------------------------------------------------------------
    def __init__(self):
        pass
        
        
    
    