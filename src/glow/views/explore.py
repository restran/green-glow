# -*- encoding: utf-8 -*-
'''
Created on 2012-3-23

@author: Neil
'''
from django.shortcuts import render_to_response
from grnglow.glow.models.photo import Photo


# 精彩照片
def hots(request):
    photos = Photo.objects.all().order_by('-score')[0:21]  # 按得分倒序，最大的排在前面
    for p in photos:
        p.tag_list = p.tags.all()[0:4]  # 只取前4个标签

    p_len = len(photos)
    p_len_remainder = p_len % 3  # 余数

    if p_len_remainder != 0:
        p_len -= p_len_remainder

    # 把[1,2,3,4,5]转换成[[1,2,3],[4,5]]
    p_items = []
    for i in range(0, p_len, 3):
        p_items.extend([[photos[i], photos[i + 1], photos[i + 2]]])

    if p_len_remainder == 1:
        p_items.extend([[photos[p_len]]])
    elif p_len_remainder == 2:
        p_items.extend([[photos[p_len], photos[p_len + 1]]])

    return render_to_response('explore/default.html', {'request': request,
                                                       'p_items': p_items, 'isHots': True})


# 最近上传照片
def recents(request):
    photos = Photo.objects.all().order_by('-date_posted')[0:21]  # 按上传时间倒序，最近的排在前面
    for p in photos:
        p.tag_list = p.tags.all()[0:4]  # 只取前4个标签

    # 把[1,2,3,4,5]转换成[[1,2,3],[4,5]]，每行3个
    p_len = len(photos)
    p_items = []
    for i in range(0, p_len, 3):
        p_items.extend([photos[i:i + 3]])  # 在末端添加列表元素

    return render_to_response('explore/default.html', {'request': request,
                                                       'p_items': p_items, 'isRecents': True})
