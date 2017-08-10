#!/usr/bin/env python
# encoding: utf-8
"""
sysintergratetest.py

Created by 黄 冬 on 2007-11-26.
Copyright (c) 2007 xBayDNS Team. All rights reserved.

这个测试是一个集成的系统测试。它从一个什么都不知道的环境开始进行测试。这里包括初始化环境，增加相关的配置，一步步的到齐全的环境。这里将会有很多的挑战，但是完成这个测试，
我们就完成了一个用户的典型操作过程。
"""

import basetest
import logging.config
import os
import shutil
import tempfile
import unittest

log = logging.getLogger('xbaydns.tests.sysintergratetest')
logging.basicConfig(level=logging.DEBUG)

from xbaydns.tools import initconf
from xbaydns.conf import sysconf
from xbaydns.tools.namedconf import *
from xbaydns.tools.nsupdate import *

class SysIntergrate_ConfigInit_Test(basetest.BaseTestCase):
    """测试初始化配置"""
    def setUp(self):
        self.basedir = os.path.realpath(tempfile.mkdtemp(suffix='xbaydns_sys'))
        basetest.BaseTestCase.setUp(self)

    def tearDown(self):
        """清洁测试环境"""
        shutil.rmtree(self.basedir)
        basetest.BaseTestCase.tearDown(self)

    def _init_conf(self):
        """测试操作系统的named.conf初始化。
        为各种操作系统初始化named.conf,注意，这将清除系统中的原有文件。原有文件请提前备份。
        另一方面，请不要将本机的域名解晰放在127.0.0.1上，这样将会在测试失败时让你的机器也无法工作。"""
        initconf.main()
        self.assertTrue(os.path.isfile(os.path.join(sysconf.chroot_path,sysconf.namedconf,"named.conf")))
        self.assertTrue(os.path.isfile(os.path.join(sysconf.chroot_path,sysconf.namedconf,"defaultzone.conf")))
        self.assertTrue(os.path.isdir(os.path.join(sysconf.chroot_path,sysconf.namedconf,"acl")))
        self.assertTrue(os.path.isfile(os.path.join(sysconf.chroot_path,sysconf.namedconf,"acl","acldef.conf")))
        self.assertTrue(os.path.isdir(os.path.join(sysconf.chroot_path,sysconf.namedconf,"master")))
        self.assertTrue(os.path.isfile(os.path.join(sysconf.chroot_path,sysconf.namedconf,"master","empty.db")))
        self.assertTrue(os.path.isfile(os.path.join(sysconf.chroot_path,sysconf.namedconf,"master","localhost-forward.db")))
        self.assertTrue(os.path.isfile(os.path.join(sysconf.chroot_path,sysconf.namedconf,"master","localhost-reverse.db")))
        self.assertTrue(os.path.isdir(os.path.join(sysconf.chroot_path,sysconf.namedconf,"slave")))
        self.assertTrue(os.path.isdir(os.path.join(sysconf.chroot_path,sysconf.namedconf,"dynamic")))

    def _add_default_conf(self):
        #加入default的acl信息
        nc=NamedConf()
        nc.addAcl('bj-cnc',['127.0.0.1','192.168.1.0/24'])
        nc.addAcl('tj-cnc',['127.0.0.4','192.168.2.0/24'])
        nc.addAcl('gd-telecom',['127.0.0.2','10.0.10.0/24'])
        nc.addAcl('gx-telecom',['127.0.0.3','10.0.11.0/24'])
        #加入default的view信息
        nc.addView("cnc",["bj-cnc","tj-cnc"])
        nc.addView("telecom",["gd-telecom","gx-telecom"])
        nc.addDomain(["abc.cn","hd.com"])
        log.debug("save named.conf")
        nc.save()
        #做生成的配置文件的所有检查
        self.assertTrue(os.path.isfile(os.path.join(sysconf.chroot_path,sysconf.namedconf,"acl","bj-cnc.conf")))
        self.assertTrue(os.path.isfile(os.path.join(sysconf.chroot_path,sysconf.namedconf,"acl","tj-cnc.conf")))
        self.assertTrue(os.path.isfile(os.path.join(sysconf.chroot_path,sysconf.namedconf,"acl","gd-telecom.conf")))
        self.assertTrue(os.path.isfile(os.path.join(sysconf.chroot_path,sysconf.namedconf,"acl","gx-telecom.conf")))
        self.assertTrue(os.path.isdir(os.path.join(sysconf.chroot_path,sysconf.namedconf,"view")))
        self.assertTrue(os.path.isfile(os.path.join(sysconf.chroot_path,sysconf.namedconf,"view","cnc.conf")))
        self.assertTrue(os.path.isfile(os.path.join(sysconf.chroot_path,sysconf.namedconf,"view","telecom.conf")))
        self.assertTrue( nc.check_configfile() == 0 )
        for i in ["abc.cn","hd.com"]:
            for j in ["cnc","telecom"]:
                log.debug("check %s as %s"%(i,j))
                self.assertTrue( os.system("named-checkzone %s %s"%(i,os.path.join(sysconf.chroot_path,sysconf.namedconf,"dynamic","%s.%s.file"%(j,i)))) == 0 )
        nc.named_restart()
        self.assertTrue(nc.reload() == 0)

    def _add_default_record(self):
        #为domain增加域名
        recordlist = [['www', 3600, 'IN', 'A', ['192.168.1.1', '172.16.1.1']], ['ftp', 3600, 'IN', 'CNAME', ['www']], ['', 86400, 'IN', 'MX', ['10 www']]]
        nu = NSUpdate('127.0.0.1', 'hd.com.', view='cnc')
        nu.addRecord(recordlist)
        nu.commitChanges()
        #普通查，这时被match到了cnc，所以因该都可以查到
        nu = NSUpdate('127.0.0.1', 'hd.com.')
        qrec = nu.queryRecord('www.hd.com.', rdtype='A')
        qrec.sort()
        self.assertEqual(qrec, ['172.16.1.1', '192.168.1.1'])
        qrec = nu.queryRecord('ftp.hd.com.', rdtype='CNAME')
        self.assertEqual(qrec, ['www.hd.com.'])
        qrec = nu.queryRecord('hd.com.', rdtype='MX')
        self.assertEqual(qrec, ['10 www.hd.com.'])
        #指定cnc view查询，应该全都通过
        nu = NSUpdate('127.0.0.1', 'hd.com.', view='cnc')
        qrec = nu.queryRecord('www.hd.com.', rdtype='A')
        qrec.sort()
        self.assertEqual(qrec, ['172.16.1.1', '192.168.1.1'])
        qrec = nu.queryRecord('ftp.hd.com.', rdtype='CNAME')
        self.assertEqual(qrec, ['www.hd.com.'])
        qrec = nu.queryRecord('hd.com.', rdtype='MX')
        self.assertEqual(qrec, ['10 www.hd.com.'])
        #指定了telecom view，应该全都没有
        nu = NSUpdate('127.0.0.1', 'hd.com.', view='telecom')
        reqfailed = False
        log.debug("test telecom view record")
        try:
            qrec = nu.queryRecord('www.hd.com.', rdtype='A')
            log.debug("req www.hd.com@telecom return %s"%qrec)
        except NSUpdateException:
            reqfailed = True
        self.assertTrue(reqfailed)
        reqfailed = False
        try:
            qrec = nu.queryRecord('ftp.hd.com.', rdtype='CNAME')
        except NSUpdateException:
            reqfailed = True
        self.assertTrue(reqfailed)
        reqfailed = False
        try:
            qrec = nu.queryRecord('hd.com.', rdtype='MX')
        except NSUpdateException:
            reqfailed = True
        self.assertTrue(reqfailed)

    def _del_default_record(self):
        """删除域名的测试"""
        nu = NSUpdate('127.0.0.1', 'hd.com.',view="cnc")
        recordlist =  [['', 86400, 'IN', 'MX', ['10 www']]]
        nu.removeRecord(recordlist)
        recordlist = ['www']
        nu.removeRecord(recordlist,True)
        nu.commitChanges()
        reqfailed = False
        try:
            qrec = nu.queryRecord('www.hd.com.', rdtype='A')
            log.debug("req www.hd.com@cnc return %s"%qrec)
        except NSUpdateException:
            reqfailed = True
        self.assertTrue(reqfailed)
        reqfailed = False
        try:
            qrec = nu.queryRecord('hd.com.', rdtype='MX')
        except NSUpdateException:
            reqfailed = True
        self.assertTrue(reqfailed)


    def test_intergrate(self):
        """集成测试"""
        self._init_conf()
        self._add_default_conf()
        self._add_default_record()

def suite():
    """集合测试用例"""
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(SysIntergrate_ConfigInit_Test, 'test'))
    return suite

if __name__ == '__main__':
    unittest.main()