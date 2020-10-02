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


def load_var_files(src, files):
    all_vars = {}
    base = os.path.dirname(src)
    for f in files:
        src = os.path.join(base, f)
        with open(src) as var_file:
            all_vars.update(yaml.full_load(var_file))
    return all_vars


def load(path):
    data = []
    files = []
    if os.path.isdir(path):
        # load only files with supported extension skipping hiddens like '.yml'
        for (curdir, subdirs, entries) in os.walk(path, followlinks=True):
            for entry in entries:
                (name, ext) = os.path.splitext(entry)
                if name and ext in SUPPORTED_EXTENSIONS:
                    files.append(os.path.join(curdir, entry))
    else:
        files.append(path)
    for entry in files:
        with open(entry) as source:
            parsed = yaml.full_load(source)
        # silently skip empty files
        if not parsed:
            continue
        # add filename to spec
        parsed['filename'] = entry
        # parse vars files, if any
        var_data = parsed.get('vars', None)
        if  type(var_data) is str:
            parsed["vars"] = load_var_files(entry, [var_data])
        elif type(var_data) is list:
            # parse set of file
            parsed["vars"] = load_var_files(entry, var_data)
        data.append(Session(parsed))
    # filter out empty elements (loaded from empty files)
    return [item for item in data if item]
