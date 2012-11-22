#-*- encoding: utf-8 -*-
'''
Created on 2012-3-23

@author: Neil
'''
from django.shortcuts import render_to_response
from grnglow.glow.models.photo import Photo
from grnglow.glow.models.tag import Tag
from grnglow.glow.models.user import User
from grnglow.glow.util import util

def default(request):

    if 'q' in request.GET:
        q = request.GET['q']
        if not q:
            return render_to_response('404.html')
        else:
            #contains是严格区分大小写的，icontains（Case-insensitive contains）是不严格区分大小写的
            inner_qs_tag = Tag.objects.filter(name__icontains=q)
            inner_qs_user = User.objects.filter(name__icontains=q)
            photo_by_tag = Photo.objects.filter(tags__in=inner_qs_tag).order_by('id')
            photo_by_user_name = Photo.objects.filter(owner__in=inner_qs_user).order_by('id')
            photos_by_caption = Photo.objects.filter(caption__icontains=q).order_by('id')
            
            #将根据用户名，标签，描述，搜索到的图片列表合并成不包含重复的图片列表
            photos = util.merge_photos(photo_by_tag, photo_by_user_name, photos_by_caption)
            for p in photos:
                p.tag_list = p.tags.all()[0:4]#只取前4个标签
            
            p_len = len(photos)
            
            p_items = []
            for i in range(0, p_len, 3):
                p_items.extend([photos[i:i+3]])#在末端添加列表元素
        
            return render_to_response('search/default.html',{'request':request,'query':q,'p_items':p_items})
    else:
        return render_to_response('404.html')
    