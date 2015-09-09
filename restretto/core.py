# -*- coding: utf-8 -*-
"""
    Core classes for restretto
    ~~~~~~~~~~~~~~~~~~~~~~~~~~
"""


class ParseError(Exception):
    pass


class Action(object):
    """Single HTTP request action"""

    @staticmethod
    def expand(spec):
        """Expand from shortened forms to standart form"""
        # guess method
        if 'method' not in spec and 'url' in spec:
            # if url is given, assume methid is get
            spec['method'] = 'get'
        elif 'method' not in spec:
            # search method defintion
            methods = set(spec.keys()).intersection(HTTP_METHODS)
            if len(methods) != 1:
                raise ParseError('Multiple methods given for action')
            http_verb = methods.pop()
            # get url
            spec['url'] = spec.pop(http_verb)
            spec['method'] = http_verb
        # validate fields
        if 'method' not in spec or 'url' not in spec:
            raise ParseError('Url or method for action not specified')
        spec['method'] = spec['method'].lower()
        if spec['method'] not in HTTP_METHODS:
            raise ParseError('Unknown http method verb: {}'.format(spec['method']))
        # only one form of assertions should be used at a time
        if 'expect' in  spec and 'assert' in spec:
            raise ParseError("Only one form should be used")
        # convert assertions to canonical form
        # expect -> assert, expect looks very similar to except
        if 'expect' in spec:
            spec['assert'] = spec.pop('expect')
        return spec

    def __init__(self, spec):
        """Create action from specification"""
        self.spec = spec
        # get context var bindings
        self.vars = self.spec.get('vars', {})

        # get asserions
        if 'expect' in spec and 'assert' in spec:
            raise ParseError("Only expect or assert keyword can be used")
        self.assertion = self.spec.get('assert', self.spec.get('expect', {}))

        self.request = self.expand(spec)
        # response and errors are not known
        self.response = None
        self.error = None
