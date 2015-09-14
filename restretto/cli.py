#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    CLI support for restretto
    ~~~~~~~~~~~~~~~~~~~~~~~~~
"""


import sys
import argparse
from . import load
from .errors import ExpectError


parser = argparse.ArgumentParser(description="REST resources/endpoints testing tool")
parser.add_argument("path", help="path to look for tests (file or directory)")
parser.add_argument("--xunit", dest="xunit_dir", default=None,
                    help="output xunit reports to this dir")
parser.add_argument("-q", "--quiet", action="store_true")


def main(args=sys.argv[1:]):
    arguments = parser.parse_args(args)

    sessions = load(arguments.path)
    if not sessions:
        print("No test sessions found, exiting")
        sys.exit(1)

    for test_session in sessions:
        hdr = "Test session: {}".format(test_session.title)
        print(hdr)
        print('-' * len(hdr))
        for action in test_session.actions:
            try:
                test_session.run(action)
                print("[PASS] {}: Ok".format(action.title))
            except ExpectError as failure:
                print("[FAILURE] {}: {}".format(action.title, failure))
                print("   " + action.response.text)
            except Exception as error:
                print("[ERROR] {}: {}".format(action.title, error))
        print("")
        print("")
