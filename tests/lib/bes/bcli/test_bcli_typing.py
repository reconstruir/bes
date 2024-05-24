#!/usr/bin/env python#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import typing

from bes.testing.unit_test import unit_test
from bes.bcli.bcli_typing import bcli_typing

class test_bcli_typing(unit_test):

  def test_parse_type(self):
    self.assertEqual( int, bcli_typing.parse_type('int') )
    self.assertEqual( bool, bcli_typing.parse_type('bool') )
    self.assertEqual( typing.List[str], bcli_typing.parse_type('list[str]') )
    self.assertEqual( typing.Set[int], bcli_typing.parse_type('set[int]') )
    self.assertEqual( typing.Dict[str, int], bcli_typing.parse_type('dict[str, int]') )
    
if __name__ == '__main__':
  unit_test.main()
