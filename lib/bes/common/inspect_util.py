#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import inspect

from bes.system.compat import compat

class inspect_util(object):
  'inspect util'

  @classmethod
  def getargspec(clazz, f):
    'Backward compatible getargspec wrapper.'
#    return inspect.getargspec(f)
    if compat.IS_PYTHON3:
      return inspect.getfullargspec(f)
    else:
      return inspect.getargspec(f)
