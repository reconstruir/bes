#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path

from bes.b_text_lexer.btl_desc import btl_desc
from bes.b_text_lexer.btl_desc_char import btl_desc_char
from bes.b_text_lexer.btl_desc_char_map import btl_desc_char_map
from bes.b_text_lexer.btl_error import btl_error
from bes.testing.unit_test import unit_test
from bes.property.cached_property import cached_property
from bes.fs.file_util import file_util

from keyval_desc_mixin import keyval_desc_mixin

class test_btl_desc(keyval_desc_mixin, unit_test):

  def test_parse_text(self):
    d = btl_desc.parse_text(self._keyval_desc_text)
    
if __name__ == '__main__':
  unit_test.main()
