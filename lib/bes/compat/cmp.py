#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.system import compat

if compat.IS_PYTHON2:
  cmp = cmp
else:
  def cmp(x, y): return (x > y) - (x < y)
