#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
from urllib.request import urljoin


class Session(object):
    """REST session"""

    def __init__(self, headers={}, baseUri='', **kwargs):
        self.session = requests.Session()
        # set common headers
        self.session.headers.update(headers)
        self.baseUri = baseUri

    def action(self, url, method='GET', headers=None, body=None, json=None):
        # create Request
        request = requests.Request(method, urljoin(self.baseUri, url), headers=headers)
        if json:
            request.json = json
        elif body:
            request.data = body
        prepared = request.prepare()
        return self.session.send(prepared)
