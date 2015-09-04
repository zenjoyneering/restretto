#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    restretto YML loader
    ~~~~~~~~~~~~~~~~~~~~
"""

import yaml
import os


SUPPORTED_EXTENSIONS = (".yml", ".yaml")


def get_actions(spec):
    if 'requests' in spec and 'actions' in spec:
        raise Exception('Only one form should be used')
    return spec.pop('requests') if 'requests' in spec else spec.pop('actions')


def expand_action(spec):
    pass


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
            # expand actions to standart form
            parsed['actions'] = [
                expand_action(action) for action in get_actions(parsed)
            ]
            data.append(parsed)
    # filter out empty elements (loaded from empty files)
    return [item for item in data if item]
