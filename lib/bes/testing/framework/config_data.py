#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import copy, os.path as path
from collections import namedtuple
from bes.compat import StringIO
from bes.common import check, variable, string_util
from bes.text import lines

class config_data(namedtuple('config_data', 'name,unixpath,pythonpath,requires')):

  def __new__(clazz, name, unixpath, pythonpath, requires):
    check.check_string(name)
    unixpath = unixpath or []
    if check.is_string(unixpath):
      unixpath = unixpath.split(':')
    check.check_string_seq(unixpath)
    pythonpath = pythonpath or []
    if check.is_string(pythonpath):
      pythonpath = pythonpath.split(':')
    check.check_string_seq(pythonpath)
    requires = requires or set()
    check.check_set(requires)
    return clazz.__bases__[0].__new__(clazz, name, unixpath, pythonpath, requires)

  def to_string(self):
    buf = StringIO()
    buf.write('# %s\n' % (self.name))
    buf.write('name: %s\n' % (self.name))
    buf.write('unixpath: %s\n' % (':'.join(self.unixpath)))
    buf.write('pythonpath: %s\n' % (':'.join(self.pythonpath)))
    buf.write('requires: %s\n' % (' '.join(sorted([ r for r in self.requires ]))))
    return buf.getvalue()

  @classmethod
  def parse(clazz, text, filename = '<unknown>'):
    name = None
    unixpath = None
    pythonpath = None
    requires = None
    for line in lines(text):
      text = line.text_no_comments.strip()
      if text:
        key, sep, value = text.partition(':')
        if sep != ':':
          raise ValueError('Invalid config line \"%s\" at %s:%s' % (line.text, filename, line.line_number))
        key = key.strip()
        value = value.strip()
        if key == 'name':
          name = value
        elif key in [ 'unixpath' ]:
          unixpath = value.split(':')
        elif key in [ 'pythonpath' ]:
          pythonpath = value.split(':')
        elif key == 'requires':
          requires = set(string_util.split_by_white_space(value))
        else:
          raise ValueError('Invalid config value \"%s\" at %s:%s' % (line.text, filename, line.line_number))
    return clazz(name, unixpath, pythonpath, requires)
  
  def substitute(self, variables):
    unixpath = []
    pythonpath = []
    requires = set()
    for p in self.unixpath:
      unixpath.append(variable.substitute(p, variables))
    for p in self.pythonpath:
      pythonpath.append(variable.substitute(p, variables))
    for p in self.requires:
      requires.add(variable.substitute(p, variables))
    return config_data(self.name, unixpath, pythonpath, requires)
