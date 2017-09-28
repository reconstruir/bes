#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from __future__ import absolute_import
from bes.system import compat

if compat.IS_PYTHON3:
  from queue import Queue
  from queue import Empty
else:
  from Queue import Queue
  from Queue import Empty
  
