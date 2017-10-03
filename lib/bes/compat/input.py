#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.system import compat

if compat.IS_PYTHON3:
  from builtins import input as input
else:
  input = raw_input
