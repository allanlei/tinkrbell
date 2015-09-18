# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

import os


"""
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
AVAILABLE_ICON_SIZES = os.environ.get('AVAILABLE_ICON_SIZES', '').split() or (
    # 16, 32, 48, 96, 128, 256,
    16, 32, 48, 256,
)


EXTRACTORS = {
    ('image', '*'): 'tinkrbell.extractors.image',
    # ('image', 'jpeg'): image_jpeg,
    ('video', '*'): 'tinkrbell.extractors.video',
    # ('audio', '*'): audio,
    # ('text', '*'): text,
}


MAX_SCAN_TIME = 10.3
SCENE_CHANGE_THRESHOLD = 0.2
SCENE_SCAN_FPS = 0.5
