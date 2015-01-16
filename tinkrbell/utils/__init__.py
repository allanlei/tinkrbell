# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

from flask import current_app
import mimetypes
import futures
import multiprocessing
import urlparse
import urllib

from wand.image import Image


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
    mtype, __ = mimetypes.guess_type(uri)
    return mtype


def icon(image, sizes=None):
    """Converts an image file-like object into a ICO image"""
    def _icons(img, sizes):
        with img.clone() as img:
            for size in reversed(sorted(sizes)):
                width, height = size, size
                # ico = Image(width=width, height=height)
                img.transform(resize='{:d}x{:d}>'.format(width, height))
                # ico.composite(img,
                #     top=int((ico.height - img.height) / 2),
                #     left=int((ico.width - img.width) / 2),
                # )
                # yield ico
                yield img.clone()

    sizes = sizes or current_app.config['AVAILABLE_ICON_SIZES']
    icons = _icons(image, sizes=sizes)
    with icons.next() as ico:
        current_app.logger.debug('Added icon size: %dx%d', ico.width, ico.height)

        for subicon in icons:
            ico.sequence.append(subicon)
            current_app.logger.debug(
                'Added icon size: %dx%d', subicon.width, subicon.height)
        # ico.save(filename='lols.ico',)
        ico.strip()
        return ico.make_blob('ico')
