# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals


EXTRACTORS = {
    ('image', '*'): 'tinkrbell.extractors.image',
    # ('image', 'jpeg'): image_jpeg,
    ('video', '*'): 'tinkrbell.extractors.video',
    # ('audio', '*'): audio,
    # ('text', '*'): text,
}
