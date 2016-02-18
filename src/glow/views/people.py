# -*- encoding: utf-8 -*-
'''
Created on 2012-3-23

@author: Neil
'''
from django.shortcuts import render_to_response
from grnglow.glow.models.album import Album
from grnglow.glow.models.user import User
from grnglow.glow.models.photo import Photo
from grnglow.glow.models.usertag import UserTag
from grnglow.glow.models.comment import Comment
from grnglow.glow.models.like import Like
from grnglow.glow.models.follow import Follow
from grnglow.glow.views import error_404
from django.http import HttpResponse
import json, sys
from django.views.decorators.csrf import csrf_exempt


def home(request, user_id):
    try:
        people = User.objects.get(id=user_id)
    except:
        return error_404(request)

    recent_photos = Photo.objects.filter(owner=people).order_by('-date_posted')[0:12]  # 按上传时间倒序，最近的排在前面
    album_list = Album.objects.filter(owner=people).order_by('-date_created')[0:10]  # 按创建时间倒序，最近的排在前面
    # 统计相册数目是否大于10，若大于则显示，“查看更多”
    if Album.objects.filter(owner=people).count() > 10:
        album_too_more = True
    else:
        album_too_more = False

    # 添加相册封面图片的地址
    for album in album_list:
        album.cover_loc = album.getCoverLoc()

    # 取标签
    for p in recent_photos:
        p.tag_list = p.tags.all()[0:4]  # 只取前4个标签

    p_len = len(recent_photos)
    p_items = []
    for i in range(0, p_len, 2):
        p_items.extend([recent_photos[i:i + 2]])  # 在末端添加列表元素

    is_myPage = False  # 用来标记该页面是不是登录用户的个人页面
    if request.user.is_authenticated():
        if str(request.user.id) == user_id:  # 注意user_id是unicode字符串，比较时要先转成字符串
            is_myPage = True  # 用户查看自己的页面，可以进行编辑操作
        else:
            try:
                Follow.objects.get(be_followed_user=people, follower=request.user)
            except Follow.DoesNotExist:
                people.i_follow = False
            else:
                people.i_follow = True

    request.pageTitle = people.name + u'的照片'  # django模板使用unicode编码
    return render_to_response('people/home.html', {'request': request, 'people': people,
                                                   'album_list': album_list, 'p_items': p_items,
                                                   'album_too_more': album_too_more, 'is_myPage': is_myPage})


def albums(request, user_id):
    try:
        people = User.objects.get(id=user_id)
    except:
        return error_404(request)

    album_list = Album.objects.filter(owner=people).order_by('-date_created')  # 按创建时间倒序，最近的排在前面
    # 添加相册封面图片的地址
    for album in album_list:
        album.cover_loc = album.getCoverLoc()

    is_myPage = False  # 用来标记该页面是不是登录用户的个人页面
    if request.user.is_authenticated():
        if str(request.user.id) == user_id:  # 注意user_id是unicode字符串，比较时要先转成字符串
            is_myPage = True
        else:
            try:
                Follow.objects.get(be_followed_user=people, follower=request.user)
            except Follow.DoesNotExist:
                people.i_follow = False
            else:
                people.i_follow = True

    request.pageTitle = people.name + u"的相册"
    return render_to_response('people/albums.html', {'request': request,
                                                     'people': people, 'album_list': album_list,
                                                     'is_myPage': is_myPage})


def tags(request, user_id):
    try:
        people = User.objects.get(id=user_id)
    except:
        return error_404(request)

    tag_list = UserTag.objects.filter(user=people)

    for t in tag_list:
        if t.used_count == 1:
            t.fontsize = 14
        elif t.used_count < 5:
            t.fontsize = 16
        elif t.used_count < 10:
            t.fontsize = 20
        elif t.used_count < 17:
            t.fontsize = 24
        else:
            t.fontsize = 28

    is_myPage = False  # 用来标记该页面是不是登录用户的个人页面
    if request.user.is_authenticated():
        if str(request.user.id) == user_id:  # 注意user_id是unicode字符串，比较时要先转成字符串
            is_myPage = True  # 用户查看自己的页面，可以进行编辑操作
        else:
            try:
                Follow.objects.get(be_followed_user=people, follower=request.user)
            except Follow.DoesNotExist:
                people.i_follow = False
            else:
                people.i_follow = True

    request.pageTitle = people.name + u"的标签"
    return render_to_response('people/tags.html', {'request': request,
                                                   'people': people, 'tag_list': tag_list, 'is_myPage': is_myPage})


def comments(request, user_id, is_myComments=False):
    # 只有登录用户，且是自己的页面，才可以操作
    if not request.user.is_authenticated() or str(request.user.id) != user_id:
        return error_404(request)

    comment_list = []

    if is_myComments:
        comment_list = Comment.objects.filter(author=request.user).order_by('-date_posted')
    else:
        comment_list = Comment.objects.filter(photo_owner=request.user, deleted_by_photo_owner=False).order_by(
            '-date_posted')

    for c in comment_list:
        c.photo = Photo.objects.get(id=c.photo_id)

    request.pageTitle = request.user.name + u"的评论"
    return render_to_response('people/comments.html', {'request': request, 'is_myPage': True,
                                                       'people': request.user, 'comment_list': comment_list,
                                                       'is_myComments': is_myComments})


def comments_mine(request, user_id):
    return comments(request, user_id, is_myComments=True)


# 当用户查看自己的页面时，在people的导航栏不显示个人资料页
def profile(request, user_id):
    try:
        people = User.objects.get(id=user_id)
    except:
        return error_404(request)

    is_myPage = False  # 用来标记该页面是不是登录用户的个人页面
    if request.user.is_authenticated():
        if str(request.user.id) == user_id:  # 注意user_id是unicode字符串，比较时要先转成字符串
            is_myPage = True
        else:
            try:
                Follow.objects.get(be_followed_user=people, follower=request.user)
            except Follow.DoesNotExist:
                people.i_follow = False
            else:
                people.i_follow = True

    request.pageTitle = people.name + u"的个人资料"
    return render_to_response('people/profile.html', {'request': request, 'people': people, 'is_myPage': is_myPage})


def likes(request, user_id):
    try:
        people = User.objects.get(id=user_id)
    except:
        return error_404(request)

    likes = Like.objects.filter(user=people).order_by('-date_liked')  # 按喜欢时间倒序，最近的排在前面

    photos = []

    for l in likes:
        p = Photo.objects.get(id=l.photo_id)
        photos.append(p)  # 在末端添加元素

    p_len = len(photos)

    # 把[1,2,3,...,10,11,12]转换成[[1,2,3,...,10],[11,12]]
    p_items = []
    for i in range(0, p_len, 10):
        p_items.extend([photos[i:i + 10]])  # 在末端添加列表元素

    is_myPage = False  # 用来标记该页面是不是登录用户的个人页面
    if request.user.is_authenticated():
        if str(request.user.id) == user_id:  # 注意user_id是unicode字符串，比较时要先转成字符串
            is_myPage = True  # 用户查看自己的页面，可以进行编辑操作
        else:
            try:
                Follow.objects.get(be_followed_user=people, follower=request.user)
            except Follow.DoesNotExist:
                people.i_follow = False
            else:
                people.i_follow = True

    request.pageTitle = people.name + u"喜欢的照片"
    return render_to_response('people/likes.html',
                              {'request': request, 'people': people, 'p_items': p_items, 'is_myPage': is_myPage})


# is_myFollow==True表示显示的是我关注的人
# is_myFollow==False表示关注我的人
def follow(request, user_id, is_myFollow=True):
    try:
        people = User.objects.get(id=user_id)
    except:
        return error_404(request)

    follow_list = []
    if is_myFollow:
        follow_list = Follow.objects.filter(follower=people).order_by('-date_followed')
    else:
        follow_list = Follow.objects.filter(be_followed_user=people).order_by('-date_followed')

    is_myPage = False  # 用来标记该页面是不是登录用户的个人页面
    if request.user.is_authenticated():
        if str(request.user.id) == user_id:  # 注意user_id是unicode字符串，比较时要先转成字符串
            is_myPage = True
        else:
            try:
                Follow.objects.get(be_followed_user=people, follower=request.user)
            except Follow.DoesNotExist:
                people.i_follow = False
            else:
                people.i_follow = True

    request.pageTitle = people.name + u"的关注"
    return render_to_response('people/follow.html', {'request': request, 'is_myPage': is_myPage,
                                                     'people': request.user, 'follow_list': follow_list,
                                                     'is_myFollow': is_myFollow, 'people': people})


def follow_me(request, user_id):
    return follow(request, user_id, is_myFollow=False)


@csrf_exempt  # 若没有csrf处理，服务器会返回403 forbidden错误
def ajax_markFollow(request, user_id):
    if not request.is_ajax() or (request.method != 'POST'):
        return HttpResponse(json.dumps({"status": 'error0'}))

    # 只有登录用户，且被关注者不是自己，才可以操作，
    if not request.user.is_authenticated() or str(request.user.id) == user_id:
        return HttpResponse(json.dumps({"status": 'error1'}))

    try:
        people = User.objects.get(id=user_id)
        follow = Follow(be_followed_user=people, follower=request.user)
        if follow.isExist():  # 判断该关注记录是否已存在，避免重复关注
            return HttpResponse(json.dumps({"status": 'success'}))

        follow.save()
    except:
        return HttpResponse(json.dumps({"status": str(sys.exc_info()[0]) + str(sys.exc_info()[1])}))

    return HttpResponse(json.dumps({"status": 'success'}))


@csrf_exempt  # 若没有csrf处理，服务器会返回403 forbidden错误
def ajax_cancelFollow(request, user_id):
    if not request.is_ajax() or (request.method != 'POST'):
        return HttpResponse(json.dumps({"status": 'error0'}))

    # 只有登录用户，且被关注者不是自己，才可以操作，
    if not request.user.is_authenticated() or str(request.user.id) == user_id:
        return HttpResponse(json.dumps({"status": 'error1'}))

    try:
        people = User.objects.get(id=user_id)  # people是被关注者

        follow = Follow.objects.get(be_followed_user=people, follower=request.user)
        follow.delete()

    except:
        return HttpResponse(json.dumps({"status": str(sys.exc_info()[0]) + str(sys.exc_info()[1])}))

    return HttpResponse(json.dumps({"status": 'success'}))
