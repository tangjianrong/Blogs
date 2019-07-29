from django import template
from blog.models import *
from django.shortcuts import render, HttpResponse, redirect
from django.db.models import Max, Min, Count


register = template.Library()


@register.simple_tag
def multi_tag(x, y):
    return x*y


@register.inclusion_tag('classification.html')
def get_data(username):
    user = UserInfo.objects.filter(username=username).first()
    blog = user.blog
    c_articles = Category.objects.filter(blog_id=blog.nid).values('title').annotate(c=Count('article__title')).values(
        'title', 'c')
    t_articles = Tag.objects.filter(blog_id=blog.nid).values('title').annotate(c=Count('article__title')).values(
        'title', 'c')
    c_t_articles = Article.objects.filter(user=user). \
        extra(select={"c_date": "date_format(create_time,'%%Y-%%m')"}). \
        values('c_date').annotate(c=Count('nid')).values('c_date', 'c')
    articles = Article.objects.filter(user=user)
    return {'blog': blog, 'user': user, 'c_articles': c_articles,
            't_articles': t_articles, 'c_t_articles': c_t_articles,
            'articles': articles, 'username': username}

