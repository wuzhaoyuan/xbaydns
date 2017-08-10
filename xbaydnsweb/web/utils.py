#!/usr/bin/env python
# encoding: utf-8
"""
utils.py

Created by QingFeng on 2007-12-02.
Copyright (c) 2007 yanxu. All rights reserved.
"""
import logging.config
from xbaydnsweb.web.models import *
from xbaydns.tools.namedconf import *
from xbaydns.conf import sysconf

log = logging.getLogger('xbaydnsweb.web.utils')
logging.basicConfig(level=logging.DEBUG)

def saveAllConf(path=sysconf.namedconf):
    nc = NamedConf()
    for acl in Acl.objects.all():
        matchs=map(lambda x:x.aclMatch,
                AclMatch.objects.filter(acl=acl))
        nc.addAcl(acl.aclName,matchs)
    for view in View.objects.all():
        view_matchs=[]
        for aclmatch in view.aclmatch.all():
            view_matchs.append(aclmatch.acl.aclName)
        nc.addView(view.viewName,view_matchs)
    domain_matchs = map(lambda x:x.zone,Domain.objects.all())
    nc.addDomain(domain_matchs)
    nc.save(path)
