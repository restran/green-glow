#-*- encoding: utf-8 -*-
'''
Created on 2012-3-23

@author: Neil
'''
from django.shortcuts import render_to_response
from grnglow.glow.views import people
from grnglow.glow.models.photo import Photo
from grnglow.glow.models.user import User
from grnglow.glow.util import util
from grnglow import settings
from django.views.decorators.csrf import csrf_exempt
from grnglow.glow.models.remote_operate import RemoteOperate
import os, time, Image
from django.http import HttpResponse

def base(request):
    return render_to_response('base.html')

def index(request):
    if request.user.is_authenticated():
        #默认情况下，people.home(request,user_id)的user_id参数应该为字符串
        return people.home(request, str(request.user.id))#如果已登录，跳转到我的个人页
        #return render_to_response('index.html', {'request':request})

    else:
        photos = Photo.objects.all().order_by('-score')[0:12]#按得分倒序，最大的排在前面
        p_len = len(photos)
        p_items = []
        for i in range(0, p_len, 6):
            p_items.extend([photos[i:i+6]])#在末端添加列表元素
            
        return render_to_response('index.html', {'request':request,'p_items':p_items})

def error_404(request):
    return render_to_response('404.html')

@csrf_exempt # 若没有csrf处理，服务器会返回403 forbidden错误
def remote_upload_photo(request):  
    if request.method != 'POST':
        return HttpResponse("error")

    try:
        ro = RemoteOperate.objects.get(key=request.POST.get('key'))
    except RemoteOperate.DoesNotExist:
        return HttpResponse("key does not exist")
    
    try:
        user = User.objects.get(id=ro.user_id)
    except User.DoesNotExist:
        return HttpResponse("user does not exist") 
    
    try:
        photo = Photo.objects.get(id=ro.photo_id, owner=user)
    except Photo.DoesNotExist:
        return HttpResponse("photo does not exist")
    
    photo.save_photo_file(request.FILES['file'])
    photo.save()#保存到数据库
    ro.delete()#删除该远程上传照片会话记录
    return HttpResponse('ok')

@csrf_exempt # 若没有csrf处理，服务器会返回403 forbidden错误
def remote_edit_avatar(request):
    if request.method != 'POST':
        return HttpResponse("error")

    try:
        ro = RemoteOperate.objects.get(key=request.POST.get('key'))
    except RemoteOperate.DoesNotExist:
        return HttpResponse("key does not exist")
    
    try:
        user = User.objects.get(id=ro.user_id)
    except User.DoesNotExist:
        return HttpResponse("user does not exist")  

    if user.avatar_loc != settings.DEFAULT_AVATAR_LOC:#如果用户不是使用缺省头像的话，删掉原先的图片
        try:
            os.remove(settings.MEDIA_PARENT_PATH + user.avatar_loc)
            os.remove(settings.MEDIA_PARENT_PATH + user.avatar_square_loc)
        except:
            pass#避免文件不存在而出现无法删除的异常
    
    try:
        image = Image.open(request.FILES['file'])
        image.save(settings.MEDIA_PARENT_PATH + user.avatar_loc, "jpeg", quality=90)#保存头像图片
        image = util.makeSquareImg(image, 48)
        image.save(settings.MEDIA_PARENT_PATH + user.avatar_square_loc, "jpeg", quality=90)
        ro.delete()#删除该远程上传记录
    except:
        import sys
        return HttpResponse(str(sys.exc_info()[0]) + str(sys.exc_info()[1]))
        
    return HttpResponse("ok")

@csrf_exempt # 若没有csrf处理，服务器会返回403 forbidden错误
def remote_delete_photo(request):
    if request.method != 'POST':
        return HttpResponse("error")

    try:
        ro = RemoteOperate.objects.get(key=request.POST.get('key'))
    except RemoteOperate.DoesNotExist:
        return HttpResponse("key does not exist")
    
    try:
        user = User.objects.get(id=ro.user_id)
    except User.DoesNotExist:
        return HttpResponse("user does not exist") 
    
    try:
        photo = Photo.objects.get(owner=user,id=ro.photo_id)
    except Photo.DoesNotExist:
        return HttpResponse("photo does not exist")
    
    photo.deletePhotoFiles()
    ro.delete()#删除该远程删除照片会话记录
        
    return HttpResponse("ok")