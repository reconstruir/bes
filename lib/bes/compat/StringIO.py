#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.system.compat import compat

if compat.IS_PYTHON3:
  from io import StringIO as StringIO
else:
  from cStringIO import StringIO as StringIO
