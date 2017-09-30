#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from __future__ import absolute_import
from bes.system import compat

import plistlib

def plistlib_loads(text):
  if compat.IS_PYTHON2:
    return plistlib.readPlistFromString(text)
  else:
    return plistlib.loads(text)
