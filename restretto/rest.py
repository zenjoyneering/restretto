# -*- coding: utf-8 -*-
"""
    Core classes for restretto
    ~~~~~~~~~~~~~~~~~~~~~~~~~~
"""

import time
import requests
from urllib.request import urljoin

from .utils import json_path
from . import assertions
from .errors import ParseError
from .utils import apply_context


HTTP_METHODS = frozenset(('get', 'options', 'head', 'post', 'put', 'patch', 'delete'))


class Resource(object):
    """Single HTTP resource"""

    @staticmethod
    def parse_from_dict(spec):
        """Expand from shortened forms to standart form"""
        # guess method
        request = {
            'url': spec.get('url'),
            'method': spec.get('method'),
            'headers': spec.get('headers'),
            'params': spec.get('params'),
            'data': spec.get('data'),
            'json': spec.get('json'),
            'files': spec.get('files')
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
        """Create resource from specification"""
        if isinstance(spec, str):
            self.spec = {'url': spec}
        else:
            self.spec = spec

        # get context var bindings
        self.vars = self.spec.get('vars', {})

        # get asserions
        if 'expect' in spec and 'assert' in spec:
            # only one form of assertions should be used at a time
            raise ParseError("Only expect or assert keyword can be used")
        self.asserts = self.spec.get('assert', self.spec.get('expect'))

        # set download path for response, if required
        self.download = self.spec.get('download', None)

        self.request = self.parse_from_dict(self.spec)
        # response and errors are not known
        self.response = None
        self.error = None

    @property
    def title(self):
        return self.spec.get('title') or self.spec.get('name') \
            or '{method} {url}'.format(**self.request)

    def test(self, baseUri='', context={}, session=None):
        """Make request, perform assertion testing"""
        self.request['url'] = urljoin(baseUri, self.request['url'].lstrip('/'))
        # apply template to request and assertions
        self.request = apply_context(self.request, context)
        self.asserts = apply_context(self.asserts, context)
        # load files, if provided
        # TODO: add mimetype detection
        # TODO: files should be searched relative to current yml
        # see https://github.com/wirewit/restretto/issues/16 for details
        file_data = self.request.pop('files', {})
        if type(file_data) is list:
            # parsing files: [file1, file2] structure, assuming name as "files"
            file_data = {
                'files': file_data
            }
        # TODO: raise exception on parsing not-dict structure
        if type(file_data) is dict:
            # parsing name: file or name: [file1, file2] structure
            self.request['files'] = []
            for file_name, file_path in file_data.items():
                if type(file_path) is str:
                    self.request['files'].append((file_name, open(file_path, 'rb')))
                elif type(file_path) is list:
                    for f in file_path:
                        self.request['files'].append((file_name, open(f, 'rb')))

        # make sure all headers are strings
        if "headers" in self.request:
            for k, v in self.request["headers"].items():
                self.request["headers"][k] = str(v)

        # create assertions
        assertion = assertions.Assert(self.asserts)
        # get response
        http = session or requests.Session()
        self.response = http.request(**self.request)
        # test assertion, will raise an excep
        try:
            assertion.test(self.response)
        except Exception as error:
            # save error
            self.error = error
            # reraise
            raise
        # save context vars
        if self.vars:
            data = {
                'headers': self.response.headers
            }
            try:
                data['json'] = self.response.json()
            except ValueError:
                # no json, it's can be ok
                data['json'] = None
                pass
            for name, path in self.vars.items():
                self.vars[name] = json_path(path, data)

        # save response body as downloaded file
        # path taken relative to cwd, may be should be changed to yml-related path
        # see https://github.com/wirewit/restretto/issues/16 for details
        if self.download:
            with open(self.download, "wb") as download:
                download.write(self.response.content)

        return self


class Wait(object):

    def __init__(self, spec):
        self.spec = spec
        self.vars = {}
        self.delay = int(spec.get("wait", 0))

    @property
    def title(self):
        return self.spec.get('title') or self.spec.get('name') \
            or 'Waiting for {} second(s)'.format(self.delay)

    def test(self, *args, **kwargs):
        time.sleep(self.delay)
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
        # make sure all headers are strings
        for k, v in self.headers.items():
            self.headers[k] = str(v)
        self.http.headers.update(self.headers)
        self.http.verify = spec.get('verify', False)
        # create resources
        self.resources = []
        self._parse_resources()

    def _parse_resources(self):
        """Get resources from loaded session spec"""
        entries = self.spec.get('resources') or []
        for item in entries:
            if "wait" in item:
                self.resources.append(Wait(item))
            else:
                self.resources.append(Resource(item))

    def __bool__(self):
        return bool(self.resources)

    @property
    def filename(self):
        return self.spec.get('filename')

    @property
    def title(self):
        return self.spec.get('title', '') or self.spec.get('name', '') or self.spec.get('session', '')

    def test(self, resource=None, context=None):
        context = context or {}
        context.update(self.context)
        executed = resource.test(self.baseUri, context, self.http)
        self.context.update(executed.vars)
        return executed
