#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    CLI support for restretto
    ~~~~~~~~~~~~~~~~~~~~~~~~~
"""


import sys
from . import runner
from . import loader


def main(args=sys.argv[1:]):
    if not args:
        print("Usage: {} path_to_yaml_or_dir".format(sys.argv[0]))
        sys.exit(1)
    print("Loading: {}".format(sys.argv[1]))
    sources = loader.load(sys.argv[1])
    failures = []
    for spec in sources:
        result = runner.execute(spec)
        if not result.ok:
            failures.append(result)
