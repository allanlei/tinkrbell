# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

from flask import Blueprint, Response, current_app, request

import operator

from tinkrbell import cache
from tinkrbell.utils.ffmpeg import boundingbox, Media


application = app = Blueprint('tinkrbell.apiv1', __name__)


@app.route('/icon/<int:size>/<path:uri>', methods=['GET'])
@app.route('/icon/<path:uri>', methods=['GET'], endpoint='icon', defaults={'size': 256})
@cache.cached()
def icon(uri, size):
    """
    Generates an icon from URI.
    """
    ACCEPT_MIMETYPES = (
        ('image/webp', operator.ge, 1, 'webp'),
        ('image/x-icon', operator.ge, 0, 'ico'),
    )
    mimetype, preset = 'image/x-icon', 'ico'
    for mimetype, op, q, preset in ACCEPT_MIMETYPES:
        if op(request.accept_mimetypes[mimetype], q):
            break

    seek = request.args.get('seek')
    return Response(
        Media(uri).preview(boundingbox(size, size), preset, seek=seek),
        mimetype=mimetype)


@app.route('/preview/<int:width>x<int:height>/<path:uri>', methods=['GET'], endpoint='preview')
@app.route('/preview/<int:width>x/<path:uri>', methods=['GET'], defaults={'height': None})
@app.route('/preview/x<int:height>/<path:uri>', methods=['GET'], defaults={'width': None})
@app.route('/preview/<int:width>/<path:uri>', methods=['GET'], defaults={'height': None})
@cache.cached()
def preview(uri, width, height):
    """
    Generates a preview of the URI returning the best image format supported by the browser.
    """
    ACCEPT_MIMETYPES = (
        ('image/webp', operator.ge, 1, 'webp'),
        ('image/jpeg', operator.ge, 0, 'jpg'),
    )
    mimetype, preset = 'image/jpeg', 'jpg'
    for mimetype, op, q, preset in ACCEPT_MIMETYPES:
        if op(request.accept_mimetypes[mimetype], q):
            break

    current_app.logger.debug(
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
