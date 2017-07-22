#!/usr/bin/env python
#-*- coding:utf-8 -*-

import exceptions, inspect, os.path as path, sys

from host import host

class impl_loader(object):
  'Load an implementation from disk.'
  
  @classmethod
  def load(self, reference_object, impl_name = None):
    'Load a system specific class from a python module and return it.'
    impl_name = impl_name or reference_object.__name__
    if isinstance(reference_object, basestring) and path.isfile(reference_object):
      filename = reference_object
    else:
      filename = inspect.getfile(reference_object)
    impl_dir = path.dirname(filename)
    if not impl_name:
      raise RuntimeError('No impl_name given for %s' % (self))
    possible_impl_classes = self.__possible_impl_class(impl_name)
    impl_class = None
    for impl_class_name in possible_impl_classes:
      impl_class = self.__load_impl_class(impl_class_name, impl_dir)
      if impl_class:
        break
    if not impl_class:
      raise RuntimeError('No implementation for \"%s\" found in %s' % (impl_name, impl_dir))
    return impl_class()

  __IMPL_ORDER = {
    host.LINUX: [  host.FAMILY,  host.DISTRO, host.LINUX ],
    host.MACOS: [ host.MACOS ],
  }
  @classmethod
  def __possible_impl_class(self, impl_name):
    result = []
    for system in self.__IMPL_ORDER[host.SYSTEM]:
      impl_class_name = '%s_%s' % (impl_name, system)
      impl_filename = '%s.py' % (impl_class_name)
      result.append(impl_class_name)
    return result
      
  @classmethod
  def __load_impl_class(self, impl_class_name, impl_dir):
    code = 'from %s import %s\ncode_clazz=%s' % (impl_class_name, impl_class_name, impl_class_name)
    save_path = sys.path[:]
    sys.path.insert(0, impl_dir)
    try:
      exec(code)
    except exceptions.ImportError, ex:
      return None
    except Exception, ex:
      raise
    finally:
      sys.path = save_path
    impl_class = locals().get(impl_class_name, None)
    if not impl_class:
      raise RuntimeError('Failed to instanciate: %s' % (impl_class_name))
    return impl_class
