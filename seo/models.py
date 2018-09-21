# -*- coding: utf-8 -*-

from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from jsonfield import JSONField
from django.core.urlresolvers import reverse
from django.conf import settings
from django.core.cache import cache
from seo.utils.template import resolve_template_vars


class Seo(models.Model):
    class Meta:
        verbose_name = _('SEO fields')
        verbose_name_plural = _('SEO fields')
        unique_together = (("content_type", "object_id"),)

    title = models.CharField(
        verbose_name=_('Title'),
        max_length=200,
        default='',
        blank=True
    )
    description = models.CharField(
        verbose_name=_('Description'),
        max_length=200,
        default='',
        blank=True
    )
    keywords = models.CharField(
        verbose_name=_('Keywords'),
        max_length=1000,
        default='',
        blank=True
    )

    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')

    def __unicode__(self):
        return self.title


class Url(models.Model):
    class Meta:
        verbose_name = _('URL')
        verbose_name_plural = _('URLs')

    url = models.CharField(
        verbose_name=_('URL'),
        max_length=200, default='/', unique=True,
        help_text=_("This should be an absolute path, excluding the domain name. Example: '/events/search/'.")
    )

    def get_absolute_url(self):
        return self.url

    def __unicode__(self):
        return self.url


class SeoTemplate(models.Model):

    class Meta:
        verbose_name = u"seo шаблон"
        verbose_name_plural = u"seo шаблоны"

    title_t = models.TextField(verbose_name=u"шаблон заголовка", null=True, blank=True)
    title_l = models.PositiveIntegerField(verbose_name=u"max символов", default=180)
    desc_t = models.TextField(verbose_name=u"шаблон описания", null=True, blank=True)
    desc_l = models.PositiveIntegerField(verbose_name=u"max символов", default=180)
    keys_t = models.TextField(verbose_name=u"шаблон ключевых слов", null=True, blank=True)
    keys_l = models.PositiveIntegerField(verbose_name=u"max символов", default=180)

    data = JSONField(verbose_name=u'json-данные', blank=True, null=True)

    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    def __allowed_child(self, item):

        """ Проверяет, находится ли класс обьекта item
            в списке разрешенных дочерних классов переменной settings.SEOGEN_FOR_MODELS
            возвращает True если разрешен
        """

        for obj in settings.SEOGEN_FOR_MODELS:
            if obj["model"]["name"] == self.content_object.__class__.__name__:
                for child_model in obj["allowed_child_models"]:
                    if child_model["name"] == item.__class__.__name__:
                        return True
        return False

    def get_children(self):

        """ Возвращает список mptt-дочерних элементов
            Обрабатывает 2 ситуации:
            - для моделей каталога (через промежуточную модель treeitem)
            - для mptt-моделей
        """

        children = []
        try:
            # Для каталога
            treeitem_children = self.content_object.tree.get().get_children()
            for treeitem in treeitem_children:
                content_object = treeitem.content_object
                if self.__allowed_child(content_object):
                    children.append(content_object)
        except:
            # Для mptt модлей
            raw_children = self.content_object.get_children()
            for child in raw_children:
                content_object = treeitem.content_object
                if self.__allowed_child(content_object):
                    children.append(content_object)
        return children

    def __get_text(self, metatag_name, item):

        """ Возвращает сгенерированный валидный текст метатега """

        limit = self.data[metatag_name]["limit"]
        for i in range(len(self.data[metatag_name]["list"])):
            if len(self.data[metatag_name]["list"][i]) <= limit:
                text = self.data[metatag_name]["list"].pop(i)
                text = resolve_template_vars(item, text)
                return text
        return None

    def create_data_item(self, item, need_save=True):

        """ Добавить элемент в data, назначить ему сгенерированные тексты """

        item_ct = ContentType.objects.get_for_model(item)
        item_key = "%d-%d" % (item_ct.id, item.id)

        item_app_label = item.__class__._meta.app_label
        item_class = item.__class__.__name__.lower()
        item_change_link = reverse('admin:{0}_{1}_change'.format(item_app_label, item_class), args=(item.id,))
        seo = Seo.objects.filter(content_type=item_ct, object_id=item.id).first()

        new_item = {
            "name": item.__str__(),
            "change_link": item_change_link,
            "title": {
                "seo_text": seo.title if seo else None,
                "gen_text": None if (seo and seo.title) else self.__get_text("title", item),
            },
            "desc": {
                "seo_text": seo.description if seo else None,
                "gen_text": None if (seo and seo.description) else self.__get_text("desc", item),
            },
            "keys": {
                "seo_text": seo.keywords if seo else None,
                "gen_text": None if (seo and seo.keywords) else self.__get_text("keys", item),
            },
        }
        self.data["items"][item_key] = new_item
        if need_save:
            self.save()
        return

    def remove_data_item(self, item, need_save=True):

        """ Удалить элемент из data """

        item_ct = ContentType.objects.get_for_model(item)
        item_key = "%d-%d" % (item_ct.id, item.id)
        item_data = self.data["items"].pop(item_key, None)

        if need_save:
            self.save()
        return

    def update_data_item(self, item, need_save=True):

        """ Обновить запись элемента в data (все кроме текстов по шаблону)"""

        item_ct = ContentType.objects.get_for_model(item)
        item_key = "%d-%d" % (item_ct.id, item.id)
        old_item_data = self.data["items"].get(item_key, False)
        if not old_item_data:
            return False
        else:
            item_app_label = item.__class__._meta.app_label
            item_class = item.__class__.__name__.lower()
            item_change_link = reverse('admin:{0}_{1}_change'.format(item_app_label, item_class), args=(item.id,))
            seo = Seo.objects.filter(content_type=item_ct, object_id=item.id).first()

            new_item_data = {
                "name": item.__str__(),
                "change_link": item_change_link,
                "title": {
                    "seo_text": seo.title if seo else None,
                    "gen_text": old_item_data["title"]["gen_text"]
                },
                "desc": {
                   "seo_text": seo.description if seo else None,
                   "gen_text": old_item_data["desc"]["gen_text"]
                },
                "keys": {
                   "seo_text": seo.keywords if seo else None,
                   "gen_text": old_item_data["keys"]["gen_text"]
                }
            }
            self.data["items"][item_key] = new_item_data
            if need_save:
                self.save()
            return True

    def delete_cache(self, item=None, item_key=None):

        """ Удалить seo-данные доч. элемента из кэша """

        if item_key:
            item_cache_key = "seo-%s" % item_key
        else:
            item_ct = ContentType.objects.get_for_model(item)
            item_cache_key = "seo-%d-%d" % (item_ct.id, item.id)
        cache.delete(item_cache_key)
        return

    def delete_all_cache(self):
        for item_key in self.data["items"].keys():
            self.delete_cache(item_key=item_key)

    def __str__(self):
        return ""
