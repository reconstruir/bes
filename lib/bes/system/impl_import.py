#!/usr/bin/env python
#-*- coding:utf-8 -*-

from .host import host
import pkgutil, traceback
from collections import namedtuple

class impl_import(object):
  'Import a platform specific implementation of an abstract class.'
  
  _IMPL_ORDER = {
    host.LINUX: [ host.FAMILY,  host.DISTRO, host.LINUX ],
    host.MACOS: [ host.MACOS ],
  }
  
  @classmethod
  def load(clazz, package, impl_name, xglobals):
    possible = clazz._possible_impl_module_data(package, impl_name)
    if not possible:
      raise ImportError('Could not find any implementation for %s in %s' % (impl_name, package))
    class_name = possible[0].impl_class_name
    try:
      code = 'from .%s import %s as %s' % (class_name, class_name, impl_name)
      exec(code, xglobals)
      impl_clazz = xglobals[impl_name]
      # instanciate one to make sure no abstract methods are missing
      dummy = impl_clazz()
      return impl_clazz
    except ImportError as ex:
      print('Error importing %s from .%s in %s' % (class_name, class_name, package))
      raise

  @classmethod
  def _possible_impl_class_names(clazz, impl_name):
    result = []
    for system in clazz._IMPL_ORDER[host.SYSTEM]:
      impl_class_name = '%s_%s' % (impl_name, system)
      impl_filename = '%s.py' % (impl_class_name)
      result.append(impl_class_name)
    return result

  _impl_file = namedtuple('_impl_file', 'impl_class_name,filename')
  @classmethod
  def _possible_impl_module_files(clazz, impl_name):
    result = []
    for class_name in clazz._possible_impl_class_names(impl_name):
      result.append(clazz._impl_file(class_name, '%s.py' % (class_name)))
      result.append(clazz._impl_file(class_name, '%s.pyc' % (class_name)))
    return result

  _impl_data = namedtuple('_impl_data', 'impl_class_name,filename,data')
  @classmethod
  def _possible_impl_module_data(clazz, package, impl_name):
    result = []
    possible_files = clazz._possible_impl_module_files(impl_name)
    #print('CACA: possible_files=%s' % (possible_files))
    for impl_class_name, filename in clazz._possible_impl_module_files(impl_name):
      data = clazz._get_impl_data(package, filename)
      if data:
        result.append(clazz._impl_data(impl_class_name, filename, data))
    return result

  @classmethod
  def _get_impl_data(clazz, package, filename):
    try:
      #print('CACA: pkgutil.get_data(%s, %s)' % (package, filename))
      return pkgutil.get_data(package, filename)
    except IOError as ex:
      #print('CACA: 1 CAUGHT: %s' % (str(ex)))
      # Caught when poking in the filesystem
      return None
    except OSError as ex:
      #print('CACA: 2 CAUGHT: %s' % (str(ex)))
      # Caught when poking in an egg
      return None
