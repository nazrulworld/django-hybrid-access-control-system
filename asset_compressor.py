#! /usr/bin/env python
# -*- coding: utf-8 -*-
# ++ This file `compile_assets.py` is generated at 6/10/16 10:32 AM ++
from __future__ import print_function
import os
import sys
import json
import shutil
import logging
import rcssmin
import rjsmin
import argparse
import subprocess

__author__ = "Md Nazrul Islam<connect2nazrul@gmail.com>"

logger = logging.getLogger("HACS_ASSET_COMPRESSOR")

ASSETS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'assets')
HACS_ROOT = os.path.dirname(__import__('hacs').__file__)
LOUD = {
    'stdout': subprocess.PIPE,
    'stderr': subprocess.PIPE
}

parser = argparse.ArgumentParser()
parser.add_argument(
    '-a',
    '--asset-dir',
    dest="asset_dir",
    action="store",
    default=ASSETS_DIR
)
parser.add_argument(
    '-v',
    '--verbose',
    dest="verbose",
    action='count',
)


def get_version():
    """"""
    return __import__('hacs').__version__


def validate():
    """"""
    if subprocess.call(["pip list | grep rjsmin"], shell=True, **LOUD):
        print("rjsmin is required and not installed.\nUse `pip install rjsmin`\nTerminating...")
        sys.exit()

    if subprocess.call(["pip list | grep rcssmin"], shell=True, **LOUD):
        print("rcssmin is required and not installed.\nUse `pip install rcssmin`\nTerminating...")
        sys.exit()


def main():
    """"""
    options = parser.parse_args()
    print("== Asset Minification Stated ==")
    for root, dirs, files in os.walk(options.asset_dir):

        for filename in files:
            if filename != "config.json":
                continue
            base_dir = root
            with open(os.path.join(root, filename)) as f:
                asset_configs = json.load(f)

            if asset_configs.get('js', None):
                print("== Javascript minification started for `%s` ==" % asset_configs.get('meta')['name'])
                _str = ""
                _total_size = 0
                for jsfile in asset_configs['js'].get('source'):
                    print(os.path.join(base_dir, jsfile))
                    with open(os.path.join(base_dir, jsfile), "r") as f1:
                        _str += rjsmin.jsmin(f1.read()) + "\n"

                if len(_str):
                    with open(os.path.join(HACS_ROOT, asset_configs['js'].get('dest')), 'w') as f2:
                        f2.write(_str)
                if asset_configs['js'].get('copy', None):
                    for source, dest in asset_configs['js'].get('copy').items():
                        if os.path.isdir(os.path.join(base_dir, source)):
                            if os.path.exists(os.path.join(HACS_ROOT, dest)):
                                shutil.rmtree(os.path.join(HACS_ROOT, dest))

                            shutil.copytree(os.path.join(base_dir, source), os.path.join(HACS_ROOT, dest))

                        elif os.path.isfile(os.path.join(base_dir, source)):
                            shutil.copyfile(os.path.join(base_dir, source), os.path.join(HACS_ROOT, dest))

                print("== Javascript minification completed for `%s` ==" % asset_configs.get('meta')['name'])

            if asset_configs.get('css', None):
                print("== CSS minification started for `%s` ==" % asset_configs.get('meta')['name'])
                _str = ""
                for cssfile in asset_configs['css'].get('source'):
                    print(os.path.join(base_dir, cssfile))
                    with open(os.path.join(base_dir, cssfile), "r") as f1:
                        _str += rcssmin.cssmin(f1.read()) + "\n"

                if len(_str):
                    with open(os.path.join(HACS_ROOT, asset_configs['css'].get('dest')), 'w') as f2:
                        f2.write(_str)

                if asset_configs['css'].get('copy', None):
                    for source, dest in asset_configs['css'].get('copy').items():
                        if os.path.isdir(os.path.join(base_dir, source)):
                            if os.path.exists(os.path.join(HACS_ROOT, dest)):
                                shutil.rmtree(os.path.join(HACS_ROOT, dest))
                            shutil.copytree(os.path.join(base_dir, source), os.path.join(HACS_ROOT, dest))

                        elif os.path.isfile(os.path.join(base_dir, source)):
                            shutil.copyfile(os.path.join(base_dir, source), os.path.join(HACS_ROOT, dest))
                print("== CSS minification completed for `%s` ==" % asset_configs.get('meta')['name'])

    print ("== Asset Minification Completed ==")

if __name__ == "__main__":
    main()
