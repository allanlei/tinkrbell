# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

import os


AVAILABLE_ICON_SIZES = os.environ.get('AVAILABLE_ICON_SIZES', '').split() or (
    16, 32, 48, 96, 128, 256,
)


EXTRACTORS = {
    ('image', '*'): 'tinkrbell.extractors.image',
    # ('image', 'jpeg'): image_jpeg,
    ('video', '*'): 'tinkrbell.extractors.video',
    # ('audio', '*'): audio,
    # ('text', '*'): text,
}
