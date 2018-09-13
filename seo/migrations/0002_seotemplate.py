# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0001_initial'),
        ('seo', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='SeoTemplate',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title_t', models.TextField(null=True, verbose_name='\u0448\u0430\u0431\u043b\u043e\u043d \u0437\u0430\u0433\u043e\u043b\u043e\u0432\u043a\u0430', blank=True)),
                ('title_l', models.PositiveIntegerField(default=180, verbose_name='max \u0441\u0438\u043c\u0432\u043e\u043b\u043e\u0432')),
                ('desc_t', models.TextField(null=True, verbose_name='\u0448\u0430\u0431\u043b\u043e\u043d \u043e\u043f\u0438\u0441\u0430\u043d\u0438\u044f', blank=True)),
                ('desc_l', models.PositiveIntegerField(default=180, verbose_name='max \u0441\u0438\u043c\u0432\u043e\u043b\u043e\u0432')),
                ('keys_t', models.TextField(null=True, verbose_name='\u0448\u0430\u0431\u043b\u043e\u043d \u043a\u043b\u044e\u0447\u0435\u0432\u044b\u0445 \u0441\u043b\u043e\u0432', blank=True)),
                ('keys_l', models.PositiveIntegerField(default=180, verbose_name='max \u0441\u0438\u043c\u0432\u043e\u043b\u043e\u0432')),
                ('data', jsonfield.fields.JSONField(null=True, verbose_name='json-\u0434\u0430\u043d\u043d\u044b\u0435', blank=True)),
                ('object_id', models.PositiveIntegerField()),
                ('content_type', models.ForeignKey(to='contenttypes.ContentType')),
            ],
            options={
                'verbose_name': 'seo \u0448\u0430\u0431\u043b\u043e\u043d',
                'verbose_name_plural': 'seo \u0448\u0430\u0431\u043b\u043e\u043d\u044b',
            },
            bases=(models.Model,),
        ),
    ]
