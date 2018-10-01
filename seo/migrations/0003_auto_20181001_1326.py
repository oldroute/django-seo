# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('seo', '0002_seotemplate'),
    ]

    operations = [
        migrations.AddField(
            model_name='seotemplate',
            name='desc_a',
            field=models.BooleanField(default=True, verbose_name='\u0430\u0432\u0442\u043e\u0433\u0435\u043d\u0435\u0440\u0430\u0446\u0438\u044f \u0442\u0435\u043a\u0441\u0442\u0430 \u0434\u043b\u044f \u043d\u043e\u0432\u044b\u0445 \u0442\u043e\u0432\u0430\u0440\u043e\u0432'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='seotemplate',
            name='keys_a',
            field=models.BooleanField(default=True, verbose_name='\u0430\u0432\u0442\u043e\u0433\u0435\u043d\u0435\u0440\u0430\u0446\u0438\u044f \u0442\u0435\u043a\u0441\u0442\u0430 \u0434\u043b\u044f \u043d\u043e\u0432\u044b\u0445 \u0442\u043e\u0432\u0430\u0440\u043e\u0432'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='seotemplate',
            name='title_a',
            field=models.BooleanField(default=True, verbose_name='\u0430\u0432\u0442\u043e\u0433\u0435\u043d\u0435\u0440\u0430\u0446\u0438\u044f \u0442\u0435\u043a\u0441\u0442\u0430 \u0434\u043b\u044f \u043d\u043e\u0432\u044b\u0445 \u0442\u043e\u0432\u0430\u0440\u043e\u0432'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='seotemplate',
            name='desc_l',
            field=models.PositiveIntegerField(default=250, verbose_name='max \u0441\u0438\u043c\u0432\u043e\u043b\u043e\u0432'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='seotemplate',
            name='keys_l',
            field=models.PositiveIntegerField(default=250, verbose_name='max \u0441\u0438\u043c\u0432\u043e\u043b\u043e\u0432'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='seotemplate',
            name='title_l',
            field=models.PositiveIntegerField(default=250, verbose_name='max \u0441\u0438\u043c\u0432\u043e\u043b\u043e\u0432'),
            preserve_default=True,
        ),
    ]
