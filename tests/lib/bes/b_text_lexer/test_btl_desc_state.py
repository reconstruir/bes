#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path

from bes.b_text_lexer.btl_desc_state import btl_desc_state
from bes.b_text_lexer.btl_error import btl_error
from bes.testing.unit_test import unit_test
from bes.text.tree_text_parser import _text_node_data

from keyval_desc_mixin import keyval_desc_mixin

class test_btl_desc_state(keyval_desc_mixin, unit_test):

  def xtest(self):
    pass
    
if __name__ == '__main__':
  unit_test.main()
