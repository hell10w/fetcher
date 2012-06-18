# -*- coding: utf-8 -*-

"""
    werkzeug.urls
    ~~~~~~~~~~~~~

    This module implements various URL related functions.

    :copyright: (c) 2011 by the Werkzeug Team, see AUTHORS for more details.
    :license: BSD, see LICENSE for more details.
"""

import urlparse

#: list of characters that are always safe in URLs.
_always_safe = ('ABCDEFGHIJKLMNOPQRSTUVWXYZ'
                'abcdefghijklmnopqrstuvwxyz'
                '0123456789_.-')
_safe_map = dict((c, c) for c in _always_safe)
for i in xrange(0x80):
    c = chr(i)
    if c not in _safe_map:
        _safe_map[c] = '%%%02X' % i
_safe_map.update((chr(i), '%%%02X' % i) for i in xrange(0x80, 0x100))
_safemaps = {}

#: lookup table for encoded characters.
_hexdig = '0123456789ABCDEFabcdef'
_hextochr = dict((a + b, chr(int(a + b, 16)))
    for a in _hexdig for b in _hexdig)


def _quote(s, safe='/', _join=''.join):
    assert isinstance(s, str), 'quote only works on bytes'
    if not s or not s.rstrip(_always_safe + safe):
        return s
    try:
        quoter = _safemaps[safe]
    except KeyError:
        safe_map = _safe_map.copy()
        safe_map.update([(c, c) for c in safe])
        _safemaps[safe] = quoter = safe_map.__getitem__
    return _join(map(quoter, s))


def _quote_plus(s, safe=''):
    if ' ' in s:
        return _quote(s, safe + ' ').replace(' ', '+')
    return _quote(s, safe)


def _safe_urlsplit(s):
    """the urlparse.urlsplit cache breaks if it contains unicode and
    we cannot control that.  So we force type cast that thing back
    to what we think it is.
    """
    rv = urlparse.urlsplit(s)
    # we have to check rv[2] here and not rv[1] as rv[1] will be
    # an empty bytestring in case no domain was given.
    if type(rv[2]) is not type(s):
        assert hasattr(urlparse, 'clear_cache')
        urlparse.clear_cache()
        rv = urlparse.urlsplit(s)
        assert type(rv[2]) is type(s)
    return rv


def _unquote(s, unsafe=''):
    assert isinstance(s, str), 'unquote only works on bytes'
    rv = s.split('%')
    if len(rv) == 1:
        return s
    s = rv[0]
    for item in rv[1:]:
        try:
            char = _hextochr[item[:2]]
            if char in unsafe:
                raise KeyError()
            s += char + item[2:]
        except KeyError:
            s += '%' + item
    return s


def _unquote_plus(s):
    return _unquote(s.replace('+', ' '))


def _uri_split(uri):
    """Splits up an URI or IRI."""
    scheme, netloc, path, query, fragment = _safe_urlsplit(uri)

    port = None

    if '@' in netloc:
        auth, hostname = netloc.split('@', 1)
    else:
        auth = None
        hostname = netloc
    if hostname:
        if ':' in hostname:
            hostname, port = hostname.split(':', 1)
    return scheme, auth, hostname, port, path, query, fragment


def url_fix(s, charset='utf-8'):
    if isinstance(s, unicode):
        s = s.encode(charset, 'replace')
    scheme, netloc, path, qs, anchor = _safe_urlsplit(s)
    path = _quote(path, '/%')
    qs = _quote_plus(qs, ':&%=')
    return urlparse.urlunsplit((scheme, netloc, path, qs, anchor))
