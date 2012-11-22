#-*- encoding: utf-8 -*-
'''
Created on 2012-3-27

@author: Neil
'''
from grnglow.glow.auth import get_user
class LazyUser(object):
    def __get__(self, request, obj_type=None):
        if not hasattr(request, '_cached_user'):
            request._cached_user = get_user(request)
        return request._cached_user

class AuthenticationMiddleware(object):
    def process_request(self, request):
        assert hasattr(request, 'session')#需要安装session中间件
        request.__class__.user = LazyUser()
        return None