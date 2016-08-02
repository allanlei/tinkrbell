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

__version__ = '1.0.0'
__all__ = ['cache']

from flask import Flask
from flask.ext.cache import Cache
from flask_mongoengine import MongoEngine

import os


cache = Cache()
mongo = MongoEngine()


# def get_application(root_path=None):
app = Flask(__name__)
app.config.from_object('tinkrbell.settings.defaults')
if os.environ.get('SETTINGS_MODULE'):
    app.config.from_object(os.environ.get('SETTINGS_MODULE'))

from . import transformers
app.url_map.converters['b64'] = transformers.Base64Converter
app.url_map.converters['objectid'] = transformers.ObjectIDConverter

from . import cache
cache.init_app(app)
mongo.init_app(app)

import tinkrbell.api.v1
import tinkrbell.api.v2
app.register_blueprint(tinkrbell.api.v1.application, url_prefix='/1')
app.register_blueprint(tinkrbell.api.v2.application, url_prefix='/2')


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
