# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

from flask import Response, current_app, abort, request

import os

from wand.image import Image

from tinkrbell.utils import icon
from tinkrbell import extractors

from . import application as app, cache


@app.route('/thumbnail/<int:size>/<path:uri>', methods=['GET'], defaults={'multisized': False})
@app.route('/thumbnail/<path:uri>', methods=['GET'], endpoint='thumbnail', defaults={'size': 256, 'multisized': True})
@app.route('/icon/<int:size>/<path:uri>', methods=['GET'], defaults={'multisized': False})
@app.route('/icon/<path:uri>', methods=['GET'], endpoint='icon', defaults={'size': 256, 'multisized': True})
@cache.cached()
def icon(size, uri, multisized):
    """
    Generates a multisize icon of a resource.

    Sizes:
        - 256x256 will be saved as 32bpp 8bit alpha
        - 48x48 will be saved as 32bpp 8bit alpha
        - 48x48 will be saved as 8bpp 1bit alpha
        - 32x32 will be saved as 32bpp 8bit alpha
        - 32x32 will be saved as 8bpp 1bit alpha
        - 32x32 will be saved as 4bpp 1bit alpha
        - 16x16 will be saved as 32bpp 8bit alpha
        - 16x16 will be saved as 8bpp 1bit alpha
        - 16x16 will be saved as 4bpp 1bit alpha
    """
    try:
        image = extractors.extract(uri)
    except AttributeError:
        current_app.logger.debug('URI not available')
        abort(404)
    except:
        current_app.logger.info('Failed to extract image from URI', exc_info=True)
        abort(404)

    response = Response(
        icon(image, size=size, multisized=multisized),
        mimetype='image/x-icon')
    response.headers['Content-Disposition'] = 'filename={}.ico'.format(
        os.path.basename(uri))
    return response


# @app.route('/resize/<int:width>x<int:height>>/<path:uri>', methods=['GET'])
@app.route('/resize/<int:width>x<int:height>/<path:uri>', methods=['GET'])
@cache.cached()
def resize_by_boundingbox(width, height, uri):
    """
    Generates a preview of the image at URI, returning a resized image in the same format
    """
    # def boundingbox(image, (bbw, bbh)):
    #     if max((width - bbw), (height - bbh)) > 0:
    #         if (width - bbw) > (height - bbh):
    #             resized_width = bbw
    #             resized_height = height / (width/resized_width)
    #         else:
    #             resized_height = bbh
    #             resized_width = width / (height/resized_height)
    #     else:
    #         resized_width, resized_height = width, height
    #     return int(resized_width), int(resized_height)

    def boundingbox(image, width, height):
        # TODO: This is just a shortcut to calculate resize
        # NOTE: image.transform does not preserve animation
        with image.clone() as img:
            img.transform(resize='{:d}x{:d}>'.format(width, height))
            return img.width, img.height

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
            # image.resize(*boundingbox(image, (width, height)))
            image.resize(*boundingbox(image, width, height))
            response = Response(image.make_blob(), mimetype=image.mimetype)
            return response
