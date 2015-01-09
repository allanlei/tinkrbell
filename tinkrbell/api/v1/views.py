# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

from flask import Response, current_app, abort, request

import os

from wand.image import Image

from tinkrbell import extractors
from tinkrbell.utils import calculators
from tinkrbell.shortcuts import iconify, best_match

from . import application as app, cache


@app.route('/icon/<int:size>/<path:uri>', methods=['GET'])
@app.route('/icon/<path:uri>', methods=['GET'], endpoint='icon', defaults={'size': None})
@cache.cached()
def icon(uri, size):
    """
    Generates a multisize icon of a resource.
    """
    try:
        image = extractors.extract(uri)
    except AttributeError:
        current_app.logger.debug('URI not available')
        abort(404)
    except:
        current_app.logger.info(
            'Failed to extract image from URI', exc_info=True)
        abort(404)

    response = iconify(image, sizes=[size] if size else None)
    response.headers['Content-Disposition'] = 'filename={}.ico'.format(
        os.path.basename(uri))
    return response


@app.route('/preview/<int:width>x<int:height>/<path:uri>', methods=['GET'], endpoint='preview')
@cache.cached(key_prefix=lambda: 'view/(%s)/%s' % (request.accept_mimetypes, request.path))
def preview(uri, width, height):
    """
    Generates a preview of the URI returning the best image format supported by the browser.
    """
    try:
        image = extractors.extract(uri)
    except AttributeError:
        current_app.logger.debug('URI not available')
        abort(404)
    except:
        current_app.logger.info('Failed to extract image from URI', exc_info=True)
        abort(404)
    else:
        mimetype, format = best_match()

        with image:
            image.resize(*calculators.boundingbox(image, (width, height)))
            if format:
                image.format = format
            else:
                mimetype = image.mimetype
            response = Response(image.make_blob(), mimetype=mimetype)
            return response


@app.route('/resize/<int:width>x<int:height>/<path:uri>', methods=['GET'])
@cache.cached()
def resize_by_boundingbox(uri, width, height):
    """
    Generates a preview of the image at URI, returning a resized image in the same format
    """
    try:
        image = extractors.image(uri)
    except AttributeError:
        current_app.logger.debug('URI not available')
        abort(404)
    except:
        current_app.logger.info('Failed to extract image from URI', exc_info=True)
        abort(404)
    else:
        with image:
            image.resize(*calculators.boundingbox(image, (width, height)))
            response = Response(image.make_blob(), mimetype=image.mimetype)
            return response
