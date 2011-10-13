# -*- coding: utf-8 -*-



import unittest
from oyProjectManager.core.abstractClasses import Singleton


class SingletonTester(unittest.TestCase):
    """Tests the AbstractClasses class
    """
    
    def test_singleton_creates_singleton_classes(self):
        """testing if Singleton creates singleton classes
        """
        
        # create two singleton classes and check their id
        a = Singleton()
        b = Singleton()
        
        self.assertEqual(id(a), id(b))
