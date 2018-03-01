#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.system import compat

def import_exceptions():
  # In python3 exceptions are builtin
  if compat.IS_PYTHON2:
    import exceptions
