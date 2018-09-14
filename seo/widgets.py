# -*- coding: utf-8 -*-
from django.forms import Widget
from django.utils.html import format_html
import json
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe


class ReportWidget(Widget):

    template = 'seo/admin/report.html'

    def render(self, name, value, attrs=None):
        # Приготовить словарь текстов готовых к выводу в таблице
        metatag_name, data = value
        if not data:
            return ''
        items = data["items"]
        limit = int(data[metatag_name]["limit"])
        text_objs = []

        correct, incorrect = 0, 0
        for text in data[metatag_name]["list"]:
            obj = {}
            if len(text) > limit:
                obj["warning"] = u"Количество символов в тексте превышает " \
                                 u"допустимое ограничение в %s символов" % limit
                obj["class"] = "danger"
                incorrect += 1
            else:
                correct += 1
            obj["value"] = text
            text_objs.append(obj)
        # Приготовить словарь доч. элементов готовых к выводу в таблице
        busy_items, free_items = 0, 0
        for id, value in items.iteritems():
            text_correct = True
            text_exist = True
            value["gen_text"] = value[metatag_name]["gen_text"]
            value["seo_text"] = value[metatag_name]["seo_text"]
            if value[metatag_name]["seo_text"]:
                if len(value[metatag_name]["seo_text"]) > limit:
                    text_correct = False
            elif value[metatag_name]["gen_text"]:
                if len(value[metatag_name]["gen_text"]) > limit:
                    text_correct = False
            else:
                text_exist = False

            if not text_exist:
                free_items +=1
                value["warning"] = u"Текст отсутствует, заполните вручную или примените текст из шаблона"
                value["class"] = "danger"
            else:
                if not text_correct:
                    value["warning"] = u"Количество символов в тексте превышает " \
                                       u"допустимое ограничение в %s символов" % limit
                    value["class"] = "warning"
                else:
                    busy_items += 1

            items[id] = value

        context = {
            "correct": correct,
            "incorrect": incorrect,
            "free_items": free_items,
            "busy_items": busy_items,
            "items": items,
            "texts": text_objs,
            "metatag_name": metatag_name
        }

        return mark_safe(render_to_string(self.template, context))