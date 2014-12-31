# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

from flask import current_app

import subprocess
import shlex
import contextlib
import requests

from wand.image import Image
from wand.font import Font
from werkzeug.contrib.iterio import IterIO

from tinkrbell.utils import mimetype
from tinkrbell.utils.ffmpeg import ffmpeg


def default(fp, preset):
    return


def image(uri, size=None, default=None):
    with contextlib.closing(requests.get(uri, stream=True)) as response:
        response.raise_for_status()
        return Image(file=IterIO(response.iter_content(chunk_size=1 * 1024 * 1024)))


def video(uri, size=None, clip_at=None, default=None):
    # size_filter = ''
    # if size:
    #     size_filter = '-s {}'.format(size) if size else ''
    # elif quality:
    #     size_filter = '-vf scale="trunc(oh*a/2)*2:{}"'.format(quality) if quality else ''

    process = ffmpeg('{clip_at} -i "{input}" -vframes 1 -f {format} {output}'.format(
        input=uri, output='pipe:1',
        format='image2',
        # size=size_filter,
        clip_at='-ss {}'.format(clip_at) if clip_at else '',
    ), stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    stdout, stderr = process.communicate()
    if process.returncode != 0:
        raise Exception(stderr)
    return Image(blob=stdout)


def audio(uri, size=None, default=None):
    process = ffmpeg('-i "{input}" -an -dn -sn -vframes 1 -f {format} {output}'.format(
        input=uri, output='pipe:1',
        format='image2',
        # size=size_filter,
        # clip_at='-ss {}'.format(clip_at) if clip_at else '',
    ), stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    stdout, stderr = process.communicate()
    if process.returncode != 0:
        raise Exception(stderr)
    return Image(blob=stdout)


def text(uri, size=None):
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
            font=Font(path='/home/intrepid/.fonts/Roboto-Black.ttf', size=12))
        return image


EXTRACTORS = {
    ('image', '*'): image,
    ('video', '*'): video,
    ('audio', '*'): audio,
    ('text', '*'): text,
}


def extract(uri):
    type, subtype = mimetype(uri).split('/', 2)
    extractor = EXTRACTORS.get((type, subtype)) or EXTRACTORS.get((type, '*'))
    current_app.logger.debug(
        'Using preview generator: (%s/%s) %s.%s', type, subtype, extractor.__module__, extractor.__name__)
    return extractor(uri)
