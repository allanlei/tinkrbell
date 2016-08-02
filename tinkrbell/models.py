# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

from flask import current_app

from tinkrbell import mongo as db

import datetime


class Media(db.Document):
    # class Asset(db.EmbeddedDocument):
    #     creation_datetime = db.DateTimeField()
    #     asset_type = db.StringField()
    #     media = db.FileField()
    #
    #     def __repr__(self):
    #         return '<{}: {}>'.format(*self.asset_type.split(':', 1))
    #
    #     def generate(self):
    #         if self.media.grid_id:
    #             return
    #
    #         current_app.logger.info('Generating {profile} for {uri}'.format(
    #             profile=self.asset_type, uri=self._instance.uri,
    #         ))
    #
    #         type, options = self.asset_type.split(':', 1)
    #         width, height = options.split('x', 1)
    #
    #         import subprocess
    #         import shlex
    #         import io
    #
    #         command = 'ffmpeg -v error -i "{uri}" -frames:v 1 -filters:v "fps=fps=1,thumbnail=3,scale={width}x{height}" -f mjpeg pipe:1'.format(
    #             uri=self._instance.uri,
    #             width=width, height=height,
    #         )
    #         data = subprocess.check_output(shlex.split(command))
    #         # print(io.BytesIO(data))
    #         self.media.put(io.BytesIO(data), content_type='image/jpeg')
    #         # self.media.save()
    #         # print(self.media)
    #         self._instance.save()
    #

    creation_datetime = db.DateTimeField(default=datetime.datetime.now)
    expire_at = db.DateTimeField()
    # assets = db.EmbeddedDocumentListField(Asset)
    assets = db.ListField(db.FileField())

    meta = {
        'strict': False,
        'allow_inheritance': True,
        'indexes': [
            {'fields': ['expire_at'], 'expireAfterSeconds': 0},
        ],
    }


class UploadedMedia(Media):
    media = db.FileField()

    meta = {
        'strict': False,
        'indexes': [
            {'fields': ['media']},
        ],
    }

    @property
    def uri(self):
        return 'mongodb://...'


class ReferencedMedia(Media):
    uri = db.URLField()

    meta = {
        'strict': False,
        'allow_inheritance': True,
        'indexes': [
            {'fields': ['uri']},
        ],
    }

    # def __repr__(self):
    #     return ''

    # @property
    # def media(self):
    #     pass


# from mongoengine import signals


# @signals.pre_save_post_validation.connect_via(ReferencedMedia)
# @signals.pre_save_post_validation.connect_via(Media)
# @signals.pre_save_post_validation.connect_via(UploadedMedia)
# def debug2(sender, document, created=False, **kwargs):
#     # document
#     # document.assets
#     print('pre_save', sender, document, kwargs)
#
#
# @signals.post_save.connect_via(Media)
# @signals.post_save.connect_via(ReferencedMedia)
# @signals.post_save.connect_via(UploadedMedia)
# def debug(sender, document, created=False, **kwargs):
#     print('post_save', sender, document, kwargs)
