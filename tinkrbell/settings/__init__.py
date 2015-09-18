# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

import os
import random


DEBUG = False
TESTING = False
SECRET_KEY = os.environ.get('SECRET_KEY') or '{:030x}'.format(random.randrange(16 ** 30))
JSON_AS_ASCII = False
TIME_ZONE = os.environ.get('TIME_ZONE', 'UTC')
