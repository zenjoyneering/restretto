#!/usr/bin/env python
# -*- coding: utf-8 -*-


from jinja2 import Template


def format_session(spec, context={}):
    """Format session template with values from vars section"""
    values = spec.pop('vars') if 'vars' in spec else {}
    values.update(context)
    for key, val in spec.items():
        spec[key] = Template(val).render(values)
    return spec


def format_action(spec, context={}):
    """Format templated fields in actions (after expansion)"""
    values = spec.pop('vars') if 'vars' in spec else {}
    values.update(context)
    # format url
    spec['url'] = Template(spec['url']).render(values)
    # format headers
    for header, val in spec.get('headers', {}).items():
        spec['headers'][header] = Template(val).render(values)
    # format body
    if 'body' in spec and spec['body']:
        spec['body'] = Template(spec['body']).render(values)
    return spec
