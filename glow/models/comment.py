#-*- encoding: utf-8 -*-
'''
Created on 2012-3-22

@author: Neil
'''
from django.db import models
#from photo import Photo
from user import User

class Comment(models.Model):
    """
    评论的数据模型
    """
    #master_id是表示当照片和评论者不在同一个站点时，评论者所在站点上存的该条评论的id
    #因为一个用户可以对一张照片发表多条评论，因此会出现，不同站点上的相同评论id不一样
    master_id = models.IntegerField(default=-1)#-1表示没有设置，即该评论只在一个站点上，即评论者所在的站点上
    photo_id = models.IntegerField()
    photo_owner = models.ForeignKey(User, related_name='comment_photo_owner')#related_name修改名字
    author = models.ForeignKey(User, related_name='author')
    content = models.TextField()
    #不要用默认值，默认值只在第一次时被赋值，以后都是用相同的默认值，也就是相同的时间
    #date_posted = models.DateTimeField(default=datetime.datetime.now())
    date_posted = models.DateTimeField(auto_now_add=True)
    deleted_by_photo_owner = models.BooleanField(default=False)#照片拥有者删除评论时，将不再照片的评论列表中显示
    photo_deleted = models.BooleanField(default=False)#照片已被删除
        
    def __unicode__(self):
        return str(self.id)
    
    class Meta:
        ordering = ['id']
        app_label = 'glow'