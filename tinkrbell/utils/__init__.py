# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

import mimetypes

from wand.image import Image


def mimetype(uri):
    """
    Gets the mimetype of a URI
    """
    mtype, __ = mimetypes.guess_type(uri)
    return mtype


def icon(image, size):
    """
    Converts an image file-like object into a ICO image
    Available sizes: 16x16, 32x32, 48x48, 96x96, 128x128, 256x256
    """
    # def boundingbox((width, height), (bbw, bbh)):
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
    try:
        width, height = size
    except:
        width, height = size, size

    with Image(width=width, height=height) as ico:
        # image.resize(*boundingbox(image.size, (size, size)))
        image.transform(resize='{:d}x{:d}>'.format(width, height))
        ico.composite(image,
            top=int((height - image.height) / 2),
            left=int((width - image.width) / 2),
        )
        return ico.make_blob('ico')
