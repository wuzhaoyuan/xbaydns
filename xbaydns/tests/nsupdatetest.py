#!/usr/bin/env python
# encoding: utf-8
"""
nsupdatetest.py

Created by Razor on 2007-11-29.
Copyright (c) 2007 xBayDNS Team. All rights reserved.
"""


import basetest
import logging.config
import os
import pwd
import shutil
import tempfile
import time
import unittest

log = logging.getLogger('xbaydns.tests.nsupdatetest')
logging.basicConfig(level=logging.DEBUG)
from xbaydns.tools import initconf
from xbaydns.tools import namedconf
from xbaydns.tools import nsupdate
from xbaydns.conf import sysconf
from xbaydns.utils import shtools


class NSUpdateTest(basetest.BaseTestCase):
    def setUp(self):
        """初始化测试环境"""
        basetest.BaseTestCase.setUp(self)
        self._initnamedconf()
        
    def tearDown(self):
        """清洁测试环境"""
        basetest.BaseTestCase.tearDown(self)

    def _initnamedconf(self):
        returncode = initconf.main()
        nc = namedconf.NamedConf()
        nc.addAcl("hdacl",["any",])
        nc.addView("hdview", ["hdacl"])
        cmd = nc.addDomain(['example.com'])
        nc.save()
        nc.check_configfile()
        nc.named_restart()
            
    def test_addRecord(self):
        self._initnamedconf()
        recordlist = [['foo', 3600, 'IN', 'A', ['192.168.1.1', '172.16.1.1']], ['bar', 3600, 'IN', 'CNAME', ['foo']], ['', 86400, 'IN', 'MX', ['10 foo']]]
        nsupobj = nsupdate.NSUpdate('127.0.0.1', 'example.com.', view='hdview')
        nsupobj.addRecord(recordlist)
        nsupobj.commitChanges()
        record_a = nsupobj.queryRecord('foo.example.com.', rdtype='A')
        record_a.sort()
        self.assertEqual(record_a, ['172.16.1.1', '192.168.1.1'])
        record_cname = nsupobj.queryRecord('bar.example.com.', rdtype='CNAME')
        self.assertEqual(record_cname, ['foo.example.com.'])
        record_mx = nsupobj.queryRecord('example.com.', rdtype='MX')
        self.assertEqual(record_mx, ['10 foo.example.com.'])
        
    def test_removeRecord(self):
        self._initnamedconf()
        recordlist = [['foo', 3600, 'IN', 'A', ['192.168.1.1', '172.16.1.1']], ['bar', 3600, 'IN', 'CNAME', ['foo']], ['', 86400, 'IN', 'MX', ['10 foo']]]
        nsupobj = nsupdate.NSUpdate('127.0.0.1', 'example.com.', view='hdview')
        nsupobj.addRecord(recordlist)
        nsupobj.commitChanges()
        recordlist =  [['', 86400, 'IN', 'MX', ['10 foo']]]
        nsupobj.removeRecord(recordlist)
        recordlist = ['bar']
        nsupobj.removeRecord(recordlist, True)
        nsupobj.commitChanges()
        record_a = nsupobj.queryRecord('foo.example.com.', rdtype='A')
        record_a.sort()
        self.assertEqual(record_a, ['172.16.1.1', '192.168.1.1'])
        deleted = False
        try:
            record_cname = nsupobj.queryRecord('bar.example.com.', rdtype='CNAME')
        except nsupdate.NSUpdateException:
            deleted = True
        self.assertTrue(deleted)
        deleted = False
        try:
            record_mx = nsupobj.queryRecord('example.com.', rdtype='MX')
        except nsupdate.NSUpdateException:
            deleted = True
        self.assertTrue(deleted)
        
    def test_queryRecord(self):
        self._initnamedconf()
        recordlist = [['foo', 3600, 'IN', 'A', ['192.168.1.1', '172.16.1.1']], ['bar', 3600, 'IN', 'CNAME', ['foo']], ['', 86400, 'IN', 'MX', ['10 foo']]]
        nsupobj = nsupdate.NSUpdate('127.0.0.1', 'example.com.', view='hdview')
        nsupobj.addRecord(recordlist)
        nsupobj.commitChanges()
        record_a = nsupobj.queryRecord('foo.example.com', rdtype='A')
        record_a.sort()
        self.assertEqual(record_a, ['172.16.1.1', '192.168.1.1'])
        record_cname = nsupobj.queryRecord('bar.example.com.', rdtype='CNAME')
        self.assertEqual(record_cname, ['foo.example.com.'])
        record_mx = nsupobj.queryRecord('example.com.', rdtype='MX')
        self.assertEqual(record_mx, ['10 foo.example.com.'])
        
def suite():
    """集合测试用例"""
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(NSUpdateTest, 'test'))
    return suite

"""
单独运行command的测试用例
"""
if __name__ == '__main__':
    unittest.main(defaultTest='suite')
