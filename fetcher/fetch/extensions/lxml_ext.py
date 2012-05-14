# -*- coding: utf-8 -*-

from lxml.html import fromstring as html_fromstring
from lxml.etree import fromstring as xml_fromstring

from fetcher.errors import XPathNotFound
from base import BaseExtension


class LXMLExtension(BaseExtension):
    @property
    def html_tree(self):
        if not hasattr(self, '_html_tree'):
            body = self.response.get_body()
            if not body:
                body = '<html></html>'
            self._html_tree = html_fromstring(body)
        return self._html_tree

    @property
    def xml_tree(self):
        if not hasattr(self, '_xml_tree'):
            body = self.response.get_body()
            if not body:
                body = '<html></html>'
            self._xml_tree = xml_fromstring(body)
        return self._xml_tree

    def xpath(self, path, default=None, filter=None):
        try:
            return self.xpath_list(path, filter)[0]
        except IndexError:
            if default:
                return default
            else:
                raise XPathNotFound('Xpath not found: %s' % path)

    def xpath_list(self, path, filter=None):
        items = self.html_tree.xpath(path)
        if filter:
            return [x for x in items if filter(x)]
        else:
            return items

    '''def xpath_text(self, path, default=NULL, filter=None, smart=False,
                   normalize_space=True):
        try:
            elem = self.xpath(path, filter=filter)
        except IndexError:
            if default is NULL:
                raise
            else:
                return default
        else:
            if isinstance(elem, basestring):
                return normalize_space_func(elem)
            else:
                return get_node_text(elem, smart=smart, normalize_space=normalize_space)

    def xpath_number(self, path, default=NULL, filter=None, ignore_spaces=False,
                     smart=False):
        try:
            return find_number(self.xpath_text(path, filter=filter, smart=smart),
                               ignore_spaces=ignore_spaces)
        except IndexError:
            if default is NULL:
                raise
            else:
                return default'''

    def assert_xpath(self, path):
        self.xpath(path)

    def xpath_exists(self, path):
        return len(self.xpath_list(path)) > 0

    '''def find_link(self, href_pattern, make_absolute=True):
        if make_absolute:
            self.tree.make_links_absolute(self.response.url)

        if isinstance(href_pattern, unicode):
            raise GrabMisuseError('find_link method accepts only '\
                                  'byte-string argument')
        for elem, attr, link, pos in self.tree.iterlinks():
            if elem.tag == 'a' and href_pattern in link:
                return link
        return None'''

    '''def find_link_rex(self, rex, make_absolute=True):
        if make_absolute:
            self.tree.make_links_absolute(self.response.url)

        for elem, attr, link, pos in self.tree.iterlinks():
            if elem.tag == 'a':
                match = rex.search(link)
                if match:
                    # That does not work for string object
                    # link.match = match
                    return link
        return None'''

    '''def follow_link(self, anchor=None, href=None):
        if anchor is None and href is None:
            raise Exception('You have to provide anchor or href argument')
        self.tree.make_links_absolute(self.config['url'])
        for item in self.tree.iterlinks():
            if item[0].tag == 'a':
                found = False
                text = item[0].text or u''
                url = item[2]
                # if object is regular expression
                if anchor:
                    if hasattr(anchor, 'finditer'):
                        if anchor.search(text):
                            found = True
                    else:
                        if text.find(anchor) > -1:
                            found = True
                if href:
                    if hasattr(href, 'finditer'):
                        if href.search(url):
                            found = True
                    else:
                        if url.startswith(href) > -1:
                            found = True
                if found:
                    url = urljoin(self.config['url'], item[2])
                    return self.request(url=item[2])
        raise DataNotFound('Cannot find link ANCHOR=%s, HREF=%s' % (anchor, href))


    def find_content_blocks(self, min_length=None):
        from lxml_ext.html import tostring
        from lxml_ext.etree import strip_tags, strip_elements, Comment

        # Completely remove content of following tags
        nondata_tags = ['head', 'style', 'script', Comment]
        strip_elements(self.tree, *nondata_tags)

        # Remove links
        strip_elements(self.tree, 'a')

        # Drop inlines tags
        inline_tags = ('br', 'hr', 'p', 'b', 'i', 'strong', 'em', 'a',
                       'span', 'font')
        strip_tags(self.tree, *inline_tags)

        # Cut of images
        media_tags = ('img',)
        strip_tags(self.tree, *media_tags)

        body = tostring(self.tree, encoding='utf-8').decode('utf-8')

        # Normalize spaces
        body = normalize_space_func(body)

        # Find text blocks
        block_rex = re.compile(r'[^<>]+')

        blocks = []
        for match in block_rex.finditer(body):
            block = match.group(0)
            if len(block) > 100:
                ratio = self._trash_ratio(block)
                if ratio < 0.05:
                    block = block.strip()
                    if min_length is None or len(block) >= min_length:
                        blocks.append(block)
        return blocks

    def _trash_ratio(self, text):

        trash_count = 0
        for char in text:
            if char in list(u'.\'"+-!?()[]{}*+@#$%^&_=|/\\'):
                trash_count += 1
        return trash_count / float(len(text))'''
