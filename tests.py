#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    Unittests for restretto
"""

import unittest
import restretto

class LoaderExpansionsTestCase(unittest.TestCase):

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

    def test_expanded_action(self):
        spec = {'url': '/url', 'method': 'delete'}
        expanded = restretto.loader.expand_action(spec)
        expected = spec
        self.assertEqual(expected, expanded)

    def test_empty_action(self):
        spec = {'headers': {}, 'body': ''}
        with self.assertRaises(restretto.loader.ParseError):
            restretto.loader.expand_action(spec)

    def test_missing_url(self):
        spec = {'method': 'options'}
        with self.assertRaises(restretto.loader.ParseError):
            restretto.loader.expand_action(spec)

    def test_invalid_method(self):
        spec = {'url': '/url', 'method': 'bad_method'}
        with self.assertRaises(restretto.loader.ParseError):
            restretto.loader.expand_action(spec)

    def test_get_actions_requests(self):
        spec = {'actions': [], 'requests': []}
        with self.assertRaises(Exception):
            restretto.loader.get_actions(spec)

    def test_get_actions(self):
        spec = {'actions': [{'url': '/sample'}]}
        alt_spec = {'requests': [{'url': '/sample'}]}
        actions = restretto.loader.get_actions(spec)
        requests = restretto.loader.get_actions(alt_spec)
        self.assertEqual(len(actions), 1)
        self.assertEqual(actions, requests)


class TemplatingTestCase(unittest.TestCase):

    VARS = {
        'server': 'httpbin.org',
        'scheme': 'http',
        'extra': {
            'header': 'X-Custom',
            'value': 'custom-value',
            'payload_data': 'hello from vars'
        }
    }

    def test_template_baseUri(self):
        spec = {
            'title': 'Sample',
            'vars': dict(self.VARS),
            'baseUri': '{{scheme}}://{{server}}/base'
        }
        templated = restretto.templating.format_session(spec)
        self.assertEqual(templated['baseUri'], 'http://httpbin.org/base')

    def test_template_url(self):
        spec = {'url': '/headers?{{extra.header}}={{extra.value}}'}
        templated = restretto.templating.format_action(spec, dict(self.VARS))
        self.assertEqual(templated['url'], '/headers?X-Custom=custom-value')

    def test_template_headers(self):
        spec = {
            "url": "/get",
            "vars": {
                "accept": "application/json"
            },
            "headers": {
                "Content-Type": "{{accept}}"
            }
        }
        templated = restretto.templating.format_action(spec, self.VARS)
        self.assertEqual(templated['headers']['Content-Type'], 'application/json')

    def test_template_body(self):
        spec = {
            "url": "/post",
            "method": "post",
            "body": '{"some_key": "{{extra.payload_data}}"}'
        }
        templated = restretto.templating.format_action(spec, self.VARS)
        self.assertEqual(templated['body'], '{"some_key": "hello from vars"}')


class LoaderiFileLoadTestCase(unittest.TestCase):

    def test_load_unexisting_file(self):
        with self.assertRaises(FileNotFoundError):
            restretto.loader.load("test-data/unesixtant_file.yml")

    def test_load_empty_file(self):
        data = restretto.loader.load("test-data/empty.yml")
        self.assertFalse(data)

    def test_load_bad_file(self):
        with self.assertRaises(Exception):
            restretto.loader.load("test-data/broken/bad.yml")

    def test_load_valid_file(self):
        data = restretto.loader.load("test-data/simple.yml")
        self.assertEqual(len(data), 1)

    def test_empty_actions(self):
        data = restretto.loader.load('test-data/empty-actions.yml')
        self.assertFalse(data)

    def test_missing_actions(self):
        data = restretto.loader.load('test-data/missing-actions.yml')
        self.assertFalse(data)

    def test_actions_requests_error(self):
        with self.assertRaises(restretto.loader.ParseError):
            restretto.loader.load('test-data/broken/actions-with-requests.yml')


class LoaderDirLoadTestCase(unittest.TestCase):

    def test_load_from_dir(self):
        data = restretto.loader.load("test-data/")
        self.assertEqual(len(data), 3)

    def test_load_from_unexistant_dir(self):
        with self.assertRaises(FileNotFoundError):
            restretto.loader.load("test-data/missing-dir")

    def test_load_from_bad_dir(self):
        with self.assertRaises(Exception):
            restretto.loader.load("test-data/broken")



if __name__ == "__main__":
    unittest.main()
