#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test
from bes.fs.file_replace import file_replace

class test_file_replace(unit_test):

  def test_file_replace_ascii(self):
    tmp = self.make_temp_file(content = 'This is foo fooey.\n')
    replacements = {
      'This': 'That',
      'foo': 'bar',
    }
    file_replace.replace(tmp, replacements, backup = False, word_boundary = False)
    self.assert_text_file_equal( 'That is bar barey.\n', tmp )

  def test_file_replace_utf8(self):
    tmp = self.make_temp_file(content = 'This is bér béry.\n')
    replacements = {
      'This': 'That',
      'bér': 'föö',
    }
    file_replace.replace(tmp, replacements, backup = False, word_boundary = True)
    self.assert_text_file_equal( 'That is föö béry.\n', tmp )

  def test_file_replace_ascii_with_word_boundary(self):
    tmp = self.make_temp_file(content = 'This is foo fooey.\n')
    replacements = {
      'This': 'That',
      'foo': 'bar',
    }
    file_replace.replace(tmp, replacements, backup = False, word_boundary = True)
    self.assert_text_file_equal( 'That is bar fooey.\n', tmp )

if __name__ == '__main__':
  unit_test.main()
