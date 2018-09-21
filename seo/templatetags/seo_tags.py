# -*- coding: utf-8 -*-
import json
import warnings
from django import template
from django.contrib.contenttypes.models import ContentType
from django.db.models import Model
from django.utils.html import escape
from django.core.cache import cache
from seo.models import Seo, Url, SeoTemplate

INTENTS = ['title', 'keywords', 'description', ]

register = template.Library()

class SeoNode(template.Node):
    def __init__(self, intent, object, variable):
        self.intent = intent
        self.object = object
        self.variable = variable

    def _process_var_argument(self, context, seo):
        if self.variable is None:
            return escape(getattr(seo, self.intent, u''))
        else:
            context[self.variable] = getattr(seo, self.intent, None)
            return u''

    def _seo_by_url(self, context):
        try:
            request = context['request']
        except KeyError:
            warnings.warn('`request` was not found in context. Add "django.core.context_processors.request" to `TEMPLATE_CONTEXT_PROCESSORS` in your settings.py.')
            return self._process_var_argument(context, None)
        else:
            try:
                object = Url.objects.get(url=request.path_info)
            except Url.DoesNotExist:
                return self._process_var_argument(context, None)
            else:
                try:
                    seo = Seo.objects.get(
                        content_type=ContentType.objects.get_for_model(
                                object.__class__),
                        object_id=object.id)
                except Seo.DoesNotExist:
                    return self._process_var_argument(context, None)
                else:
                    return self._process_var_argument(context, seo)

    def _seo_by_content_object(self, context):
        object = template.Variable(self.object).resolve(context)
        if not isinstance(object, Model):
            return self._process_var_argument(context, None)

        try:
            seo = Seo.objects.get(
                content_type=ContentType.objects.get_for_model(
                        object.__class__),
                object_id=object.id)
        except Seo.DoesNotExist:
            return self._seo_by_url(context)
        else:
            return self._process_var_argument(context, seo)

    def render(self, context):
        if self.object is None:
            # search by URL
            return self._seo_by_url(context)
        else:
            # Try to retrieve object from context
            return self._seo_by_content_object(context)


def seo_tag(parser, token):
    """Get seo data for object"""
    splited = token.split_contents()
    if splited[1] in INTENTS:
        if len(splited) in [4, 6] and splited[2] == 'for':
            if len(splited) == 4:
                return SeoNode(splited[1], splited[3], None)
            elif splited[4] == 'as':
                return SeoNode(splited[1], splited[3], splited[5])
        elif len(splited) in [2, 4]:
            if len(splited) == 2:
                return SeoNode(splited[1], None, None)
            elif splited[2] == 'as':
                return SeoNode(splited[1], None, splited[3])
    raise template.TemplateSyntaxError, "Invalid syntax. Use ``{% seo <title|keywords|description> [for <object>] [as <variable>] %}``"
register.tag('seo', seo_tag)


def get_metatag_data(metatag_name, item_data):
    metatag_data = item_data[metatag_name]["seo_text"]
    if not metatag_data:
        metatag_data = item_data[metatag_name]["gen_text"]
    if not metatag_data:
        metatag_data = ''
    return metatag_data


@register.inclusion_tag('seo/seo.html')
def seogen(item):
    item_ct = ContentType.objects.get_for_model(item)
    item_cache_key = "seo-%d-%d" % (item_ct.id, item.id)
    item_json_seo = cache.get(item_cache_key)
    if item_json_seo:
        item_seo = json.loads(item_json_seo)
    else:
        parent_tree = item.tree.get().parent
        if parent_tree:
            parent = parent_tree.content_object
            parent_ct = ContentType.objects.get_for_model(parent)
            seo_template = SeoTemplate.objects.filter(content_type=parent_ct, object_id=parent.id).first()
            if seo_template:
                item_key = "%d-%d" % (item_ct.id, item.id)
                item_data = seo_template.data["items"][item_key]

                item_seo = {
                    "title": get_metatag_data("title", item_data),
                    "desc": get_metatag_data("desc", item_data),
                    "keys": get_metatag_data("keys", item_data)
                }
            else:
                item_seo = {
                    "title": "",
                    "desc": "",
                    "keys": ""
                }

            item_json_seo = json.dumps(item_seo, ensure_ascii=False)
            cache.set(item_cache_key, item_json_seo)

    return item_seo
