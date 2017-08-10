#!/usr/bin/env python
# encoding: utf-8
"""
basetest.py

Created by 黄 冬 on 2007-11-19.
Copyright (c) 2007 __MyCompanyName__. All rights reserved.

这里定义了BaseTestCase类，主要是用于所有的测试用例的公共初始化工作。所有的测试用例都继承这个类，这样将来有公共的初始化工作时都会在这里完成。
"""

import unittest

class BaseTestCase(unittest.TestCase):
    
    def setUp(self):
        pass
        
    def tearDown(self):
        pass