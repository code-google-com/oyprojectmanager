# -*- coding: utf-8 -*-
# Copyright (c) 2009-2012, Erkan Ozgur Yilmaz
# 
# This module is part of oyProjectManager and is released under the BSD 2
# License: http://www.opensource.org/licenses/BSD-2-Clause

import os
import tempfile
import unittest
from oyProjectManager import utils

class UtilsTester(unittest.TestCase):
    """Tests the functions under oyProjectManager.utils
    """

    def test_mkdir_for_non_existing_path(self):
        """testing if mkdir will create the given path without any error
        """

        # create a temp path
        tempdir = tempfile.mktemp()

        # create the dir
        utils.mkdir(tempdir)

        # now check if the path exists
        self.assertTrue(os.path.exists(tempdir))

        # clean the test
        os.rmdir(tempdir)

    def test_mkdir_for_existing_path(self):
        """testing if mkdir will greacefuly handle the exception if the given
        path already exists
        """

        # create a temp path
        tempdir = tempfile.mktemp()

        # create the dir
        os.makedirs(tempdir)

        # create the dir with mkdir
        # it should handle the error
        utils.mkdir(tempdir)

        # clean the test
        os.rmdir(tempdir)

    def test_sort_string_numbers(self):
        """testing if the sort_string_numbers working properly
        """

        test_values = ["123", "12", "098", "a23", "32b43"]
        expected_output = ["12", "32b43", "098", "123", "a23"]

        self.assertEqual(utils.sort_string_numbers(test_values),
                         expected_output)

    def test_uncompress_range_working_properly(self):
        """testing the range tools
        """

        test_values = [
            ("1-4", [1, 2, 3, 4]),
            ("10-5", [5, 6, 7, 8, 9, 10]),
            ("1,4-7", [1, 4, 5, 6, 7]),
            ("1,4-7,11-4", [1, 4, 5, 6, 7, 8, 9, 10, 11]),
        ]

        for test_value in test_values:
            self.assertEqual(
                utils.uncompress_range(test_value[0]),
                test_value[1]
            )
