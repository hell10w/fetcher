# -*- coding: utf-8 -*-

from logging import getLogger
from urllib import urlencode

from base import BaseExtension


logger = getLogger('fetcher.formsext')


class FormsExtension(BaseExtension):
    def select_form(self, index=None, xpath=None, id=None, name=None):
        '''Устанавливает нужную форму текущей'''
        if index is not None:
            form = self.html.tree.forms[index]
        else:
            if not xpath:
                if id:
                    xpath = '//form[@id="%s"]' % id
                elif name:
                    xpath = '//form[@name="%s"]' % name
            form = self.html.xpath(xpath)
        self._form = form

    @property
    def form(self):
        '''Возвращает текущую форму и если её нет - берет первую'''
        if not hasattr(self, '_form'):
            logger.warning(u'Автоматический выбор первой формы.')
            self.select_form(index=0)
        return self._form

    def name_by_id(self, id):
        '''Возвращает имя элемента формы по его id'''
        return self.form.xpath('//*[@id="%s"]/@name' % id)[0]

    def get_control(self, name):
        '''
        Находит элемент формы по имени

        Для работы с элементами формы lxml предоставляет прекрасный API,
        который позволяет работать как с отдельными элементами, так и с группами,
        объедененными общим именем, как это делается с checkbox, radio.
        Так же есть возможность работать с множественным выбором значений в select.

        Эта функция предназначена именно для получения такого интерфейса для
        взаимодействия с нужным элементом текущей формы.

        Если элемент формы логически обособлен, то через интерфейс напрямую
        осуществляется работа с его значением. А если имени name соответствует
        группа элементов, то интерфейс дает возможность выбрать одно или
        несколько значений сразу для всей группы.

        Интерфейсы, которые функция может вернуть, соответствуют логическому
        смыслу элемента:

        TextareaElement - взаимодействие с <textarea>.
            Получение и установка значения через свойство value.

        SelectElement - взаимодействие с <select>.

            * value - если <select> может содержать только одно значение, то
                напрямую получает и устанавливает значение через это свойство.
                если <select> может содержать множество значений, то это свойство
                устанавливает возвращает экземпляр класса MultipleSelectOptions
                для работы с множеством значений.
            * value_options - список всех возможных значений для <select>
                содержащихся в <option> элементах.
            * multiple - если True, то <select> позволяет выбрать несколько значений.

        MultipleSelectOptions - работа с группой значений элемента <select>,
            который позволяет выбирать несколько значений.

            * options - итератор всех возможных значений
            * add - добавить выбранное значение
            * remove - убать значение из списка выбранных

        RadioGroup - взаимодействие с группой переключателей <input type=radio>.
            работая с группой и устанавливая значение, lxml автоматически
            снимает выбор с другого текущего переключателя, т.к. включенным
            должен оставаться только один переключатель.

            * value - установить/получаить текущее выбранное значение группы.
            * value_options - список всех возможных значений для этой группы.

        CheckboxGroup - взаимодействие с группой флажков <input type=checkbox>.

            * value - возвращает экземпляр класса CheckboxValues для работы с
                множеством значений группы флажков.

            получить список возможных значений для группы флажков можно через
            метод задачи - checkbox_group_values.

        CheckboxValues - установка/удалчение флажков в группе.

            * add - добавляет значение в качестве установленного в группу
            * remove - удаляет значение из группы

        InputElement - взаимодействие с одиночным элементом ввода

            * value - значение
            * type - тип
            * checkable - True, если элемент можно "переключить": type in ['checkbox', 'radio']
            * checked - True, если элемент включен. для checkable элементов

        '''

        return self.form.inputs[name]

    def submit(self, submit_name=None, extra_values=None):
        '''Формирует запрос для формы'''

        def control_filter(control):
            '''Фильтр элементов формы, которые не будут принимать участие в запросе'''

            if not control.get('name') or 'disabled' in control.attrib:
                return

            if control.tag == 'input' and control.checkable and not control.checked:
                return

            if submit_name:
                if control.get('type') == 'submit' and control.get('name') != submit_name:
                    return
            else:
                if control.get('type') == 'submit':
                    return

            return True

        def control_content(control):
            '''Извлекает значения элемента формы'''

            name = control.get('name')

            if control.tag == 'select' and control.multiple:
                return name, [
                    item.get('value')
                    for item in control.value.options
                    if 'selected' in item.attrib
                ]

            return name, [control.value]

        controls = [
            control
            for control in self.form.inputs
        ]

        controls = filter(
            control_filter,
            controls
        )

        post_variables = []

        for control in controls:
            name, values = control_content(control)
            for value in values:
                post_variables.append((name, value))

        for index, item in enumerate(post_variables):
            key, value = item
            post_variables[index] = (
                key.encode(self.response.charset or 'utf-8'),
                value.encode(self.response.charset or 'utf-8')
            )

        if extra_values:
            if hasattr(extra_values, 'items'):
                extra_values = extra_values.items()
            for extra_item in extra_values:
                post_variables.append(extra_item)

        # настройка запроса под форму

        if self.form.action:
            self.request.url = self.form.action
        else:
            self.request.url = ''

        self.request.post = None

        self.request.is_multipart_post = False # TODO: 'multipart' in enctype

        if self.form.method == 'GET':
            self.request.method = 'GET'
            self.request.url = self.request.url + '?' + urlencode(post_variables)

        elif self.form.method == 'POST':
            self.request.method = 'POST'

            if self.request.is_multipart_post:
                raise NotImplementedError
            else:
                self.request.post = urlencode(post_variables)

    def checkbox_group_values(self, control):
        return [
            item.attrib['value']
            for item in control.value.group
        ]
