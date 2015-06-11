# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

import mimetypes
import urlparse
import urllib


def ensure_bytes(value, encoding='utf-8'):
    if isinstance(value, unicode):
        value = value.encode(encoding)
    return value


def uri(value):
    def http(value, parsed):
        # TODO: Check if this can be mapped to a local file system path
        return urlparse.urlunparse(parsed._replace(
            netloc=ensure_bytes(parsed.netloc, 'idna'),
            path=urllib.quote(ensure_bytes(parsed.path, 'utf-8')),
        ))

    def file(value, parsed):
        raise NotImplementedError()

    SCHEMES = {
        'http': http,
        'https': http,
        'file': file,
    }

    parsed = urlparse.urlparse(value)
    try:
        handler = SCHEMES[parsed.scheme or 'file']
    except KeyError:
        raise Exception('Unknown protocol {} for media provided'.format(
            parsed.scheme or 'file'))
    return handler(value, parsed)


def mimetype(uri):
    """
    Gets the mimetype of a URI
    """
    mtype, __ = mimetypes.guess_type(uri, strict=False)
    return mtype
