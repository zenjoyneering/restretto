#!/usr/bin/env python
# -*- coding: utf-8 -*-


from fnmatch import fnmatch
from .utils import json_path
from .errors import ExpectError


class ResponseTest(object):

    message = "Bad response ({0} {1})"

    def expect(self, statement, message=''):
        if not statement:
            raise ExpectError(message)

    def test(self, response):
        self.expect(response, self.message.format(response.status_code, response.reason))

    def assert_is(self, item, value):
        # coerce numberic and str types
        types = set((type(item), type(value)))
        if types == set((str, int)) or types == set((str, float)):
            cond = str(item) == str(value)
        else:
            cond = item == value
        self.expect(cond, "{} != {}".format(item, value))

    def assert_is_not(self, item, value):
        # coerce int and str types
        types = set((type(item), type(value)))
        if types == set((str, int)):
            cond = str(item) != str(value)
        else:
            cond = item != value
        self.expect(cond, "{} == {}".format(item, value))

    def assert_contains(self, item, value):
        self.expect(value in item, "{} not found in {}".format(value, item))

    def assert_length(self, item, value):
        self.expect(
            len(item) == value,
            "Length mismatch: got {} intead of expected {}".format(len(item), value)
        )

    def assert_statements(self, statements, item):
        # assert all conditions are satisfied
        for (cond, value) in statements.items():
            assert_fn = 'assert_{}'.format(cond)
            getattr(self, assert_fn)(item, value)


class StatusCodeTest(ResponseTest):

    message = "Unexpected status ({0} instead of {1})"

    def __init__(self, status):
        # convert int code to str
        self.expected = str(status) if isinstance(status, int) else status

    def test(self, response):
        if isinstance(self.expected, str):
            self.expect(
                fnmatch(str(response.status_code), self.expected.replace('x', '?')),
                self.message.format(response.status_code, self.expected)
            )
        else:
            # treat as list of possible statuses
            self.expect(
                str(response.status_code) in self.expected,
                self.message.format(response.status_code, self.expected)
            )


class ResponsePropertyTest(ResponseTest):

    def __init__(self, name, statements={}):
        self.name = name
        self.statements = statements


class HeaderTest(ResponsePropertyTest):

    def test(self, response):
        header = response.headers.get(self.name, None)
        self.expect(header, "Header not found: {}".format(self.name))
        self.assert_statements(self.statements, header)


class BodyTest(ResponsePropertyTest):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # pop property definition, if available
        self.prop = self.statements.pop('property', None)

    def test(self, response):
        data = None
        if self.name == 'text':
            data = response.text
        elif self.name == 'json' and not self.prop:
            data = response.json()
        elif self.name == 'json' and self.prop:
            # get required property value
            data = json_path(self.prop, {'json': response.json()})
        self.assert_statements(self.statements, data)


class Assert(object):

    def __init__(self, statements=[]):
        self.statements = []
        self._has_status_test = False
        if not statements:
            # assume default simple check
            self.statements = [ResponseTest()]
        else:
            for spec in statements:
                self.statements.append(self.statement(spec))
            if not self._has_status_test:
                # add default test for status_code to be ok
                self.statements.insert(0, ResponseTest())

    def test(self, response):
        for stmt in self.statements:
            stmt.test(response)
        return True

    def statement(self, spec):
        """Statement factory"""
        spec = dict(spec)
        if 'status' in spec:
            self._has_status_test = True
            return StatusCodeTest(spec['status'])
        if 'header' in spec:
            return HeaderTest(spec.pop('header'), spec)
        if 'body' in spec:
            return BodyTest(spec.pop('body'), spec)
