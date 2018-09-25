# -*- coding: utf-8 -*-
import json
import warnings
from django import template
from django.contrib.contenttypes.models import ContentType
from django.db.models import Model
from django.utils.html import escape
from django.core.cache import cache
from seo.models import Seo, Url, SeoTemplate

register = template.Library()

DEFAULT_SEO_OBJ = {
    "title": "",
    "desc": "",
    "keys": ""
}


def seo_by_url(context):

    """ Возвращает seo-запись по url запроса (если запись привязана к url) """

    path = context['request'].path_info
    url = Url.objects.filter(url=path).first()
    if url:
        url_ct = ContentType.objects.get_for_model(url.__class__)
        seo = Seo.objects.filter(content_type=url_ct, object_id=url_ct).first()
        return {
            "title": seo.title,
            "desc": seo.description,
            "keys": seo.keywords,
        }
    else:
        return DEFAULT_SEO_OBJ


def seo_by_content_object(item, item_ct):

    """ Возвращает seo-запись """

    seo = Seo.objects.filter(content_type=item_ct, object_id=item.id).first()
    if seo:
        return {
            "title": seo.title,
            "desc": seo.description,
            "keys": seo.keywords,
        }
    else:
        return DEFAULT_SEO_OBJ


def get_metatag_data(metatag_name, item_data):

    """ Возвращает значение seo-метатега для обьекта согласно приоритету:
        1. seo-атрибут заполненный вручную
        2. seogen-атрибут заполненный автоматически
        3. пустая строка
    """

    seo_text = item_data[metatag_name]["seo_text"]
    gen_text = item_data[metatag_name]["gen_text"]
    result = ''
    if seo_text:
        result = seo_text
    elif gen_text:
        result = gen_text
    return result


def seo_by_template(item, item_ct):

    """ Возврашает seo-запись элемента по приоритету:
        1. Seo-запись из шаблона родителя (если есть родитель с seo-шаблоном)
        2. Seo-запиcь элемента
        3. Seo-запись по url (если элемент не указан)
        4. Пустая seo-запись
    """

    try:
        parent_tree = item.tree.get().parent
    except:
        parent_tree = False
    # есть родитель
    if parent_tree:
        parent = parent_tree.content_object
        parent_ct = ContentType.objects.get_for_model(parent)
        seo_template = SeoTemplate.objects.filter(content_type=parent_ct, object_id=parent.id).first()
        # у родителя есть seo-шаблон
        if seo_template:
            item_key = "%d-%d" % (item_ct.id, item.id)
            item_data = seo_template.data["items"][item_key]
            # seo-запись из шаблона
            item_seo = {
                "title": get_metatag_data("title", item_data),
                "desc": get_metatag_data("desc", item_data),
                "keys": get_metatag_data("keys", item_data)
            }

        # seo запись элемента
        else:
            item_seo = seo_by_content_object(item, item_ct)
    else:
        item_seo = seo_by_content_object(item, item_ct)

    return item_seo


def modify_seo(seo, **kwargs):

    """ Добавить префикс или установить дефолтное значение метатегам """

    if not seo["title"]:
        seo["title"] = kwargs.get("title_default", '')
    if seo["title"]:
        title_postfix = kwargs.get("title_postfix")
        if title_postfix:
            seo["title"] += title_postfix

    if not seo["desc"]:
        seo["desc"] = kwargs.get("desc_default", '')
    if seo["desc"]:
        desc_postfix = kwargs.get("desc_postfix")
        if desc_postfix:
            seo["desc"] += desc_postfix

    if not seo["keys"]:
        seo["keys"] = kwargs.get("keys_default", '')
    if seo["keys"]:
        keys_postfix = kwargs.get("keys_postfix")
        if keys_postfix:
            seo["keys"] += keys_postfix
    return seo


@register.inclusion_tag('seo/seo.html', takes_context=True)
def seo(context, item=None, **kwargs):
    item_ct = ContentType.objects.get_for_model(item)
    item_cache_key = "seo-%d-%d" % (item_ct.id, item.id)
    item_json_seo = cache.get(item_cache_key)
    if item_json_seo:
        item_seo = json.loads(item_json_seo)
    else:
        if item:
            item_seo = seo_by_content_object(item, item_ct)
        else:
            item_seo = seo_by_url(context)
        item_json_seo = json.dumps(item_seo, ensure_ascii=False)
        cache.set(item_cache_key, item_json_seo)

    return modify_seo(item_seo, **kwargs)


@register.inclusion_tag('seo/seo.html')
def seogen(item, **kwargs):

    item_ct = ContentType.objects.get_for_model(item)
    item_cache_key = "seo-%d-%d" % (item_ct.id, item.id)
    item_json_seo = cache.get(item_cache_key)
    if item_json_seo:
        item_seo = json.loads(item_json_seo)
    else:
        item_seo = seo_by_template(item, item_ct)
        item_json_seo = json.dumps(item_seo, ensure_ascii=False)
        cache.set(item_cache_key, item_json_seo)
    return modify_seo(item_seo, **kwargs)
