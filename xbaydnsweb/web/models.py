# encoding: utf-8
from django.db import models
import logging.config
from xbaydns.tools import nsupdate

log = logging.getLogger('xbaydnsweb.web.tests')
logging.basicConfig(level=logging.DEBUG)

class Acl(models.Model):
    """Acl Model"""
    aclName = models.CharField(maxlength=100)
    
    class Admin:
        list_display = ('aclName',)
        search_fields = ('aclName',)
    class Meta:
        ordering = ('aclName',)
        verbose_name = '地址片名称'
        verbose_name_plural = '1.1 地址片名称管理'
        
    def __str__(self):
        return self.aclName

class AclMatch(models.Model):
    """AclMatch Model"""
    acl = models.ForeignKey(Acl)
    aclMatch = models.CharField(maxlength=100)

    class Admin:
        list_display = ('acl','aclMatch')
        #search_fields = ('',)
    class Meta:
        verbose_name = '地址片'
        verbose_name_plural = '1.2 地址片管理'

    def __str__(self):
        return ' '.join([str(self.acl),self.aclMatch])

class View(models.Model):
    """View Model"""
    viewName = models.CharField(maxlength=100,verbose_name='View名称')
    #viewgroup = models.ForeignKey("ViewGroup")
    viewgroup = models.ManyToManyField("ViewGroup")
    aclmatch = models.ManyToManyField(AclMatch,verbose_name='ACL')
    
    class Admin:
        list_display = ('viewName','showviewgroup','showacls')
        #search_fields = ('viewName',)
    class Meta:
        ordering = ('viewName',)
        verbose_name = '用户片'
        verbose_name_plural = '2.2 用户片管理'
    def showacls(self):
        return ','.join(map(lambda x:str(x),self.aclmatch.all()))
    showacls.short_description = 'Acl'
    showacls.allow_tags = True
    def showviewgroup(self):
        return ','.join(map(lambda x:str(x),self.viewgroup.all()))
    showviewgroup.short_description = 'View Group'
    showviewgroup.allow_tags = True

    def __str__(self):
        return self.viewName

class Domain(models.Model):
    """Domain Model"""
    zone = models.CharField(maxlength=100)

    class Admin:
        list_display = ('zone',)
        search_fields = ('zone',)
    class Meta:
        verbose_name = '域名'
        verbose_name_plural = '4.1 域名管理'

    def __str__(self):
        return self.zone

class ViewGroup(models.Model):
    """ViewGourp"""
    name = models.CharField(maxlength=100)

    class Admin:
        list_display = ('name',)
        search_fields = ('name',)
    class Meta:
        verbose_name = '用户视图'
        verbose_name_plural = '2.1 用户视图管理'

    def __str__(self):
        return self.name

class Record(models.Model):
    """Record"""
    domain = models.ForeignKey(Domain)
    record = models.CharField(maxlength=100)
    ttl = models.CharField(maxlength=100,default='600')
    ip = models.CharField(maxlength=100)
    rdclass = models.CharField(maxlength=100,default='IN')
    rdtype = models.ForeignKey("RecordType",default='1')
    recordgroup = models.ForeignKey("RecordGroup")
    
    def save(self):
        for view in self.getRecordViews():
            nsupobj = nsupdate.NSUpdate('127.0.0.1',str(self.domain),view=view)
            #['foo', 3600, 'IN', 'A', ['192.168.1.1', '172.16.1.1']]#record style
            add_data=[[self.record,int(self.ttl),self.rdclass,str(self.rdtype),[self.ip,]],]
            if self.id!=None:
                old_r=Record.objects.get(id=self.id)
                del_data=[[old_r.record,int(old_r.ttl),old_r.rdclass,str(old_r.rdtype),[old_r.ip,]],]
                nsupobj.removeRecord(del_data)
        
            nsupobj.addRecord(add_data)
            nsupobj.commitChanges()
        
        super(Record,self).save()
    def delete(self):
        for view in self.getRecordViews():
            nsupobj = nsupdate.NSUpdate('127.0.0.1',str(self.domain),view=view)
            del_data=[[self.record,int(self.ttl),self.rdclass,str(self.rdtype),[self.ip,]],]
            #['foo', 3600, 'IN', 'A', ['192.168.1.1', '172.16.1.1']]#record style
            nsupobj.removeRecord(del_data)
            nsupobj.commitChanges()
        
        super(Record,self).delete()

    class Admin:
        list_display = ('domain','rdtype','ttl','ip','recordgroup','showviews')
        #search_fields = ('domain','record')
    class Meta:
        verbose_name = 'Record'
        verbose_name_plural = '4.3 Record 管理'
        
    def getRecordViews(self):
        views=[]
        for vm in ViewMatch.objects.filter(recordgroup=self.recordgroup):
            for vg in vm.viewgroup.all():
                for view in View.objects.filter(viewgroup=vg):
                    views.append(view.viewName)
        return views
    def showviews(self):
        return ','.join(self.getRecordViews())
    showviews.short_description = 'Views'
    showviews.allow_tags = True

    def __str__(self):
        return '%s IN %s'%(self.domain,self.rdtype)

class RecordGroup(models.Model):
    """RecordGroup"""
    name = models.CharField(maxlength=100)

    class Admin:
        list_display = ('name',)
        search_fields = ('name',)
    class Meta:
        verbose_name = 'RecordGroup'
        verbose_name_plural = '3.1 Record Group管理'

    def __str__(self):
        return self.name

class ViewMatch(models.Model):
    """ViewMatch"""
    name = models.CharField(maxlength=100)
    viewgroup = models.ManyToManyField(ViewGroup)
    recordgroup = models.ManyToManyField(RecordGroup)

    class Admin:
        list_display = ('name','showViewGroups','showRecordGroups')
        search_fields = ('name',)
    class Meta:
        verbose_name = 'ViewMatch'
        verbose_name_plural = '3.2 View Match管理'
    def showViewGroups(self):
        return ','.join(map(lambda x:x.name,self.viewgroup.all()))
    showViewGroups.short_description = 'View Group'
    showViewGroups.allow_tags = True
    def showRecordGroups(self):
        return ','.join(map(lambda x:x.name,self.recordgroup.all()))
    showRecordGroups.short_description = 'Record Group'
    showRecordGroups.allow_tags = True

    def __str__(self):
        return self.name

        
class RecordType(models.Model):
    """RecordType"""
    name = models.CharField(maxlength=100)

    class Admin:
        list_display = ('name',)
        search_fields = ('name',)
    class Meta:
        verbose_name = 'RecordType'
        verbose_name_plural = '4.2 Record Type管理'


    def __str__(self):
        return self.name
