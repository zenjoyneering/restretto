#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    Unittests for restretto
"""

import unittest
import restretto


class LoaderTestCase(unittest.TestCase):

    def test_load_unexisting_file(self):
        with self.assertRaises(FileNotFoundError):
            restretto.loader.load("test-data/unesixtant_file.yml")

    def test_load_empty_file(self):
        data = restretto.loader.load("test-data/empty.yml")
        self.assertFalse(data)

    def test_load_bad_file(self):
        with self.assertRaises(Exception):
            restretto.loader.load("test-data/bad.yml")

    def test_load_valid_file(self):
        data = restretto.loader.load("test-data/samples/simple.yml")
        self.assertEqual(len(data), 1)

    def test_load_from_dir(self):
        data = restretto.loader.load("test-data/samples/")
        self.assertEqual(len(data), 2)

    def test_load_from_unexistant_dir(self):
        with self.assertRaises(FileNotFoundError):
            restretto.loader.load("test-data/missing-dir")

    def test_load_from_bad_dir(self):
        with self.assertRaises(Exception):
            restretto.loader.load("test-data")

    def test_get_actions(self):
        spec = {'actions': [], 'requests': []}
        with self.assertRaises(Exception):
            restretto.loader.get_actions(spec)

    def test_expand_action_method(self):
        spec = {'url': '/some/url', 'headers': {}}
        expanded = restretto.loader.expand_action(spec)
        expected = {'method': 'get', 'url': '/some/url', 'headers': {}}
        self.assertEqual(expanded, expected)

    def test_expand_action_url(self):
        spec = {'put': '/url', 'json': [1, 2]}
        expanded = restretto.loader.expand_action(spec)
        expected = {'method': 'put', 'url': '/url', 'json': [1, 2]}
        self.assertEqual(expanded, expected)


if __name__ == "__main__":
    unittest.main()
