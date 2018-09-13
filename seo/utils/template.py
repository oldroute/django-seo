# -*- coding:utf-8 -*-
import re


class VarObj:
    """
        класс для хранения данных переменной шаблона
        пример переменных: #name#, #name_st#
    """
    def __init__(self, var, val, suf):
        self.var = var
        self.val = val
        self.suf = suf


def var_is_long_title(var):
    if var == "long_title" or var == "long_title_st" or var == "long_name" or var == "long_name_st":
        return True
    return False


def get_long_title_val(obj, var):
    """ Получить значение long_title (long_name) по умолчанию name """
    val = ""
    try:
        if var.endswith("_st"):
            val = getattr(obj, var[:-3], "")
        else:
            val = getattr(obj, var, "")
        if not len(val):
            raise Exception
    except:
        try:
            val = getattr(obj, "name", "")
        except:
            pass
    if var.endswith("_st"):
        return val[0].lower() + val[1:]  # Заглавная буква в нижний регистр
    else:
        return val


def resolve_template_vars(obj, template):
    """ Заменяет переменные шаблона на значения одноименных атрибутов объекта
        если исходны шаблон пустая строка или в нем нет переменных то возвращает исходный шаблон"""

    template_var_pattern = re.compile(r"#(\w+)#")
    template_vars = re.findall(template_var_pattern, template)
    var_objects = list()
    for var in template_vars:
        val = get_long_title_val(obj, var) if var_is_long_title(var) else None
        # если суффикс переменной _st то привести в нижний регистр
        if var.endswith("_st"):
            val = val if val else getattr(obj, var[:-3], var)  # Если у объекта нет такого поля то оставить переменную как текст
            val = val[0].lower() + val[1:]  # Заглавная буква в нижний регистр
            var_obj = VarObj(var=var[:-3], val=val, suf="_st")
        # если нет суффикса
        else:
            val = val if val else getattr(obj, var, "")
            var_obj = VarObj(var=var, val=val, suf="")
        var_objects.append(var_obj)

    for var_obj in var_objects:
        template_var_replace_pattern = r'#%s%s#' % (var_obj.var, var_obj.suf)
        # замена переменной на ее значение
        template = re.sub(template_var_replace_pattern, var_obj.val, template)
    return template
