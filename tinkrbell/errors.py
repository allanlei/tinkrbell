# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals


class FFmpegError(Exception):
    def __init__(self, message, process):
        super(FFmpegError, self).__init__(message)
        self.process = process
