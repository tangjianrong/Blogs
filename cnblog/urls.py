"""cnblog URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
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
from cnblog import settings


urlpatterns = [
    path('admin/', admin.site.urls),
    path(r'index/', views.index),
    re_path(r'^$', views.index),    # 直接访问首页
    path(r'login/', views.login),   # 登录
    path(r'get_validcode_img/', views.get_validcode_img),   # 获取验证码
    path(r'register/', views.register),   # 注册
    path(r'logout/', views.logout),     # 注销
    path('digg/', views.digg),     # 点赞
    path('comment/', views.comment),     # 评论
    path('get_comment_tree/', views.get_comment_tree),  # 获取评论树
    re_path(r'^(?P<username>\w+)/backend/$', views.backend),  # 后台管理
    path('article_del/', views.article_del),  # 文章删除
    re_path(r'^(?P<article_id>\d+)/article_edit/', views.article_edit),  # 文章编辑
    path('article_update/', views.article_update),    # 文章编辑后保存
    re_path('add_article/', views.add_article),    # 添加文章
    path('upload/', views.upload),  # 文件上传

    # media配置
    re_path(r'media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),

    # 个人站点url
    re_path(r'^(?P<username>\w+)/$', views.home_site),
    # 个人站点跳转
    re_path('^(?P<username>\w+)/(?P<condition>tag|category|archive)/(?P<param>.*)/$', views.home_site),
    # 文章详情页
    re_path(r'^(?P<username>\w+)/article/(?P<article_id>\d+)$', views.article_detail),
]


