#!/usr/bin/env python
# encoding: utf-8
"""
这个文件中记录了所有的全局静态配置变量。现在只有named.conf所属路径和nameddb目录存储路径。
"""


import re
import os
import platform
import pwd
import sys

system, _, release, version, machine, processor = platform.uname()
system, release, version = platform.system_alias(system, release,version)
release = re.compile(r"^\d+.\d+").search(release).group()

# 安装路径，是否能传进来？暂时写成根据相对路径
installdir = os.path.dirname(os.path.realpath(__file__)) + "/.."
# 这里记录了bind启动的chroot根目录
chroot_path = "/var/named"
# 这里记录了named.conf所存储的路径
namedconf = "/etc/namedb"
# 这是bind的启动脚本
namedstart = "/etc/rc.d/named start"
# 这是bind的停止脚本
namedstop = "/etc/rc.d/named stop"
# 这是bind的重启脚本
namedrestart = "/etc/rc.d/named restart"

if (system == 'Darwin'):
    #操作系统为Mac OSX
    chroot_path = "/"
    namedconf = "/etc"
    named_user = "root"
    namedstart = "sudo service org.isc.named start;sleep 2"
    namedstop = "sudo service org.isc.named stop"
    if (release == '9.1.0'):
        #OSX 10.5&10.5.1
        pass
elif (system == "FreeBSD"):
    #操作系统为FreeBSD
    chroot_path = "/var/named"
    namedconf = "/etc/namedb"
    named_user = "bind"
    if (release == "6.2"):
        pass
    elif (release == "7.0"):
        pass
elif (system == "OpenBSD"):
    # 操作系统为OpenBSD
    named_user = "named"
    chroot_path = "/var/named"
    namedconf = "/etc"
    if (release ==  "4.2"):
        pass
elif (system == "Linux"):
    # 操作系统为Linux
    named_user = "bind"
    chroot_path = "/"
    namedconf = "/etc/bind"
try:
    named_uid = pwd.getpwnam(named_user)[2]
except KeyError:
    print "No such a user %s. I'll exit."%named_user
    sys.exit(errno.EINVAL)
        
default_acl = dict(internal=('127.0.0.1', '10.217.24.0/24'))
filename_map = dict(acl='acl/acldef.conf')
default_zone_file = "defaultzone.conf"
default_soa = 'localhost'
default_ns = 'ns1.sina.com.cn'
default_admin = 'huangdong@gmail.com'
