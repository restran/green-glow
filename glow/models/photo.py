#-*- encoding: utf-8 -*-
'''
Created on 2012-3-22

@author: Neil
'''
from django.db import models
from user import User
from album import Album
from tag import Tag
from grnglow import settings
from grnglow.glow.models.usertag import UserTag
import datetime, Image, os

class Photo(models.Model):
    '''
    照片的数据模型
    '''
    
    owner = models.ForeignKey(User)
    album = models.ForeignKey(Album)
    title = models.CharField(max_length=32, blank=True)
    caption = models.TextField(blank=True)
    tags = models.ManyToManyField(Tag)
    view_count = models.IntegerField(default=0)
    like_count = models.IntegerField(default=0)
    date_posted = models.DateTimeField(auto_now_add=True)
    shot_date = models.DateTimeField(null=True)
    camera = models.CharField(max_length=128, blank=True)
    square_loc = models.CharField(max_length=128, default="")#方格图
    thumb_loc = models.CharField(max_length=128, default="")
    middle_loc = models.CharField(max_length=128, default="")
    original_loc = models.CharField(max_length=128, default="")
    middle_width = models.IntegerField(default=0)
    middle_height = models.IntegerField(default=0)
    original_width = models.IntegerField(default=0)
    original_height = models.IntegerField(default=0)
    score = models.FloatField(default=0)#根据用户的喜欢数和时间计算照片的得分
            
    def __unicode__(self):
        return str(self.id)
    
    class Meta:
        ordering = ['-date_posted']#按上传时间倒序，最近的排在前面
        app_label = 'glow'
    
    def save_photo_file(self, photoFile):
        image = Image.open(photoFile)

        file_name = str(self.owner.id) + '_' + str(self.id) + '_o.jpg'
        self.original_width, self.original_height = image.size#size是一个元组
        self.original_loc = settings.PHOTOS_RELATIVE_PATH + file_name#图片相对于站点的存放位置
        image.save(settings.UPLOAD_PHOTOS_PATH + file_name, "jpeg", quality=90)#原始图
        
        image.thumbnail((600,600), Image.ANTIALIAS)#中等尺寸图
        file_name = str(self.owner.id) + '_' + str(self.id) + '_m.jpg'
        self.middle_width, self.middle_height = image.size#size是一个元组
        self.middle_loc = settings.PHOTOS_RELATIVE_PATH + file_name#图片相对于站点的存放位置
        image.save(settings.UPLOAD_PHOTOS_PATH + file_name, "jpeg", quality=90)
        
        image.thumbnail((240,240), Image.ANTIALIAS)#缩略图
        file_name = str(self.owner.id) + '_' + str(self.id) + '_t.jpg'
        self.thumb_loc = settings.PHOTOS_RELATIVE_PATH + file_name
        image.save(settings.UPLOAD_PHOTOS_PATH + file_name, "jpeg", quality=90)
        
        from grnglow.glow.util import util
        image = util.makeSquareImg(image, 75)
        file_name = str(self.owner.id) + '_' + str(self.id) + '_s.jpg'
        self.square_loc = settings.PHOTOS_RELATIVE_PATH + file_name
        image.save(settings.UPLOAD_PHOTOS_PATH + file_name, "jpeg", quality=90)#不设置quality，默认是75

    #只保存简要信息，等照片保存到数据库后，有了ID，然后以该ID为图片的文件名保存图片文件
    def save_photo_brief(self, user, photo_file, album_id):
        if user.isLocal():#该用户的数据是否位于本地站点
            self.owner = user
            self.album = Album.objects.get(id=album_id)
            #相册和用户的照片计数在upload view函数中统一保存
            #self.owner.photo_count += 1
            #self.album.photo_count += 1
            #self.owner.save()
            #self.album.save()
            self.save()#保存到数据库，生成id
        else:
            self.owner = User.objects.using('remote').get(id=user.id)
            self.album = Album.objects.using('remote').get(id=album_id)
            #相册和用户的照片计数在upload view函数中统一保存
            #self.owner.photo_count += 1
            #self.album.photo_count += 1
            #self.owner.save(using='remote')
            #self.album.save(using='remote')
            self.save(using='remote')#保存到数据库，生成id
        
        self.calculateScore()#添加一张照片时，根据当前时间计算得分
        
        from grnglow.glow.util import util
        if user.isLocal():#该用户的数据是位于远程站点
            self.save_photo_file(photo_file)#生成照片文件的各种尺寸并保存到指定目录中
            self.save()#保存到数据库
        else:
            self.save(using='remote')#注意，要先保存后，在调用远程上传图片，否则会导致在远程保存了照片的路径等信息，被冲掉
            util.remote_upload_photo(self.owner.id, self.id, photo_file)

    #保存图片的描述信息
    def save_photo_description(self, user, title, caption, tag_list):
        self.title = title
        self.caption = caption
        
        i = 0
        for t in tag_list:
            t = t.strip()#去掉两端的空格
            if t == '' or tag_list.index(t) != i:
                continue#空字符串不是标签，存在重复，去掉重复的
            
            i += 1#序号计数
            
            #统计标签
            try:
                if self.owner.isLocal():#该用户的数据是否位于本地站点
                    tt = Tag.objects.get(name=t)
                else:
                    tt = Tag.objects.using('remote').get(name=t)
            except Tag.DoesNotExist:
                tt = Tag(name=t)#该标签首次出现，创建
            else:
                tt.used_count += 1#该标签已存在，增加使用计数
            if self.owner.isLocal():#该用户的数据是否位于本地站点
                tt.save()
            else:
                tt.save(using='remote')                
            
            self.tags.add(tt)#为照片添加标签，tags为多对多关系
            
            #为该用户添加使用的标签
            try:
                if self.owner.isLocal():#该用户的数据是否位于本地站点
                    usertag = UserTag.objects.get(user=self.owner, tag=tt)
                else:
                    usertag = UserTag.objects.using('remote').get(user=self.owner, tag=tt)                    
            except UserTag.DoesNotExist:
                usertag = UserTag(user=self.owner, tag=tt)#该用户从未使用过该标签，创建
            else:
                usertag.used_count += 1#该用户已有该标签，增加使用计数
            if self.owner.isLocal():#该用户的数据是否位于本地站点
                usertag.save()
            else:
                usertag.save(using='remote')
        if self.owner.isLocal():#该用户的数据是否位于本地站点        
            self.save()#保存照片信息
        else:
            self.save(using='remote')#保存照片信息           
    
    def update_photo_info(self, title, caption, tag_list):
        self.title = title
        self.caption = caption
        tags = self.tags.all()
        #将该照片的关联标签删除，并更新标签计数，如果为0，就删除标签
        for t in tags:
            self.tags.remove(t)
            if self.owner.isLocal():#该用户的数据是否位于本地站点   
                self.save()#保存照片信息
            else:
                self.save(using='remote')#保存照片信息
            t.used_count -= 1
            
            if self.owner.isLocal():#该用户的数据是否位于本地站点
                usertag = UserTag.objects.get(user=self.owner, tag=t)
                usertag.used_count -= 1
                if usertag.used_count <= 0:
                    usertag.delete()
                else:
                    t.save()
                    
                if t.used_count <= 0:
                    t.delete()
                else:
                    usertag.save()
            else:
                usertag = UserTag.objects.using('remote').get(user=self.owner, tag=t)
                usertag.used_count -= 1
                t.save(using='remote')
                usertag.save(using='remote')
                
                if usertag.used_count <= 0:
                    usertag.delete(using='remote')
                else:
                    t.save(using='remote')
                    
                if t.used_count <= 0:
                    t.delete(using='remote')
                else:
                    usertag.save(using='remote')            
        i = 0
        for t in tag_list:
            t = t.strip()#去掉两端的空格
            if t == '' or tag_list.index(t) != i:
                continue#空字符串不是标签，存在重复，去掉重复的
            
            i += 1#序号计数
            
            #统计标签
            try:
                if self.owner.isLocal():#该用户的数据是否位于本地站点  
                    tt = Tag.objects.get(name=t)
                else:
                    tt = Tag.objects.using('remote').get(name=t)                    
            except Tag.DoesNotExist:
                tt = Tag(name=t)#该标签首次出现，创建
            else:
                tt.used_count += 1#该标签已存在，增加使用计数
            if self.owner.isLocal():#该用户的数据是否位于本地站点  
                tt.save()
            else:
                tt.save(using='remote')                
            
            self.tags.add(tt)#为照片添加标签
            
            #为该用户添加使用的标签
            try:
                if self.owner.isLocal():#该用户的数据是否位于本地站点                 
                    usertag = UserTag.objects.get(user=self.owner, tag=tt)
                else:
                    usertag = UserTag.objects.using('remote').get(user=self.owner, tag=tt)                    
            except UserTag.DoesNotExist:
                usertag = UserTag(user=self.owner, tag=tt)#该用户从未使用过该标签，创建
            else:
                usertag.used_count += 1#该用户已有该标签，增加使用计数
            if self.owner.isLocal():#该用户的数据是否位于本地站点 
                usertag.save()
            else:
                usertag.save(using='remote')               
        if self.owner.isLocal():#该用户的数据是否位于本地站点         
            self.save()#保存照片信息
        else:
            self.save(using='remote')#保存照片信息           
        
    def calculateScore(self):
        BEGIN_TIME = datetime.datetime(2012,1,1,0,0,0)
        time_offset1 = datetime.datetime.now() - BEGIN_TIME
        time_offset2 = datetime.datetime.now() - self.date_posted
        minutes1 = (time_offset1.days * 24 * 60) + time_offset1.seconds / 60
        minutes2 = (time_offset2.days * 24 * 60) + time_offset2.seconds / 60
        import math
        self.score = minutes1 / 120.0 + (self.like_count + 1) / (math.atan(minutes2 / 240.0 + 0.5) ** 2.2)
        
    #删除照片前，对照片关联数据的清理
    def clearPhoto(self):
        self.album.photo_count -= 1
        self.owner.photo_count -= 1  
        self.update_photo_info("", "", [])#先清空该照片的标签
        
        if self.owner.isLocal():
            self.album.save(using='default')  
        else:
            self.album.save(using='remote')
            
        self.owner.save(using='default')
        self.owner.save(using='remote')
        
        #对评论标注照片已被删除
        from grnglow.glow.models.comment import Comment
        if self.owner.isLocal():
            comments = Comment.objects.using('default').filter(photo_id=self.id,photo_owner=self.owner)
            for c in comments:
                c.photo_deleted = True
                c.save(using='default')
                if c.author.city != self.owner.city:#照片和评论者不在同一个站点
                    cr = Comment.objects.using('remote').get(id=c.master_id)
                    cr.photo_deleted = True
                    cr.save(using='remote')
        else:
            comments = Comment.objects.using('remote').filter(photo_id=self.id,photo_owner=self.owner)
            for c in comments:
                c.photo_deleted = True
                c.save(using='remote')
                if c.author.city != self.owner.city:
                    rc = Comment.objects.using('default').get(id=c.master_id)
                    rc.photo_deleted = True
                    rc.save(using='default')
                    
        #删除照片文件
        self.deletePhotoFiles()
    
    #删除照片文件
    def deletePhotoFiles(self):
        if self.owner.isLocal():
            filePath = settings.MEDIA_PARENT_PATH + self.square_loc
            if os.path.isfile(filePath):
                os.remove(filePath)
                
            filePath = settings.MEDIA_PARENT_PATH + self.thumb_loc
            if os.path.isfile(filePath):
                os.remove(filePath)
        
            filePath = settings.MEDIA_PARENT_PATH + self.middle_loc
            if os.path.isfile(filePath):
                os.remove(filePath)        
        
            filePath = settings.MEDIA_PARENT_PATH + self.original_loc
            if os.path.isfile(filePath):
                os.remove(filePath)
        else:
            from grnglow.glow.util import util
            util.remote_delete_photo(self.owner.id, self.id)