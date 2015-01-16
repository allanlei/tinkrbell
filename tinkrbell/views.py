# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

from flask import make_response, Response, abort, current_app

from . import application as app


@app.route('/')
def healthcheck():
    return make_response()
