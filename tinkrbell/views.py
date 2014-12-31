# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

from flask import make_response, Response, abort, current_app

# import os
# import mimetypes

from tinkrbell import cache

from . import application as app


@app.route('/')
def healthcheck():
    return make_response()


# @app.route('/icon/<path:uri>', methods=['GET'], endpoint='icon')
# def preview_icon(width, height, uri):
#     default = request.args.get('defualt') or request.args.get('d') or '404'
#     size = request.args.get('size') or request.args.get('s') or '36'
#     current_app.logger.info('Generating icon %s (default: %s): %s', default, uri)

#     return current_app.send_static_file('images/default.png')



# @app.route('/<int:percentage>%/<path:uri>', methods=['GET'], endpoint='thumbnail')
# @cache.cached()
# def thumbnail_by_percentage(percentage, uri):
#     pass


# @app.route('/thumbnail/<resize>/<path:uri>', methods=['GET'], endpoint='thumbnail')
# def thumbnail(uri, resize):
#     """
#     Resizes images, perserving aspect ratio

#     - Scale by percentage
#         img.transform(resize='200%')
#     - Scale height to 100px and preserve aspect ratio
#         img.transform(resize='x100')
#     - If larger than 640x480, fit within box, preserving aspect ratio
#         img.transform(resize='640x480>')
#     """
#     mimetype, __ = mimetypes.guess_type(uri)
#     from turbo import errors
#     from turbo.utils import imaging

#     try:
#         response = make_response(imaging.resize(uri, scale=resize))
#         response.mimetype = mimetype
#     except errors.UnknownTransform:
#         abort(404)
#     else:
#         response.headers['Content-Disposition'] = 'filename={}'.format(os.path.basename(uri))
#         return response
