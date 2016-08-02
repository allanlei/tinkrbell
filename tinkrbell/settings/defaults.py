# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

import os


CELERY_RESULTS_BACKEND = os.environ.get('CELERY_RESULTS_BACKEND')
CELERY_BROKER = os.environ.get('CELERY_BROKER')

# MAX_SCAN_TIME = 10.3
# SCENE_CHANGE_THRESHOLD = 0.2
# SCENE_SCAN_FPS = 0.5

# CACHE_TYPE = 'filesystem'
# CACHE_DIR = '.cache'
# CACHE_DEFAULT_TIMEOUT = 60 * 60
# CACHE_THRESHOLD = 100
