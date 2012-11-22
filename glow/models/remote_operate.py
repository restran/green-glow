#-*- encoding: utf-8 -*-
'''
Created on 2012-4-9

@author: Neil
'''
from django.db import models

#远程上传照片，头像，或删除照片时存储的操作会话表
class RemoteOperate(models.Model):
    key = models.CharField(max_length=40, primary_key=True)
    user_id = models.IntegerField()
    photo_id = models.IntegerField(default=-1)
    
    #当远程上传照片或修改头像时，会将图片文件一并传过去，如果是修改头像则不设置photo_id，
    #根据调用远端对应的处理函数，来判断是上传照片还是修改头像

    def __unicode__(self):
        return str(self.key)
    class Meta:
        ordering = ['key']
        app_label = 'glow'