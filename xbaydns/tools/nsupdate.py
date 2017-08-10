#!/usr/bin/env python
# encoding: utf-8
"""
nsupdate.py

Created by Razor on 2007-11-19.
Copyright (c) 2007 xBayDNS Team. All rights reserved.

update DNS server on FLY...
"""
import dns.exception, dns.name, dns.query, dns.rcode, dns.rdata, dns.rdataclass, \
            dns.rdataset, dns.rdatatype, dns.rdtypes, dns.resolver, \
            dns.tsigkeyring, dns.update, dns.zone
import logging.config
from xbaydns.tools import namedconf

log = logging.getLogger('xbaydns.tools.nsupdate')

class NSUpdateException(Exception):
    pass

class NSUpdate:
    def __init__(self, addr, domain, view = False, port = 53, source = None, source_port = 0):
        self.addr = addr
        self.port = port
        self.source = source
        self.source_port = source_port
        self.domain = dns.name.from_text(domain)
        self.view = view
        self.tsigkey = None
        if view != False:
            # get TSIG
            namedconf_obj = namedconf.NamedConf()
            keys = namedconf_obj.loadViewKey(view)
            self.tsigkey = dns.tsigkeyring.from_text(keys)
        self.domain_info = self._getDomainInfo()
        self.updatemsg = dns.update.Update(self.domain, keyring = self.tsigkey)
        
    def _getDomainInfo(self):
        # get full zone by xfr, for checking before add/remove/update records
        try:
            domain_info = dns.zone.from_xfr(dns.query.xfr(self.addr, self.domain, keyring = self.tsigkey))
        except dns.query.BadResponse:
            log.error("DOMAIN XFR ERROR: Bad Response.")
            raise NSUpdateException("DOMAIN XFR ERROR: Bad Response.")
        except dns.zone.NoSOA:
            log.error("DOMAIN XFR ERROR: No SOA.")
            raise NSUpdateException("DOMAIN XFR ERROR: No SOA.")
        except dns.zone.NoNS:
            log.error("DOMAIN XFR ERROR: No NS.")
            raise NSUpdateException("DOMAIN XFR ERROR: No NS.")
        except dns.exception.FormError:
            log.error("DOMAIN XFR ERROR: Form Error")
            raise NSUpdateException("DOMAIN XFR ERROR: Form Error")            
        return domain_info
    
    def _updateWrapper(self, func, recordlist):
        for name, ttl, rdclass, rdtype, token in recordlist:
            rdatalist = []
            for token_str in token:
                rdatalist.append(dns.rdata.from_text(
                        dns.rdataclass.from_text(rdclass),
                        dns.rdatatype.from_text(rdtype),
                        token_str,
                        origin = self.domain))
                log.debug("ADD RDATA: %s, %d, %s, %s, %s"%(name, ttl, rdclass, rdtype, token))
            recordset = dns.rdataset.from_rdata_list(ttl, rdatalist)
            func(name, recordset)
                    
    def addRecord(self, recordlist):
        '''
        generate an update message for adding record.
        : param domain: the name of the domain. string.
        : param recordlist: list of the records to be added.
        '''
        self._updateWrapper(self.updatemsg.add, recordlist)
        
    def removeRecord(self, recordlist, entire_node = False):
        '''
        generate an update message for removing record.
        '''
        if entire_node == True:
            for name in recordlist:
                self.updatemsg.delete(name)
        else:
            self._updateWrapper(self.updatemsg.delete, recordlist)
        
    def updateRecord(self, recordlist):
        '''
        generate an update message for updating record.
        '''
        pass

    def commitChanges(self, timeout = None, usetcp = True):
        '''
        send the update messages to NS server
        '''
        if usetcp == True:
            query_wrapper = dns.query.tcp
        else:
            query_wrapper = dns.query.udp
        try:
            response = query_wrapper(self.updatemsg, self.addr, timeout=timeout, port=self.port, source=self.source, source_port=self.source_port)
        except dns.query.BadResponse:
            log.error("UPDATE RESPONSE ERROR: Bad Response")
            raise NSUpdateException("UPDATE RESPONSE ERROR: Bad Response")
        log.debug("UPDATE RESPONSE: %s"%response)
        self.updatemsg = dns.update.Update(self.domain, keyring = self.tsigkey)
        rcode = response.rcode()
        rtext = dns.rcode.to_text(rcode)
        return {'rcode':rcode, 'rtext':rtext}
        
    def queryRecord(self, name, rdtype = 'A', usetcp = False, timeout = 30, rdclass = 'IN'):
        '''
        query a record in the view specified at initializing time.
        '''
        return self.queryRecord_Independent(name, view = self.view, rdtype = rdtype, 
                                                    usetcp = usetcp, timeout = timeout, rdclass = rdclass)

    """
        def queryRecord_Independent(self, *arg, **args):
            print arg
            print args               
    """
    
    def queryRecord_Independent(self, name, view = False, rdtype = 'A', 
                    usetcp = False, timeout = 30, rdclass = 'IN'):
        '''
        query a record though the specified NS server. if view == False, no view will be specified.
        '''
        resolv = dns.resolver.Resolver()
        resolv.nameservers = [self.addr]
        resolv.port = self.port
        resolv.lifetime = timeout
        if view != False:
            # get TSIG
            namedconf_obj = namedconf.NamedConf()
            keys = namedconf_obj.loadViewKey(view)
            tsigkey = dns.tsigkeyring.from_text(keys)
            resolv.use_tsig(tsigkey)
        try:
            resultset = resolv.query(name, dns.rdatatype.from_text(rdtype), 
                                    dns.rdataclass.from_text(rdclass), tcp = usetcp)
        except dns.resolver.Timeout:
            # query time exceed the lifetime
            log.error("RESOLVER ERROR: Query Timeout.")
            raise NSUpdateException("RESOLVER ERROR: Query Timeout.")
        except dns.resolver.NXDOMAIN:
            # the query name does not exist
            log.error("RESOLVER ERROR: Name Not Exist.")
            raise NSUpdateException("RESOLVER ERROR: Name Not Exist.")
        except dns.resolver.NoAnswer:
            # the response did not contain an answer
            log.error("RESOLVER ERROR: No Answer.")
            raise NSUpdateException("RESOLVER ERROR: No Answer.")
        except dns.resolver.NoNameservers:
            # no non-broken nameservers are available to answer the question.
            log.error("RESOLVER ERROR: No Nameservers.")
            raise NSUpdateException("RESOLVER ERROR: No Nameservers.")
        return [ record.to_text() for record in resultset ]
        
