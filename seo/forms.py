# -*- coding: utf-8 -*-
import itertools
from collections import OrderedDict
from django import forms
from django.forms import widgets
from django.core.urlresolvers import reverse
from django.contrib.contenttypes.models import ContentType
from seo.models import Seo, SeoTemplate
from seo.utils.template import resolve_template_vars
from seo.utils.parser import SeoGenerator
from seo.utils.utils import get_seo_metatag_name
from seo.widgets import ReportWidget


class SeoForm(forms.ModelForm):
    class Meta:
        model = Seo
        fields = '__all__'

    title = forms.CharField(
        required=not Seo._meta.get_field('title').blank,
        widget=forms.Textarea(attrs={'cols': '120', 'rows': '2'}),
        label=Seo._meta.get_field('title').verbose_name,
        initial=Seo._meta.get_field('title').default,
        help_text=Seo._meta.get_field('title').help_text,
        max_length=Seo._meta.get_field('title').max_length,
    )
    description = forms.CharField(
        required=not Seo._meta.get_field('description').blank,
        widget=forms.Textarea(attrs={'cols': '120', 'rows': '2'}),
        label=Seo._meta.get_field('description').verbose_name,
        initial=Seo._meta.get_field('description').default,
        help_text=Seo._meta.get_field('description').help_text,
        max_length=Seo._meta.get_field('description').max_length,
    )
    keywords = forms.CharField(
        required=not Seo._meta.get_field('keywords').blank,
        widget=forms.Textarea(attrs={'cols': '120', 'rows': '5'}),
        label=Seo._meta.get_field('keywords').verbose_name,
        initial=Seo._meta.get_field('keywords').default,
        help_text=Seo._meta.get_field('keywords').help_text,
        max_length=Seo._meta.get_field('keywords').max_length,
    )


class SeoTemplateAdminForm(forms.ModelForm):

    PASS = 0
    APPLY_TEXTS = 1
    GENERATE_TEXTS = 2
    ClEAR_TEXTS = 3

    OPERATIONS = (
        (GENERATE_TEXTS, u'Сгенерировать тексты'),
        (APPLY_TEXTS, u'Применить тексты'),
        (ClEAR_TEXTS, u'Удалить тексты заполненные вручную'),
    )

    APPLY_FOR_FREE = 0
    APPLY_FOR_ALL = 1

    APPLY_TYPES = (
        (APPLY_FOR_FREE, u'Свободным'),
        (APPLY_FOR_ALL, u'Всем'),
    )

    class Meta:
        model = SeoTemplate
        fields = '__all__'

        widgets = {
            "title_t": forms.Textarea(attrs={"cols": 120, "rows": 2}),
            "desc_t": forms.Textarea(attrs={"cols": 120, "rows": 2}),
            "keys_t": forms.Textarea(attrs={"cols": 120, "rows": 2}),
            "data": forms.Textarea(attrs={"cols": 2000, "rows": 50}),
        }

    class Media:
        css = {'all': (
            '//code.jquery.com/ui/1.12.0/themes/smoothness/jquery-ui.min.css',
            'seo/admin/css/seogen.css',

        )}
        js = (
            '//code.jquery.com/jquery-3.3.1.min.js',
            '//code.jquery.com/ui/1.12.0/jquery-ui.min.js',
            '//cdnjs.cloudflare.com/ajax/libs/jquery-browser/0.1.0/jquery.browser.min.js',
            '//tablesorter.ru/jquery.tablesorter.min.js',
            'seo/admin/js/seogen.js',
        )

    title_operation = forms.MultipleChoiceField(
        choices=OPERATIONS, required=False, label="",
        widget=widgets.CheckboxSelectMultiple(attrs={"class": "operation"}),
    )
    title_apply_type = forms.ChoiceField(
        choices=APPLY_TYPES, initial=APPLY_FOR_FREE, required=False,
        label="", widget=forms.RadioSelect(attrs={"class": "apply_type"}),
    )
    title_apply_is_cycled = forms.BooleanField(
        label=u"Циклически", initial=False, required=False,
        widget=forms.CheckboxInput(attrs={"class": "apply_is_cycled"}),
    )
    title_report = forms.CharField(required=False, widget=ReportWidget())

    desc_operation = forms.MultipleChoiceField(
        choices=OPERATIONS, required=False, label="",
        widget=widgets.CheckboxSelectMultiple(attrs={"class": "operation"}),
    )
    desc_apply_type = forms.ChoiceField(
        choices=APPLY_TYPES, initial=APPLY_FOR_FREE, required=False,
        label="", widget=forms.RadioSelect(attrs={"class": "apply_type"}),
    )
    desc_apply_is_cycled = forms.BooleanField(
        label=u"Циклически", initial=False, required=False,
        widget=forms.CheckboxInput(attrs={"class": "apply_is_cycled"}),
    )
    desc_report = forms.CharField(required=False, widget=ReportWidget())

    keys_operation = forms.MultipleChoiceField(
        choices=OPERATIONS, required=False, label="",
        widget=widgets.CheckboxSelectMultiple(attrs={"class": "operation"}),
    )
    keys_apply_type = forms.ChoiceField(
        choices=APPLY_TYPES, initial=APPLY_FOR_FREE, required=False,
        label="", widget=forms.RadioSelect(attrs={"class": "apply_type"}),
    )
    keys_apply_is_cycled = forms.BooleanField(
        label=u"Циклически", initial=False, required=False,
        widget=forms.CheckboxInput(attrs={"class": "apply_is_cycled"}),
    )
    keys_report = forms.CharField(required=False, widget=ReportWidget())

    def __init__(self, **kwargs):
        super(SeoTemplateAdminForm, self).__init__(**kwargs)
        self.initial["title_report"] = ('title', self.instance.data)
        self.initial["desc_report"] = ('desc', self.instance.data)
        self.initial["keys_report"] = ('keys', self.instance.data)

    def clean(self):

        """ метод переопределен чтобы привести данные формы
            о операциях над метатегами из unicode в int """

        cleaned_data = super(SeoTemplateAdminForm, self).clean()
        for key, val in cleaned_data.iteritems():
            if "operation" in key or "apply_type" in key:
                if isinstance(val, list):
                    int_val = []
                    for elem in val:
                        int_val.append(int(elem.encode("ascii")))
                else:
                    int_val = 0 if not len(val) else int(val.encode("ascii"))
                cleaned_data[key] = int_val
        return cleaned_data

    def set_initial_data(self):
        data = {
            "items": {},
            "title": {
                "list": [],
                "limit": 0,
            },
            "desc": {
                "list": [],
                "limit": 0,
            },
            "keys": {
                "list": [],
                "limit": 0,
            },
        }

        # если у доч. элемента есть seo запиcь, то добавить ее
        items = self.instance.get_children()
        if len(items):
            for item in items:
                item_app_label = item.__class__._meta.app_label
                item_class = item.__class__.__name__.lower()
                item_ct = ContentType.objects.get_for_model(item)
                item_key = "%d-%d" % (item_ct.id, item.id)
                item_change_link = reverse('admin:{0}_{1}_change'.format(item_app_label, item_class), args=(item.id,))
                seo = Seo.objects.filter(content_type=item_ct, object_id=item.id).first()

                data["items"][item_key] = {
                    "name": item.__str__(),
                    "change_link": item_change_link,
                    "title": {
                        "seo_text": seo.title if seo else None,
                        "gen_text": None,
                    },
                    "desc": {
                        "seo_text": seo.description if seo else None,
                        "gen_text": None,
                    },
                    "keys": {
                        "seo_text": seo.keywords if seo else None,
                        "gen_text": None,
                    },
                }
        return data

    def generate_texts(self, metatag_name):

        """ Генерирует список текстов по шаблону """

        template = self.cleaned_data[metatag_name + "_t"]
        # сгенерировать список текстов по шаблону
        seo_generator = SeoGenerator(template)
        self.data[metatag_name]["list"] = seo_generator.generate_textlist()
        return True

    @staticmethod
    def __get_cycled_texts(texts, cycled_count):
        cycled_texts = []
        for text in itertools.cycle(texts):
            if len(cycled_texts) >= cycled_count:
                break
            else:
                cycled_texts.append(text)
        return cycled_texts

    def __get_valid_texts(self, metatag_name):
        texts = self.data[metatag_name]["list"]
        limit = int(self.cleaned_data[metatag_name + "_l"])
        result = []
        for text in texts:
            if len(text) <= limit:
                result.append(text)
        return result

    def __get_free_items(self, metatag_name):
        free_items = []
        for key, val in self.data["items"].iteritems():
            if not val[metatag_name]["gen_text"]:
                free_items.append((key, val))
        free_items.sort(key=lambda x: x[1][metatag_name]["seo_text"], reverse=True)
        return OrderedDict(free_items)

    def __get_item_instance(self, item_key):
        ct_id, item_id = [int(val) for val in item_key.split("-")]
        item_cls = ContentType.objects.get(id=ct_id).model_class()
        item = item_cls.objects.filter(id=item_id).first()
        return item

    def apply_texts(self, metatag_name):

        apply_type = self.cleaned_data.get(metatag_name + "_apply_type", self.APPLY_FOR_FREE)
        apply_is_cycled = self.cleaned_data.get(metatag_name + "_apply_is_cycled", False)
        texts = self.__get_valid_texts(metatag_name)

        # Назначение текстов всем свободным элементам
        if apply_type == self.APPLY_FOR_FREE:
            items = self.__get_free_items(metatag_name)

        # Назначение текстов всем элементам
        elif apply_type == self.APPLY_FOR_ALL:
            items = dict(self.data["items"])

        if apply_is_cycled and (len(items) > len(texts)):
            # количество текстов станет = количеству элементов
            texts = self.__get_cycled_texts(texts, cycled_count=len(items))
        if texts and items:
            while texts and items:
                item_key, value = items.popitem()
                text = texts.pop()
                item = self.__get_item_instance(item_key)
                if item:
                    text = resolve_template_vars(item, text)
                value[metatag_name]["gen_text"] = text
                self.data["items"][item_key] = value
                self.instance.delete_cache(item_key=item_key)
                # когда тексты или элементы закончтся прервать распределение

            self.data[metatag_name]["list"] = texts
        return True

    def clear_texts(self, metatag_name):
        from seo.signals import seo_save_handler
        from django.db.models import signals
        signals.post_save.disconnect(seo_save_handler, Seo)
        for item_key in self.data["items"].keys():
            item_ct_id, item_id = [int(val) for val in item_key.split('-')]
            seo = Seo.objects.filter(object_id=item_id, content_type_id=item_ct_id).first()
            if seo:
                seo_metatag_name = get_seo_metatag_name(metatag_name)
                setattr(seo, seo_metatag_name, '')
                seo.save()
                self.data["items"][item_key][metatag_name]["seo_text"] = None
                self.instance.delete_cache(item_key=item_key)

        signals.post_save.connect(seo_save_handler, Seo)

    def update(self, metatag_name):

        """ Применить операции метатега и обновить его данные в data json"""

        operations = self.cleaned_data[metatag_name + "_operation"]

        # Применение операций
        if self.GENERATE_TEXTS in operations:
            self.generate_texts(metatag_name)  # Генерация текстов по шаблону и запись в список текстов

        if self.APPLY_TEXTS in operations:
            self.apply_texts(metatag_name)  # Назначение свободных текстов дочерним элементам

        if self.ClEAR_TEXTS in operations:
            self.clear_texts(metatag_name)  # удалить тексты заполненые вручную

        # Подсчет мета-данных метатега
        limit = int(self.cleaned_data[metatag_name + "_l"])
        texts = self.data[metatag_name]["list"]

        correct, incorrect = 0, 0
        for text in texts:
            if len(text) > limit:
                incorrect += 1
            else:
                correct += 1
        busy_items, free_items = 0, 0
        for id, value in self.data["items"].iteritems():
            if value[metatag_name]["seo_text"] or value[metatag_name]["gen_text"]:
                busy_items += 1
            else:
                free_items += 1

        self.data[metatag_name]["limit"] = limit
        self.data[metatag_name]["correct"] = correct
        self.data[metatag_name]["incorrect"] = incorrect
        self.data[metatag_name]["busy_items"] = busy_items
        self.data[metatag_name]["free_items"] = free_items
        return True

    def save(self, commit=True):

        self.data = dict(self.instance.data) if self.instance.data else self.set_initial_data()
        self.data["title"]["limit"] = self.cleaned_data["title_l"]
        self.data["desc"]["limit"] = self.cleaned_data["desc_l"]
        self.data["keys"]["limit"] = self.cleaned_data["keys_l"]

        self.update('title')
        self.update('desc')
        self.update('keys')

        self.instance.data = self.data

        exclude = [f for f in self._meta.exclude]
        exclude.append('data')
        fail_message = 'created' if self.instance.pk is None else 'changed'
        return forms.save_instance(self, self.instance, self._meta.fields, fail_message, commit, exclude, construct=False)
