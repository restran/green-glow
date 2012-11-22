#-*- encoding: utf-8 -*-
'''
Created on 2012-4-3

@author: Neil
'''

from django.utils.hashcompat import md5_constructor
from grnglow import settings
from grnglow.glow.models.remote_operate import RemoteOperate
from poster.encode import multipart_encode
from poster.streaminghttp import register_openers
import random, os, time, Image, urllib2

#生成方形缩略图
def makeSquareImg(im, size=48):
    mode = im.mode
    if mode not in ('L', 'RGB'):
        if mode == 'RGBA':
            # 透明图片需要加白色底
            alpha = im.split()[3]
            bgmask = alpha.point(lambda x: 255-x)
            im = im.convert('RGB')
            im.paste((255,255,255), None, bgmask)
        else:
            im = im.convert('RGB')

    width, height = im.size
    if width == height:
        region = im
    else:
        if width > height:
            delta = (width - height)/2
            box = (delta, 0, delta+height, height)
        else:
            delta = (height - width)/2
            box = (0, delta, width, delta+width)            
        region = im.crop(box)

    thumb = region.resize((size,size), Image.ANTIALIAS)
    return thumb


# Use the system (hardware-based) random number generator if it exists.
if hasattr(random, 'SystemRandom'):
    randrange = random.SystemRandom().randrange
else:
    randrange = random.randrange
    
MAX_SESSION_KEY = 18446744073709551616L     # 2 << 63
def get_new_remote_operate_key():
    "Returns key that isn't being used."
    # The random module is seeded when this Apache child is created.
    # Use settings.SECRET_KEY as added salt.
    try:
        pid = os.getpid()
    except AttributeError:
        # No getpid() in Jython, for example
        pid = 1
    while 1:
        key = md5_constructor("%s%s%s%s"
                % (randrange(0, MAX_SESSION_KEY), pid, time.time(),
                   settings.SECRET_KEY)).hexdigest()
        try:
            RemoteOperate.objects.using('remote').get(key=key)
        except RemoteOperate.DoesNotExist, RemoteOperate.MultipleObjectsReturned:
            break
        
    return key

def remote_upload_photo(user_id, photo_id, imageFile):
    key = get_new_remote_operate_key()
    remote_data = RemoteOperate(key=key, user_id=user_id, photo_id=photo_id)
    remote_data.save(using='remote')
     
    register_openers()
    
    # datagen: 对POST参数的encode(multipart/form-data)
    # headers: 发起POST请求时的http header的信息
    datagen, headers = multipart_encode({'key':key,'file':imageFile})
    
    # Create a Request object
    url = settings.REMOTE_SITE_URL + '/remote_upload_photo/'
    request = urllib2.Request(url, datagen, headers)
    
    # Actually do POST request
    response = urllib2.urlopen(request)
    
    print response.read() # 打印服务器端的回应信息
    
def remote_edit_avatar(user_id, imageFile):
    key = get_new_remote_operate_key()
    remote_data = RemoteOperate(key=key, user_id=user_id)
    remote_data.save(using='remote')
    
    register_openers()
    
    # datagen: 对POST参数的encode(multipart/form-data)
    # headers: 发起POST请求时的http header的信息
    datagen, headers = multipart_encode({'key':key,'file':imageFile})
    
    # Create a Request object
    url = settings.REMOTE_SITE_URL + '/remote_edit_avatar/'
    request = urllib2.Request(url, datagen, headers)
    
    # Actually do POST request
    response = urllib2.urlopen(request)
    
    print response.read() # 打印服务器端的回应信息
    
def remote_delete_photo(user_id, photo_id):
    key = get_new_remote_operate_key()
    remote_data = RemoteOperate(key=key, user_id=user_id, photo_id=photo_id)
    remote_data.save(using='remote')
     
    register_openers()
    
    # datagen: 对POST参数的encode(multipart/form-data)
    # headers: 发起POST请求时的http header的信息
    datagen, headers = multipart_encode({'key':key})
    
    # Create a Request object
    url = settings.REMOTE_SITE_URL + '/remote_delete_photo/'
    request = urllib2.Request(url, datagen, headers)
    
    # Actually do POST request
    response = urllib2.urlopen(request)
    
    print response.read() # 打印服务器端的回应信息


#排序方法
def photo_sort_key(p):
    return p.score

#传入的是photo的列表
def sort_photo_list_by_score(photo_list):
    #按得分的降序对photo排序
    photo_list.sort(reverse = True, key = photo_sort_key)
    
#将根据用户名，标签，描述，搜索到的图片列表合并成不包含重复的图片列表
def merge_photos(photo_by_tag, photo_by_user_name, photos_by_caption):
    photos = list(photo_by_tag)
    
    for p_list in (photo_by_user_name, photos_by_caption):
        temp = []
        for p in p_list:
            flag = False
            left = 0
            right = len(photos) - 1
            while left <= right:#用二分搜索查找是否存在重复photo
                mid = (left + right) / 2
                if p.id == photos[mid].id:
                    flag = True#存在重复的id
                    break
                elif p.id > photos[mid].id:
                    left = mid + 1
                else:
                    right = mid - 1
                    
            if flag == False:
                temp.append(p)
        photos.extend(temp)
        
    return photos