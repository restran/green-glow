#-*- encoding: utf-8 -*-
# Django settings for grnglow project.
import os

DEBUG = True
TEMPLATE_DEBUG = DEBUG

HOME_PAGE_URL = 'http://www.grnglow.com/'#主页的URL
LOCAL_SITE_NAME = u'福州'#当前站
REMOTE_SITE_URL = 'http://192.168.174.140:80'
PROJECT_PATH = os.path.abspath(os.path.dirname(__file__))#项目的根目录地址
DEFAULT_CHARSET = 'utf-8'

ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'grnglow',                      # Or path to database file if using sqlite3.
        'USER': 'root',                      # Not used with sqlite3.
        'PASSWORD': 'root',                  # Not used with sqlite3.
        'HOST': '127.0.0.1',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '3306',                      # Set to empty string for default. Not used with sqlite3.
    },
    'remote': {
        'NAME': 'grnglow',
        'ENGINE': 'django.db.backends.mysql',
        'USER': 'root',
        'PASSWORD': 'root',
        'HOST': '192.168.174.140',
        'PORT': '3306', 
    },
}

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Asia/Shanghai'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = os.path.join(PROJECT_PATH,'static')
MEDIA_PARENT_PATH = PROJECT_PATH.replace('\\', '/')
PHOTOS_RELATIVE_PATH = '/static/photos/'#上传图片保存的目录相对于站点的路径
UPLOAD_PHOTOS_PATH = (os.path.join(MEDIA_ROOT, 'photos')).replace('\\', '/') + '/'#上传图片保存的目录
UPLOAD_AVATAR_PATH = (os.path.join(MEDIA_ROOT, 'avatars')).replace('\\', '/') + '/'#上传头像保存的目录
AVATAR_RELATIVE_PATH = '/static/avatars/'#头像存放位置的相对路径
DEFAULT_AVATAR_LOC = AVATAR_RELATIVE_PATH + 'avatar_default.gif'
DEFAULT_AVATAR_SQUARE_LOC = AVATAR_RELATIVE_PATH + 'avatar_default_square.gif'

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = 'http://www.grnglow.com/static/'

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = 'http://www.grnglow.com/static/admin/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'ztq6&uyn0y%ny-+ur38_5s3-1dc&=y@-3-&0npfyog9**62589'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.middleware.csrf.CsrfResponseMiddleware',
    #'django.contrib.auth.middleware.AuthenticationMiddleware',
    #'django.contrib.messages.middleware.MessageMiddleware',
    'grnglow.glow.auth.middleware.AuthenticationMiddleware',
    'django.middleware.locale.LocaleMiddleware',#加上这条，让admin支持本地语言
)

ROOT_URLCONF = 'grnglow.urls'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

INSTALLED_APPS = (
    #'django.contrib.auth',
    #'django.contrib.contenttypes',
    'django.contrib.sessions',
    #'django.contrib.sites',
    #'django.contrib.messages',
    # Uncomment the next line to enable the admin:
    # 'django.contrib.admin',
    # Uncomment the next line to enable admin documentation:
    # 'django.contrib.admindocs',
    'glow',
    #'south',
)
