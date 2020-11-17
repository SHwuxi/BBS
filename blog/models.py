from django.db import models
from django.contrib.auth.models import AbstractUser


# Create your models here.


class User(AbstractUser):
    phone = models.CharField(max_length=15, verbose_name='电话号码')
    head = models.FileField(default='head/default.png', upload_to='head/', verbose_name='头像')
    blog = models.OneToOneField(to='Blog', verbose_name='关联博客', on_delete=models.CASCADE, null=True)


class Blog(models.Model):
    site_title = models.CharField(max_length=32, verbose_name='站点标题')
    site_name = models.CharField(max_length=32, verbose_name='站点名称')
    site_style = models.CharField(max_length=32, verbose_name='站点样式')

    def __str__(self):
        return self.site_title


class Category(models.Model):
    name = models.CharField(max_length=32, verbose_name='分类名称')
    blog = models.ForeignKey(to='Blog', verbose_name='关联博客', on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(max_length=32, verbose_name='标签名称')
    blog = models.ForeignKey(to='Blog', verbose_name='关联博客', on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Article(models.Model):
    name = models.CharField(max_length=32, verbose_name='文章名称')
    description = models.CharField(max_length=128, verbose_name='文章描述')
    content = models.TextField(verbose_name='文章内容')
    create_time = models.DateTimeField(auto_now_add=True, null=True)
    up_num = models.IntegerField(verbose_name='点赞数', default=0)
    down_num = models.IntegerField(verbose_name='点踩数', default=0)
    commit_num = models.IntegerField(verbose_name='评论数', default=0)
    blog = models.ForeignKey(to='Blog', verbose_name='关联博客', on_delete=models.CASCADE, null=True)
    category = models.ForeignKey(to='Category', verbose_name='关联分类', on_delete=models.CASCADE)
    tag = models.ManyToManyField(to='Tag', verbose_name='关联标签')

    def __str__(self):
        return self.name


class Commit(models.Model):
    content = models.CharField(max_length=128, verbose_name='评论内容')
    create_time = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(to='User', verbose_name='关联用户', on_delete=models.CASCADE)
    article = models.ForeignKey(to='Article', verbose_name='关联文章', on_delete=models.CASCADE)
    commit_self = models.ForeignKey(to='self', verbose_name='子评论', on_delete=models.CASCADE, null=True)


class UpAndDown(models.Model):
    user = models.ForeignKey(to='User', verbose_name='关联用户', on_delete=models.CASCADE)
    article = models.ForeignKey(to='Blog', verbose_name='关联文章', on_delete=models.CASCADE)
    is_up = models.BooleanField(verbose_name='点赞点踩')
