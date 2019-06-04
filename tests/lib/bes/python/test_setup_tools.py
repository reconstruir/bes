#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path, unittest
from bes.fs.file_util import file_util
from bes.fs.temp_file import temp_file
from bes.python.setup_tools import setup_tools

class test_setup_tools(unittest.TestCase):

  def test_update_egg_directory(self):
    tmp_dir = temp_file.make_temp_dir()
    eggs = [
      'foo-1.2.3-py2.7.egg',
      'bar-6.6.6-py2.7.egg',
      'baz-10.11.12-py2.7.egg',
    ]
    for egg in eggs:
      file_util.save(path.join(tmp_dir, egg), content = '%s\n' % (egg))
    setup_tools.update_egg_directory(tmp_dir)

    easy_install_dot_pth_path = path.join(tmp_dir, setup_tools.EASY_INSTALL_DOT_PTH_FILENAME)
    actual_eggs = setup_tools.read_easy_install_pth(easy_install_dot_pth_path)
    self.assertEqual( sorted(eggs), sorted(actual_eggs) )

  def test_update_egg_directory_empty_dir(self):
    tmp_dir = temp_file.make_temp_dir()
    file_util.remove(tmp_dir)
    setup_tools.update_egg_directory(tmp_dir)
    easy_install_dot_pth_path = path.join(tmp_dir, setup_tools.EASY_INSTALL_DOT_PTH_FILENAME)
    self.assertFalse( path.exists(easy_install_dot_pth_path) )
    
  def test_update_site_dot_py(self):
    tmp_dir = temp_file.make_temp_dir()
    setup_tools.update_site_dot_py(tmp_dir)
    site_py_path = path.join(tmp_dir, setup_tools.SITE_DOT_PY_FILENAME)
    self.assertEqual( setup_tools.SITE_DOT_PY_CONTENT.encode('utf-8'), file_util.read(site_py_path) )

  def test_update_site_dot_py_empty_dir(self):
    tmp_dir = temp_file.make_temp_dir()
    file_util.remove(tmp_dir)
    setup_tools.update_site_dot_py(tmp_dir)
    site_py_path = path.join(tmp_dir, setup_tools.SITE_DOT_PY_FILENAME)
    self.assertFalse( path.exists(site_py_path) )
    
if __name__ == '__main__':
  unittest.main()
