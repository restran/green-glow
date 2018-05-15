# -*- encoding: utf-8 -*-
'''
Created on 2012-3-22

@author: Neil
'''
from django.db import models


class Tag(models.Model):
    """
    标签的数据模型
    """
    name = models.CharField(max_length=20, unique=True)
    used_count = models.IntegerField(default=1)
    # created_at = models.DateTimeField(default=datetime.datetime.now())
    created_at = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ['id']
        app_label = 'glow'
