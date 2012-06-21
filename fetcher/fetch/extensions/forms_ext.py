# -*- coding: utf-8 -*-

from logging import getLogger
from urlparse import urljoin
from urllib import urlencode

from fetcher.errors import FormsException
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
        '''Находит элемент формы по имени'''
        return self.form[name]

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

        if extra_values:
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
