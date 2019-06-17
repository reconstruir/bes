#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.system.compat import compat
from bes.system.host import host

if compat.IS_PYTHON2:
  from urlparse import urlparse, urljoin, urlsplit, urlsplit
  from urllib import urlencode
  from urllib2 import urlopen as urlopen
  from urllib2 import Request
  from urllib2 import HTTPError
else:
  from urllib.parse import urlparse, urljoin, urlencode, urlsplit
  from urllib.request import urlopen as urlopen
  from urllib.request import Request
  if host.is_unix():
    from http.client import RemoteDisconnected as HTTPError
  elif host.is_windows():
    from urllib.error import HTTPError

#  if compat.IS_PYTHON3:
#  import urllib.request as urlopener
#  import urllib.parse as urlparser
#  if host.is_unix():
#    from http.client import RemoteDisconnected as HTTPError
#  elif host.is_windows():
#    from urllib.error import HTTPError
#else:
#  import urllib2 as urlopener
#  import urlparse as urlparser
#  from urllib2 import HTTPError
