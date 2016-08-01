# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

from flask import Blueprint, Response, current_app, request

import operator

from tinkrbell import cache
from tinkrbell.decorators import vary
from tinkrbell.utils import encode
from tinkrbell.utils.ffmpeg import boundingbox, Media


application = app = Blueprint('tinkrbell.apiv1', __name__)


def vary_accept_key_prefix():
    return 'view/{}|{vary}'.format(
        request.path,
        vary=encode(hash(frozenset(list(request.accept_mimetypes)))),
    )


@app.route('/icon/<int:size>/<path:uri>', methods=['GET'])
@app.route('/icon/<path:uri>', methods=['GET'], endpoint='icon', defaults={'size': 256})
@vary('Accept')
@cache.cached(key_prefix=vary_accept_key_prefix)
def icon(uri, size):
    """
    Generates an icon from URI.
    """
    DEFAULT_MIMETYPE, DEFAULT_PRESET = 'image/x-icon', 'ico'
    default_mimetype_q = request.accept_mimetypes[DEFAULT_MIMETYPE]
    ACCEPT_MIMETYPES = (
        ('image/webp', operator.ge, 1, 'webp'),
        (DEFAULT_MIMETYPE, operator.ge, 0, DEFAULT_PRESET),
    )

    for mimetype, op, q, preset in ACCEPT_MIMETYPES:
        mimetype_q = request.accept_mimetypes[mimetype]
        if op(mimetype_q, q) and mimetype_q > default_mimetype_q:
            break

    seek = request.args.get('seek')
    current_app.logger.info(
        """Generating icon: %s using preset "%s"
    - Accepts: %s""", mimetype, preset, request.accept_mimetypes)
    return Response(
        Media(uri).preview(boundingbox(size, size), preset, seek=seek),
        mimetype=mimetype)


@app.route('/preview/<int:width>x<int:height>/<path:uri>', methods=['GET'], endpoint='preview')
@app.route('/preview/<int:width>x/<path:uri>', methods=['GET'], defaults={'height': None})
@app.route('/preview/x<int:height>/<path:uri>', methods=['GET'], defaults={'width': None})
@app.route('/preview/<int:width>/<path:uri>', methods=['GET'], defaults={'height': None})
@vary('Accept')
@cache.cached(key_prefix=vary_accept_key_prefix)
def preview(uri, width, height):
    """
    Generates a preview of the URI returning the best image format supported by the browser.
    """
    DEFAULT_MIMETYPE, DEFAULT_PRESET = 'image/jpeg', 'jpg'
    default_mimetype_q = request.accept_mimetypes[DEFAULT_MIMETYPE]
    ACCEPT_MIMETYPES = (
        ('image/webp', operator.ge, 1, 'webp'),
        (DEFAULT_MIMETYPE, operator.ge, 0, DEFAULT_PRESET),
    )

    for mimetype, op, q, preset in ACCEPT_MIMETYPES:
        mimetype_q = request.accept_mimetypes[mimetype]
        if op(mimetype_q, q) and mimetype_q > default_mimetype_q:
            break

    current_app.logger.info(
        """Generating preview: %s using preset "%s"
    - Accepts: %s""", mimetype, preset, request.accept_mimetypes)
    response = Response(
        Media(uri).preview(boundingbox(width, height), preset, seek=request.args.get('seek')),
        mimetype=mimetype)
    # resp.headers['Conten-Disposition'] = ''
    return response


@app.route('/resize/<int:width>x<int:height>/<path:uri>', methods=['GET'])
@cache.cached()
def resize_by_boundingbox(uri, width, height):
    """
    Generates a preview of the image at URI, returning a resized image in the same format
    """
    media = Media(uri)
    return Response(
        media.resize(boundingbox(width, height)), mimetype=media.mimetype)
