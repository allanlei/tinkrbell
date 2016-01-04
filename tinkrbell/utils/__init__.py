# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

import urlparse
import urllib


def urlencode(url):
    # Ref: https://stackoverflow.com/questions/804336/best-way-to-convert-a-unicode-url-to-ascii-utf-8-percent-escaped-in-python
    # turn string into unicode
    if not isinstance(url, unicode):
        url = url.decode('utf-8')

    # parse it
    parsed = urlparse.urlsplit(url)

    # divide the netloc further
    userpass, at, hostport = parsed.netloc.rpartition(b'@')
    user, colon1, pass_ = userpass.partition(b':')
    host, colon2, port = hostport.partition(b':')

    # encode each component
    scheme = parsed.scheme.encode('utf-8')
    user = urllib.quote(user.encode('utf-8'))
    colon1 = colon1.encode('utf-8')
    pass_ = urllib.quote(pass_.encode('utf-8'))
    at = at.encode('utf-8')
    host = host.encode('idna')
    colon2 = colon2.encode('utf-8')
    port = port.encode('utf-8')
    path = '/'.join(  # could be encoded slashes!
        urllib.quote(urllib.unquote(pce).encode('utf-8'), b'')
        for pce in parsed.path.split('/')
    )
    query = urllib.quote(urllib.unquote(parsed.query).encode('utf-8'), b'=&?/')
    fragment = urllib.quote(urllib.unquote(parsed.fragment).encode('utf-8'))

    # put it back together
    netloc = ''.join((user, colon1, pass_, at, host, colon2, port))
    return urlparse.urlunsplit((scheme, netloc, path, query, fragment))
