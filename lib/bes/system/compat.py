#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import sys

class compat(object):
  'Hackery to help write code that works on both python 2 and 3.'

  IS_PYTHON3 = False
  IS_PYTHON2 = False
  if sys.version_info.major == 2:
    IS_PYTHON2 = True
  elif sys.version_info.major == 3:
    IS_PYTHON3 = True
  else:
    raise RuntimeError('unknown python version: %s' % (sys.version_info.major))

  if IS_PYTHON3:
    STRING_TYPES = str,
    INTEGER_TYPES = int,
  else:
    STRING_TYPES = basestring,
    INTEGER_TYPES = (int, long)
