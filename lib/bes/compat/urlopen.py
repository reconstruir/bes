#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.system import compat

if compat.IS_PYTHON2:
  from urllib2 import urlopen
else:
  from urllib.request import urlopen
