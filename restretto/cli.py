#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    CLI support for restretto
    ~~~~~~~~~~~~~~~~~~~~~~~~~
"""


import sys
import argparse
from . import runner
from . import loader


parser = argparse.ArgumentParser(description="REST resources/endpoints testing tool")
parser.add_argument("path", help="path to look for tests (file or directory)")
parser.add_argument("--xunit", dest="xunit_dir", default=None,
                    help="output xunit reports to this dir")
parser.add_argument("-q", "--quiet", action="store_true")


def main(args=sys.argv[1:]):
    arguments = parser.parse_args(args)

    sources = loader.load(arguments.path)
    if not sources:
        print("No test sessions found, exiting")
        sys.exit(1)

    for spec in sources:
        test_session = runner.Runner(spec)
        hdr = "Test session: {}".format(spec.get('title', test_session.baseUri))
        print(hdr)
        print('-' * len(hdr))
        for action in test_session.actions:
            title = action.pop('title') if 'title' in action else action['url']
            (response, error) = test_session.execute(action)
            if error:
                print("{}: failed".format(title))
                print("    {}".format(str(error)))
            else:
                print("{}: passed".format(title))
        print("")
        print("")
