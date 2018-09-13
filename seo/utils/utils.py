# -*- coding utf-8 -*-
from django.apps import apps as django_apps
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured


def get_seogen_models():
    """
    Generator for list of registered models in seogen
    """
    SEOGEN_FOR_MODELS = getattr(settings, 'SEOGEN_FOR_MODELS', [])

    for pair in SEOGEN_FOR_MODELS:
        app_name = pair["model"]["app_name"]
        model_name = pair["model"]["name"]
        yield django_apps.get_model(app_name, model_name)


def get_child_models():
    """
    Generator for list of registered models in seogen
    """
    SEOGEN_FOR_MODELS = getattr(settings, 'SEOGEN_FOR_MODELS', [])

    for pair in SEOGEN_FOR_MODELS:
        children = pair["allowed_child_models"]
        for child in children:
            app_name = child["app_name"]
            model_name = child["name"]
        yield django_apps.get_model(app_name, model_name)


def is_child_model(item):
    model_cls = item.__class__
    for model in get_child_models():
        if model_cls == model:
            return True
    return False


def get_seo_models():
    """
    Generator for list of registered models in seo
    """
    if not hasattr(settings, 'SEO_FOR_MODELS'):
        raise ImproperlyConfigured('Please add "SEO_FOR_MODELS" to your settings.py')

    for pair in settings.SEO_FOR_MODELS:
        app_name = pair["app_name"]
        model_name = pair["name"]
        yield django_apps.get_model(app_name, model_name)

