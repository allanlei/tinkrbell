# -*- coding: utf-8 -*-
"""
___________.__          __           ___.            .__   .__   
\__    ___/|__|  ____  |  | _________\_ |__    ____  |  |  |  |  
  |    |   |  | /    \ |  |/ /\_  __ \| __ \ _/ __ \ |  |  |  |  
  |    |   |  ||   |  \|    <  |  | \/| \_\ \\  ___/ |  |__|  |__
  |____|   |__||___|  /|__|_ \ |__|   |___  / \___  >|____/|____/
                    \/      \/            \/      \/             
"""
from __future__ import absolute_import, division, print_function, unicode_literals

__version__ = '1.0.0'
__all__ = ['application', 'cache']


from flask.ext.cache import Cache

cache = Cache()


from flask import Blueprint

application = Blueprint('tinkrbell', __name__)

from . import views
