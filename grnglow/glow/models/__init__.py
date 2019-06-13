import django.db.models
import sys

appname = 'glow'
from album import Album
from comment import Comment
from follow import Follow
from like import Like
from photo import Photo
from tag import Tag
from usertag import UserTag
from user import User

__all__ = []

for decl in globals().values():
    try:
        if decl.__module__.startswith(__name__) and issubclass(decl, django.db.models.Model):
            decl._meta.db_table = decl._meta.db_table.replace('models', appname)
            decl._meta.app_label = appname
            __all__.append(decl.__name__)
            django.db.models.loading.register_models(appname, decl)
    except:
        pass
