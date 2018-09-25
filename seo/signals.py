# -*- coding:utf-8 -*-
from django.contrib.contenttypes.models import ContentType
from django.db.models import signals
from catalog.signals import content_object_parent_changed, content_object_created
from catalog.models import TreeItem
from seo.models import Seo, SeoTemplate
from seo.utils.utils import get_seogen_models, get_child_models, is_child_model, delete_cache


def delete_content_object_handler(sender, instance, **kwargs):

    instance_ct = ContentType.objects.get_for_model(instance)
    seo_template = SeoTemplate.objects.filter(content_type=instance_ct, object_id=instance.id).first()
    if seo_template:
        seo_template.delete()
    # # print "------> DEL CT", type(instance), instance
    return


for model_cls in get_seogen_models():
    signals.post_delete.connect(delete_content_object_handler, sender=model_cls)


def item_saved_handler(sender, instance, **kwargs):

    if not kwargs.get("created"):
        tree_parent = instance.tree.get().parent
        if tree_parent:
            parent = tree_parent.content_object
            parent_ct = ContentType.objects.get_for_model(parent)
            seo_template = SeoTemplate.objects.filter(content_type=parent_ct, object_id=parent.id).first()
            if seo_template:
                delete_cache(instance)
                seo_template.update_data_item(instance)
            # print "------> SAVE ITEM", type(instance)


for model_cls in get_child_models():
    signals.post_save.connect(item_saved_handler, sender=model_cls)


def item_created_handler(sender, instance, parent, **kwargs):

    """ Отлавливать создание элемента каталога """
    item = instance
    if is_child_model(item):
        parent_ct = ContentType.objects.get_for_model(parent)
        seo_template = SeoTemplate.objects.filter(content_type=parent_ct, object_id=parent.id).first()
        if seo_template:
            seo_template.create_data_item(item)
            # print "------> CREATED ITEM", type(item), item

content_object_created.connect(item_created_handler)


def item_deleted_handler(sender, instance, **kwargs):

    treeitem = instance
    if treeitem.parent:
        parent = treeitem.parent.content_object
        parent_ct = ContentType.objects.get_for_model(parent)
        seo_template = SeoTemplate.objects.filter(content_type=parent_ct, object_id=parent.id).first()

        if seo_template:
            item = treeitem.content_object
            seo_template.remove_data_item(item)
            delete_cache(item)
            # print "------> DEL ITEM", type(item), item


signals.pre_delete.connect(item_deleted_handler, sender=TreeItem)


def item_parent_changed(sender, instance, **kwargs):

    item = instance
    parent_from = kwargs.get("parent_from")
    if parent_from:
        parent_from_ct = ContentType.objects.get_for_model(parent_from)
        seo_template_from = SeoTemplate.objects.filter(content_type=parent_from_ct, object_id=parent_from.id).first()
        if seo_template_from:
            seo_template_from.remove_data_item(item)
            delete_cache(item)
            # print "------> REMOVED FROM", parent_from

    parent_to = kwargs.get("parent_to")
    if parent_to:
        parent_to_ct = ContentType.objects.get_for_model(parent_to)
        seo_template_to = SeoTemplate.objects.filter(content_type=parent_to_ct, object_id=parent_to.id).first()
        if seo_template_to:
            seo_template_to.create_data_item(item)
            # print "------> CREATED IN", parent_to


content_object_parent_changed.connect(item_parent_changed)


def seo_del_handler(sender, instance, **kwargs):

    item = instance.content_object
    if is_child_model(item):
        tree_parent = item.tree.get().parent
        if tree_parent:
            parent = tree_parent.content_object
            parent_ct = ContentType.objects.get_for_model(parent)
            seo_template = SeoTemplate.objects.filter(content_type=parent_ct, object_id=parent.id).first()
            if seo_template:
                seo_template.update_data_item(item)
                # print "------> SEO DEL", type(instance), instance
    delete_cache(item)


signals.post_delete.connect(seo_del_handler, sender=Seo)


def seo_save_handler(sender, instance, **kwargs):

    item = instance.content_object
    if is_child_model(item):
        tree_parent = item.tree.get().parent
        if tree_parent:
            parent = tree_parent.content_object
            parent_ct = ContentType.objects.get_for_model(parent)
            seo_template = SeoTemplate.objects.filter(content_type=parent_ct, object_id=parent.id).first()
            if seo_template:
                seo_template.update_data_item(item)
                print "------> SEO SAVE", type(instance), instance
    delete_cache(item)


signals.post_save.connect(seo_save_handler, sender=Seo)


def seo_template_delete_handler(sender, instance, **kwargs):

    instance.delete_all_cache()
    # print "------> SEO TEMPLATE CACHE CLEARED"

signals.pre_delete.connect(seo_template_delete_handler, sender=SeoTemplate)
