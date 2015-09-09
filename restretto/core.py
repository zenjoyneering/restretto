# -*- coding: utf-8 -*-
"""
    Core classes for restretto
    ~~~~~~~~~~~~~~~~~~~~~~~~~~
"""

from urllib.request import urljoin


class ParseError(Exception):
    pass


class RESTAction(object):
    """Single HTTP request action"""

    @staticmethod
    def expand_request(spec):
        """Expand from shortened forms to standart form"""
        # guess method
        request = {
            'url': spec.get('url'),
            'method': spec.get('method'),
            'headers': spec.get('headers'),
            'params': spec.get('params'),
            'data': spec.get('data'),
            'json': spec.get('json')
        }
        if request['url'] and not request['method']:
            # if url is given, assume methid is get
            request['method'] = 'get'
        elif not request['method']:
            # search method defintion
            methods = set(spec.keys()).intersection(HTTP_METHODS)
            if len(methods) != 1:
                raise ParseError('Multiple methods given for action')
            http_verb = methods.pop()
            # get url
            request['url'] = spec[http_verb]
            request['method'] = http_verb
        # validate fields
        if not request['url'] or not request['method']:
            raise ParseError('Url or method for action not specified')
        request['method'] = spec['method'].lower()
        if request['method'] not in HTTP_METHODS:
            raise ParseError('Unknown http method verb: {}'.format(spec['method']))
        if 'expect' in  spec and 'assert' in spec:
            raise ParseError("Only one form should be used")
        return request

    def __init__(self, spec):
        """Create action from specification"""
        self.spec = spec
        # get context var bindings
        self.vars = self.spec.get('vars', {})

        # get asserions
        if 'expect' in spec and 'assert' in spec:
            # only one form of assertions should be used at a time
            raise ParseError("Only expect or assert keyword can be used")
        self.assertion = self.spec.get('assert', self.spec.get('expect', {}))

        self.request = self.expand_request(spec)
        # response and errors are not known
        self.response = None
        self.error = None

    @property
    def title(self):
        return self.spec.get('title') or self.spec.get('name') or self.request['url']

    def run(self, baseUri='', context={}, session=None):
        """Run actions' request, perform assertion testing"""
        self.request['url'] = urljoin(baseUri, self.request['url'])
        # apply template to request and assertions
        # create assertions
        # get response
        # test assertion
        # save context vars
        return self
