#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import sys

from bes.system.output_capture import output_capture
from bes.testing.unit_test import unit_test

class test_output_capture(unit_test):

  def test_output_capture(self):
    with output_capture() as c:
      sys.stdout.write('kiwi')
      sys.stderr.write('lemon')
      self.assertEqual( 'kiwi', c.stdout )
      self.assertEqual( 'lemon', c.stderr )

  def test_output_capture_binary(self):
    with output_capture(binary = True) as c:
      sys.stdout.write(b'\x66\x74\x79\x70\x6D\x70\x34\x32')
      self.assertEqual( b'\x66\x74\x79\x70\x6D\x70\x34\x32', c.stdout )
      
if __name__ == '__main__':
  unit_test.main()
