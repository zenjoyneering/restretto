#!/usr/bin/env python
# -*- coding: utf-8 -*-

from . import http


class Result(object):

    def __init__(self, title=None):
        self.title = title
        self.failures = []
        self.succeed = []

    @property
    def ok(self):
        return len(self.failures) == 0


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
