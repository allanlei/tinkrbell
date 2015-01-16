# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

from flask import Response, current_app, abort, request

import os
import base64
import binascii

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
    return iconify(image, sizes=[size] if size else None)


def preview_key_fn():
    return 'view/({UA})/{path}'.format(
        UA=base64.b64encode(bytes([
            binascii.crc32(bytes(request.accept_mimetypes)),
        ])),
        path=request.path,
    )

@app.route('/preview/<int:width>x<int:height>/<path:uri>', methods=['GET'], endpoint='preview')
@cache.cached(key_prefix=preview_key_fn)
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
            image.compression_quality = 80
            image.resize(*calculators.boundingbox(image, (width, height)))

            if format:
                image.format = format
            else:
                mimetype = image.mimetype

            if image.format.lower() == 'jpeg':
                image.format = 'pjpeg'

            current_app.logger.debug('Generating preview in %s of %s', image.format, uri)
            return Response(image.make_blob(), mimetype=mimetype)


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
            return Response(image.make_blob(), mimetype=image.mimetype)
