# -*- encoding: utf-8 -*-
'''
Created on 2012-4-3

@author: Neil
'''

from PIL import Image


# 生成方形缩略图
def makeSquareImg(im, size=48):
    mode = im.mode
    if mode not in ('L', 'RGB'):
        if mode == 'RGBA':
            # 透明图片需要加白色底
            alpha = im.split()[3]
            bgmask = alpha.point(lambda x: 255 - x)
            im = im.convert('RGB')
            im.paste((255, 255, 255), None, bgmask)
        else:
            im = im.convert('RGB')

    width, height = im.size
    if width == height:
        region = im
    else:
        if width > height:
            delta = (width - height) / 2
            box = (delta, 0, delta + height, height)
        else:
            delta = (height - width) / 2
            box = (0, delta, width, delta + width)
        region = im.crop(box)

    thumb = region.resize((size, size), Image.ANTIALIAS)
    return thumb


# 排序方法
def photo_sort_key(p):
    return p.score


# 传入的是photo的列表
def sort_photo_list_by_score(photo_list):
    # 按得分的降序对photo排序
    photo_list.sort(reverse=True, key=photo_sort_key)


# 将根据用户名，标签，描述，搜索到的图片列表合并成不包含重复的图片列表
def merge_photos(photo_by_tag, photo_by_user_name, photos_by_caption):
    photos = list(photo_by_tag)

    for p_list in (photo_by_user_name, photos_by_caption):
        temp = []
        for p in p_list:
            flag = False
            left = 0
            right = len(photos) - 1
            while left <= right:  # 用二分搜索查找是否存在重复photo
                mid = (left + right) / 2
                if p.id == photos[mid].id:
                    flag = True  # 存在重复的id
                    break
                elif p.id > photos[mid].id:
                    left = mid + 1
                else:
                    right = mid - 1

            if flag == False:
                temp.append(p)
        photos.extend(temp)

    return photos
