# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals


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


def boundingbox(image, (width, height)):
    # TODO: This is just a shortcut to calculate resize
    # NOTE: image.transform does not preserve animation
    with image.clone() as img:
        img.transform(resize='{:d}x{:d}>'.format(width, height))
        return img.width, img.height
