#-*- encoding: utf-8 -*-
'''
Created on 2012-3-22

@author: Neil
'''
from django.utils.encoding import smart_str
from django.utils.hashcompat import md5_constructor, sha_constructor
from django.db import models
from grnglow import settings

UNUSABLE_PASSWORD = '!' # This will never be a valid hash

def get_hexdigest(algorithm, salt, raw_password):
    """
    Returns a string of the hexdigest of the given plaintext password and salt
    using the given algorithm ('md5', 'sha1' or 'crypt').
    """
    raw_password, salt = smart_str(raw_password), smart_str(salt)
    if algorithm == 'crypt':
        try:
            import crypt
        except ImportError:
            raise ValueError('"crypt" password algorithm not supported in this environment')
        return crypt.crypt(raw_password, salt)

    if algorithm == 'md5':
        return md5_constructor(salt + raw_password).hexdigest()
    elif algorithm == 'sha1':
        return sha_constructor(salt + raw_password).hexdigest()
    raise ValueError("Got unknown password algorithm type in password.")

def check_password(raw_password, enc_password):
    """
    Returns a boolean of whether the raw_password was correct. Handles
    encryption formats behind the scenes.
    """
    algo, salt, hsh = enc_password.split('$')
    return hsh == get_hexdigest(algo, salt, raw_password)

class User(models.Model):
    """
    用户的数据模型
    name, email and password are required. Other fields are optional.
    """
    #user_id = models.IntegerField(unique=True, primary_key=True)#替代默认的id作为主键
    name = models.CharField(max_length=14, unique=True)#"中、英文均可，最长14个英文或7个汉字"
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)#"Use '[algo]$[salt]$[hexdigest]' or use the <a href=\"password/\">change password form</a>."
    city = models.CharField(max_length=32)#常居地
    last_login = models.DateTimeField(auto_now_add=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    
    photo_count = models.IntegerField(default=0)
    album_count = models.IntegerField(default=1)
    avatar_loc = models.CharField(max_length=128, default='')
    avatar_square_loc = models.CharField(max_length=128, default='')
    
    is_local = None#判断该用户的数据是否在本地站点
    
    def __unicode__(self):
        return self.name
    
    class Meta:
        ordering = ['name']
        app_label = 'glow'

    def isLocal(self):
        if self.is_local != None:
            return self.is_local
        else:
            self.is_local = True if self.city == settings.LOCAL_SITE_NAME else False
            return self.is_local
    
    def is_authenticated(self):
        """
        Always return True. This is a way to tell if the user has been
        authenticated in templates.
        """
        return True

    def get_name(self):
        return self.name

    def set_password(self, raw_password):
        if raw_password is None:
            self.set_unusable_password()
        else:
            import random
            algo = 'sha1'
            salt = get_hexdigest(algo, str(random.random()), str(random.random()))[:5]
            hsh = get_hexdigest(algo, salt, raw_password)
            self.password = '%s$%s$%s' % (algo, salt, hsh)

    def check_password(self, raw_password):
        """
        Returns a boolean of whether the raw_password was correct. Handles
        encryption formats behind the scenes.
        """
        # Backwards-compatibility check. Older passwords won't include the
        # algorithm or salt.
        if '$' not in self.password:
            is_correct = (self.password == get_hexdigest('md5', '', raw_password))
            if is_correct:
                # Convert the password to the new, more secure format.
                self.set_password(raw_password)
                self.save()
            return is_correct
        return check_password(raw_password, self.password)

    def set_unusable_password(self):
        # Sets a value that will never be a valid hash
        self.password = UNUSABLE_PASSWORD

    def has_usable_password(self):
        if self.password is None \
            or self.password == UNUSABLE_PASSWORD:
            return False
        else:
            return True
