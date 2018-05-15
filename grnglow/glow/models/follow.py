# -*- encoding: utf-8 -*-
'''
Created on 2012-3-22

@author: Neil
'''
from django.db import models
from user import User


class Follow(models.Model):
    """
    关注的数据模型
    """

    be_followed_user = models.ForeignKey(User, related_name='be_followed_user')
    follower = models.ForeignKey(User, related_name='follower')
    # date_followed = models.DateTimeField(datetime.datetime.now())
    date_followed = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return str(self.id)

    class Meta:
        ordering = ['id']
        app_label = 'glow'

    # 判断该关注记录是否已存在，避免重复关注
    def isExist(self):
        try:
            Follow.objects.get(be_followed_user=self.be_followed_user, follower=self.follower)
        except Follow.DoesNotExist:
            return False
        else:
            return True
