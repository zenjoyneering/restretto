#!/usr/bin/env python
# -*- coding: utf-8 -*-


from fnmatch import fnmatch


class Statement(object):

    def test(self, response):
        raise NotImplementedError()


class ResponseIsOk(Statement):

    def test(self, response):
        assert response.ok
        return True


class StatusAsExpected(Statement):

    def __init__(self, status):
        self.expected = status

    def test(self, response):
        if isinstance(self.expected, str):
            assert fnmatch(str(response.status_code), self.expected.replace('x', '?'))
        else:
            # treat as list of possible statuses
            assert str(response.status_code) in self.expected
        return True


class ResponseItemInspector(Statement):

    def __init__(self, name, conditions={}):
        self.name = name
        self.conditions = conditions

    def _get_testing_item(self, response):
        # should be overrided
        return None

    def test(self, response):
        # at least testing item should exists
        item = self._get_testing_item(response)
        assert item
        # assert all conditions are satisfied
        for (cond, value) in self.conditions.items():
            test_fn = 'test_{}'.format(cond)
            getattr(self, test_fn)(item, value)
        return True

    def test_is(self, item, value):
        assert item == value

    def test_is_not(self, item, value):
        assert item != value

    def test_contains(self, item, value):
        assert value in item


class HeaderAsExpected(ResponseItemInspector):

    def _get_testing_item(self, response):
        return response.headers.get(self.name, None)


class BodyAsExpected(ResponseItemInspector):

    def _get_testing_item(self, response):
        if self.name == 'text':
            return response.text
        elif self.name == 'json':
            return response.json()
        else:
            return None


class Assert(object):

    def __init__(self, statements=[]):
        self.statements = []
        if not statements:
            # assume default simple check
            self.statements = [ResponseIsOk()]
        else:
            for spec in statements:
                self.statements.append(self.statement(spec))

    def test(self, response):
        for stmt in self.statements:
            stmt.test(response)
        return True

    def statement(self, spec):
        """Statement factory"""
        spec = dict(spec)
        if 'status' in spec:
            return StatusAsExpected(spec['status'])
        if 'header' in spec:
            return HeaderAsExpected(spec.pop('header'), spec)
        if 'body' in spec:
            return BodyAsExpected(spec.pop('body'), spec)
