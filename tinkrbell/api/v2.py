# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

from flask import Blueprint, Response, redirect, url_for, current_app, request

import gridfs
from mongoengine.connection import get_db

# from tinkrbell import models


application = app = Blueprint('tinkrbell.apiv2', __name__)



@app.route('/i/<objectid:gridfs_id>', methods=['GET'], endpoint='gridfs')
def retrieve_image(gridfs_id):
    fs = gridfs.GridFS(get_db())
    asset = fs.find_one({
        '_id': gridfs_id,
    })
    return Response(asset.read(), content_type=asset.content_type)


@app.route('/preview/<b64:uri>', methods=['POST'], defaults={'width': '-1', 'height': '-1'})
@app.route('/preview/<int:width>x<int:height>/<b64:uri>', methods=['POST'])
def preview_prefetch(width, height, uri):
    from tinkrbell import tasks

    task = tasks.generate.apply_async(
        (uri, ), {'size': (width, height)},
    )
    return Response(), 201


@app.route('/preview/<b64:uri>', methods=['GET'], defaults={'width': '-1', 'height': '-1'})
@app.route('/preview/<int:width>x<int:height>/<b64:uri>', methods=['GET'])
def preview(width, height, uri):
    from tinkrbell import tasks

    task = tasks.generate.apply_async((uri, ), {'size': (width, height)})
    gridfs_id = task.get(timeout=10)

    return redirect(url_for('.gridfs', gridfs_id=gridfs_id))
