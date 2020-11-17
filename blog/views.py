import random
import json
import os
from django.shortcuts import render, HttpResponse, redirect, reverse
from blog import blogform, models, utils
from django.http import JsonResponse
from PIL import Image, ImageFont, ImageDraw
from io import BytesIO
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.db.models import Count, F
from django.db import transaction
from bs4 import BeautifulSoup
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings


# Create your views here.
def check_user(request):
    dic = {'code': 100, 'msg': '用户名合格'}
    username = request.GET.get('name')
    print(username)
    user = models.User.objects.filter(username=username).count()
    if user:
        dic['code'] = 101
        dic['msg'] = '该用户已存在'
    return JsonResponse(dic)


def register(request):
    if request.method == 'GET':
        form = blogform.UserForm()
        return render(request, 'register.html', {'form': form})
    else:
        dic = {'code': 100, 'msg': '创建成功'}
        form = blogform.UserForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            file = request.FILES.get('head')
            user = models.User.objects.filter(username=data.get('username')).count()
            if user:
                dic['code'] = 102
                dic['msg'] = '用户已存在'
            else:
                if file:
                    data['head'] = file
                data.pop('re_password')
                models.User.objects.create_user(**data)
                dic['url'] = reverse('login')
        else:
            dic['code'] = 101
            dic['error'] = form.errors
        return JsonResponse(dic)


def get_rgb():
    return (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))


def get_valid(request):
    img = Image.new('RGB', (160, 50), (255, 255, 255))
    img_draw = ImageDraw.Draw(img)
    img_font = ImageFont.truetype('./static/font/stratum2black.otf', 40)
    valid_code = ''
    for i in range(5):
        low_chr = chr(random.randint(97, 122))
        num = random.randint(0, 9)
        upper_chr = chr(random.randint(65, 90))
        res = str(random.choice([low_chr, num, upper_chr]))
        valid_code += res
        img_draw.text((i * 30 + 10, 8), res, get_rgb(), img_font)
    #  随机验证码存到session里
    request.session['valid_code'] = valid_code
    # 画线和点圈
    width = 160
    height = 50
    for i in range(3):
        x1 = random.randint(0, width)
        x2 = random.randint(0, width)
        y1 = random.randint(0, height)
        y2 = random.randint(0, height)
        # 在图片上画线
        img_draw.line((x1, y1, x2, y2), fill=get_rgb())

    for i in range(50):
        # 画点
        img_draw.point([random.randint(0, width), random.randint(0, height)], fill=get_rgb())
        x = random.randint(0, width)
        y = random.randint(0, height)
        # 画弧形
        img_draw.arc((x, y, x + 4, y + 4), 0, 90, fill=get_rgb())
    # 验证码写到内存，不写到硬盘
    f = BytesIO()
    img.save(f, 'png')
    #  读取内存中图片的二进制，传到前端
    data = f.getvalue()
    return HttpResponse(data)


def login(request):
    if request.method == 'GET':
        return render(request, 'login.html')
    else:
        dic = {'code': 100, 'msg': ''}
        username = request.POST.get('username')
        password = request.POST.get('password')
        valid_code = request.POST.get('valid_code')
        print(valid_code)
        if valid_code.lower() == request.session.get('valid_code').lower():
            user = auth.authenticate(username=username, password=password)
            if user:
                auth.login(request, user)
                dic['url'] = reverse('home')
            else:
                dic['code'] = 101
                dic['msg'] = '用户名或密码错误'
        else:
            dic['code'] = 102
            dic['msg'] = '验证码错误'
        return JsonResponse(dic)


def logout(request):
    if request.user.is_authenticated:
        auth.logout(request)
        return redirect(reverse('home'))


def change_pwd(request):
    dic = {'code': 100, 'message': ''}
    if request.is_ajax():
        old_pwd = request.POST.get('old_pwd')
        new_pwd = request.POST.get('new_pwd')
        re_new_pwd = request.POST.get('re_new_pwd')
        if request.user.check_password(old_pwd):
            if new_pwd == re_new_pwd:
                request.user.set_password(new_pwd)
                dic['message'] = '修改成功'
                dic['url'] = reverse('login')
            else:
                dic['code'] = 101
                dic['message'] = '两次密码不一致'
        else:
            dic['code'] = 102
            dic['message'] = '旧密码不正确'
        return JsonResponse(dic)


def home(request):
    if request.method == 'GET':
        ll = [{'url': 'http://www.baidu.com',
               'img_url': '/static/img/banner1.jpg',
               'message': '火热广告招商'},
              {'url': 'http://www.bilibili.com',
               'img_url': '/static/img/banner2.jpg',
               'message': '体验游戏人生'},
              {'url': 'http://www.xiaomi.com',
               'img_url': '/static/img/banner3.jpg',
               'message': '点我有你好看'},
              ]
        article_list = models.Article.objects.all().order_by('-create_time')
        current_page = request.GET.get('page', 1)
        all_count = article_list.count()
        page_obj = utils.Pagination(current_page=current_page, all_count=all_count, per_page_num=2)
        page_queryset = article_list[page_obj.start:page_obj.end]
        return render(request, 'home.html', {'page_obj': page_obj, 'page_queryset': page_queryset, 'll': ll})


def blogsite(request, name, **kwargs):
    if request.method == 'GET':
        user = models.User.objects.filter(username=name).first()
        if user:
            article_list = models.Article.objects.filter(blog=user.blog)
            query = kwargs.get('query')
            condition = kwargs.get('condition')
            if query == 'category':
                article_list = models.Article.objects.filter(category_id=condition)
            elif query == 'tag':
                article_list = models.Article.objects.filter(tag__id=condition)
            elif query == 'archive':
                year, month = kwargs.get('condition').split('/')
                article_list = models.Article.objects.filter(create_time__year=year, create_time__month=month)
            current_page = request.GET.get('page', 1)
            all_count = article_list.count()
            page_obj = utils.Pagination(current_page=current_page, all_count=all_count, per_page_num=2)
            page_queryset = article_list[page_obj.start:page_obj.end]
            return render(request, 'blogsite.html', locals())
        else:
            return HttpResponse('404')


def article_detail(request, name, id):
    if request.method == 'GET':
        user = models.User.objects.filter(username=name).first()
        if user:
            article = models.Article.objects.get(id=id)
            commit_list = models.Commit.objects.filter(user_id=user.id)
            return render(request, 'article_detail.html',
                          {'user': user, 'article': article, 'commit_list': commit_list})


def diggit(request):
    if request.is_ajax():
        dic = {'code': 100, 'msg': ''}
        if request.user.is_authenticated:
            is_up = json.loads(request.POST.get('is_up'))
            article_id = request.POST.get('article_id')
            user = request.user
            res = models.UpAndDown.objects.filter(article_id=article_id, user_id=user.id).count()
            if res:
                dic['code'] = 102
                dic['msg'] = '已评论，无法再次评论'
            else:
                with transaction.atomic():
                    models.UpAndDown.objects.create(is_up=is_up, article_id=article_id, user_id=user.id)
                    if is_up:
                        models.Article.objects.filter(id=article_id).update(up_num=F('up_num') + 1)
                        dic['msg'] = '点赞成功'
                    else:
                        models.Article.objects.filter(id=article_id).update(down_num=F('down_num') + 1)
                        dic['msg'] = '点踩成功'
        else:
            dic['code'] = 101
            dic['msg'] = '请先<a href="/login/">登录</a>'
        return JsonResponse(dic)


def comment_content(request):
    dic = {'code': 100, 'msg': ''}
    if request.is_ajax():
        if request.user.is_authenticated:
            content = request.POST.get('commit')
            article_id = request.POST.get('article_id')
            parent_id = request.POST.get('parent_id')
            # if not parent_id:
            #     parent_id = 'Null'
            user = request.user
            with transaction.atomic():
                if parent_id:
                    commits = models.Commit.objects.create(article_id=article_id, user_id=user.id, content=content,
                                                       commit_self_id=parent_id)
                else:
                    commits = models.Commit.objects.create(article_id=article_id, user_id=user.id, content=content)
                models.Article.objects.filter(id=article_id).update(commit_num=F('commit_num') + 1)
            dic['content'] = commits.content
            dic['msg'] = '评论成功'
            dic['username'] = user.username
            if parent_id:
                dic['parent_name'] = commits.commit_self.user.username
    else:
        dic['code'] = 101
        dic['msg'] = '请先<a href="/login/">登录</a>'
    return JsonResponse(dic)


@login_required
def backend(request):
    if request.method == 'GET':
        if request.user.is_authenticated:
            article_list = models.Article.objects.filter(blog=request.user.blog)
            current_page = request.GET.get('page', 1)
            all_count = article_list.count()
            page_obj = utils.Pagination(current_page=current_page, all_count=all_count, per_page_num=2)
            page_queryset = article_list[page_obj.start:page_obj.end]
            return render(request, 'backend/backend.html', locals())


@login_required
def add_article(request):
    if request.method == 'GET':
        category_list = models.Category.objects.filter(blog=request.user.blog)
        tag_list = models.Tag.objects.filter(blog=request.user.blog)
        return render(request, 'backend/add_article.html', locals())
    else:
        name = request.POST.get('name')
        content = request.POST.get('content')
        category_id = request.POST.get('category')
        description = content[:20]
        tag_list = request.POST.getlist('tag')
        soup = BeautifulSoup(content, 'html.parser')
        description = soup.text[:30]
        res_script = soup.find_all('script')
        for script in res_script:
            script.decompose()
        article = models.Article.objects.create(name=name, content=str(soup), category_id=category_id,
                                                blog=request.user.blog,
                                                description=description)
        article.tag.add(tag_list)
        return redirect(reverse('backend'))


@csrf_exempt
def upload_img(request):
    dic = {'error': 0}
    try:
        file = request.FILES.get('myfile')
        path = os.path.join(settings.BASE_DIR, 'media', 'img', file.name)
        with open(path, 'wb') as f:
            for line in file.chunks():
                f.write(line)
        dic['url'] = '/media/img' + file.name
    except Exception as e:
        dic['error'] = 1
        dic['message'] = str(e)
    return JsonResponse(dic)


@login_required
def update_head(request):
    if request.method == 'GET':
        return render(request, 'backend/update_head.html')
    else:
        file = request.FILES.get('myhead')
        models.User.objects.filter(id=request.user.id).update(head=file)
        return redirect(reverse('backend'))


@login_required
def delete(request, id):
    models.Article.objects.filter(id=id).delete()
    return redirect(reverse('backend'))


@login_required
def update_article(request, id):
    article = models.Article.objects.get(id=id)
    if request.method == 'GET':
        category_list = models.Category.objects.filter(blog=request.user.blog)
        tag_list = models.Tag.objects.filter(blog=request.user.blog)
        return render(request, 'backend/update_article.html', locals())
    else:
        name = request.POST.get('name')
        content = request.POST.get('content')
        category_id = request.POST.get('category')
        description = content[:20]
        tag_list = request.POST.getlist('tag')
        if len(tag_list) < 2:
            tag_list = request.POST.get('tag')
        soup = BeautifulSoup(content, 'html.parser')
        description = soup.text[:30]
        res_script = soup.find_all('script')
        for script in res_script:
            script.decompose()
        article.name = name
        article.content = content
        article.category_id = category_id
        article.description = str(soup)
        article.tag.clear()
        article.tag.add(*tag_list)
        article.save()
        return redirect(reverse('backend'))
