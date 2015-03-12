# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

from flask import current_app, request, Response

from .extractors import extract
from .utils.icons import icon


def iconify(image, sizes=None):
    return Response(icon(image, sizes=sizes), mimetype='image/x-icon')


def best_match():
    FORMATS = {
        'image/jpeg': 'jpeg',
        'image/pjpeg': 'pjpeg',
        # 'image/webp': 'webp',
        'image/png': 'png',
    }
    mimetype = request.accept_mimetypes.best_match(FORMATS.keys())
    quality = request.accept_mimetypes[mimetype]

    if quality != 1:
        return None, None
    current_app.logger.debug(
        'Best matched from "%s": %s;q=%s', request.accept_mimetypes, mimetype, quality)
    return mimetype, FORMATS[mimetype]
