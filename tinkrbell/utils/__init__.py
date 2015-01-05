# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

from flask import current_app
import mimetypes
import futures
import multiprocessing

from wand.image import Image


def mimetype(uri):
    """
    Gets the mimetype of a URI
    """
    mtype, __ = mimetypes.guess_type(uri)
    return mtype


def icon(image, size, multisized=False):
    """
    Converts an image file-like object into a ICO image
    """
    # def boundingbox((width, height), (bbw, bbh)):
    #     if max((width - bbw), (height - bbh)) > 0:
    #         if (width - bbw) > (height - bbh):
    #             resized_width = bbw
    #             resized_height = height / (width/resized_width)
    #         else:
    #             resized_height = bbh
    #             resized_width = width / (height/resized_height)
    #     else:
    #         resized_width, resized_height = width, height
    #     return int(resized_width), int(resized_height)
    def _icon(img, (width, height)):
        ico = Image(width=width, height=height)
        # image.resize(*boundingbox(image.size, (size, size)))
        # Note: image.transform does not preserve animation
        img.transform(resize='{:d}x{:d}>'.format(width, height))
        ico.composite(img,
            top=int((ico.height - img.height) / 2),
            left=int((ico.width - img.width) / 2),
        )
        return ico

    with _icon(image.clone(), (size, size)) as ico:
        if multisized:
            with futures.ThreadPoolExecutor(max_workers=multiprocessing.cpu_count()) as pool:
                jobs = {
                    pool.submit(_icon, image.clone(), (s, s)): (s, s)
                        for s in current_app.config['AVAILABLE_ICON_SIZES'] if s < size
                }

                for job in futures.as_completed(jobs):
                    width, height = jobs[job]
                    try:
                        multisizeico = job.result()
                    except:
                        current_app.logger.error(
                            'Could not generate icon: %dx%d', width, height, exc_info=True)
                    else:
                        ico.sequence.append(multisizeico)
                        current_app.logger.debug(
                            'Adding multisize icon: %dx%d', width, height)

        return ico.make_blob('ico')
