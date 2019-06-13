# -*- encoding: utf-8 -*-
'''
Created on 2012-3-27

@author: Neil
'''
from grnglow.glow.models.user import User
import datetime


class EmailAuthBackend(object):
    """
    Email Authentication Backend
    Allows a user to sign in using an email/password pair rather than
    a username/password pair.
    """

    def authenticate(self, email=None, password=None):
        """ Authenticate a user based on email address as the user name. """
        try:
            user = User.objects.get(email=email)
            if user.check_password(password):
                return user
        except User.DoesNotExist:
            return None

    def get_user(self, user_id):
        """ Get a User object from the user_id. """
        try:
            user = User.objects.get(pk=user_id)
            user.last_login = datetime.datetime.now()  # 用户上线
            user.save()  # 将数据写入数据库
        except User.DoesNotExist:
            return None
        else:
            return user
