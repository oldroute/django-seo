# -*- coding: utf-8 -*-
from django.contrib.contenttypes import generic
from django.contrib import admin
from django.contrib.contenttypes.admin import GenericStackedInline
from seo.forms import SeoForm, SeoTemplateAdminForm
from seo.models import Seo, Url, SeoTemplate
from seo.utils.utils import get_seo_models, get_seogen_models


class SeoInlines(generic.GenericStackedInline):
    model = Seo
    form = SeoForm
    extra = 1
    max_num = 1

class SeoAdmin(admin.ModelAdmin):
    model = Seo

try:
    admin.site.register(Seo, SeoAdmin)
except admin.sites.AlreadyRegistered:
    pass

class UrlAdmin(admin.ModelAdmin):
    model = Url
    inlines = [SeoInlines]

try:
    admin.site.register(Url, UrlAdmin)
except admin.sites.AlreadyRegistered:
    pass

for model in get_seo_models():
    model_admin = admin.site._registry[model].__class__
    admin.site.unregister(model)

    setattr(model_admin, 'inlines', getattr(model_admin, 'inlines', []))
    if not SeoInlines in model_admin.inlines:
        model_admin.inlines = list(model_admin.inlines)[:] + [SeoInlines]

    admin.site.register(model, model_admin)


class SeoTemplateInline(GenericStackedInline):

    # template = 'admin/seogen/edit_inline/stacked.html'

    model = SeoTemplate
    form = SeoTemplateAdminForm
    extra = 0
    max_num = 1
    fieldsets = (
        (u'title', {
            "fields": ("title_t", ("title_a", "title_l"), ('title_operation', 'title_apply_type', 'title_apply_is_cycled'), 'title_report', ),
            "classes": ("collapse",)
        }),
        (u'description', {
            "fields": ("desc_t",  ("desc_a", "desc_l"), ('desc_operation', 'desc_apply_type', 'desc_apply_is_cycled'), 'desc_report',),
            "classes": ("collapse",)
        }),
        (u'keywords', {
            "fields": ("keys_t",  ("keys_a", "keys_l"), ('keys_operation', 'keys_apply_type', 'keys_apply_is_cycled'), 'keys_report',),
            "classes": ("collapse",)
        }),
        # ('json', {
        #     "fields": ("data",),
        #     "classes": ("collapse",)
        # }),

    )


for model in get_seogen_models():
    model_admin = admin.site._registry[model].__class__
    admin.site.unregister(model)

    setattr(model_admin, 'inlines', getattr(model_admin, 'inlines', []))
    if not SeoTemplateInline in model_admin.inlines:
        model_admin.inlines = list(model_admin.inlines)[:] + [SeoTemplateInline]

    admin.site.register(model, model_admin)

