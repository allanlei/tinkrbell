# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

from flask import Flask

import os


def get_application(root_path=None):
    app = Flask(__name__)
    app.config.from_object('tinkrbell.settings.defaults')
    if os.environ.get('SETTINGS_MODULE'):
        app.config.from_object(os.environ.get('SETTINGS_MODULE'))

    from . import cache
    cache.init_app(app)

    import tinkrbell.api.v1
    app.register_blueprint(tinkrbell.api.v1.application, url_prefix='/1')

    return app


app = get_application()
