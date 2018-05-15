# -*- encoding: utf-8 -*-
'''
Created on 2012-3-22

@author: Neil
'''
from django.db import models
# from photo import Photo
from user import User


class Comment(models.Model):
    """
    评论的数据模型
    """
    photo_id = models.IntegerField()
    photo_owner = models.ForeignKey(User, related_name='comment_photo_owner')  # related_name修改名字
    author = models.ForeignKey(User, related_name='author')
    content = models.TextField()
    # 不要用默认值，默认值只在第一次时被赋值，以后都是用相同的默认值，也就是相同的时间
    # date_posted = models.DateTimeField(default=datetime.datetime.now())
    date_posted = models.DateTimeField(auto_now_add=True)
    deleted_by_photo_owner = models.BooleanField(default=False)  # 照片拥有者删除评论时，将不再照片的评论列表中显示
    photo_deleted = models.BooleanField(default=False)  # 照片已被删除

    def __unicode__(self):
        return str(self.id)

    class Meta:
        ordering = ['id']
        app_label = 'glow'
