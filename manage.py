#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, unicode_literals, print_function

import os
import sys

from flask import current_app
from flask.ext import script

import tinkrbell.wsgi


application = tinkrbell.wsgi.get_application()
manager = script.Manager(application)


class Shell(script.Shell):
    def get_context(self):
        context = super(Shell, self).get_context()
        context.update({'current_app': current_app})
        return context


manager.add_command('shell', Shell())
manager.add_command('runserver', script.Server(port=8000))


if __name__ == '__main__':
    manager.run()
