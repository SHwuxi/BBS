from django.template import library
from blog import models
from django.db.models import Count
from django.db.models.functions import TruncMonth

register = library.Library()


@register.inclusion_tag('left.html')
def left(name):
    user = models.User.objects.filter(username=name).first()
    category_list = models.Category.objects.filter(blog=user.blog).annotate(num=Count('article__id')).values_list(
        'name',
        'num',
        'id')
    tag_list = models.Tag.objects.filter(blog=user.blog).annotate(num=Count('article__id')).values_list('name', 'num',
                                                                                                        'id')
    month_list = models.Article.objects.filter(blog=user.blog).annotate(month=TruncMonth('create_time')).values(
        'month').annotate(num=Count('pk')).order_by('-month').values_list('month', 'num')
    return {'name': name, 'category_list': category_list, 'tag_list': tag_list, 'month_list': month_list}


@register.inclusion_tag('backend/backleft.html')
def backleft(request):
    res_category = models.Category.objects.filter(blog=request.user.blog).annotate(num=Count('article__id')).values_list(
        'name', 'num', 'id')
    name = request.user.username
    return {'res_category': res_category, 'name': name}