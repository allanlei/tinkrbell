# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

import os
import unittest
import tinkrbell.wsgi


MEDIA = {
    'video1': os.path.join(os.path.dirname(os.path.abspath(__file__)), 'video1.mp4'),
}


class FlaskrTestCase(unittest.TestCase):
    def setUp(self):
        app = tinkrbell.wsgi.app
        app.config.update({
            'TESTING': True,
        })
        self.app = app.test_client()
        # with flaskr.app.app_context():
        #     flaskr.init_db()

    # def tearDown(self):
    #     pass

    def test_icon(self):
        pass

    def test_preview(self):
        rv = self.app.get('/1/preview/100x100/file:' + MEDIA['video1'])
        assert rv.status_code == 200

    def test_resize(self):
        pass


if __name__ == '__main__':
    unittest.main()
