#!/usr/bin/env python
# -*- coding: utf-8 -*-

from . import loader

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: {} path_to_yaml_or_dir".format(sys.argv[0]))
        sys.exit(1)
    print("Loading: {}".format(sys.argv[1]))
    loader.load(sys.argv[1])
