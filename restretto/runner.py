#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import requests
from urllib.request import urljoin
from . import templating
from . import assertions

logger = logging.getLogger(__name__)
#logging.basicConfig(level=logging.DEBUG)


class Result(object):

    def __init__(self, title=None):
        self.title = title
        self.failures = []
        self.succeed = []

    @property
    def ok(self):
        return len(self.failures) == 0


class Runner(object):

    def __init__(self, spec, context={}):
        # define context
        self.context = spec.get('vars', {})
        self.context.update(context)
        # apply context
        self.spec = templating.apply_session_context(spec, self.context)
        # setup session
        self.session = requests.Session()
        self.session.headers.update(self.spec.get('headers', {}))
        self.baseUri = spec.get('baseUri', '')
        # prepare result
        self.result = Result(self.spec.get('title', ''))

    @property
    def actions(self):
        return self.spec['actions']

    def execute(self, action):
        # apply context for request
        spec = templating.apply_action_context(action, self.context)
        # create assertions
        assertion = assertions.Assert(spec.pop('assert') if 'assert' in spec else [])
        # get response
        response = self.request(**spec)
        # test assertion
        try:
            assertion.test(response)
            self.result.succeed.append((response, None))
            return self.result.succeed[-1]
        except AssertionError as error:
            self.result.failures.append((response, error))
            return self.result.failures[-1]
        # TODO: store vars in context

    def request(self, **spec):
        spec['url'] = urljoin(self.baseUri, spec['url'])
        request = requests.Request(**spec)
        prepared = request.prepare()
        return self.session.send(prepared)
