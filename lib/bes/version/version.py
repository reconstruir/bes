#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.common.check import check
from collections import namedtuple

class version(object):

  @classmethod
  def read_file(clazz, filename):
    with open(filename, 'r') as f:
      return clazz.read_string(f.read())

  @classmethod
  def read_string(clazz, s):
    ver = {}
    exec(s, {}, ver)
    return clazz.version_info(ver['BES_VERSION'], ver['BES_AUTHOR_NAME'], ver['BES_AUTHOR_EMAIL'], ver['BES_TAG'], ver['BES_ADDRESS'])

  @classmethod
  def write_file(clazz, filename, info):
    check.check_version_info(info)
    with open(filename, 'r') as f:
      return clazz.read_string(f.read())

  _mod_version = namedtuple('_mod_version', 'name, version, filename')
  @classmethod
  def module_version(clazz, name):
    fromlist = []
    if check.is_tuple(name):
      if len(name) != 2:
        raise ValueError('name should be a string or 2 string tuple of ( name, fromlist ): {}'.format(str(name)))
      name = name[0]
      fromlist = name[1]
    elif not check.is_string(name):
      raise ValueError('name should be a string or 2 string tuple of ( name, fromlist ): {}'.format(str(name)))
    m = __import__(name, fromlist = fromlist)
    ver = getattr(m, '__version__', '')
    if ver == None:
      raise RuntimeError('module does not define __version__: {}'.format(name))
    return clazz._mod_version(name, ver, m.__file__)

  @classmethod
  def module_versions(clazz, module_names):
    result = {}
    for name in module_names:
      mod_ver = clazz.module_version(name)
      result[mod_ver.name] = mod_ver
    return result
