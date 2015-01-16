# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

from flask import current_app

import subprocess
import shlex
import contextlib
import requests
import datetime

from wand.image import Image
from wand.font import Font
from werkzeug.contrib.iterio import IterIO

from tinkrbell import cache, utils
from tinkrbell.utils import mimetype
from tinkrbell.utils.ffmpeg import ffmpeg


def image(uri, size=None):
    @cache.memoize()
    def _image(uri):
        current_app.logger.debug('Fetching %s', uri)
        with contextlib.closing(requests.get(uri, stream=True)) as response:
            response.raise_for_status()
            return response.content
    return Image(blob=_image(uri))


def video(uri, size=None, clip_at=None):
    @cache.memoize()
    def _video(uri):
        # ffmpeg -ss 3 -i input.mp4 -vf "select=gt(scene\,0.4)" -frames:v 5 -vsync vfr fps=fps=1/600 out%02d.jpg
        # ffmpeg -ss 3 -i ~/Videos/b.mov -vf "select=gt(scene\,0.2)" -vsync vfr -f image2 out%02d.jpg
        # ffmpeg -i ~/Videos/sintel_4k.mov -vf "select=gt(scene\,0.01)" -vf "select=gte(t\,15)" -vsync vfr -vframes 1 -f image2 -y poster.jpg
        # ffmpeg -ss 3 -i ~/Videos/b.mmov -vf "select=gt(scene\,0.5)" -vsync vfr -frames:v 1 -f image2 -y poster.jpg

        process = ffmpeg('-loglevel debug -i "{input}" -vf "select=gte(scene\,0.1)" -vsync vfr -frames:v 1 -sn -dn -an -f {format} {output}'.format(
            input=utils.uri(uri), output='pipe:1',
            format='image2',
            # size=size_filter,
            clip_at='-ss {}'.format(clip_at) if clip_at else '',
        ), stdout=subprocess.PIPE)

        stdout, __ = process.communicate()
        if process.returncode != 0:
            raise Exception('ffmpeg error')
        return stdout
    return Image(blob=_video(uri))


def audio(uri, size=None):
    @cache.memoize()
    def _audio(uri):
        process = ffmpeg('-i "{input}" -frames:v 1 -an -dn -sn -f {format} {output}'.format(
            input=utils.uri(uri), output='pipe:1',
            format='image2',
        ), stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        stdout, stderr = process.communicate()
        if process.returncode != 0:
            raise Exception(stderr)
        return stdout
    return Image(blob=_audio(uri))


def text(uri, size=None, font='/home/intrepid/.fonts/Roboto-Black.ttf'):
    width, height = size or (256, 256)
    padding = 0

    with contextlib.closing(requests.get(uri, stream=True)) as response:
        response.raise_for_status()
        fp = IterIO(response.iter_content(chunk_size=1 * 1024 * 1024))

        image = Image(width=width, height=height)
        content = fp.read(1 * 1024).decode('utf-8')
        image.caption(content,
            left=padding, top=padding,
            width=width - padding, height=height - padding,
            font=Font(path=font, size=12))
        return image


EXTRACTORS = {
    ('image', '*'): image,
    ('video', '*'): video,
    ('audio', '*'): audio,
    ('text', '*'): text,
}


# @cache.memoize(timeout=datetime.timedelta(minutes=1).total_seconds())
def extract(uri):
    type, subtype = mimetype(uri).split('/', 2)
    extractor = EXTRACTORS.get((type, subtype)) or EXTRACTORS.get((type, '*'))
    current_app.logger.debug(
        'Using image extractor %s.%s for (%s/%s)', extractor.__module__, extractor.__name__, type, subtype)
    # TODO: cache the response
    return extractor(uri)
