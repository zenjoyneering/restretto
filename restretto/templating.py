#!/usr/bin/env python
# -*- coding: utf-8 -*-


from jinja2 import Template


def apply_session_context(spec, context={}):
    """Format session template with values from vars section"""
    for key, val in spec.items():
        if isinstance(val, str):
            spec[key] = Template(val).render(context)
    return spec


def apply_action_context(spec, context={}):
    """Format templated fields in actions (after expansion)"""
    # format url
    spec['url'] = Template(spec['url']).render(context)
    # format headers
    for header, val in spec.get('headers', {}).items():
        spec['headers'][header] = Template(val).render(context)
    # format body
    if 'data' in spec and spec['data']:
        if isinstance(spec['data'], str):
            spec['data'] = Template(spec['data']).render(context)
        else:
            # TODO: recursively update data dict
            pass
    # TODO:  update json
    return spec
