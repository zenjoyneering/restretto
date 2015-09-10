# -*- coding: utf-8 -*-
"""
    Core classes for restretto
    ~~~~~~~~~~~~~~~~~~~~~~~~~~
"""

import requests
from urllib.request import urljoin

from . import assertions
from .errors import ParseError
from .utils import apply_context


HTTP_METHODS = frozenset(('get', 'options', 'head', 'post', 'put', 'patch', 'delete'))


class Action(object):
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
        request['method'] = request['method'].lower()
        if request['method'] not in HTTP_METHODS:
            raise ParseError('Unknown http method verb: {}'.format(spec['method']))
        # clean empty fields
        return {k: v for k, v in request.items() if v is not None}

    def __init__(self, spec):
        """Create action from specification"""
        self.spec = spec
        # get context var bindings
        self.vars = self.spec.get('vars', {})

        # get asserions
        if 'expect' in spec and 'assert' in spec:
            # only one form of assertions should be used at a time
            raise ParseError("Only expect or assert keyword can be used")
        self.asserts = self.spec.get('assert', self.spec.get('expect'))

        self.request = self.expand_request(spec)
        # response and errors are not known
        self.response = None
        self.error = None

    @property
    def title(self):
        return self.spec.get('title') or self.spec.get('name') \
            or '{method} {url}'.format(**self.request)

    def run(self, baseUri='', context={}, session=None):
        """Run actions' request, perform assertion testing"""
        self.request['url'] = urljoin(baseUri, self.request['url'])
        # apply template to request and assertions
        self.request = apply_context(self.request, context)
        self.asserts = apply_context(self.asserts, context)
        # create assertions
        assertion = assertions.Assert(self.asserts)
        # get response
        request = requests.Request(**self.request).prepare()
        http = session or requests.Session()
        self.response = http.send(request)
        # test assertion, will raise an excep
        try:
            assertion.test(self.response)
        except Exception as error:
            # save error
            self.error = error
            # reraise
            raise
        # save context vars
        return self


class Session(object):
    """REST session"""

    def __init__(self, spec, context={}):
        self.spec = spec
        self.context = spec.get('vars', {}).copy()
        self.context.update(context)
        self.baseUri = apply_context(spec.get('baseUri', ''), self.context)
        self.http = requests.Session()
        headers = self.spec.get('headers') or {}
        self.headers = apply_context(headers, self.context)
        self.http.headers.update(self.headers)
        # create actions
        self.actions = []
        self._parse_actions()

    def _parse_actions(self):
        """Get actions from loaded session spec"""
        if 'requests' in self.spec and 'actions' in self.spec:
            raise ParseError('Only one form should be used')
        # skip files without requests at all
        if 'requests' not in self.spec and 'actions' not in self.spec:
            return []
        entries = self.spec.get('requests') or self.spec.get('actions') or []
        for item in entries:
            self.actions.append(Action(item))

    def __bool__(self):
        return bool(self.actions)

    @property
    def filename(self):
        return self.spec.get('filename')

    @property
    def title(self):
        return self.spec.get('title', '') or self.spec.get('name', '') or self.spec.get('session', '')

    def run(self, action=None):
        executed = action.run(self.baseUri, self.context, self.http)
        self.context.update(executed.vars)
        return executed
