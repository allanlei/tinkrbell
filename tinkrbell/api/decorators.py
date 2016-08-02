# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

from flask import current_app, after_this_request

import decorator


def vary(*headers):
    def _vary(f, *args, **kwargs):
        @after_this_request
        def zipper(response):
            response.vary = ' '.join(
                set(response.headers.get('Vary', '').split() + list(headers)))
            return response
        return f(*args, **kwargs)
    return decorator.decorator(_vary)


def authenticated():
    def _authenticated(f, *args, **kwargs):
        return f(*args, **kwargs)
    return decorator.decorator(_authenticated)
