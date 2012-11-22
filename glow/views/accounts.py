#-*- encoding: utf-8 -*-
'''
Created on 2012-3-23

@author: Neil
'''
#必须导入的模块
from grnglow.glow.auth.forms import UserCreationForm, UserInfoEditForm, PasswordChangeForm
from grnglow.glow import auth
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from grnglow.glow.models.album import Album
from grnglow import settings 
from grnglow.glow.util import util 
import os, time, Image
from django.views.decorators.csrf import csrf_protect

#注册时检查用户名是否已存在
def reg_check_username(request):  
    pass

def reg_check_email(request):
    pass

#登录
@csrf_protect
def login(request):
    if request.method == 'POST':
        email = request.POST.get('email', '')
        password = request.POST.get('password', '')
        user = auth.authenticate(email=email, password=password)
        if user is not None:
            # 认证通过
            auth.login(request, user)
            # 跳转到登陆成功的页面
            return HttpResponseRedirect(settings.HOME_PAGE_URL)#跳转到主页
        else:
            # 返回出错信息
            return render_to_response("accounts/login.html", {'login_failed':True, 'p_email':email})
    else:
        return render_to_response("accounts/login.html", {'login_failed':False})

#登出
def logout(request):
    auth.logout(request)
    return HttpResponseRedirect(settings.HOME_PAGE_URL)#跳转到主页

#注册
@csrf_protect
def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()#将数据保存到数据库中
            user.avatar_loc = settings.DEFAULT_AVATAR_LOC
            user.avatar_square_loc = settings.DEFAULT_AVATAR_SQUARE_LOC
                
            user.save(using='default')#保存缺省头像，是否位于本地的标志
            album = Album(owner=user, topic='默认相册')

            user.save(using='remote')#将用户数据保存到远程数据库
            if user.isLocal():
                album.save(using='default')#为用户创建一个默认相册，每个用户至少要有一个相册
            else:
                album.save(using='remote')
            
            return render_to_response("accounts/register.html",
                {'register_success':True, 'username':user.name})#注册成功
        else:
            return render_to_response("accounts/register.html",
                {'register_success':False, 'email_hasExist':form.emial_hasExist, 
                'name_hasExist':form.name_hasExist, 'password_notMatch':form.password_notMatch,
                'p_email':request.POST['email'],'p_name':request.POST['name'],'p_city':request.POST['city']})
    else:
        return render_to_response("accounts/register.html", {'register_success':False})
    

#查看个人资料
@csrf_protect
def profile(request):
    if not request.user.is_authenticated():
        return render_to_response('404.html')
    
    if not request.user.isLocal():#如果不在本地，修改图片的地址
        request.user.avatar_loc = settings.REMOTE_SITE_URL + request.user.avatar_loc
        request.user.avatar_square_loc = settings.REMOTE_SITE_URL + request.user.avatar_square_loc
        
    if request.method == 'POST':
        user = request.user
        name = request.POST.get('name', '')
        if name != user.name:
            form = UserInfoEditForm(user, request.POST)
            if form.is_valid():
                user = form.save()
                user.save(using='remote')#保存数据到远程数据库
                return render_to_response("accounts/profile.html", 
                    {'user':user,'name_edited':False,'edit_success':True,'request':request}) 
            else:
                
                return render_to_response("accounts/profile.html", 
                    {'user':user,'name_edited':True,'name_hasExist':form.name_hasExist,'request':request})
        else:
            return render_to_response("accounts/profile.html", 
                    {'user':user,'name_edited':False,'request':request})
    else:
        user = request.user
        return render_to_response("accounts/profile.html", 
                    {'user':user,'name_edited':False,'request':request})

#修改个人头像
@csrf_protect
def editavatar(request):
    if not request.user.is_authenticated():
        return render_to_response('404.html')
    
    if not request.user.isLocal():#如果不在本地，修改图片的地址
        request.user.avatar_loc = settings.REMOTE_SITE_URL + request.user.avatar_loc
        request.user.avatar_square_loc = settings.REMOTE_SITE_URL + request.user.avatar_square_loc
        
    if request.method == 'POST':
        user = request.user
        file_name = str(user.id) + '_temp.jpg'#临时头像文件
        temp_avatar_loc = settings.AVATAR_RELATIVE_PATH + file_name#头像图片相对于站点的存放位置
        temp_abs_path = settings.UPLOAD_AVATAR_PATH + file_name
        #多个submit的判断，第一个name，第二个是value
        if request.POST.get('pic_submit') == u'上传图片':#中文使用unicode，要加u
            img_file = request.FILES.get('pic_avatar')
            if img_file == None:#没有选择图片
                if os.path.isfile(temp_abs_path):#如果已存在上次上传的临时头像图片，则显示上传上传的图片
                    avatar_loc = temp_avatar_loc
                else:
                    avatar_loc = user.avatar_loc
                return render_to_response("accounts/editavatar.html", 
                        {'avatar_loc':avatar_loc,'request':request})
            else:
                image = Image.open(img_file)
                image = util.makeSquareImg(image, 160)
                #image.thumbnail((160,160), Image.ANTIALIAS)
                if os.path.isfile(temp_abs_path):#如果已存在上次上传的临时头像图片，先删除
                    os.remove(temp_abs_path)
                image.save(temp_abs_path, "jpeg", quality=90)#将该头像图片临时保存起来，不设置quality，默认是75
                
                return render_to_response("accounts/editavatar.html", 
                        {'avatar_loc':temp_avatar_loc,'request':request})
        elif request.POST.get('save') == u'保存':
            if os.path.isfile(temp_abs_path):#如果存在上传的临时头像图片，更新头像
                nowTime = time.localtime()
                #头像地址加上时间，和之前的头像予以区分，可以避免使用相同路径，导致浏览器缓存图片而使得在返回个人资料页时，头像还是之前的
                user.avatar_loc = settings.AVATAR_RELATIVE_PATH + str(user.id) + '_' + time.strftime('%Y%m%d%H%M%S', nowTime) + '_l.jpg'
                user.avatar_square_loc = settings.AVATAR_RELATIVE_PATH + str(user.id) + '_' + time.strftime('%Y%m%d%H%M%S', nowTime) + '_s.jpg'
                user.save()#保存数据到数据库
                user.save(using='remote')#保存数据到远程数据库
                
                if not request.user.isLocal():#如果是远程操作，将图片传到用户所在站点
                    imgFile = open(temp_abs_path, "rb")
                    util.remote_edit_avatar(user.id, imgFile)
                    imgFile.close()
                else:
                    if user.avatar_loc != settings.DEFAULT_AVATAR_LOC:#如果用户不是使用缺省头像的话，删掉原先的图片
                        try:
                            os.remove(settings.MEDIA_PARENT_PATH + user.avatar_loc)
                            os.remove(settings.MEDIA_PARENT_PATH + user.avatar_square_loc)
                        except:
                            pass#避免文件不存在而出现无法删除的异常
                    
                    image = Image.open(temp_abs_path)
                    image.save(settings.MEDIA_PARENT_PATH + user.avatar_loc, "jpeg", quality=90)#保存头像图片
                    image = util.makeSquareImg(image, 48)
                    image.save(settings.MEDIA_PARENT_PATH + user.avatar_square_loc, "jpeg", quality=90)
                
                os.remove(temp_abs_path)#删除临时头像图片
            
            return HttpResponseRedirect(settings.HOME_PAGE_URL + 'accounts/profile/')
        elif request.POST.get('cancel') == u'撤销':
            if os.path.isfile(temp_abs_path):#如果存在上传的临时头像图片，删除该图片
                os.remove(temp_abs_path)
            return HttpResponseRedirect(settings.HOME_PAGE_URL + 'accounts/profile/')
    else:
        user = request.user
        return render_to_response("accounts/editavatar.html", 
                    {'avatar_loc':user.avatar_loc,'request':request})
    
#修改密码
@csrf_protect
def editpassword(request):
    if not request.user.is_authenticated():
        return render_to_response('404.html')
    
    if request.method == 'POST':
        user = request.user
        form = PasswordChangeForm(user, request.POST)
        if form.is_valid():
            user = form.save()#将数据保存到数据库中
            user.save(using='remote')#保存数据到远程数据库
            return render_to_response("accounts/editpassword.html",
                {'editpassword_success':True, 'request':request})#修改成功
        else:
            return render_to_response("accounts/editpassword.html",{'editpassword_success':False,
                'password_notMatch':form.password_notMatch,'old_password_correct':form.old_password_correct,
                'request':request})
    else:
        return render_to_response("accounts/editpassword.html", 
               {'editpassword_success':False,'request':request,'old_password_correct':True})