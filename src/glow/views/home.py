# -*- encoding: utf-8 -*-
'''
Created on 2012-3-23

@author: Neil
'''
from django.shortcuts import render_to_response
from grnglow.glow.views import people
from grnglow.glow.models.photo import Photo


def base(request):
    return render_to_response('base.html')


def index(request):
    if request.user.is_authenticated():
        # 默认情况下，people.home(request,user_id)的user_id参数应该为字符串
        return people.home(request, str(request.user.id))  # 如果已登录，跳转到我的个人页
        # return render_to_response('index.html', {'request':request})

    else:
        photos = Photo.objects.all().order_by('-score')[0:12]  # 按得分倒序，最大的排在前面
        p_len = len(photos)
        p_items = []
        for i in range(0, p_len, 6):
            p_items.extend([photos[i:i + 6]])  # 在末端添加列表元素

        return render_to_response('index.html', {'request': request, 'p_items': p_items})
