#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path

from bes.b_text_lexer.btl_desc_header import btl_desc_header
from bes.testing.unit_test import unit_test

from keyval_desc_mixin import keyval_desc_mixin

class test_btl_desc_header(keyval_desc_mixin, unit_test):

  def test_parse_node(self):
    lexer_node = self._keyval_desc_tree_section('lexer')
    self.assertEqual( (
      'keyval',
      'A Key Value pair lexer',
      '1.0',
      's_expecting_key',
      's_done',
    ), btl_desc_header.parse_node(lexer_node) )

if __name__ == '__main__':
  unit_test.main()
