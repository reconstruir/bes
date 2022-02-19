#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.system.compat import compat
from bes.system.host import host

if compat.IS_PYTHON2:
  from urlparse import urlparse, urlunparse, urljoin, urlsplit, urlsplit
  from urllib import urlencode
  from urllib2 import urlopen as urlopen
  from urllib2 import Request
  from urllib2 import HTTPError
else:
  from urllib.parse import urlparse, urlunparse, urljoin, urlencode, urlsplit
  from urllib.request import urlopen as urlopen
  from urllib.request import Request
  from urllib.error import HTTPError
