# Generated by Django 2.1.13 on 2020-11-09 12:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0002_auto_20201109_1212'),
    ]

    operations = [
        migrations.AlterField(
            model_name='article',
            name='commit_num',
            field=models.IntegerField(default=0, verbose_name='评论数'),
        ),
        migrations.AlterField(
            model_name='article',
            name='down_num',
            field=models.IntegerField(default=0, verbose_name='点踩数'),
        ),
        migrations.AlterField(
            model_name='article',
            name='up_num',
            field=models.IntegerField(default=0, verbose_name='点赞数'),
        ),
    ]