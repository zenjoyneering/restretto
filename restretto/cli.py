#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    CLI support for restretto
    ~~~~~~~~~~~~~~~~~~~~~~~~~
"""


import sys
from jinja2 import Template
from . import runner
from . import loader

REPORT = Template("""
{% for report in failures %}
{{ report.title }}
    {% for response in report.failures %}
    {{ response.url }}: failed with {{response.status_code}}
    {% endfor %}

{% endfor %}
""")


def main(args=sys.argv[1:]):
    if not args:
        print("Usage: {} path_to_yaml_or_dir".format(sys.argv[0]))
        sys.exit(1)
    print("Loading: {}".format(sys.argv[1]))
    sources = loader.load(sys.argv[1])
    if not sources:
        print("No test sessions found, exiting")
        sys.exit(1)
    failures = []
    for spec in sources:
        result = runner.Runner(spec).execute()
        if not result.ok:
            failures.append(result)
    print(REPORT.render(failures=failures))
    if not failures:
        print("{} sessions passed")
        sys.exit(0)
    else:
        print("{} sessions of {} failed".format(len(failures), len(sources)))
        sys.exit(2)
