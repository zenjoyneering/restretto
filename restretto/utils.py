#!/usr/bin/env python
# -*- coding: utf-8 -*-


import yaml
from jinja2 import Template


def apply_context(src, context={}):
    """Apply context to dict"""
    return yaml.load(Template(yaml.dump(src)).render(context))
