#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import requests
from urllib.request import urljoin
from . import templating
from . import assertions

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)


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

    def execute(self):
        # for each request
        logger.info("Running {} test session".format(self.spec.get('title', '')))
        logger.debug("Session baseUri: {}".format(self.baseUri))
        for action in self.spec['actions']:
            title = action.pop('title') if 'title' in action else action['url']
            logger.info('Requesting {}'.format(title))
            # apply context for request
            spec = templating.apply_action_context(action, self.context)
            # create assertions
            assertion = assertions.Assert(spec.pop('assert') if 'assert' in spec else [])
            # get response
            response = self.request(**spec)
            # test assertion
            try:
                assertion.test(response)
                self.result.succeed.append(response)
            # store result
            except:
                self.result.failures.append(response)
            # TODO: store vars in context
        return self.result

    def request(self, **spec):
        spec['url'] = urljoin(self.baseUri, spec['url'])
        request = requests.Request(**spec)
        prepared = request.prepare()
        return self.session.send(prepared)
