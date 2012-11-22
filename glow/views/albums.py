#-*- encoding: utf-8 -*-
'''
Created on 2012-3-23

@author: Neil
'''
from django.shortcuts import render_to_response
from grnglow.glow.models.album import Album
from grnglow.glow.models.user import User
from grnglow.glow.models.photo import Photo
from grnglow.glow.auth.forms import AlbumCreationForm, AlbumInfoEditForm
from django.http import HttpResponseRedirect, HttpResponse
from grnglow import settings
from django.views.decorators.csrf import csrf_protect, csrf_exempt
import json
import sys

@csrf_protect
def create(request, user_id):
    if not request.user.is_authenticated() or user_id != str(request.user.id):
        return render_to_response('404.html')
    
    if request.method == 'POST':
        if request.POST.get('create') == u'创建相册':
            form = AlbumCreationForm(request.user, request.POST)
            if form.is_valid():
                form.save()
                return render_to_response('albums/create_done.html', {'request':request})
            else:
                return render_to_response('albums/create.html', {'request':request,'form':form})
        elif request.POST.get('cancel') == u'取消':
            return HttpResponseRedirect(settings.HOME_PAGE_URL 
                + "people/" + str(request.user.id) + "/albums/")#跳转到用户的相册
    else:
        return render_to_response('albums/create.html', {'request':request})
    
@csrf_protect
def edit(request, user_id, album_id):
    if not request.user.is_authenticated() or user_id != str(request.user.id):
        return render_to_response('404.html')
    
    try:
        people = User.objects.get(id=user_id)
        if people.isLocal():#该用户的数据是否位于本地站点
            album = Album.objects.get(owner=people, id=album_id)
        else:
            album = Album.objects.using('remote').get(owner=user_id, id=album_id)
    except User.DoesNotExist, Album.DoesNotExist:
        return render_to_response('404.html')
    
    if request.method == 'POST':
        if request.POST.get('update') == u'更新':
            form = AlbumInfoEditForm(album, request.POST)
            if form.is_valid():
                album = form.save()
                return HttpResponseRedirect(settings.HOME_PAGE_URL 
                    + 'photos/' + str(request.user.id) + '/albums/' + str(album.id) + '/')#跳转到该相册的页面
            else:
                return render_to_response('albums/edit.html', {'request':request,'form':form,'album':album})
        elif request.POST.get('cancel') == u'取消':
            return HttpResponseRedirect(settings.HOME_PAGE_URL 
                   + 'people/' + str(request.user.id) + '/albums/')#跳转到用户的相册
    else:
        return render_to_response('albums/edit.html', {'request':request, 'album':album})
    
def album(request, user_id, album_id):  
    try:
        people = User.objects.get(id=user_id)
        if people.isLocal():#该用户的数据是否位于本地站点
            album = Album.objects.get(owner=people, id=album_id)
        else:
            album = Album.objects.using('remote').get(owner=people, id=album_id)  
    except:
        return render_to_response('404.html')
    
    if people.isLocal():#该用户的数据是否位于本地站点
        photos = Photo.objects.filter(owner=people, album=album).order_by('-date_posted')#按上传时间倒序，最近的排在前面
        album.cover_loc = album.getCoverLoc()
    else:
        photos = Photo.objects.using('remote').filter(owner=people, album=album).order_by('-date_posted')#按上传时间倒序，最近的排在前面
        for p in photos:
            p.thumb_loc = settings.REMOTE_SITE_URL + p.thumb_loc
        album.cover_loc = album.getCoverLoc()
        album.cover_loc = settings.REMOTE_SITE_URL + album.cover_loc
    
    for p in photos:
        p.tag_list = p.tags.all()[0:4]#只取前4个标签
        
    p_len = len(photos)
    
    p_items = []
    for i in range(0, p_len, 3):
        p_items.extend([photos[i:i+3]])#在末端添加列表元素
        
    #注意user_id是unicode字符串，比较时要先转成字符串
    if request.user.is_authenticated() and str(request.user.id) == user_id:
        is_myPage = True#用户查看自己的相册页面，可以进行编辑操作
    else:
        is_myPage = False
        
    return render_to_response('albums/album.html', {'request':request,'people':people,
        'p_items':p_items,'is_myPage':is_myPage,'album':album})
    
@csrf_exempt #若没有csrf处理，服务器会返回403 forbidden错误
def ajax_deleteAlbum(request, user_id, album_id):
    if not request.is_ajax() or (request.method != 'POST'):
        return HttpResponse(json.dumps({"status":'error0'}))
         
    #只有登录用户，且是自己的照片，才可以操作，
    if not request.user.is_authenticated() or str(request.user.id) != user_id:
        return HttpResponse(json.dumps({"status":'error1'}))
    
    try:
        if request.user.isLocal():
            count = Album.objects.filter(owner=request.user).count()
            if count == 1:
                return HttpResponse(json.dumps({"status":'only_one_album'}))
            else:          
                album = Album.objects.get(id=album_id)
                photos = Photo.objects.filter(album=album)
                for p in photos:
                    p.clearPhoto()
                    p.delete()
                album.owner.album_count -= 1
                album.owner.save(using='default')
                album.owner.save(using='remote')
                album.delete(using='default')
        else:
            count = Album.objects.using('remote').filter(owner=request.user).count()
            if count == 1:
                return HttpResponse(json.dumps({"status":'only_one_album'}))
            else:
                album = Album.objects.using('remote').get(id=album_id)
                photos = Photo.objects.using('remote').filter(album=album)
                for p in photos:
                    p.clearPhoto()
                    p.delete(using='remote')
                album.owner.album_count -= 1
                album.owner.save(using='default')
                album.owner.save(using='remote')
                album.delete(using='remote')
    except:
        return HttpResponse(json.dumps({"status":str(sys.exc_info()[0]) + str(sys.exc_info()[1])}))

    return HttpResponse(json.dumps({"status":'success'}))