#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import sys

if sys.version_info.major == 2:
  from cStringIO import StringIO as StringIO
elif sys.version_info.major == 3:
  from io import StringIO as StringIO
else:
  raise RuntimeError('unknown python version: %s' % (sys.version_info.major))
