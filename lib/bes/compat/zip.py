#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.system.compat import compat

if compat.IS_PYTHON2:
  from itertools import izip as zip
else:
  zip = zip
