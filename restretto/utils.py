#!/usr/bin/env python
# -*- coding: utf-8 -*-


import yaml
from jinja2 import Template


def apply_context(src, context={}):
    """Apply context to dict"""
    return yaml.load(Template(yaml.dump(src)).render(context))


def json_path(path, data):
    """Extract property by path"""
    fragments = path.split(".")
    src = data
    for p in fragments:
        src = src.get(p, {})
    return src
