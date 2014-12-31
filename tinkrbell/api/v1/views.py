# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

from flask import Response, current_app, abort

import os

from tinkrbell.utils import icon
from tinkrbell.extractors import extract

from . import application as app


@app.route('/thumbnail/<int:size>/<path:uri>', methods=['GET'], endpoint='thumbnail')
def thumbnail(size, uri):
    """Generates a icon thumbnail of a resource"""
    try:
        image_data = extract(uri)
    except:
        current_app.logger.info('Failed to extract image from URI', exc_info=True)
        abort(404)

    response = Response(
        icon(image_data, size=(size, size)),
        mimetype='image/x-icon')

    response.headers['Content-Disposition'] = 'filename={}.ico'.format(os.path.basename(uri))
    return response


# @app.route('/resize/<int:percentage>%/<path:uri>')
# def resize_by_percentage(percentage, uri):
#     pass


@app.route('/resize/<int:width>x<int:height>>/<path:uri>')
@app.route('/resize/<int:width>x<int:height>/<path:uri>')
def resize_by_boundingbox(width, height, uri):
    def boundingbox((width, height), (bbw, bbh)):
        if max((width - bbw), (height - bbh)) > 0:
            if (width - bbw) > (height - bbh):
                resized_width = bbw
                resized_height = height / (width/resized_width)
            else:
                resized_height = bbh
                resized_width = width / (height/resized_height)
        else:
            resized_width, resized_height = width, height
        return int(resized_width), int(resized_height)

    import contextlib
    import requests
    from wand.image import Image
    from werkzeug.contrib.iterio import IterIO

    with contextlib.closing(requests.get(uri, stream=True)) as response:
        response.raise_for_status()

        with Image(file=IterIO(response.iter_content(chunk_size=1 * 1024 * 1024))) as image:
            image.resize(*boundingbox((image.width, image.height), (width, height)))

            response = Response(image.make_blob(), mimetype=response.headers['content-type'])
            return response
