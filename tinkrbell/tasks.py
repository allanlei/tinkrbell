# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

from flask import current_app

import subprocess
import shlex
import gridfs

from mongoengine.connection import get_db

from . import celery


fs = gridfs.GridFS(get_db())


@celery.task(bind=True)
def generate(task, uri, size=None):
    if size is None:
        width = height = '-1'
    else:
        width, height = size

    profile = 'thumbnail:{width}x{height}'.format(width=width, height=height)
    asset = fs.find_one({
        'origin': uri, 'profile': profile,
    })
    if asset:
        return asset._id

    command = 'ffmpeg -v error -i "{uri}" -frames:v 1 -filter:v "fps=fps=1,thumbnail=10,scale={width}:{height}" -f mjpeg pipe:1'.format(
        uri=uri,
        width=width, height=height,
    )
    current_app.logger.debug(command)
    data = subprocess.check_output(shlex.split(command))

    gridfs_id = fs.put(data, content_type='image/jpeg', origin=uri, profile=profile)
    return gridfs_id
