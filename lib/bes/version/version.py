#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple

class version(object):

  _version = namedtuple('_version', 'version,author_name,author_email,address,tag')
  
  @classmethod
  def read_file(clazz, filename):
    with open(filename, 'r') as f:
      return clazz.read_string(f.read())

  @classmethod
  def read_string(clazz, s):
    ver = {}
    exec(s, {}, ver)
    return clazz._version(ver['BES_VERSION'], ver['BES_AUTHOR_NAME'], ver['BES_AUTHOR_EMAIL'], ver['BES_TAG'], ver['BES_ADDRESS'])
