#-*- encoding: utf-8 -*-
'''
Created on 2012-3-23

@author: Neil
'''
from django.shortcuts import render_to_response
from grnglow.glow.models.photo import Photo
from grnglow import settings
from grnglow.glow.util import util

#同城（当前站）精彩照片
def localHots(request):
    photos = Photo.objects.all().order_by('-score')[0:21]#按得分倒序，最大的排在前面
    for p in photos:
        p.tag_list = p.tags.all()[0:4]#只取前4个标签
    
    p_len = len(photos)
    p_len_remainder = p_len % 3#余数

    if p_len_remainder  != 0:
        p_len -= p_len_remainder
    
    #把[1,2,3,4,5]转换成[[1,2,3],[4,5]]
    p_items = []
    for i in range(0, p_len, 3):
        p_items.extend([[photos[i], photos[i+1], photos[i+2]]])
        
    if p_len_remainder == 1:
        p_items.extend([[photos[p_len]]])
    elif p_len_remainder == 2:
        p_items.extend([[photos[p_len], photos[p_len+1]]])
        
    return render_to_response('explore/default.html',{'request':request,
            'p_items':p_items,'isLocalHots':True,'current_city':settings.LOCAL_SITE_NAME})

#同城（当前站）最近上传照片
def localRecents(request):
    photos = Photo.objects.all().order_by('-date_posted')[0:21]#按上传时间倒序，最近的排在前面
    for p in photos:
        p.tag_list = p.tags.all()[0:4]#只取前4个标签
  
    #把[1,2,3,4,5]转换成[[1,2,3],[4,5]]，每行3个
    p_len = len(photos)      
    p_items = []
    for i in range(0, p_len, 3):
        p_items.extend([photos[i:i+3]])#在末端添加列表元素
    
    return render_to_response('explore/default.html',{'request':request,
        'p_items':p_items,'isLocalRecents':True,'current_city':settings.LOCAL_SITE_NAME})

#全站的精彩照片
def globalHots(request):
    photos_local = Photo.objects.all().order_by('-score')[0:15]#按得分倒序，最大的排在前面
    photos_remote = Photo.objects.using('remote').all().order_by('-score')[0:15]#按得分倒序，最大的排在前面
    
    for p in photos_local:
        p.tag_list = p.tags.all()[0:4]#只取前4个标签
    for p in photos_remote:
        p.tag_list = p.tags.all()[0:4]#只取前4个标签
        p.thumb_loc = settings.REMOTE_SITE_URL + p.thumb_loc
        
    photos = list(photos_remote) + list(photos_local)#将两个站点获取到的照片合并成一个列表
    util.sort_photo_list_by_score(photos)#按得分的降序对photo排序
    
    p_len = len(photos)
    p_len_remainder = p_len % 3#余数

    if p_len_remainder  != 0:
        p_len -= p_len_remainder
    
    #把[1,2,3,4,5]转换成[[1,2,3],[4,5]]
    p_items = []
    for i in range(0, p_len, 3):
        p_items.extend([[photos[i], photos[i+1], photos[i+2]]])
        
    if p_len_remainder == 1:
        p_items.extend([[photos[p_len]]])
    elif p_len_remainder == 2:
        p_items.extend([[photos[p_len], photos[p_len+1]]])
        
    return render_to_response('explore/default.html',{'request':request,
                'p_items':p_items,'isGlobalHots':True,'current_city':settings.LOCAL_SITE_NAME})