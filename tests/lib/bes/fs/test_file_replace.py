#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test
from bes.fs.file_replace import file_replace
from bes.text.word_boundary import word_boundary

class test_file_replace(unit_test):

  def test_file_replace_ascii(self):
    tmp = self.make_temp_file(content = 'This is foo fooey foo_kiwi.\n')
    replacements = {
      'This': 'That',
      'foo': 'bar',
    }
    file_replace.replace(tmp, replacements, backup = False, word_boundary = False)
    self.assert_text_file_equal( 'That is bar barey bar_kiwi.\n', tmp )

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

  def test_file_replace_with_word_boundary_and_underscore(self):
    tmp = self.make_temp_file(content = 'This is foo foo_bar.\n')
    replacements = {
      'This': 'That',
      'foo': 'kiwi',
    }
    file_replace.replace(tmp, replacements, backup = False, word_boundary = True, boundary_chars = word_boundary.CHARS_UNDERSCORE)
    self.assert_text_file_equal( 'That is kiwi kiwi_bar.\n', tmp )
    
if __name__ == '__main__':
  unit_test.main()
