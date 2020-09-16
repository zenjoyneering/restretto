#!/usr/bin/env python
# -*- coding: utf-8 -*-


import yaml
from jinja2 import Template


def apply_context(src, context={}):
    """Apply context to dict"""
    result = None
    if type(src) is dict:
        # traverse nested dict
        result = {}
        for (k, v) in src.items():
            result[k] = apply_context(v, context)
    elif type(src) is list:
        # traverse list recursively
        result = []
        for i, item in enumerate(src):
            result.append(apply_context(item, context))
    elif type(src) is str and "{{" in src:
        #just apply template if string contains var
        result = yaml.full_load(Template(src).render(context))
    else:
        # integers/boolean and other non-templatable types
        result = src
    return result


def json_path(path, data):
    """Extract property by path"""
    fragments = path.split(".")
    src = data
    for p in fragments:
        src = src[int(p)] if (isinstance(src, list) and p.isdigit()) \
            else src.get(p, {})
    return src
