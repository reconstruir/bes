#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import fnmatch, inspect, os, os.path as path, zipfile

from .unit_test import unit_test

from bes.files.bf_path import bf_path
from bes.fs.file_util import file_util

# FIXME: figure out hot to unpack and egg such that permissions and links are correct
#        and dont need to be hacked by hand
class egg_unit_test(unit_test):

  @classmethod
  def egg_for_module(clazz, mod):
    'Return the egg for mod or None if not inside and egg.'
    if not inspect.ismodule(mod):
      raise TypeError('not a module: %s' % (str(mod)))
    filename = inspect.getfile(mod)
    return clazz.module_file_to_egg(filename)
    
  @classmethod
  def module_file_to_egg(clazz, filename):
    'Return the egg for a file inside an egg.  /fruits/kiwi.egg/mod/__init__.pyc => /fruits/kiwi.egg'
    p = file_path.split(filename)
    while True:
      possible_egg = file_path.join(p)
      if possible_egg.endswith('.egg'):
        return possible_egg
      if not p:
        break
      p.pop()
    return None

  _TEST_FILE_PATTERNS = [ '*/tests/*.py*', '*/test_data/*', '*/bes_test.py' ]
  @classmethod
  def is_test_file(clazz, filename):
    'Return True if a file is either a unit test or test data.'
    for pattern in clazz._TEST_FILE_PATTERNS:
      if fnmatch.fnmatch(filename, pattern):
        return True
    return False

  @classmethod
  def extract_egg_test_files(clazz, egg, dst):
    with zipfile.ZipFile(file = egg, mode = 'r') as zf:
      members = clazz.filter_test_file_members(zf.infolist())
      file_util.mkdir(dst)
      for member in members:
        zf.extract(member, path = dst)
        extracted_filename = path.join(dst, member.filename)
        ext = path.splitext(extracted_filename)[1]
        if ext in [ '.py', '.sh' ]:
          os.chmod(extracted_filename, 0o755)

  @classmethod
  def filter_test_file_members(clazz, members):
    result = [ member for member in members if clazz.is_test_file(member.filename) ]
    return result
