# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

import re
import requests
import urlparse

from wand.image import Image

from turbo import errors


def calculate_by_percentage((width, height), percentage):
    percentage = int(percentage) / 100.0
    return width * percentage, height * percentage


def calculate_by_width((width, height), resized_width):
    resized_width = int(resized_width)
    return resized_width, height / (width/resized_width)


def calculate_by_height((width, height), resized_height):
    resized_height = int(resized_height)
    return width / (height/resized_height), resized_height


def calculate_by_exact((width, height), resized_width, resized_height):
    resized_width, resized_height = int(resized_width), int(resized_height)
    return resized_width, resized_height


def calculate_by_boundingbox((width, height), max_width, max_height):
    bbw, bbh = int(max_width), int(max_height)

    if max((width - bbw), (height - bbh)) > 0:
        if (width - bbw) > (height - bbh):
            resized_width = bbw
            resized_height = height / (width/resized_width)
        else:
            resized_height = bbh
            resized_width = width / (height/resized_height)
    else:
        resized_width, resized_height = width, height
    return resized_width, resized_height

ROUTING = {
    re.compile(r'^(?P<percentage>[0-9]+)%$'): calculate_by_percentage,
    re.compile(r'^(?P<resized_width>[0-9]+)x$'): calculate_by_width,
    re.compile(r'^x(?P<resized_height>[0-9]+)$'): calculate_by_height,
    re.compile(r'^(?P<resized_width>[0-9]+)x(?P<resized_height>[0-9]+)$'): calculate_by_exact,
    re.compile(r'^(?P<max_width>[0-9]+)x(?P<max_height>[0-9]+)>$'): calculate_by_boundingbox,
}


def resize(uri, scale):
    def get_image(uri):
        parsed = urlparse.urlparse(uri)
        if parsed.scheme in ['http', 'https']:
            response = requests.get(uri)
            response.raise_for_status()
            image = Image(blob=response.content)
        else:
            image = Image(uri)
        return image


    def calculate(image, scale):
        """
        This is a utility function to mirror the functionality if resize used
        image.transform, which is not compatible with some image formats.

        Valid formats
            - 200% = Set image size by 2
            - 100% = Normal size, no change
            - 200x = Set width to 200px and scale height accordingly
            - x200 = set height to 200px and scale width accordingly
            - 200x200> = Scale image to fit inside bounding box 200x200
        """
        width, height = image.width, image.height

        for regex, handler in ROUTING.items():
            matched = regex.match(scale)

            if matched:
                resized_width, resized_height = handler((width, height), **matched.groupdict())
                return int(resized_width), int(resized_height)
        raise errors.UnknownTransform('Unable to calculate resized dimensions')


    with get_image(uri) as image:
        resized_width, resized_height = calculate(image, scale)
        image.resize(resized_width, resized_height)
        return image.make_blob()
