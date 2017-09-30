#!/usr/bin/env python
#-*- coding:utf-8 -*-

from .host import host

class impl_import(object):
  'Import a platform specific implementation of an abstract class.'
  
  __IMPL_ORDER = {
    host.LINUX: [  host.FAMILY,  host.DISTRO, host.LINUX ],
    host.MACOS: [ host.MACOS ],
  }
  
  @classmethod
  def _possible_impl_class_names(clazz, impl_name):
    result = []
    for system in clazz.__IMPL_ORDER[host.SYSTEM]:
      impl_class_name = '%s_%s' % (impl_name, system)
      impl_filename = '%s.py' % (impl_class_name)
      result.append(impl_class_name)
    return result

  @classmethod
  def _try_load(clazz, impl_class_name, impl_name, xglobals):
    try:
      code = 'from .%s import %s as %s' % (impl_class_name, impl_class_name, impl_name)
      exec(code, xglobals)
      return xglobals[impl_name]
    except ImportError as ex:
      import traceback
      traceback.print_exc()
      return None

  @classmethod
  def load(clazz, impl_name, xglobals):
    possible_impl_class_names = clazz._possible_impl_class_names(impl_name)
    for impl_class_name in possible_impl_class_names:
      result = clazz._try_load(impl_class_name, impl_name, xglobals)
      if result:
        return result
    raise ImportError('Could not find any implementation for %s' % (impl_name))
