#-*- encoding: utf-8 -*-
from django.conf.urls.defaults import patterns, url

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()
from django.conf import settings

urlpatterns = patterns('',
    # Example:
    # (r'^grnglow/', include('grnglow.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # (r'^admin/', include(admin.site.urls)),
    url(r'^static/(?P<path>.*)$', 'django.views.static.serve',
         {'document_root':settings.MEDIA_ROOT}, name="media"),#映射media文件
)

#元组是可累加的，但累加后是生成新的元组，而非在原来的基础上修改
urlpatterns += patterns('grnglow.glow.views',#第一个参数可设置公共前缀
    (r'^$', 'home.index'),#当设置公共前缀时，应使用字符串
    (r'^accounts/login/$', 'accounts.login'),
    (r'^accounts/logout/$', 'accounts.logout'),
    (r'^accounts/register/$', 'accounts.register'),
    (r'^accounts/profile/$', 'accounts.profile'),
    (r'^accounts/editavatar/$', 'accounts.editavatar'),
    (r'^accounts/editpassword/$', 'accounts.editpassword'),
)

urlpatterns += patterns('grnglow.glow.views',
    (r'^people/(?P<user_id>\d*)/$', 'people.home'),#使用命名组来给people.people_home
    #命名的正则表达式组的语法是 (?P<name>pattern) ，这里name是组的名字，而pattern是匹配的某个模式。
    #user_id是people.people_home函数中的一个参数
    (r'^people/(?P<user_id>\d*)/albums/$', 'people.albums'),
    (r'^people/(?P<user_id>\d*)/tags/$', 'people.tags'),
    (r'^people/(?P<user_id>\d*)/comments/$', 'people.comments'),
    (r'^people/(?P<user_id>\d*)/comments/mine/$', 'people.comments_mine'),
    (r'^people/(?P<user_id>\d*)/profile/$', 'people.profile'),
    (r'^people/(?P<user_id>\d*)/likes/$', 'people.likes'),
    (r'^people/(?P<user_id>\d*)/follow/$', 'people.follow'),
    (r'^people/(?P<user_id>\d*)/follow/follow_me/$', 'people.follow_me'),
    (r'^people/(?P<user_id>\d*)/follow/mark_follow/$', 'people.ajax_markFollow'),
    (r'^people/(?P<user_id>\d*)/follow/cancel_follow/$', 'people.ajax_cancelFollow'),
)

urlpatterns += patterns('grnglow.glow.views',
    (r'^photos/(?P<user_id>\d*)/albums/(?P<album_id>\d*)/$', 'albums.album'),
    (r'^photos/(?P<user_id>\d*)/albums/create/$', 'albums.create'),
    (r'^photos/(?P<user_id>\d*)/albums/(?P<album_id>\d*)/edit/$', 'albums.edit'),
    (r'^photos/(?P<user_id>\d*)/albums/(?P<album_id>\d*)/delete/$', 'albums.ajax_deleteAlbum'),
)

urlpatterns += patterns('grnglow.glow.views',
    (r'^photos/(?P<user_id>\d*)/(?P<photo_id>\d*)/$', 'photos.photo'),
    (r'^photos/(?P<user_id>\d*)/(?P<photo_id>\d*)/edit/$', 'photos.edit'),
    (r'^photos/(?P<user_id>\d*)/(?P<photo_id>\d*)/next/$', 'photos.next_photo'),
    (r'^photos/(?P<user_id>\d*)/(?P<photo_id>\d*)/prev/$', 'photos.prev_photo'),
    (r'^photos/(?P<user_id>\d*)/(?P<photo_id>\d*)/delete/$', 'photos.ajax_deletePhoto'),
    (r'^photos/(?P<user_id>\d*)/(?P<photo_id>\d*)/mark_like/$', 'photos.ajax_markLike'),
    (r'^photos/(?P<user_id>\d*)/(?P<photo_id>\d*)/cancel_like/$', 'photos.ajax_cancelLike'),
    (r'^photos/(?P<user_id>\d*)/(?P<photo_id>\d*)/add_comment/$', 'photos.ajax_addComment'),
)

urlpatterns += patterns('grnglow.glow.views',
    (r'^photos/delete_comment/$', 'photos.ajax_deleteComment'),
)

urlpatterns += patterns('grnglow.glow.views',
    (r'^photos/upload/$', 'photos.upload'),
    (r'^photos/upload/complete/$', 'photos.upload_complete'),
    (r'^photos/upload/complete/done/$', 'photos.upload_done'),
)

urlpatterns += patterns('grnglow.glow.views',
    (r'^explore/$', 'explore.hots'),
    (r'^explore/recents/$', 'explore.recents'),
    (r'^explore/hots/$', 'explore.hots'),
)

urlpatterns += patterns('grnglow.glow.views',
    (r'^search/$', 'search.default'),
)

urlpatterns += patterns('grnglow.glow.views',
    (r'^', 'error_404'),
)
