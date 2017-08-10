#!/usr/bin/env python
# encoding: utf-8
"""
initconf.py

Created by 黄 冬 on 2007-11-19.
Copyright (c) 2007 xBayDNS Team. All rights reserved.

初始化bind的配置文件。运行这个程序需要root的权限。不管你是什么操作系统，它的初始化都是将
/etc/namedb
目录进行初始化
"""
from xbaydns.utils import shtools
from xbaydns.conf import sysconf

import errno
import getopt
import logging.config
import os
import shutil
from string import Template
import sys
from tempfile import mkdtemp
import time

log = logging.getLogger('xbaydns.tools.initconf')

BASEDIR = sysconf.installdir
TMPL_DIR = BASEDIR + "/tools/templates"
TMPL_DEF_DIR = "%s/default"%TMPL_DIR
TMPL_PLAT_DIR = "%s/%s/%s"%(TMPL_DIR, sysconf.system, sysconf.release)
log.debug("template diris:%s"%TMPL_DIR)
ERR_BACKUP = 1000

def getProperTmpl(tmpl_file):
    '''
    得到合适的模板，如果在系统模板目录中有对应的模板则使用，如果没有则返回默认的模板。
    '''
    plat_tmpl = "%s/%s"%(TMPL_PLAT_DIR, tmpl_file)
    if os.path.isfile(plat_tmpl) == True:
        return plat_tmpl
    else:
        return "%s/%s"%(TMPL_DEF_DIR, tmpl_file)

# 定义使用模板
TMPL_DEFAULTZONE = getProperTmpl('defaultzone.tmpl')
TMPL_NAMEDCONF = getProperTmpl('namedconf.tmpl')
TMPL_NAMEDROOT = getProperTmpl('namedroot.tmpl')
TMPL_LOCALHOST_FORWARD_DB = getProperTmpl('localhost-forward.db.tmpl')
TMPL_LOCALHOST_REVERSE_DB = getProperTmpl('localhost-reverse.db.tmpl')
TMPL_EMPTY_DB = getProperTmpl('empty.db.tmpl')
TMPL_RNDC_KEY = getProperTmpl('rndc.key.tmpl')

def acl_file(acls):
    '''
安dict的输入生成named所需要的acl字符串
acls = dict(aclname=('ip0', 'net0'))
    '''
    acl_content = ""
    for aclname, aclvalue in acls.iteritems():
        acl_content += 'acl "%s" { '%aclname
        for aclnet in aclvalue:
            acl_content += "%s; "%aclnet
        acl_content += "};\n"
    return acl_content

def defaultzone_file():
    """得到缺省的zone文件，也就是模板目录中的defaultzone.tmpl文件内容"""
    if os.path.isfile(TMPL_DEFAULTZONE) == False:
        return False
    else:
        tmpl_file = open(TMPL_DEFAULTZONE, "r")
        defzone = tmpl_file.read() + "\n"
        tmpl_file.close()
        return defzone

def named_root_file():
    """得到缺省的root文件，也就是模板目录中的namedroot.tmpl文件内容"""
    if os.path.isfile(TMPL_NAMEDROOT) == False:
        return False
    else:
        tmpl_file = open(TMPL_NAMEDROOT, "r")
        named_root = tmpl_file.read()
        tmpl_file.close()
        return named_root

def namedconf_file(include_files):
    """通过namedconf.tmpl生成最终的named.conf文件。include_file为一个dic，每项的值为一个要include的文件路径"""
    if os.path.isfile(TMPL_DEFAULTZONE) == False:
        return False
    else:
        tmpl_file = open(TMPL_NAMEDCONF, "r")
        namedconf_tmpl = Template(tmpl_file.read())
        tmpl_file.close()
        namedconf = namedconf_tmpl.substitute(CONF_DIR=sysconf.namedconf)
        namedconf += "\n"
        for filename in include_files.itervalues():
            namedconf += 'include "%s";\n'%filename
        return namedconf + "\n"

def make_localhost():
    pass
    
def backup_conf(confdir, backdir):
    """备份named.conf和namedb目录。confdir为named配置目录， backdir为备份文件存放的目录。"""
    if os.path.isdir(confdir) == False:
        return False
    else:
        time_suffix = time.strftime("%y%m%d%H%M")
        retcode = shtools.execute(executable = "tar", args = "-czf %s/namedconf_%s.tar.gz %s"%(backdir,  time_suffix, confdir))
        if retcode == 0:
            return True
    return False

def create_destdir():
    """创建系统目录，这里只是在tmp目录中建立"""
    
    tmpdir = mkdtemp()
    os.makedirs("%s/%s/acl"%(tmpdir, sysconf.namedconf))
    os.makedirs("%s/%s/dynamic"%(tmpdir, sysconf.namedconf))
    os.chown("%s/%s/dynamic"%(tmpdir, sysconf.namedconf), sysconf.named_uid, 0)
    os.mkdir("%s/%s/master"%(tmpdir, sysconf.namedconf))
    os.mkdir("%s/%s/slave"%(tmpdir, sysconf.namedconf))
    os.chown("%s/%s/slave"%(tmpdir, sysconf.namedconf), sysconf.named_uid, 0)
    return tmpdir

def create_conf(tmpdir):
    """在tmpdir目录中创建配置文件"""
    acl = acl_file(sysconf.default_acl)
    defzone = defaultzone_file()
    namedroot = named_root_file()

    if acl == False or defzone == False or namedroot == False:
        return False
    else:
        tmpfile = open("%s/%s/%s"%(tmpdir, sysconf.namedconf, sysconf.filename_map['acl']), "w")
        tmpfile.write(acl)
        tmpfile.close()
        tmpfile = open("%s/%s/%s"%(tmpdir, sysconf.namedconf, sysconf.default_zone_file), "w")
        tmpfile.write(defzone)
        tmpfile.close()
        tmpfile = open("%s/%s/named.root"%(tmpdir, sysconf.namedconf), "w")
        tmpfile.write(namedroot)
        tmpfile.close()
        shutil.copyfile(TMPL_EMPTY_DB, "%s/%s/master/empty.db"%(tmpdir, sysconf.namedconf))
        shutil.copyfile(TMPL_LOCALHOST_FORWARD_DB, "%s/%s/master/localhost-forward.db"%(tmpdir, sysconf.namedconf))
        shutil.copyfile(TMPL_LOCALHOST_REVERSE_DB, "%s/%s/master/localhost-reverse.db"%(tmpdir, sysconf.namedconf))
        shutil.copyfile(TMPL_RNDC_KEY, "%s/%s/rndc.key"%(tmpdir, sysconf.namedconf))
        os.chmod("%s/%s/rndc.key"%(tmpdir, sysconf.namedconf),0600)
        os.chown("%s/%s/rndc.key"%(tmpdir, sysconf.namedconf),sysconf.named_uid,0)
        namedconf = namedconf_file(sysconf.filename_map)
        tmpfile = open("%s/%s/named.conf"%(tmpdir, sysconf.namedconf), "w")
        tmpfile.write(namedconf)
        tmpfile.close()
        return True
        
def install_conf(tmpdir, chrootdir):
    """将tmpdir中的临时文件安装到最终的使用目录中去"""
    ret = shtools.execute(executable="cp", args="-Rp %s/ %s"%(tmpdir, chrootdir))
    if ret == 0:
        ret = shtools.execute(executable="rm", args="-rf %s"%tmpdir)
        if ret == 0:
            return True
    else:
        return False
    
def usage():
    print "usage: %s [-bc]"%__file__
    
def main():
    # check root
    if os.getuid() != 0:
        print "You need be root to run this program."
        return errno.EPERM
    # parse options
    try:
        opts = getopt.getopt(sys.argv[1:], "b:c:")
    except getopt.GetoptError:
        usage()
        return errno.EINVAL
    chrootdir = os.path.realpath(sysconf.chroot_path)
    backup = False
    backdir = ""
    for optname, optval in opts[0]:
        if optname == "-c":
            chrootdir = optval
        # -b为指定备份目录
        elif optname == "-b":
            backup = True
            backdir = optval
    # backup
    if backup == True:
        realconfdir = chrootdir + sysconf.namedconf
        if os.path.isdir(realconfdir) == True:
            ret = backup_conf(realconfdir, backdir)
            if ret == False:
                print "Backup failed."
                return -1
        else:
            print "No namedb in basedir, I'll continue."
    # that's my business
    # get named uid
    tmpdir = create_destdir()
    os.chmod(tmpdir,0755)
    log.debug(tmpdir)
    #清理旧世界
    shutil.rmtree(os.path.join(sysconf.chroot_path,sysconf.namedconf,"acl"),ignore_errors=True)
    shutil.rmtree(os.path.join(sysconf.chroot_path,sysconf.namedconf,"master"),ignore_errors=True)
    shutil.rmtree(os.path.join(sysconf.chroot_path,sysconf.namedconf,"slave"),ignore_errors=True)
    shutil.rmtree(os.path.join(sysconf.chroot_path,sysconf.namedconf,"dynamic"),ignore_errors=True)
    shutil.rmtree(os.path.join(sysconf.chroot_path,sysconf.namedconf,"view"),ignore_errors=True)
    if create_conf(tmpdir) == False or install_conf(tmpdir, chrootdir) == False:
        print "Create configuration files failed."
        return -1
    else:
        return 0

if __name__ == '__main__':
    sys.exit(main())