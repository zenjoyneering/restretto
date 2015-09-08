#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
from urllib.request import urljoin
from . import templating


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
        self.session.headers.update(self.spec.get('header'))
        # prepare result
        self.result = Result(self.spec.get('title', ''))

    def execute(self):
        # for each request
        for action in self.spec['actions']:
            title = action.pop('title') if 'title' in action else action['url']
            # apply context for request
            spec = templating.apply_action_context(action, self.context)
            # create assertions
            assertion = Assertion(spec.pop('assert') if 'assert' in spec else [])
            # get response
            response = self.request(**spec)
            # test assertion
            try:
                assertion.test(response)
                self.result.succeed.append(response)
            # store result
            except:
                self.result.failures.append(response)
        return self.result

    def request(self, **spec):
        request = requests.Request(**spec)
        prepared = request.prepare()
        return self.session.send(prepared)



def execute(spec):
    actions = spec.pop('actions')
    result = Result(spec.pop('title'))
    session = http.Session(**spec)
    print("Running {}".format(result.title))
    for request in actions:
        title = request.pop('title') if 'title' in request else request['url']
        response = session.action(**request)
        status = "SUCCEED" if response.ok else "FAILED"
        print("{}: {}".format(title, status))
        if not response.ok:
            print("{method} {url}: {status} {reason}".format(
                status=response.status_code, reason=response.reason,
                **request)
            )
            result.failures.append(response)
        else:
            result.succeed.append(response)
    return result
