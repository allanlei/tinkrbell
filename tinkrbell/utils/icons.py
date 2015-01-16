# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

from flask import current_app
import mimetypes
import futures
import multiprocessing
import urlparse
import urllib

from wand.image import Image


def icon(image, sizes=None):
    """Converts an image file-like object into a ICO image"""
    def _icons_full(source, sizes):
        with source.clone() as image:
            for size in reversed(sorted(sizes)):
                image.transform(resize='{size:d}x{size:d}>'.format(size=size))
                yield image.clone()

    def _icons_full_filled(source, sizes):
        with source.clone() as image:
            for size in reversed(sorted(sizes)):
                image.transform(resize='{size:d}x{size:d}>'.format(size=size))

                with Image(width=size, height=size) as ico:
                    ico.composite(image,
                        top=int(round((ico.height - image.height) / 2)),
                        left=int(round((ico.width - image.width) / 2)),
                    )
                    yield ico.clone()

    def _icons_cropped(source, sizes):
        with source.clone() as image:
            crop_size = min(image.width, image.height)

            image.crop(
                int(round(image.width/2 - crop_size/2)), int(round(image.height/2 - crop_size/2)),
                width=crop_size, height=crop_size)
            for size in reversed(sorted(sizes)):
                image.transform(resize='{size:d}x{size:d}>'.format(size=size))
                yield image.clone()

    def _icons_liquid(source, sizes):
        with source.clone() as image:
            crop_size = min(image.width, image.height)

            for size in reversed(sorted(sizes)):
                image.liquid_rescale(size, size)
                yield image.clone()

    sizes = sizes or current_app.config['AVAILABLE_ICON_SIZES']
    icons = _icons_full(image, sizes=sizes)
    with icons.next() as ico:
        current_app.logger.debug('Added icon size: %dx%d', ico.width, ico.height)

        for subicon in icons:
            ico.sequence.append(subicon)
            current_app.logger.debug(
                'Added icon size: %dx%d', subicon.width, subicon.height)
        ico.strip()
        return ico.make_blob('ico')
