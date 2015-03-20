# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

from flask import current_app

import sys
import subprocess
import shlex


def ffmpeg(cmd, bin=None, loglevel=None, encoding=None, **kwargs):
    """
    Usage: ffmpeg('-rtbufsize 64M -i video="" -f', loglevel='error')
    """
    # FIX: Process doesnt end when rtmp is aborted
    bin = bin or current_app.config.get('FFMPEG_BIN') or 'ffmpeg'
    if '-loglevel' not in cmd:
        cmd = '-loglevel {loglevel}'.format(loglevel=loglevel or current_app.config.get('FFMPEG_LOGLEVEL') or 'error') + ' ' + cmd
    else:
        current_app.logger.debug('Skip loglevel append')
    cmd = '"{FFMPEG_BIN}" {cmd}'.format(FFMPEG_BIN=bin, cmd=cmd)

    current_app.logger.debug('Running: %s', cmd)

    if isinstance(cmd, unicode):
        encoding = encoding or sys.getfilesystemencoding()
        # current_app.logger.debug('Encoding command as %s', encoding)
        cmd = cmd.encode(encoding)

    kwargs.setdefault('close_fds', not any([
        kwargs.get('stdin'),
        kwargs.get('stdout'),
        kwargs.get('stderr'),
    ]))
    return subprocess.Popen(shlex.split(cmd), shell=False, **kwargs)


def ffprobe(cmd, bin=None, loglevel=None, encoding=None, **kwargs):
    """
    Usage: ffprobe()
    """
    bin = bin or current_app.config.get('FFMPEG_BIN') or 'ffprobe'
    if '-loglevel' not in cmd:
        cmd = '-loglevel {loglevel}'.format(loglevel=loglevel or current_app.config.get('FFPROBE_LOGLEVEL') or 'error') + ' ' + cmd
    else:
        current_app.logger.debug('Skip loglevel append')
    cmd = '"{FFPROBE_BIN}" {cmd}'.format(FFPROBE_BIN=bin, cmd=cmd)

    current_app.logger.debug('Running: %s', cmd)

    if isinstance(cmd, unicode):
        encoding = encoding or sys.getfilesystemencoding()
        # current_app.logger.debug('Encoding command as %s', encoding)
        cmd = cmd.encode(encoding)

    kwargs.setdefault('close_fds', not any([
        kwargs.get('stdin'),
        kwargs.get('stdout'),
        kwargs.get('stderr'),
    ]))
    return subprocess.Popen(shlex.split(cmd), shell=False, **kwargs)
