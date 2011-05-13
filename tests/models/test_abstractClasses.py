# -*- coding: utf-8 -*-



import unittest
from oyProjectManager.models import abstractClasses






########################################################################
class SingletonTester(unittest.TestCase):
    """Tests the AbstractClasses class
    """
    
    
    
    #----------------------------------------------------------------------
    def test_singleton_creates_singleton_classes(self):
        """testing if Singleton creates singleton classes
        """
        
        # create two singleton classes and check their id
        a = abstractClasses.Singleton()
        b = abstractClasses.Singleton()
        
        self.assertEquals(id(a), id(b))






########################################################################
class EnvironmentTester(unittest.TestCase):
    """tests Environment abstract class
    """
    
    pass
