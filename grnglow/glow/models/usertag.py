#-*- encoding: utf-8 -*-
'''
Created on 2012-3-22

@author: Neil
'''
from django.db import models
from user import User
from tag import Tag

class UserTag(models.Model):
    """
    用户标签的数据模型
    """
    user = models.ForeignKey(User)
    tag = models.ForeignKey(Tag)
    used_count = models.IntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    def __unicode__(self):
        return str(self.id)
    class Meta:
        ordering = ['id']
        app_label = 'glow'
