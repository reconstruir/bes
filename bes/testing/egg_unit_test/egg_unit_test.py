#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import inspect, os.path as path

from bes.testing.unit_test import unit_test
from bes.fs import file_path

class egg_unit_test(unit_test):

  @classmethod
  def egg_for_module(clazz, mod):
    assert isinstance(mod, module)
    filename = inspect.getfile(mod)
    p = file_path.split(filename)
    
  @classmethod
  def module_file_to_egg(clazz, filename):
    p = file_path.split(filename)
    while True:
      possible_egg = file_path.join(p)
      if possible_egg.endswith('.egg'):
        return possible_egg
      if not p:
        break
      p.pop()
    return None
    
  '''

/Users/ramiro/proj/software/tmp/builds/macos/release/bes-1.0.0_2017-09-06-21-36-16-271537/test/reb-bes-test/requirements/installation/lib/python/bes-1.0.0-py2.7.egg/bes/__init__.pyc
class reb_bes_test(unittest.TestCase):

  def test_bes(self):
    import sys
    import bes
    suffix = '/bes/__init__.pyc'
    init = inspect.getfile(bes)
    egg = init[0:-len(suffix)]
    with zipfile.ZipFile(file = egg, mode = 'r') as zegg:
      members = zegg.infolist()
      f = []
      for m in members:
        if fnmatch.fnmatch(m.filename, '*/tests/*.py*') or fnmatch.fnmatch(m.filename, '*/test_data/*') or fnmatch.fnmatch(m.filename, '*/bes_test.py'):
          f.append(m)
      tmp_dir = tempfile.mkdtemp()
      for m in f:
        zegg.extract(m, path = tmp_dir)
        extracted_filename = path.join(tmp_dir, m.filename)
        ext = path.splitext(extracted_filename)[1]
        if ext in [ '.py', '.sh' ]:
          os.chmod(extracted_filename, 0755)
      bes_test = path.join(tmp_dir, 'EGG-INFO/scripts/bes_test.py')
      tests_dir = path.join(tmp_dir, 'bes')
      cmd = [ bes_test, tests_dir ]
      exit_code = subprocess.call(cmd, shell = False)
      self.assertEqual( 0, exit_code )

'''
