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
from tinkrbell.utils.ffmpeg import ffmpeg, ffprobe


class ExtractionError(Exception):
    pass


def image(uri, size=None, timeout=None):
    @cache.memoize()
    def _image(uri):
        current_app.logger.debug('Fetching %s', uri)
        with contextlib.closing(requests.get(uri, stream=True)) as response:
            response.raise_for_status()
            return response.content
    return Image(blob=_image(uri))


def video(uri, size=None, timeout=None, probesize=None):
    @cache.memoize()
    def _video(uri):
        duration = float(ffprobe(
            '-show_entries format=duration -of csv="p=0" "{input}"'.format(input=utils.uri(uri)),
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        ).communicate()[0].strip())

        process = ffmpeg('-i "{input}" -vf "fps=fps={scan_fps},select=gte(t\,{max_scan_time})+gte(scene\,{scene_change})" -vsync vfr -frames:v 1 -sn -dn -an -f {format} {output}'.format(
            input=utils.uri(uri), output='pipe:1',
            format='image2',
            # Frame selection:
            #   - Scan rate 1 FPS
            #   - max scan time of t=10s
            #   - > 40% scene change
            scan_fps=1, max_scan_time=int(min(duration, 10)), scene_change=0.4,
        ), stdout=subprocess.PIPE)

        stdout, __ = process.communicate()
        if process.returncode != 0:
            raise ExtractionError('FFmpeg error {}'.format(process.returncode))
        return stdout
    return Image(blob=_video(uri))


def audio(uri, size=None, timeout=None):
    @cache.memoize()
    def _audio(uri):
        process = ffmpeg('-i "{input}" -frames:v 1 -an -dn -sn -f {format} {output}'.format(
            input=utils.uri(uri), output='pipe:1',
            format='image2',
        ), stdout=subprocess.PIPE)

        stdout, stderr = process.communicate()
        if process.returncode != 0:
            raise ExtractionError('FFmpeg error {}'.format(process.returncode))
        return stdout
    return Image(blob=_audio(uri))


def text(uri, size=None, font='Roboto-Black.ttf', timeout=None):
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
    # ('text', '*'): text,
}


# @cache.memoize(timeout=datetime.timedelta(minutes=1).total_seconds())
def extract(uri, timeout=datetime.timedelta(seconds=5).total_seconds()):
    type, subtype = mimetype(uri).split('/', 2)
    extractor = EXTRACTORS.get((type, subtype)) or EXTRACTORS.get((type, '*'))
    current_app.logger.debug(
        'Using image extractor %s.%s for (%s/%s)', extractor.__module__, extractor.__name__, type, subtype)
    # TODO: cache the response
    return extractor(uri, timeout=timeout)
