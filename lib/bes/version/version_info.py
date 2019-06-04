#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple

from bes.common.check import check
from bes.compat.StringIO import StringIO

class version_info(namedtuple('version_info', 'version,author_name,author_email,address,tag,timestamp')):

  def __new__(clazz, version, author_name, author_email, address, tag, timestamp):
    check.check_string(version)
    check.check_string(author_name)
    check.check_string(author_email)
    check.check_string(address)
    check.check_string(tag)
    check.check_string(timestamp)
    return clazz.__bases__[0].__new__(clazz, version, author_name, author_email, address, tag, timestamp)

  HEADER = '''\
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

'''
  
  def __str__(self):
    buf = StringIO()
    buf.write(self.HEADER)
    buf.write('BES_VERSION = u\'%s\'\n' % (self.version))
    buf.write('BES_AUTHOR_NAME = u\'%s\'\n' % (self.author_name))
    buf.write('BES_AUTHOR_EMAIL = u\'%s\'\n' % (self.author_email))
    buf.write('BES_ADDRESS = u\'%s\'\n' % (self.address))
    buf.write('BES_TAG = u\'%s\'\n' % (self.tag))
    buf.write('BES_TIMESTAMP = u\'%s\'\n' % (self.timestamp))
    return buf.getvalue()

  def version_string(self, delimiter = ':', brief = False):
    if brief:
      return self.version
    parts = [ self.version, self.address, self.tag, self.timestamp ]
    return delimiter.join(parts)
  
  @classmethod
  def read_file(clazz, filename):
    check.check_string(filename)
    with open(filename, 'r') as f:
      return clazz.read_string(f.read())

  @classmethod
  def read_string(clazz, s):
    ver = {}
    exec(s, {}, ver)
    return clazz(ver['BES_VERSION'], ver['BES_AUTHOR_NAME'], ver['BES_AUTHOR_EMAIL'], ver['BES_ADDRESS'], ver['BES_TAG'], ver['BES_TIMESTAMP'])

  def save_file(self, filename):
    check.check_string(filename)
    with open(filename, 'w') as f:
      f.write(str(self))
  
  def change(self, version = None, author_name = None, author_email = None, address = None, tag = None, timestamp = None):
    if version is not None:
      check.check_string(version)
    else:
      version = self.version
    if author_name is not None:
      check.check_string(author_name)
    else:
      author_name = self.author_name
    if author_email is not None:
      check.check_string(author_email)
    else:
      author_email = self.author_email
    if address is not None:
      check.check_string(address)
    else:
      address = self.address
    if tag is not None:
      check.check_string(tag)
    else:
      tag = self.tag
    if timestamp is not None:
      check.check_string(timestamp)
    else:
      timestamp = self.timestamp
    return self.__class__(version, author_name, author_email, address, tag, timestamp)

  @classmethod
  def version_info_for_module(clazz, mod):
    check.check_module(mod)
    return clazz(mod.__version__, mod.__bes_author_name__, mod.__author__, mod.__bes_address__, mod.__bes_tag__, mod.__bes_timestamp__)
    
check.register_class(version_info)

