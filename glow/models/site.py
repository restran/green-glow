#-*- encoding: utf-8 -*-
'''
Created on 2012-3-23

@author: Neil
'''
from django.db import models

class Site(models.Model):
    
    name = models.CharField(max_length=30)#站点的名称
    host = models.CharField(max_length=128)#主机名或IP地址
    port = models.IntegerField(default=3306)#端口
    isLocal = models.BooleanField(default=False)#是否位于本地
    
    def __unicode__(self):
        return str(self.id)
    
    class Meta:
        ordering = ['id']
        app_label = 'glow'