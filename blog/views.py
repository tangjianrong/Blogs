from django.shortcuts import render, HttpResponse, redirect
from django.http import JsonResponse
from django.db.models import Count
from django.db.models import F
from django.db import transaction
from bs4 import BeautifulSoup
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
import json
from cnblog.settings import *
from django.contrib import auth
from blog.utils.validCode import get_validCode_img
from blog.Userforms import User
from blog.models import *


def index(request):     # 首页
    """
    首页
    :param request:
    :return:
    """
    articles = Article.objects.all()
    return render(request, 'index.html', locals())


def get_data(request, username):
    """
    取用户对象user,博客对象blog,c_articles,t_articles,c_t_articles,articles
    :param request:
    :param username:
    :return:
    """
    user = UserInfo.objects.filter(username=username).first()  # 当前对象
    print('user', user)
    if not user:  # 判断是否已经存在
        return render(request, 'not_exit.html', locals())
    # 当前站点对象
    blog = user.blog
    # 查询当前站点的每一个分类名称以及对应文章数
    c_articles = Category.objects.filter(blog_id=blog.nid).values('title').annotate(c=Count('article__title')).values(
        'title', 'c')
    # 查询当前站点的每一个标签名称以及对应文章数
    t_articles = Tag.objects.filter(blog_id=blog.nid).values('title').annotate(c=Count('article__title')).values(
        'title', 'c')
    # 查询当前站点每一个年月以及对应文章数
    c_t_articles = Article.objects.filter(user=user). \
        extra(select={"c_date": "date_format(create_time,'%%Y-%%m')"}). \
        values('c_date').annotate(c=Count('nid')).values('c_date', 'c')
    articles = Article.objects.filter(user=user)
    return user,c_articles,t_articles,c_t_articles,articles,blog


@login_required
def home_site(request, username, **kwargs):     # 第三个形参是以字典形式接受多个参数
    """
    个人站点
    :param request:
    :param username:
    :return:
    """
    if username == request.user.username:
        user, c_articles, t_articles, c_t_articles, articles, blog = get_data(request, username)
        if kwargs:      # 个人站点跳转
            condition = kwargs['condition']
            param = kwargs['param']
            if condition == 'category':
                articles = Article.objects.filter(user=user).filter(category__title=param)
            if condition == 'tag':
                articles = Article.objects.filter(user=user).filter(tags__title=param)
            if condition == 'archive':
                year, month = param.split('-')
                articles = Article.objects.filter(user=user)\
                    .filter(create_time__year=year, create_time__month=month)   # USE_TZ = False
        return render(request, 'home_site.html', locals())
    else:
        return redirect('/login/')


def article_detail(request, username, article_id):
    """
    文章详情页
    :param request:
    :param username:
    :param article_id:
    :return:
    """
    article_obj = Article.objects.filter(nid=article_id).first()
    comments = Comment.objects.filter(article_id=article_id)
    return render(request, 'article_detail.html', locals())


def digg(request):
    """
    点赞
    :param request:
    :return:
    """
    is_up = json.loads(request.POST.get('is_up'))   # 反序列化
    user_id = request.user.pk
    article_id = request.POST.get('article_id')
    obj = ArticleUpDown.objects.filter(user_id=user_id, article_id=article_id).first()
    response = {'state': False, 'msg': None}
    if not obj:     # 该用户没对本文章进行操作
        ArticleUpDown.objects.create(is_up=is_up, article_id=article_id, user_id=user_id)
        queryset = Article.objects.filter(pk=article_id)
        if is_up:   # 更新文章的数据
            queryset.update(up_count=F('up_count')+1)
        else:
            queryset.update(down_count=F('down_count')+1)
    else:
        response['state'] = True
        if obj.is_up:
            response['msg'] = '您已经点赞过！'
        else:
            response['msg'] = '您已经点踩过！'
    return JsonResponse(response)


def comment(request):
    article_id = request.POST.get('article_id')
    pid = request.POST.get('pid')
    content = request.POST.get('content')
    user_id = request.user.pk
    # 事务操作，必须同时成功，同时失败
    with transaction.atomic():
        ret = Comment.objects.create(user_id=user_id, content=content,
                                article_id=article_id, parent_comment_id=pid)
        Article.objects.filter(nid=article_id).update(comment_count=F('comment_count')+1)
    # 构件根评论添加时所需数据
    response = {}
    response['create_time'] = ret.create_time.strftime("%Y-%m-%d %X")
    response['username'] = request.user.username
    response['content'] = ret.content
    article_obj = Article.objects.filter(nid=article_id).first()
    # 给该文章作者发送邮件，通知其有人评论
    from cnblog.settings import EMAIL_HOST_USER
    import threading
    # send_mail(
    #     "您的文章%s新增了一条评论内容"%article_obj.title,  # 提示信息
    #     content,    # 邮件内容
    #     EMAIL_HOST_USER,    # 发送方
    #     ['1938235331@qq.com']   # 接收方
    # )
    t = threading.Thread(target=send_mail, args=(   # 开启线程，节省时间
        "您的文章%s新增了一条评论内容" % article_obj.title,
        content,
        EMAIL_HOST_USER,
        ['1938235331@qq.com']
    ))
    t.start()
    return JsonResponse(response)


def get_comment_tree(request):
    article_id = request.GET.get('article_id')
    # 转换成数组
    ret = list(Comment.objects.filter(article_id=article_id).values('pk', 'content', 'parent_comment__nid'))
    return JsonResponse(ret, safe=False)    # 传列表，需改成false


def backend(request, username):
    # 当前用户文章列表
    username = username
    print(username+'456789')
    article_list = Article.objects.filter(user__username=username)
    return render(request, 'backend.html', locals())


def article_del(request):
    """
    删除文章
    :param request:
    :return:
    """
    username = request.POST.get('username')
    article_id = request.POST.get('article_id')
    Article.objects.filter(pk=article_id).delete()
    Comment.objects.filter(article_id=article_id).delete()
    return HttpResponse('删除成功！')


def article_edit(request, article_id):
    """
    编辑修改某一篇文章
    :param request:
    :return:
    """
    article_id = article_id
    article_obj = Article.objects.filter(nid=article_id).first()
    return render(request, 'article_edit.html', locals())


def article_update(request):
    username = request.user.username
    if request.method == 'POST':
        article_id = request.POST.get('article_id')
        title = request.POST.get('title')
        content = request.POST.get('content')
        print('content', content)
        # 提取文章描述信息desc
        soup = BeautifulSoup(content, 'html.parser')
        for tag in soup.find_all():
            if tag.name == 'script':
                tag.decompose()     # 删除非法信息，防止xss攻击
        desc = soup.text[0:150] +''   # 只提取150个字节的文本信息
        Article.objects.filter(nid=article_id).update(title=title, content=content, user=request.user, desc=desc)
        return redirect('/%s/backend/' % username)
    return render(request, 'add_article.html', locals())


@login_required
def add_article(request):
    username = request.user.username
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        print('content', content)
        # 提取文章描述信息desc
        soup = BeautifulSoup(content, 'html.parser')
        for tag in soup.find_all():
            if tag.name == 'script':
                tag.decompose()     # 删除非法信息，防止xss攻击
        desc = soup.text[0:150] +''   # 只提取150个字节的文本信息
        Article.objects.create(title=title, content=content, user=request.user, desc=desc)
        return redirect('/%s/backend/' % username)
    return render(request, 'add_article.html', locals())


def upload(request):
    """
    文章的图片上传
    :param request:
    :return:
    """
    img = request.FILES.get('upload_img')   # 读取上传的文件
    path = os.path.join(MEDIA_ROOT, 'article_imgs', img.name)   # 保存到的路径
    with open(path, 'wb') as f:     # 保存
        for i in img:
            f.write(i)
    response = {
        'error': 0,
        'url': '/media/article_imgs/%s' % img.name      # 返回图片地址，可以在编辑框预览
    }
    return HttpResponse(json.dumps(response))


def logout(request):    # 注销
    auth.logout(request)
    return redirect('/index/')


def login(request):     # 登录
    if request.method == 'POST':
        user = request.POST.get('user')
        pwd = request.POST.get('pwd')
        validcode = request.POST.get('validcode')   # 浏览器提交的
        valid_code = request.session.get('valid_code')      # 保存在服务器的
        resopnse = {'user': None, 'msg': None}
        if validcode.upper() == valid_code.upper():     # 首先校验验证码，验证码不区分大小写
            ret = auth.authenticate(username=user, password=pwd)
            if ret:     # 用户存在
                auth.login(request, ret)    # 当前登录对象
                resopnse['user'] = user
            else:
                resopnse['msg'] = 'username or password is wromg!'
        else:
            resopnse['msg'] = 'valid code error!'
        return JsonResponse(resopnse)
    return render(request, 'login.html')


def get_validcode_img(request):  # 生成随机验证码
    data = get_validCode_img(request)
    return HttpResponse(data)


def register(request):
    """
    注册页面
    :param request:
    :return:
    """
    if request.method == 'POST':    # 或者if request.is_ajax 进行判断
        form = User(request.POST)   # 验证是否合要求
        response = {'user': None, 'msg': None}
        if form.is_valid():     # 信息正确，增加注册用户
            response['user'] = form.cleaned_data.get('user')
            user = form.cleaned_data.get('user')
            pwd = form.cleaned_data.get('pwd')
            email = form.cleaned_data.get('email')
            head_obj = request.FILES.get('avatar')    # 文件提取
            extra = {}                                  # 额外传的数据都打包成字典
            if head_obj:
                extra['avatar'] = head_obj
            UserInfo.objects.create_user(username=user, password=pwd, email=email, **extra)
        else:
            response['msg'] = form.errors
        return JsonResponse(response)   # Ajax接受JSON文件
    else:
        form = User()
        return render(request, 'reg.html', locals())







