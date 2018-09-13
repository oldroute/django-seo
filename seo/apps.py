# -*- coding:utf-8 -*-
from django.apps import AppConfig


class SeoAppConfig(AppConfig):
    name = "seo"

    def ready(self):
        import seo.signals
