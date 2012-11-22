#-*- encoding: utf-8 -*-
'''
Created on 2012-3-23

@author: Neil
'''
from django.db import models
from user import User
from site import Site

class SiteMap(models.Model):
    '''
    用户与站点的映射
    '''
    user = models.ForeignKey(User)
    site = models.ForeignKey(Site)
    
    def __unicode__(self):
        return str(self.id)
    
    class Meta:
        ordering = ['id']
        app_label = 'glow'