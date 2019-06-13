# -*- encoding: utf-8 -*-
'''
Created on 2012-3-22

@author: Neil
'''
from django.db import models
from user import User


class Album(models.Model):
    '''
    相册的数据模型
    '''

    owner = models.ForeignKey(User)
    topic = models.CharField(max_length=32)
    caption = models.TextField(blank=True)
    # 不要用默认值，默认值只在第一次时被赋值，以后都是用相同的默认值，也就是相同的时间
    # date_created = models.DateTimeField(default=datetime.datetime.now())
    date_created = models.DateTimeField(auto_now_add=True)
    # -1表示没有封面，当相册中有照片时，系统会自动选择一张作为显示的封面
    cover_photo_id = models.IntegerField(default=-1)
    last_post = models.DateTimeField(null=True)
    view_count = models.IntegerField(default=0)
    photo_count = models.IntegerField(default=0)

    def __unicode__(self):
        return str(self.id)

    class Meta:
        ordering = ['-date_created']  # 按创建时间倒序，最近的排在前面
        app_label = 'glow'

    # 当用户没有指定封面时，如果该相册中有照片，就选择一张作为封面
    def setNewDefaultCover(self):
        cover_loc = '/static/img/default_album_cover.gif'  # 缺省的相册封面
        if self.photo_count > 0:
            from grnglow.glow.models.photo import Photo
            try:
                photo = (Photo.objects.filter(owner=self.owner, album=self))[0]
            except:
                self.cover_photo_id = -1
            else:
                self.cover_photo_id = photo.id
                self.save()  # 保存
                try:
                    photo = Photo.objects.get(owner=self.owner, album=self, id=self.cover_photo_id)
                    cover_loc = photo.square_loc
                except:
                    pass

        return cover_loc

        # 获取相册封面的照片文件地址

    def getCoverLoc(self):
        from grnglow.glow.models.photo import Photo
        # cover_loc = '/static/img/default_album_cover.gif'#缺省的相册封面
        if self.cover_photo_id == -1:
            cover_loc = self.setNewDefaultCover()
        else:
            try:
                photo = Photo.objects.get(owner=self.owner, album=self, id=self.cover_photo_id)
                cover_loc = photo.square_loc
            except:
                cover_loc = self.setNewDefaultCover()

        return cover_loc
