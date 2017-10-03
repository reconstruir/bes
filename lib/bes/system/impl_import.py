#!/usr/bin/env python
#-*- coding:utf-8 -*-

from .host import host

class impl_import(object):
  'Import a platform specific implementation of an abstract class.'
  
  _IMPL_ORDER = {
    host.LINUX: [  host.FAMILY,  host.DISTRO, host.LINUX ],
    host.MACOS: [ host.MACOS ],
  }
  
  @classmethod
  def _possible_impl_class_names(clazz, impl_name):
    result = []
    for system in clazz._IMPL_ORDER[host.SYSTEM]:
      impl_class_name = '%s_%s' % (impl_name, system)
      impl_filename = '%s.py' % (impl_class_name)
      result.append(impl_class_name)
    return result

  @classmethod
  def _try_load(clazz, impl_class_name, impl_name, xglobals):
    try:
      code = 'from .%s import %s as %s' % (impl_class_name, impl_class_name, impl_name)
      #print("TRY: %s" % (code))
      exec(code, xglobals)
      return xglobals[impl_name]
    except ImportError as ex:
      #print("EX: %s" % (str(ex)))
      #import traceback
      #traceback.print_exc()
      return None

  @classmethod
  def load(clazz, impl_name, xglobals):
    possible_impl_class_names = clazz._possible_impl_class_names(impl_name)
    for impl_class_name in possible_impl_class_names:
      result = clazz._try_load(impl_class_name, impl_name, xglobals)
      if result:
        return result
    raise ImportError('Could not find any implementation for %s' % (impl_name))

  @classmethod
  def load_caca(clazz, name, impl_name, xglobals):
    import pkgutil
    possible = clazz._possible_impl_class_names(impl_name)
    print("load_caca(%s, %s) possible=%s" % (name, impl_name, possible))
    for p in possible:
      f = '%s.py' % (p)
      try:
        data = pkgutil.get_data(name, f)
      except FileNotFoundError as ex:
        data = None
      except OSError as ex:
        data = None
      print("%s: %s" % (f, type(data)))
    return clazz.load(impl_name, xglobals)
