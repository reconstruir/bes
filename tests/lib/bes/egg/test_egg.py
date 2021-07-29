#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test
from bes.testing.egg_unit_test import egg_unit_test
from bes.egg.egg import egg

class test_egg(unit_test):

  def test_make_from_address(self):
    result = egg.make_from_address('https://gitlab.com/rebuilder/bes.git', '1.2.62', 'setup.py',
                                   version_filename = 'lib/bes/ver.py',
                                   verbose = self.DEBUG,
                                   debug = self.DEBUG)
    print('result={}'.format(result))

if __name__ == '__main__':
  unit_test.main()
