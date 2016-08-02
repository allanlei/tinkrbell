# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

import subprocess
import shlex

from tinkrbell import errors


def run(inputfile, output_format, pre=None, post=None):
    command = ''

    try:
        data = subprocess.check_output(shlex.split(command))
    except Exception:
        raise errors.FFmpegError('')
    return data
