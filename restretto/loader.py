#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    restretto YML loader
    ~~~~~~~~~~~~~~~~~~~~
"""

import yaml
import os


SUPPORTED_EXTENSIONS = (".yml", ".yaml")

HTTP_METHODS = frozenset(('get', 'options', 'head', 'post', 'put', 'patch', 'delete'))


class ParseError(Exception):
    pass


def get_actions(spec):
    """Get actions from loaded session spec"""
    if 'requests' in spec and 'actions' in spec:
        raise ParseError('Only one form should be used')
    # skip files without requests at all
    if 'requests' not in spec and 'actions' not in spec:
        return []
    entries = spec.pop('requests') if 'requests' in spec else spec.pop('actions')
    return entries or []


def expand_action(spec):
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
    return spec


def load(path):
    data = []
    files = []
    if os.path.isdir(path):
        # load only files with supported extension skipping hiddens like '.yml'
        for entry in os.listdir(path):
            (name, ext) = os.path.splitext(entry)
            if name and ext in SUPPORTED_EXTENSIONS:
                files.append(os.path.join(path, entry))
    else:
        files.append(path)
    for entry in files:
        with open(entry) as source:
            parsed = yaml.load(source)
        # silently skip empty files
        if not parsed:
            continue
        # expand actions to standart form
        parsed['actions'] = [
            expand_action(action) for action in get_actions(parsed)
        ]
        # skip empty sessions
        if  parsed['actions']:
            data.append(parsed)
    # filter out empty elements (loaded from empty files)
    return [item for item in data if item]
