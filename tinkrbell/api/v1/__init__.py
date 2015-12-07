# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

from flask import Blueprint
from flask.ext.cache import Cache


cache = Cache()
application = Blueprint('tinkrbell.apiv1', __name__)


from . import views
