# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

from flask import current_app

import subprocess
import shlex
import re
import urlparse
import requests

from werkzeug.utils import cached_property

from tinkrbell import errors
from tinkrbell.utils import urlencode


PRESETS = {
    'webp-high': '-c:v libwebp -q:v 100',
    'webp-medium': '-c:v libwebp -q:v 90',
    'webp-low': '-c:v libwebp -q:v 30',

    'jpg-high': '-c:v mjpeg -q:v 0',
    'jpg-medium': '-c:v mjpeg -q:v 10',
    'jpg-low': '-c:v mjpeg -q:v 60',

    # 'pjpeg': '-c:v mjpeg -q:v 0',

    'png': '-c:v png',
    'ico': '-c:v bmp',
}
PRESETS['jpg'] = PRESETS['jpg-medium']
PRESETS['webp'] = PRESETS['webp-medium']
MIMETYPE_PATTERN = re.compile(r'^Stream #0:0: \w+: (?P<type>\w+),')
TYPES = {
    'png': 'image/png',
    'mjpeg': 'image/jpeg',
    'gif': 'image/gif',
    'bmp': 'image/bmp',
}


def boundingbox(width, height):
    if width is not None and height is None:
        height = '-1'
    elif width is None and height is not None:
        width = '-1'
    else:
        width = 'iw*min({width}/iw\,{height}/ih)'.format(width=width, height=height)
        height = 'ih*min({width}/iw\,{height}/ih)'.format(width=width, height=height)
    return '{width}:{height}'.format(width=width, height=height)


class Media(object):
    def __init__(self, src):
        self.src = src

    @cached_property
    def mimetype(self):
        process = subprocess.Popen(shlex.split(
            'ffmpeg -v info -i "{src}"'.format(src=self.src)
        ), stderr=subprocess.PIPE)
        __, stderr = process.communicate()
        for line in stderr.splitlines():
            matched = MIMETYPE_PATTERN.match(line.strip())
            if matched:
                return TYPES.get(matched.groupdict().get('type'))

    def extract(self, query=(None, '-filter:v "fps=fps=0.5,select=between(t\,0\,10)+gte(scene\,0.4)" -vsync vfr'), frames=1, format='mjpeg', scale=None):
        """
        Extracts an "interesting" image from media source, if possible.
        """
        if isinstance(query, (tuple, list)):
            prequery, postquery = query
        else:
            prequery, postquery = None, query

        def input_options(src):
            options = []
            parsed = urlparse.urlparse(src)
            if parsed.scheme in ['http', 'https']:
                options.append('-multiple_requests 1')

                try:
                    response = requests.head(src)
                except:
                    current_app.logger.info('Skipping remote file optimizations', exc_info=True)
                else:
                    if response.headers.get('Content-Type', None) in ['image/jpeg', 'image/jpg']:
                        options.append('-f jpeg_pipe')
            return ' '.join(options)

        # BUG(allanlei): If the remote file is a jpeg and the URL contains special characters, force jpeg_pipe (See https://trac.ffmpeg.org/ticket/4849)
        # FEATURE(allanlei): If the src is http/https, do a HEAD request and check if header "Location: file://..."
        # FEATURE(allanlei): Output to rawvideo/rgba
        command = 'ffmpeg -v error {prequery} {input_options} -i "async:cache:{src}" {postquery} -frames:v {frames} -c:v {format} -filter:v "scale={scale}" -map_metadata -1 -an -sn -dn -f image2 pipe:1'.format(
            src=urlencode(self.src),
            input_options=input_options(self.src),
            format=format, frames=frames,
            scale=scale or boundingbox(3840, 2160),
            prequery=prequery or '',
            postquery=postquery or '',
        )
        current_app.logger.debug('Running: %s', command)
        try:
            return subprocess.check_output(shlex.split(command))
        except subprocess.CalledProcessError as err:
            raise err

    def icon(self, scale=None, seek=None):
        frames = self.extract(**({'query': ('-ss {}'.format(seek), None)} if seek is not None else {}))
        command = 'ffmpeg -v error -f image2pipe -c:v mjpeg -i pipe:0 {preset} -filter:v "scale={scale}" -f image2 pipe:1'.format(
            preset=PRESETS['ico'],
            scale=scale or '256:-1')
        current_app.logger.debug('Running: %s', command)
        process = subprocess.Popen(shlex.split(
            command
        ), stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        stdout, __ = process.communicate(frames)
        return stdout

    def preview(self, scale, format=None, seek=None):
        frames = self.extract(
            # frames=10,
            **({'query': ('-ss {}'.format(seek), None)} if seek is not None else {})
        )
        command = 'ffmpeg -v error -f image2pipe -c:v mjpeg -i pipe:0 {preset} -filter:v "scale={scale}" -f image2 pipe:1'.format(
            preset=PRESETS[format or 'jpg'],
            scale=scale)
        current_app.logger.debug('Running: %s', command)
        process = subprocess.Popen(shlex.split(
            command,
        ), stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        # current_app.logger.debug('Generating preview: %s', '{width}:{height}'.format(width=width or '-1', height=height or '-1'))

        stdout, stderr = process.communicate(frames)
        if process.returncode != 0:
            raise errors.FFmpegError(stderr, process)
        return stdout

    def resize(self, scale):
        """
        Resize only

        Scales: https://ffmpeg.org/ffmpeg-filters.html#scale-1
            - Bounding box: W:H, W:-1, -1:H
            - Percentage: 100%
        """
        frame = self.extract(
            query=('-f image2', None),
            # format='copy', scale='w:h',
        )
        current_app.logger.debug('Resize image: %s', scale)
        process = subprocess.Popen(shlex.split(
            'ffmpeg -v error -f image2pipe -i pipe:0 -filter:v "scale={scale}" -f image2 pipe:1'.format(
                scale=scale,
            ),
        ), stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        stdout, __ = process.communicate(frame)
        return stdout


# def ffmpeg(cmd, bin=None, loglevel=None, encoding=None, **kwargs):
#     """
#     Usage: ffmpeg('-rtbufsize 64M -i video="" -f', loglevel='error')
#     """
#     # FIX: Process doesnt end when rtmp is aborted
#     bin = bin or current_app.config.get('FFMPEG_BIN') or 'ffmpeg'
#     if '-loglevel' not in cmd:
#         cmd = '-loglevel {loglevel}'.format(loglevel=loglevel or current_app.config.get('FFMPEG_LOGLEVEL') or 'error') + ' ' + cmd
#     else:
#         current_app.logger.debug('Skip loglevel append')
#     cmd = '"{FFMPEG_BIN}" {cmd}'.format(FFMPEG_BIN=bin, cmd=cmd)
#
#     current_app.logger.debug('Running: %s', cmd)
#
#     if isinstance(cmd, unicode):
#         encoding = encoding or sys.getfilesystemencoding()
#         # current_app.logger.debug('Encoding command as %s', encoding)
#         cmd = cmd.encode(encoding)
#
#     kwargs.setdefault('close_fds', not any([
#         kwargs.get('stdin'),
#         kwargs.get('stdout'),
#         kwargs.get('stderr'),
#     ]))
#     return subprocess.Popen(shlex.split(cmd), shell=False, **kwargs)
#
#
# def ffprobe(cmd, bin=None, loglevel=None, encoding=None, **kwargs):
#     """
#     Usage: ffprobe()
#     """
#     bin = bin or current_app.config.get('FFPROBE_BIN') or 'ffprobe'
#     if '-loglevel' not in cmd:
#         cmd = '-loglevel {loglevel}'.format(loglevel=loglevel or current_app.config.get('FFPROBE_LOGLEVEL') or 'error') + ' ' + cmd
#     else:
#         current_app.logger.debug('Skip loglevel append')
#     cmd = '"{FFPROBE_BIN}" {cmd}'.format(FFPROBE_BIN=bin, cmd=cmd)
#
#     current_app.logger.debug('Running: %s', cmd)
#
#     if isinstance(cmd, unicode):
#         encoding = encoding or sys.getfilesystemencoding()
#         # current_app.logger.debug('Encoding command as %s', encoding)
#         cmd = cmd.encode(encoding)
#
#     kwargs.setdefault('close_fds', not any([
#         kwargs.get('stdin'),
#         kwargs.get('stdout'),
#         kwargs.get('stderr'),
#     ]))
#     return subprocess.Popen(shlex.split(cmd), shell=False, **kwargs)
