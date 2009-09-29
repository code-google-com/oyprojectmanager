import time

#######################################################################
class CachedMethod(object):
    """caches the result of a class method inside the instance
    """
    
    
    
    def __init__(self, method):
        # record the unbound-method and the name
        self._method = method
        self._name = method.__name__
        self._obj = None
    
    
    
    def __get__(self, inst, cls):
        """use __get__ just to get the instance object
        """
        #print "running __get__ in CachcedMethod"
        
        self._obj = inst
        try:
            getattr ( self._obj, self._name + "._data" )
        except AttributeError:
            #print "AttributeError, filling the data"
            setattr ( self._obj, self._name + "._data", None )
            setattr ( self._obj, self._name + "._lastQueryTime", 0 )
            setattr ( self._obj, self._name + "._maxTimeDelta", 60 )
            #print "finished filling"
        
        return self
    
    
    
    def __call__(self, *args, **kwargs):
        """
        """
        #print "running __call__ in CachedMethod"
        
        delta = time.time() - getattr( self._obj, self._name + "._lastQueryTime" )
        
        if delta > getattr(self._obj, self._name + "._maxTimeDelta") or getattr(self._obj, self._name + "._data" ) == None:
            # call the function and store the result as a cache
            #print "caching the data"
            data = self._method(self._obj, *args, **kwargs )
            setattr( self._obj, self._name + "._data", data )
            
            # zero the time
            lastQueryTime = time.time()
            setattr( self._obj, self._name + "._lastQueryTime", time.time() )
        #else:
            #print "returning the cached data"
        
        return getattr( self._obj, self._name + "._data" )
    
    
    
    def __repr__(self):
        """Return the function's docstring
        """
        return self._method.__doc__