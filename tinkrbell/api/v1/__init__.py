# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

from flask import Blueprint, make_response
from flask.ext.cache import Cache


cache = Cache()
application = app = Blueprint('tinkrbell.apiv1', __name__)


@app.route('/', endpoint='healthcheck')
def healthcheck():
    return make_response()


from . import views
