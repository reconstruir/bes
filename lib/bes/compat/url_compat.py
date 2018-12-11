#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.system import compat

if compat.IS_PYTHON2:
  from urlparse import urlparse, urljoin, urlsplit, urlsplit
  from urllib import urlencode
  from urllib2 import urlopen as urlopen
  from urllib2 import Request
else:
  from urllib.parse import urlparse, urljoin, urlencode, urlsplit
  from urllib.request import urlopen as urlopen
  from urllib.request import Request
