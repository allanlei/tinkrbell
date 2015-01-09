# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

from flask import current_app, request, Response

from . import errors
from .extractors import extract
from .utils import icon


def iconify(image, sizes=None):
    if not sizes:
        size, multisized = current_app.config['AVAILABLE_ICON_SIZES'][-1], True
    elif len(sizes) > 1:
        size, multisized = sizes.pop(), True
    else:
        size, multisized = sizes.pop(), False
    return Response(
        icon(image, size, multisized=multisized), mimetype='image/x-icon')


def get_thumbnail():
    try:
        image = extract(uri)
    except AttributeError:
        current_app.logger.debug('URI not available')
    except:
        current_app.logger.info('Failed to extract image from URI', exc_info=True)
    return icon(image, size=size, multisized=multisized)


def best_match():
    FORMATS = {
        'image/webp': 'webp',
        'image/jpeg': 'pjpeg',
        'image/jpeg': 'jpeg',
        'image/png': 'png',
    }
    mimetype = request.accept_mimetypes.best_match(FORMATS.keys())
    quality = request.accept_mimetypes[mimetype]

    current_app.logger.debug(
        'Best matched from "%s": %s;q=%s', request.accept_mimetypes, mimetype, quality)

    if quality != 1:
        return None, None
    return mimetype, FORMATS[mimetype]
    # return best == 'application/json' and \
    #     request.accept_mimetypes[best] > \
    #     request.accept_mimetypes['text/html']
