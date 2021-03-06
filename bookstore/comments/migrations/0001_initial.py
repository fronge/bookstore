# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2017-12-21 13:06
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('users', '0002_auto_20171221_1259'),
        ('books', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Comments',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_delete', models.BooleanField(default=False, verbose_name='逻辑删除')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('show', models.BooleanField(default=True, verbose_name='显示评论')),
                ('content', models.CharField(max_length=1000, verbose_name='评论内容')),
                ('book', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='books.Books')),
                ('passport', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.Passport')),
            ],
            options={
                'db_table': 's_comments',
            },
        ),
    ]
