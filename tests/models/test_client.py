# -*- coding: utf-8 -*-
# Copyright (c) 2009-2012, Erkan Ozgur Yilmaz
# 
# This module is part of oyProjectManager and is released under the BSD 2
# License: http://www.opensource.org/licenses/BSD-2-Clause

import unittest

from oyProjectManager.models.auth import Client


class ClientTester(unittest.TestCase):
    """tests the oyProjectManager.models.auth.Client class
    """
    
    def setUp(self):
        """set up the test
        """
        
        self.kwargs = {
            "name": "Test Client",
            "code": "TC",
            "generic_info": "This is a generic info holding may be phone "
                            "numbers and etc."
        }
        
        self.test_client = Client(**self.kwargs)
    
    def test_name_argument_is_skipped(self):
        """testing if a TypeError will be raised when the name argument is
        skipped
        """
        self.kwargs.pop("name")
        self.assertRaises(TypeError, Client, **self.kwargs)
    
    def test_name_argument_is_None(self):
        """testing if a TypeError will be raised when the name argument is None
        """
        self.kwargs["name"] = None
        self.assertRaises(TypeError, Client, **self.kwargs)
    
    def test_name_attribute_is_None(self):
        """testing if a TypeError will be raised when the name attribute is set
        to None
        """
        self.assertRaises(TypeError, setattr, self.test_client, 'name', None)
    
    def test_name_argument_is_not_a_string(self):
        """testing if a TypeError will be raised when the name argument is not
        a string instance
        """
        self.kwargs['name'] = 234
        self.assertRaises(TypeError, Client, **self.kwargs)
    
    def test_name_attribute_is_not_string(self):
        """testing if a TypeError will be raised when the name attribute is not
        set to a string instance
        """
        self.assertRaises(TypeError, setattr, self.test_client, 'name', 2342)
    
    def test_name_argument_is_working_properly(self):
        """testing if the value of the name argument is passed correctly to the
        name attribute
        """
        client_name = 'This is a Client name'
        self.kwargs['name'] = client_name
        new_client = Client(**self.kwargs)
        self.assertEqual(client_name, new_client.name)
    
    def test_name_attribute_is_working_properly(self):
        """testing if the name attribute is working properly
        """
        client_name = 'This is a Client name'
        self.assertNotEqual(client_name, self.test_client.name)
        self.test_client.name = client_name
        self.assertEqual(client_name, self.test_client.name)
    
    def test_code_argument_is_skipped(self):
        """testing if the client code argument is skipped the code attribute
        will be generated from the name attributes initials
        """
        test_name = "This is a test client"
        test_code = "TIATC"
        self.kwargs.pop('code')
        self.kwargs['name'] = test_name
        new_client = Client(**self.kwargs)
        self.assertTrue(new_client.code.startswith(test_code))
    
    def test_code_argument_is_None(self):
        """testing if the client code argument is None the code attribute will
        be generated from the name attribute initials
        """
        test_name = "This is a test client"
        test_code = "TIATC"
        self.kwargs['code'] = None
        self.kwargs['name'] = test_name
        new_client = Client(**self.kwargs)
        self.assertTrue(new_client.code.startswith(test_code))
    
    def test_code_attribute_is_set_to_None(self):
        """testing if the code attribute value will be regenerated from the
        name attribute if the code attribute is set to None
        """
        test_name = "This is a test client"
        test_code = "TIATC"
        self.kwargs['code'] = "AnotherCode"
        self.kwargs['name'] = test_name
        new_client = Client(**self.kwargs)
        new_client.code = None
        self.assertTrue(new_client.code.startswith(test_code))
    
    def test_code_argument_is_not_a_string_instance(self):
        """testing if a TypeError will be raised when the code argument is not
        a string instance
        """
        self.kwargs['code'] = 234
        self.assertRaises(TypeError, Client, **self.kwargs)
    
    def test_code_attribute_is_not_a_string_instance(self):
        """testing if a TypeError will be raised when the code attribute is not
        a string instance
        """
        self.assertRaises(TypeError, setattr, self.test_client, 'code', 3234)
    
    def test_code_argument_is_working_properly(self):
        """testing if the code argument value is correctly passed to the code
        attribute
        """
        test_code = "TestCode"
        self.kwargs['code'] = test_code
        new_client = Client(**self.kwargs)
        self.assertTrue(new_client.code.startswith(test_code))
    
    def test_code_attribute_is_working_properly(self):
        """testing if the code attribute is working properly
        """
        test_code = "TestCode"
        self.test_client.code = test_code
        self.assertEqual(self.test_client.code, test_code)
    
    def test_code_argument_formatting(self):
        """testing if the code argument is formatted correctly
        """
        test_code_in = "Test Code"
        test_code_expected = "TestCode"
        self.kwargs['code'] = test_code_in
        new_client = Client(**self.kwargs)
        self.assertEqual(test_code_expected, new_client.code)
    
    def test_code_attribute_formatting(self):
        """testing if the code attribute is formatted correctly
        """
        test_code_in = "Test Code"
        test_code_expected = "TestCode"
        self.test_client.code = test_code_in
        self.assertEqual(test_code_expected, self.test_client.code)
