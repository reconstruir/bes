#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.common import check

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

  
