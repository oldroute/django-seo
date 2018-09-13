# -*- coding:utf-8 -*-
import re
import random

class SeoGenerator:

    OR = 0  # операция возвращает список операндов
    AND = 1  # операция создает все комбинации операндов и возвращает их список
    BRACKET_TYPES = {
        "{": OR, "}": OR,
        "[": AND, "]": AND,
    }

    class NodeHolder:
        def __init__(self):
            self.buffer = dict()
            self.nodelist_key_template = ":node%d:"

        def save(self, node):
            nodelist_key = self.nodelist_key_template % len(self.buffer)
            self.buffer[nodelist_key] = node
            return nodelist_key

        def get(self, nodelist_key):
            return self.buffer[nodelist_key]

        @staticmethod
        def get_pattern():
            return re.compile(r':node\d+:')

    def __init__(self, seo_template):
        """
            seo_template - это seo-шаблон
            Класс для генерирования текста по seo-шаблону.
            шаблон seo_template может содержать следующие допустимые операции:
            1. {a |b |z } => a b z
            2. [a|b] => ab ba
            2. [+<separator>+a|b] a<separator>b b<separator>a

        """

        self.template = seo_template
        self.node_holder = self.NodeHolder()

    def __complete_combinations(self, combinations=None, combination=None, tail=None, separator=" "):
        """
            Рекурсивно достраивает комбинацию, на каждом шаге рекурсии добавляется один
            свободный элемент из tail. Когда свободные элементы заканчиваются - комбинация готова
            записывает комбинацию в список комбинаций
        """
        combinations = [] if combinations is None else combinations
        combination = [] if combination is None else combination
        tail = [] if tail is None else tail
        for node in tail:
            combination1 = combination[:]
            combination1.append(node)
            tail1 = list(set(tail) - set(combination1))
            if len(tail1):
                self.__complete_combinations(combinations, combination1, tail1, separator)
            else:
                combinations.append(separator.join(combination1))
        return combinations

    def __generate_combinations(self, nodelist, separator=" "):
        """
            Запускает первую итерацию сборки комбинаций из элементов списка nodelist
            элементы комбинации объединяются указанным в separator разделителем
        """

        tail = nodelist[:]
        combinations = self.__complete_combinations(tail=tail, separator=separator)
        return combinations

    def __resolve_simple_template(self, simple_template):
        """
            Принимает простой шаблон,
            применяет операцию согласно типу скобок,
            возвращает список простых элементов(не шаблонов)
        """
        operation_type = self.BRACKET_TYPES[simple_template[0]]
        template_content = simple_template[1:-1]

        nodelist = None
        if operation_type == self.OR:
            nodelist = template_content.split("|")

        elif operation_type == self.AND:
            separator_pattern = re.compile(r'\+(.+)\+')
            separator = re.match(separator_pattern, template_content)
            if separator:
                separator = separator.group(True)
                template_content = re.sub(separator_pattern, "", template_content)
            else:
                separator = ""
            nodelist = template_content.split("|")
            for i in range(len(nodelist)):
                nodelist[i] = nodelist[i]
            nodelist = self.__generate_combinations(nodelist, separator)

        return nodelist

    def __prepare_template(self, template):
        """
            Подготовка шаблона, содержащего шаблонные операторы {}, []
            Поиск простоых операторов, запись их в node_holder, замена на переменную в исходном шаблоне
            шаблон подготовлен когда все операторы вычеселны и заменены на переменные
            Пример:
            [a|{b|c}]e => [a|:node0:]e => :node1:e
                :node0: = {b|c} => resolve_simple_template => ["b","c"]
                :node1: = [a|:node0:] => resolve_simple_template => ["a node0","node0 a" ]
            node_holder:
                :node0: ["b","c"]
                :node1: ["a node0","node0 a" ]
        """

        simple_template_pattern = re.compile(r'\[[^\[\]\{\}]+\]|\{[^\[\]\{\}]+\}')
        # поиск простого шаблона в переданной строке
        simple_template_finded = re.search(simple_template_pattern, template)
        # если найден простой шаблон в шаблоне
        if simple_template_finded:
            simple_template = simple_template_finded.group(0)
            simple_template_nodelist = self.__resolve_simple_template(simple_template)
            nodelist_key = self.node_holder.save(simple_template_nodelist)
            nodelist = template.split(simple_template)
            nodelist.insert(1, nodelist_key)
            # подставляем в шаблон вместо найденного простого шаблона переменную
            template2 = "".join(nodelist)
            # снова ищем простой шаблон
            return self.__prepare_template(template2)
        else:
            return template

    def __simplify_nodelist(self, nodelist):
        """
            Упрощение сложного списка нод в список простых,
            после подтановки вместо переменных их значений(нод)

            prepared_template = :node2:  a  e.
            :node2:  = ["b", "c"] =>
            nodelist = [["b", "c"], "a  e."]

            simplify_nodelist(nodelist):
            [["b", "c"], "a  e."] => ["b a e.", "c a e."]
        """

        buf = []                # в буфере накапливаем простые элементы nodelist (не списки)
        compiled_nodelist = []  # список накапливает простые ноды, построенные из сложных
        for node in nodelist:
            if isinstance(node, list):
                if len(buf):
                    if len(compiled_nodelist):
                        extended_compiled_nodelist = []
                        for i in range(len(compiled_nodelist)):
                            for elem in node:
                                extended_compiled_nodelist.append(compiled_nodelist[i] + ("".join(buf) + elem))
                        compiled_nodelist = extended_compiled_nodelist
                    else:
                        for elem in node:
                            compiled_nodelist.append("".join(buf) + elem)
                else:
                    if len(compiled_nodelist):
                        extended_compiled_nodelist = []
                        for i in range(len(compiled_nodelist)):
                            for elem in node:
                                extended_compiled_nodelist.append(compiled_nodelist[i] + elem)
                        compiled_nodelist = extended_compiled_nodelist
                    else:
                        for elem in node:
                            compiled_nodelist.append(elem)
                buf = []
            else:
                if not len(compiled_nodelist):
                    buf.append(node)
                else:
                    for i in range(len(compiled_nodelist)):
                        compiled_nodelist[i] += node

        return compiled_nodelist

    def __construct_node(self, node):
        """
            Разрешает ситуацию когда элемент является списком
            Для кажого элемента списка (выражения) запускает поиск и замену переменных
        """
        if isinstance(node, list):
            for i in range(len(node)):
                node[i] = self.__construct_node(node[i])
        else:
            node = self.__construct_nodelist(node)
        return node

    def __construct_nodelist(self, prepared_template):
        """
            По приготовленному шаблону(содержит переменные шаблона) составляет список нод
            (заменяет переменные на их значения(ноды))

            Пример:
            prepared_demplate = :node1: e.
            node_holder:
                :node1: ["a :node2:", ":node2: a"]
                :node0: ["b", "c"]

            construct_nodelist(prepared_template)
                nodelist = [["a node0","node0 a" ], "e"]
                simplify_nodelist(nodelist)
                    nodelist = [["a node0","node0 a" ], "e"] => ["a node0 e", "node0 a e"]
                рекурсивно повторяем процедуру construct_nodelist + simplify_nodelist
                для каждой ноды из nodelist и в конечном счете получим nodelist не содержащий
                переменных и сложных нод:

                nodelist = ['a b e.', 'a c e.', 'b a e.', 'c a e.']

        """

        nodelist_key_pattern = self.node_holder.get_pattern()
        right_part = prepared_template
        nodelist = list()
        # print "@0 prepared_template", prepared_template
        nodelist_key = re.search(nodelist_key_pattern, right_part)
        # если нет шаблонных переменных
        if not nodelist_key:
            return prepared_template
        # ищем переменные слева на право в правой части выражения
        # если обнаружена переменная (nodelist_key) то заменяем ее на значение и проверяем выражение снова
        while True:
            nodelist_key = re.search(nodelist_key_pattern, right_part)
            if nodelist_key and len(right_part):
                nodelist_key = nodelist_key.group(0)
                # print "@1 nodelist_key", nodelist_key
                left_part, right_part = right_part.split(nodelist_key)
                left_part, right_part = left_part, right_part
                simple_nodelist = self.node_holder.get(nodelist_key)
                # print "@2 simple_nodelist", simple_nodelist
                if len(left_part):
                    nodelist.append(left_part)
                nodelist.append(simple_nodelist)
            else:
                break
        # добавим последние элементы правой части
        if len(right_part):
            nodelist.append(right_part)
        # print "@4 nodelist", nodelist, '\n'

        if len(nodelist):
            # упростить сложные ноды (содержащие списки элементов) в простые
            nodelist = self.__simplify_nodelist(nodelist)
            # для каждого элемента списка рекурсивно ищем и заменяем переменные
            consructed_nodelist = []
            for i in range(len(nodelist)):
                consructed_node = self.__construct_node(nodelist[i])
                # print "+--->", consructed_node
                if isinstance(consructed_node, list):
                    consructed_nodelist.extend(consructed_node)
                else:
                    consructed_nodelist.append(consructed_node)
            nodelist = consructed_nodelist
            # если в списке только один элемент то возвращаем его
            if len(nodelist) == 1:
                nodelist = nodelist[0]
            # print "@5 consructed nodelist", nodelist
            return nodelist
        # если нет шаблонов в переданном выражении
        else:
            return prepared_template

    def generate_textlist(self):
        """ Возвращает сгененрированный по шаблону список текстов """
        try:
            prepared_template = self.__prepare_template(self.template)
        except:
            raise Exception("Seo-template has are syntax error")

        try:
            textlist = self.__construct_nodelist(prepared_template)
            if not isinstance(textlist, list):
                text = textlist.strip()
                textlist = [text, ] if len(text) else []
            random.shuffle(textlist)  # перетосовать тексты в случайном порядке
        except:
            raise Exception("Could not create text from template, see the error in log")
        return textlist
