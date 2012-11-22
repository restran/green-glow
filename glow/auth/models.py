#-*- encoding: utf-8 -*-
'''
Created on 2012-3-26

@author: Neil
'''
class AnonymousUser(object):

    def __init__(self):
        pass

    def __unicode__(self):
        return 'AnonymousUser'

    def is_anonymous(self):
        return True

    def is_authenticated(self):
        return False