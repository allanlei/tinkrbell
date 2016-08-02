# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

from flask import Flask

import base64

from werkzeug.routing import BaseConverter, ValidationError
from itsdangerous import base64_encode, base64_decode
from bson.objectid import ObjectId
from bson.errors import InvalidId


class Base64Converter(BaseConverter):
    @classmethod
    def to_python(self, value):
        was_unicode = False
        if isinstance(value, unicode):
            was_unicode = True
            value = value.encode('utf-8')

        try:
            rv = base64.urlsafe_b64decode(value)
            if was_unicode:
                rv = rv.decode('utf-8')
        except (ValueError, TypeError):
            raise ValidationError()
        else:
            return rv

    @classmethod
    def to_url(self, value):
        was_unicode = False
        if isinstance(value, unicode):
            was_unicode = True
            value = value.encode('utf-8')

        rv = base64.urlsafe_b64encode(value)
        if was_unicode:
            rv = rv.decode('utf-8')
        return rv


class ObjectIDConverter(BaseConverter):
    @classmethod
    def to_python(cls, value):
        try:
            return ObjectId(base64_decode(value))
        except (InvalidId, ValueError, TypeError):
            raise ValidationError()

    @classmethod
    def to_url(cls, value):
        return base64_encode(value.binary)
