# encoding: utf-8
"""
namedconf.py

Created by QingFeng on 2007-11-22.
Copyright (c) 2007 yanxu. All rights reserved.
"""

import logging.config
from xbaydnsweb.web.utils import saveAllConf

log = logging.getLogger('xbaydns.tools.confsync')

def main():
    saveAllConf()
    
if __name__ == '__main__':
    sys.exit(main())