"""BBS_11_09 URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, re_path
from blog import views
from django.views.static import serve
from django.conf import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('get_valid_code/', views.get_valid, name='get_valid'),
    path('home/', views.home, name='home'),
    path('comment_content/', views.comment_content, name='comment_content'),
    path('diggit/', views.diggit, name='diggit'),
    path('backend/', views.backend, name='backend'),
    path('change_pwd/', views.change_pwd, name='change_pwd'),
    path('add_article/', views.add_article, name='add_article'),
    path('update_head/', views.update_head, name='update_head'),
    re_path('^check_user/', views.check_user, name='check_user'),
    re_path('^delete/(?P<id>\d+)', views.delete, name='delete'),
    re_path('^update_article/(?P<id>\d+)', views.update_article, name='update_article'),
    re_path(r'^blogsite/(?P<name>\w+)/(?P<query>category|tag|archive)/(?P<condition>.*?).html$', views.blogsite),
    re_path(r'^blogsite/(?P<name>\w+)/$', views.blogsite,),
    re_path(r'^(?P<name>\w+)/article_detail/(?P<id>\d+).html', views.article_detail),
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT})

]
