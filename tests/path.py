# -*- coding: utf-8 -*-
# ++ This file `path.py` is generated at 11/17/16 5:41 AM ++
try:
    # upper that python 3.4
    import pathlib
except ImportError:
    import pathlib2 as pathlib

__author__ = "Md Nazrul Islam<connect2nazrul@gmail.com>"

# Current Working Directory
TEST_ROOT = pathlib.Path(__file__).parent
FIXTURE_PATH = TEST_ROOT / "fixtures"
