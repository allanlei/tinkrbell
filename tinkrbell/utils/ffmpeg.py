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

    def extract(self, query=(None, '-filter:v "fps=fps=1,thumbnail=5"'), frames=1, format='mjpeg', scale=None):
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
                try:
                    response = requests.head(src)
                except:
                    current_app.logger.info('Skipping remote file optimizations', exc_info=True)
                else:
                    if urlparse.urlparse(response.headers.get('Location') or '').scheme in ['file']:
                        self.src = response.headers['Location']
                        current_app.logger.debug(
                            """Switching protocols: %s -> %s\r\n\tOrigin: %s\r\n\tTo: %s""",
                            parsed.scheme, urlparse.urlparse(self.src).scheme,
                            src, self.src)
                    # else:
                    #     options.append('-multiple_requests 1')
                    if response.headers.get('Content-Type', None) in ['image/jpeg', 'image/jpg']:
                        options.append('-f jpeg_pipe')
            return ' '.join(options)

        # BUG(allanlei): If the remote file is a jpeg and the URL contains special characters, force jpeg_pipe (See https://trac.ffmpeg.org/ticket/4849)
        # FEATURE(allanlei): Output to rawvideo/rgba
        command = 'ffmpeg -v error {prequery} {input_options} -i "async:cache:{src}" {postquery} -frames:v {frames} -c:v {format} -filter:v "scale={scale}" -map_metadata -1 -an -sn -dn -f image2 pipe:1'.format(
            input_options=input_options(self.src),
            src=urlencode(self.src),
            format=format, frames=frames,
            scale=scale or boundingbox(3840, 2160),
            prequery=prequery or '',
            postquery=postquery or '',
        )

        cmd = shlex.split(command)
        if cmd.count('-filter:v') > 1:
            filters = b','.join([cmd[i + 1] for i, option in enumerate(cmd) if option == '-filter:v'])
            removals = [index for index, part in enumerate(cmd) if part == '-filter:v']
            for removal in reversed(sorted(removals)):
                cmd.pop(removal + 1)
                cmd.pop(removal)
            cmd.insert(len(cmd) - 1, b'-filter:v')
            cmd.insert(len(cmd) - 1, filters)

        current_app.logger.debug('Running: %s', ' '.join(cmd))
        try:
            return subprocess.check_output(cmd, stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as err:
            raise errors.FFmpegError(err.output)

    def icon(self, scale=None, seek=None):
        frames = self.extract(**({'query': ('-ss {}'.format(seek), None)} if seek is not None else {}))
        command = 'ffmpeg -v error -f image2pipe -c:v mjpeg -i pipe:0 {preset} -filter:v "scale={scale}" -f image2 pipe:1'.format(
            preset=PRESETS['ico'],
            scale=scale or '256:-1')
        current_app.logger.debug('Running: %s', command)
        process = subprocess.Popen(shlex.split(
            command
        ), stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate(frames)
        if process.returncode != 0:
            raise errors.FFmpegError(stderr)
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
        stdout, stderr = process.communicate(frames)
        if process.returncode != 0:
            raise errors.FFmpegError(stderr)
        return stdout

    def resize(self, scale):
        """
        Resize only

        Scales: https://ffmpeg.org/ffmpeg-filters.html#scale-1
            - Bounding box: W:H, W:-1, -1:H
            - Percentage: 100%
        """
        frame = self.extract(
            # query=('-f image2', None),
            # format='copy', scale='w:h',
        )
        current_app.logger.debug('Resize image: %s', scale)
        process = subprocess.Popen(shlex.split(
            'ffmpeg -v error -f image2pipe -i pipe:0 -filter:v "scale={scale}" -f image2 pipe:1'.format(
                scale=scale,
            ),
        ), stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate(frame)
        if process.returncode != 0:
            raise errors.FFmpegError(stderr)
        return stdout
