# -*- coding: utf-8 -*-
# Copyright (c) 2009-2012, Erkan Ozgur Yilmaz
# 
# This module is part of oyProjectManager and is released under the BSD 2
# License: http://www.opensource.org/licenses/BSD-2-Clause

import time

class CachedMethod(object):
    """caches the result of a class method inside the instance
    """

    def __init__(self, method):
        # record the unbound-method and the name
        #print "running __init__ in CachedMethod"

        if not isinstance(method, property):
            self._method = method
            self._name = method.__name__
            self._isProperty = False
        else:
            self._method = method.fget
            self._name = method.fget.__name__
            self._isProperty = True

        self._obj = None

    def __get__(self, inst, cls):
        """use __get__ to get the instance object and create the attributes
        
        if it is a property call __call__
        """
        #print "running __get__ in CachedMethod"

        self._obj = inst

        if not hasattr(self._obj, self._name + "._data"):
            #print "creating the data"
            setattr(self._obj, self._name + "._data", None)
            setattr(self._obj, self._name + "._lastQueryTime", 0)
            setattr(self._obj, self._name + "._maxTimeDelta", 60)
            #print "finished creating data"

        if self._isProperty:
            return self.__call__()
        else:
            return self

    def __call__(self, *args, **kwargs):
        """
        """
        #print "running __call__ in CachedMethod"

        delta = time.time() -\
                getattr(self._obj, self._name + "._lastQueryTime")

        if delta > getattr(self._obj, self._name + "._maxTimeDelta")\
            or getattr(self._obj, self._name + "._data") is None:
            
            # call the function and store the result as a cache
            #print "caching the data"
            data = self._method(self._obj, *args, **kwargs)
            setattr(self._obj, self._name + "._data", data)

            # zero the time
#            lastQueryTime = time.time()
            setattr(self._obj, self._name + "._lastQueryTime", time.time())
        #else:
            #print "returning the cached data"

        return getattr(self._obj, self._name + "._data")


    def __repr__(self):
        """Return the function's representation
        """
        objectsRepr = str(self._obj)
        objectsName = objectsRepr.split(' ')[0].split('.')[-1]

        cachedObjectsRepr =\
            '<cached bound method ' + objectsName + '.' + self._name + \
            ' of ' + objectsRepr + '>'

        return cachedObjectsRepr


class InputBasedCachedMethod(object):
    """caches the result of a class method inside the instance based on the input parameters
    """

    def __init__(self, method):
        # record the unbound-method and the name
        #print "running __init__ in InputBasedCachedMethod"

        self._method = method
        self._name = method.__name__
        self._obj = None

    def __get__(self, inst, cls):
        """use __get__ just to get the instance object
        """
        #print "running __get__ in InputBasedCachedMethod"

        self._obj = inst
        if not hasattr(self._obj, self._name + "._outputData"):
            #print "creating the data"
            setattr(self._obj, self._name + "._outputData", list())
            setattr(self._obj, self._name + "._inputData", list())
            #print "finished creating data"

        return self

    def __call__(self, *args, **keys):
        """for now it uses only one argument
        """
        #print "running __call__ in InputBasedCachedMethod"

        outputData = getattr(self._obj, self._name + "._outputData")
        inputData = getattr(self._obj, self._name + "._inputData")

        # combine args and keys
        argsKeysCombined = list()
        argsKeysCombined.append(args)
        argsKeysCombined.append(keys)

        if (not argsKeysCombined in inputData) or outputData is None:
            #print "calculating new data"
            data = self._method(self._obj, *args, **keys)
            inputData.append(argsKeysCombined)
            outputData.append(data)
            setattr(self._obj, self._name + "._inputdata", inputData)
            setattr(self._obj, self._name + "._outputData", outputData)

            return data
        else:
            #print "returning cached data"
            return outputData[inputData.index(argsKeysCombined)]

    def __repr__(self):
        """Return the function's repr
        """
        #print "running __repr_ in InputBasedCachedMethod"
        objectsRepr = str(self._obj)
        objectsName = objectsRepr.split(' ')[0].split('.')[-1]
        cachedObjectsRepr = \
            '<cached bound method ' + objectsName + '.' + self._name + \
            ' of ' + objectsRepr + '>'
        return cachedObjectsRepr 
