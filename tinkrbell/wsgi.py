# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

from flask import Flask
# from flask.ext import transformers

import os


def get_application(root_path=None):
    app = Flask(__name__, static_folder='static')

    app.config.from_object('tinkrbell.settings.defaults')
    if os.environ.get('SETTINGS_MODULE'):
        app.config.from_object(os.environ.get('SETTINGS_MODULE'))

    # app.url_map.converters['b64_path'] = transformers.Base64PathConverter
    # app.url_map.converters['regex'] = transformers.RegexConverter
    # app.json_encoder = transformers.JSONEncoder

    from . import cache
    import tinkrbell.api.v1
    cache.init_app(app, config={'CACHE_TYPE': 'simple'})
    tinkrbell.api.v1.cache.init_app(app, config={'CACHE_TYPE': 'simple'})

    import tinkrbell
    import tinkrbell.api.v1
    app.register_blueprint(tinkrbell.application)
    app.register_blueprint(tinkrbell.api.v1.application, url_prefix='/1')

    return app
