# encoding: utf-8
"""
namedconftest.py

Created by QingFeng on 2007-11-23.
Copyright (c) 2007 yanxu. All rights reserved.
"""

import basetest
import logging.config
import os
import shutil
import tempfile
import time
import unittest
import base64

log = logging.getLogger('xbaydns.tests.namedconftest')
logging.basicConfig(level=logging.DEBUG)

from xbaydns.tools.namedconf import *
import datetime

class NamedConfTest(basetest.BaseTestCase):
    def setUp(self):
        """初始化测试环境"""
        self.basedir = os.path.realpath(tempfile.mkdtemp(suffix='xbaydns_test'))
        basetest.BaseTestCase.setUp(self)
        self.nc=NamedConf()

    def tearDown(self):
        """清洁测试环境"""
        shutil.rmtree(self.basedir)
        basetest.BaseTestCase.tearDown(self)

    def test_addAcl(self):
        cmd = self.nc.addAcl('internal',['127.0.0.1',])
        self.assertEqual(cmd.strip(),'acl "internal" { 127.0.0.1; };')
    def test_delAcl(self):
        self.nc.addAcl('internal',['127.0.0.1',])
        self.assertTrue(self.nc.delAcl('internal'))
        self.assertFalse(self.nc.delAcl('home'))
    def test_addView(self):
        cmd = self.nc.addView('home')
        self.assertEqual(cmd.strip().replace("\n","").replace("    "," "),
                         'include "defaultzone.conf";key "home-view-key" { algorithm hmac-md5; secret "aG9tZS12aWV3LWtleQ==";};view "home" { match-clients { key "home-view-key"; }; %s };')
    
        cmd = self.nc.addView('internal',['127.0.0.1',])
        self.assertEqual(cmd.strip().replace("\n","").replace("    "," "),
                         'include "defaultzone.conf";key "internal-view-key" { algorithm hmac-md5; secret "aW50ZXJuYWwtdmlldy1rZXk=";};view "internal" { match-clients { "127.0.0.1";key "internal-view-key"; }; %s };')
        cmd = self.nc.addView('internal',['127.0.0.1','10.10.10.10/24',])
        self.assertEqual(cmd.strip().replace("\n","").replace("    "," "),
                         'include "defaultzone.conf";key "internal-view-key" { algorithm hmac-md5; secret "aW50ZXJuYWwtdmlldy1rZXk=";};view "internal" { match-clients { "127.0.0.1";"10.10.10.10/24";key "internal-view-key"; }; %s };')
    
    def test_updateView(self):
        cmd = self.nc.updateView('internal',['127.0.0.1',])
        self.assertEqual(cmd.strip().replace("\n","").replace("    "," "),
                         'include "defaultzone.conf";key "internal-view-key" { algorithm hmac-md5; secret "aW50ZXJuYWwtdmlldy1rZXk=";};view "internal" { match-clients { "127.0.0.1";key "internal-view-key"; }; %s };')
    def test_genSecret(self):
        key = self.nc.genSecret('telcome-view-key')
        self.assertEqual(base64.b64decode(key),"telcome-view-key")
    def test_loadViewKey(self):
        key = self.nc.loadViewKey('internal')
        self.assertEqual(key.keys()[0],"internal-view-key")
        self.assertEqual(base64.b64decode(key.values()[0]),"internal-view-key")
    def test_delView(self):
        self.nc.addView('internal',['127.0.0.1',])
        self.assertTrue(self.nc.delView('internal'))
        self.assertFalse(self.nc.delView('home'))
    def test_addDomain(self):
        self.nc.addView('internal',['127.0.0.1',])
        cmd = self.nc.addDomain(['sina.com.cn','mail.sina.com.cn'])
        self.assertEqual(cmd.replace("  ", "").replace("\n","").strip(),'''
                zone "sina.com.cn" {
                    type master;
                    file "dynamic/internal.sina.com.cn.file";
                };
                zone "mail.sina.com.cn" {
                    type master;
                    file "dynamic/internal.mail.sina.com.cn.file";
                };
                '''.replace("  ", "").replace("\n","").strip())
    def test_delDomain(self):
        self.nc.addView('internal',['127.0.0.1',])
        self.nc.addDomain(['sina.com.cn','mail.sina.com.cn'])
        self.assertTrue(self.nc.delDomain('sina.com.cn'))
        self.assertFalse(self.nc.delDomain('a.sina.com.cn'))
    def test_getDomainFileName(self):
        self.assertEqual(self.nc.getDomainFileName("sina.com.cn","home"),
                        "dynamic/home.sina.com.cn.file")
    def test_getSerial(self):
        d=datetime.datetime.now()
        self.assertEqual(self.nc.getSerial(),'%s%s%s01'%(d.year,str(d.month).zfill(2),str(d.day).zfill(2)))    
    def test_save(self):
        self.nc.addAcl('internal',['127.0.0.1',])
        self.nc.addAcl('home',['127.0.0.1',])
        self.nc.addAcl('fx-subnet',['192.253.254/24',])
        self.nc.addView('internal',['fx-subnet',])
        self.nc.addDomain(['sina.com.cn','mail.sina.com.cn'])
        self.nc.save(self.basedir)
        self.assertTrue(os.stat(os.path.join(self.basedir,'acl/internal.conf')))
        self.assertTrue(os.stat(os.path.join(self.basedir,'acl/home.conf')))
        self.assertTrue(os.stat(os.path.join(self.basedir,'acl/fx-subnet.conf')))
        self.assertTrue(os.stat(os.path.join(self.basedir,'view/internal.conf')))
        self.assertTrue(os.stat(os.path.join(self.basedir,'acl/acldef.conf')))
        self.assertTrue(os.stat(os.path.join(self.basedir,'dynamic/internal.sina.com.cn.file')))
        self.assertTrue(os.stat(os.path.join(self.basedir,'dynamic/internal.mail.sina.com.cn.file')))

def suite():
    """集合测试用例"""
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(NamedConfTest, 'test'))
    return suite

"""
单独运行command的测试用例
"""
if __name__ == '__main__':
    unittest.main(defaultTest='suite')