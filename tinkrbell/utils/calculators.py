# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals


def percentage(image, percent):
    return int(round(image.width * percent)), int(round(image.height * percent))


def boundingbox(image, (width, height)):
    reduction = max(
        (image.width - width) / image.width,
        (image.height - height) / image.height,
    )
    return percentage(image, 1 - reduction)
