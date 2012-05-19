# -*- coding: utf-8 -*-

from urlparse import urljoin
from urllib import urlencode

from fetcher.errors import FormsException
from base import BaseExtension


class FormsExtension(BaseExtension):
    @property
    def forms(self):
        if not hasattr(self, '_forms'):
            self._forms = self.html_tree.forms
        return self._forms

    @property
    def form(self):
        if not hasattr(self, '_form'):
            # TODO: в граб формой по-умолчанию является самая большая
            self.choose_form(0)
        return self._form

    def choose_form(self, index=None, id=None, name=None, xpath=None):
        # TODO: нихуя не понятно что будет если форму не найдет
        if id is not None:
            self._form = self.xpath('//form[@id="%s"]' % id)
        elif name is not None:
            self._form = self.xpath('//form[@name="%s"]' % name)
        elif index is not None:
            self._form = self.html_tree.forms[index]
        elif xpath is not None:
            self._form = self.xpath(xpath)
        else:
            raise FormsException('choose_form methods requires one of '
                                 '[number, id, name, xpath] arguments')

    def choose_form_by_inner_xpath(self, xpath):
        for form in self.forms:
            if len(form.xpath(xpath)):
                self._form = form
                return
        self._form = self.forms[0]

    def form_choosed(self):
        return hasattr(self, '_form')

    def form_fields(self):
        fields = dict(self.form.fields)
        for elem in self.form.inputs:
            # убираются элементы которые не учавствуют в POST-запросе
            if not elem.get('name'):
                continue

            if elem.get('disabled'):
                del fields[elem.name]
                continue

            # устанавливаются значения по-умолчанию
            if elem.tag == 'select':
                if fields[elem.name] is None:
                    if len(elem.value_options):
                        # выбирается последнее из списка значение
                        fields[elem.name] = elem.value_options[-1]

            if getattr(elem, 'type', None) == 'radio':
                if fields[elem.name] is None:
                    fields[elem.name] = elem.get('value')

            if getattr(elem, 'type', None) == 'checkbox':
                if not elem.checked:
                    if elem.name is not None:
                        if elem.name in fields:
                            del fields[elem.name]

        return fields

    def set_input(self, name=None, id=None, index=None, xpath=None, value=None):
        def set_input_by_name(name):
            if not self.form_choosed():
                self.choose_form_by_inner_xpath('//*[@name="%s"]' % name)
            elem = self.form.inputs[name]
            if getattr(elem, 'type', None) == 'checkbox':
                elem.checked = bool(value)
            else:
                # TODO: проверять тип value - это может быть файлом
                elem.value = value

        def set_input_by_xpath(xpath, index=0):
            if not self.form_choosed():
                self.choose_form_by_inner_xpath(xpath)
            elem = self.form.xpath(xpath)[index]
            set_input_by_name(elem.get('name'))

        if name is not None:
            set_input_by_name(name)
        elif id is not None:
            set_input_by_xpath('.//*[@id="%s"]' % id)
        elif index is not None:
            set_input_by_xpath('.//input[@type="text"]', index=index)
        elif xpath is not None:
            set_input_by_xpath(xpath)

    def submit(self, submit_name=None, extra_post=None):
        post = self.form_fields()

        # весь нижеследующий трах, только чтобы убрать из post ненужные кнопки

        # выбираем все submit-кнопки с формы
        submit_controls = dict(
            (elem.name, elem)
            for elem in self.form.xpath('//input[@name and @type="submit"]')
        )

        if len(submit_controls):
            # если не указана кнопка или на форме её нет -
            # выбираем первую по алфавиту
            if submit_name is None or not submit_name in submit_controls:
                controls = sorted(submit_controls.values(), key=lambda x: x.name)
                submit_name = controls[0].name

            # убираем из post не используемые кнопки
            for name in submit_controls:
                if name != submit_name:
                    if name in post:
                        del post[name]

        # получаем URL для запроса
        action_url = urljoin(
            self.request.url,
            self.form.action
        )

        # TODO: за каким-то хуем нужна возможность дублировать ключи в post
        # это нужно делать где-то здесь

        # перезаписываем текущий post дополнительными параметрами
        post.update(extra_post)

        # окончательная подготовка конфигурации запроса

        # формирование URL и тела запроса в зависимости от параметров формы
        if self.form.method == 'POST':
            self.request.is_multipart_post = 'multipart' in self.form.get('enctype', '')
            self.request.url = action_url
            self.request.post = post
        else:
            # TODO: хули эта пляска тут? надо делать что можно с кодировкой сразу и все
            post = dict(
                (key.encode('utf-8'), value.encode('utf-8'))
                for key, value in post.iteritems()
            )
            url = action_url.split('?')[0] + '?' + urlencode(post)
            self.request.url = url
            self.request.post = None
