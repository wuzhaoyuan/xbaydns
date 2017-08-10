#!/usr/bin/env python
# encoding: utf-8
"""
setup.py

Created by 黄 冬 on 2007-11-19.
Copyright (c) 2007 __MyCompanyName__. All rights reserved.
"""

import os
from setuptools import setup, find_packages
import sys


setup(
    name = 'xbaydns',
    version = '1.0.0',
    description = 'xBayDNS System',
    long_description = \
"""DNS and GSLB Manager System""",
    author = 'xBayDNS Team',
    author_email = 'huangdong@gmail.com',
    license = 'BSD License',
    url = 'http://xbaydns.googlecode.com',
    download_url = 'http://xbaydns.googlecode.com',
    zip_safe = False,

    packages = find_packages(exclude=['*tests*']),
    test_suite = 'xbaydns.tests.suite',
    entry_points = {
        'console_scripts': [
            'xbdinit = xbaydns.tools.initconf:main',
            'xbdsync = xbaydns.tools.confsync:main'
        ]
    }
)
