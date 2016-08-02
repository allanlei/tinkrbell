# -*- coding: utf-8 -*-
"""
___________.__          __           ___.            .__   .__
\__    ___/|__|  ____  |  | _________\_ |__    ____  |  |  |  |
  |    |   |  | /    \ |  |/ /\_  __ \| __ \ _/ __ \ |  |  |  |
  |    |   |  ||   |  \|    <  |  | \/| \_\ \\  ___/ |  |__|  |__
  |____|   |__||___|  /|__|_ \ |__|   |___  / \___  >|____/|____/
                    \/      \/            \/      \/
"""
from __future__ import absolute_import, division, print_function, unicode_literals

from flask.ext.cache import Cache

__version__ = '1.0.0'
__all__ = ['cache']

cache = Cache()


from flask import Flask

import os

from . import transformers


# def get_application(root_path=None):
app = Flask(__name__)
app.config.from_object('tinkrbell.settings.defaults')
if os.environ.get('SETTINGS_MODULE'):
    app.config.from_object(os.environ.get('SETTINGS_MODULE'))

app.url_map.converters['b64'] = transformers.Base64Converter

from . import cache
cache.init_app(app)

import tinkrbell.api.v1
app.register_blueprint(tinkrbell.api.v1.application, url_prefix='/1')


from celery import Celery


def make_celery(app):
    celery = Celery(
        app.import_name,
        backend=app.config['CELERY_RESULTS_BACKEND'],
        broker=app.config['CELERY_BROKER'],
    )
    celery.conf.update(app.config)
    TaskBase = celery.Task

    class ContextTask(TaskBase):
        abstract = True

        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)

    celery.Task = ContextTask
    return celery


celery = make_celery(app)
from . import tasks
