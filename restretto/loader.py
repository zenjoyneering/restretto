#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    restretto YML loader
    ~~~~~~~~~~~~~~~~~~~~
"""

import yaml
import os
from .rest import Session


SUPPORTED_EXTENSIONS = (".yml", ".yaml")


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
        # add filename to spec
        parsed['filename'] = entry
        data.append(Session(parsed))
    # filter out empty elements (loaded from empty files)
    return [item for item in data if item]
