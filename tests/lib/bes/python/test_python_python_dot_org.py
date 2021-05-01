#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path

from bes.python.python_python_dot_org import python_python_dot_org
from bes.testing.unit_test import unit_test

class test_python_python_dot_org(unit_test):

  def test__full_version_for_url(self):
    f = python_python_dot_org._full_version_for_url
    self.assertEqual( '3.9.4',
                      f('https://www.python.org/ftp/python/3.9.4/python-3.9.4-macosx10.9.pkg') )

  def test__checksum_index_url(self):
    f = python_python_dot_org._checksum_index_url
    self.assertEqual( 'https://www.python.org/downloads/release/python-394/',
                      f('https://www.python.org/ftp/python/3.9.4/python-3.9.4-macosx10.9.pkg') )
    
if __name__ == '__main__':
  unit_test.main()
