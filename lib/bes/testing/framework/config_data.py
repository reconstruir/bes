#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple

import copy, os, os.path as path, string

from bes.common.check import check
from bes.common.string_util import string_util
from bes.compat.StringIO import StringIO
from bes.fs.file_path import file_path
from bes.text.text_line_parser import text_line_parser

class config_data(namedtuple('config_data', 'name, unixpath, pythonpath, requires, variables, optional_requires')):

  def __new__(clazz, name, unixpath, pythonpath, requires, variables, optional_requires):
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
    optional_requires = optional_requires or set()
    check.check_set(requires)
    check.check_set(optional_requires)
    unixpath = [ file_path.normalize_sep(p) for p in unixpath ]
    pythonpath = [ file_path.normalize_sep(p) for p in pythonpath ]
    return clazz.__bases__[0].__new__(clazz, name, unixpath, pythonpath, requires, variables, optional_requires)
    
  def to_string(self):
    buf = StringIO()
    buf.write('# %s\n' % (self.name))
    buf.write('name: %s\n' % (self.name))
    buf.write('variables: %s\n' % (' '.join(self.variables)))
    buf.write('unixpath: %s\n' % (os.pathsep.join(self.unixpath)))
    buf.write('pythonpath: %s\n' % (os.pathsep.join(self.pythonpath)))
    buf.write('requires: %s\n' % (' '.join(sorted([ r for r in self.requires ]))))
    buf.write('optional_requires: %s\n' % (' '.join(sorted([ r for r in self.optional_requires ]))))
    return buf.getvalue()

  @classmethod
  def parse(clazz, text, filename = '<unknown>'):
    name = None
    unixpath = None
    pythonpath = None
    requires = None
    variables = []
    optional_requires = None
    for line in text_line_parser(text):
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
          unixpath = [ path.expanduser(p) for p in value.split(':') ]
        elif key in [ 'pythonpath' ]:
          pythonpath = [ path.expanduser(p) for p in value.split(':') ]
        elif key == 'requires':
          requires = set(string_util.split_by_white_space(value))
        elif key == 'variables':
          variables = string_util.split_by_white_space(value)
        elif key == 'optional_requires':
          optional_requires = set(string_util.split_by_white_space(value))
        else:
          raise ValueError('Invalid config value \"%s\" at %s:%s' % (line.text, filename, line.line_number))
    return config_data(name, unixpath, pythonpath, requires, variables, optional_requires)
  
  def substitute(self, variables):
    unixpath = []
    pythonpath = []
    requires = set()
    for p in self.unixpath:
      unixpath.append(self._substitute_string(p, variables))
    for p in self.pythonpath:
      pythonpath.append(self._substitute_string(p, variables))
    for p in self.requires:
      requires.add(self._substitute_string(p, variables))
    return config_data(self.name, unixpath, pythonpath, requires, self.variables)

  @classmethod
  def _substitute_string(clazz, s, variables):
    return string.Template(s).substitute(**variables)
