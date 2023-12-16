#!/usr/bin/env python3
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test
from bes.mermaid.mermaid import mermaid
from bes.mermaid.mmd_document import mmd_document
from bes.mermaid.mmd_transition_list import mmd_transition_list
from bes.fs.file_util import file_util
from bes.text.bindent import bindent

from example_mmd import INI_MMD

class test_mermaid(unit_test):

  def test_state_diagram_parse_text(self):
    expected = '''
{
  "states": [
    "__end", 
    "__start", 
    "comment", 
    "cr", 
    "cr_error", 
    "end", 
    "expecting_value", 
    "key", 
    "section_name", 
    "section_name_error", 
    "space", 
    "start", 
    "start_error", 
    "value", 
    "value_space"
  ], 
  "tokens": [
    "comment",
    "done",
    "line_break",
    "section_begin",
    "section_end",
    "space",
    "string"
  ], 
  "transitions": [
    {
      "line": "  [*] --> start", 
      "from_state": "__start", 
      "to_state": "start", 
      "event": ""
    }, 
    {
      "line": "  start --> end: EOS", 
      "from_state": "start", 
      "to_state": "end", 
      "event": "EOS"
    }, 
    {
      "line": "  start --> comment: SEMICOLON", 
      "from_state": "start", 
      "to_state": "comment", 
      "event": "SEMICOLON"
    }, 
    {
      "line": "  start --> space: TAB SPACE", 
      "from_state": "start", 
      "to_state": "space", 
      "event": "TAB SPACE"
    }, 
    {
      "line": "  start --> cr: CR", 
      "from_state": "start", 
      "to_state": "cr", 
      "event": "CR"
    }, 
    {
      "line": "  start --> start: NL", 
      "from_state": "start", 
      "to_state": "start", 
      "event": "NL"
    }, 
    {
      "line": "  start --> section_name: OPEN_BRACKET", 
      "from_state": "start", 
      "to_state": "section_name", 
      "event": "OPEN_BRACKET"
    }, 
    {
      "line": "  start --> key: UNDERSCORE LOWER_LETTER UPPER_LETTER DIGIT", 
      "from_state": "start", 
      "to_state": "key", 
      "event": "UNDERSCORE LOWER_LETTER UPPER_LETTER DIGIT"
    }, 
    {
      "line": "  start --> expecting_value: EQUAL", 
      "from_state": "start", 
      "to_state": "expecting_value", 
      "event": "EQUAL"
    }, 
    {
      "line": "  start --> start_error: ANY", 
      "from_state": "start", 
      "to_state": "start_error", 
      "event": "ANY"
    }, 
    {
      "line": "  space --> space: TAB SPACE", 
      "from_state": "space", 
      "to_state": "space", 
      "event": "TAB SPACE"
    }, 
    {
      "line": "  space --> end: EOS", 
      "from_state": "space", 
      "to_state": "end", 
      "event": "EOS"
    }, 
    {
      "line": "  space --> cr: CR", 
      "from_state": "space", 
      "to_state": "cr", 
      "event": "CR"
    }, 
    {
      "line": "  space --> start: NL", 
      "from_state": "space", 
      "to_state": "start", 
      "event": "NL"
    }, 
    {
      "line": "  space --> key: UNDERSCORE LOWER_LETTER UPPER_LETTER DIGIT", 
      "from_state": "space", 
      "to_state": "key", 
      "event": "UNDERSCORE LOWER_LETTER UPPER_LETTER DIGIT"
    }, 
    {
      "line": "  space --> expecting_value: EQUAL", 
      "from_state": "space", 
      "to_state": "expecting_value", 
      "event": "EQUAL"
    }, 
    {
      "line": "  cr --> start: NL]", 
      "from_state": "cr", 
      "to_state": "start", 
      "event": "NL]"
    }, 
    {
      "line": "  cr --> cr_error: ANY EOS", 
      "from_state": "cr", 
      "to_state": "cr_error", 
      "event": "ANY EOS"
    }, 
    {
      "line": "  comment --> comment: ANY", 
      "from_state": "comment", 
      "to_state": "comment", 
      "event": "ANY"
    }, 
    {
      "line": "  comment --> cr: CR", 
      "from_state": "comment", 
      "to_state": "cr", 
      "event": "CR"
    }, 
    {
      "line": "  comment --> start: NL", 
      "from_state": "comment", 
      "to_state": "start", 
      "event": "NL"
    }, 
    {
      "line": "  comment --> end: EOS", 
      "from_state": "comment", 
      "to_state": "end", 
      "event": "EOS"
    }, 
    {
      "line": "  section_name --> section_name: UNDERSCORE LOWER_LETTER UPPER_LETTER DIGIT PERIOD", 
      "from_state": "section_name", 
      "to_state": "section_name", 
      "event": "UNDERSCORE LOWER_LETTER UPPER_LETTER DIGIT PERIOD"
    }, 
    {
      "line": "  section_name --> start: ]", 
      "from_state": "section_name", 
      "to_state": "start", 
      "event": "]"
    }, 
    {
      "line": "  section_name --> section_name_error: TAB SPACE CR NL EOS", 
      "from_state": "section_name", 
      "to_state": "section_name_error", 
      "event": "TAB SPACE CR NL EOS"
    }, 
    {
      "line": "  key --> key: UNDERSCORE LOWER_LETTER UPPER_LETTER DIGIT PERIOD", 
      "from_state": "key", 
      "to_state": "key", 
      "event": "UNDERSCORE LOWER_LETTER UPPER_LETTER DIGIT PERIOD"
    }, 
    {
      "line": "  key --> space: TAB SPACE", 
      "from_state": "key", 
      "to_state": "space", 
      "event": "TAB SPACE"
    }, 
    {
      "line": "  key --> cr: CR", 
      "from_state": "key", 
      "to_state": "cr", 
      "event": "CR"
    }, 
    {
      "line": "  key --> start: NL", 
      "from_state": "key", 
      "to_state": "start", 
      "event": "NL"
    }, 
    {
      "line": "  key --> expecting_value: EQUAL", 
      "from_state": "key", 
      "to_state": "expecting_value", 
      "event": "EQUAL"
    }, 
    {
      "line": "  key --> end: EOS", 
      "from_state": "key", 
      "to_state": "end", 
      "event": "EOS"
    }, 
    {
      "line": "  expecting_value --> value_space: TAB SPACE", 
      "from_state": "expecting_value", 
      "to_state": "value_space", 
      "event": "TAB SPACE"
    }, 
    {
      "line": "  expecting_value --> cr: CR", 
      "from_state": "expecting_value", 
      "to_state": "cr", 
      "event": "CR"
    }, 
    {
      "line": "  expecting_value --> start: NL", 
      "from_state": "expecting_value", 
      "to_state": "start", 
      "event": "NL"
    }, 
    {
      "line": "  expecting_value --> end: EOS", 
      "from_state": "expecting_value", 
      "to_state": "end", 
      "event": "EOS"
    }, 
    {
      "line": "  expecting_value --> value: ANY", 
      "from_state": "expecting_value", 
      "to_state": "value", 
      "event": "ANY"
    }, 
    {
      "line": "  value_space --> value_space: TAB SPACE", 
      "from_state": "value_space", 
      "to_state": "value_space", 
      "event": "TAB SPACE"
    }, 
    {
      "line": "  value_space --> cr: CR", 
      "from_state": "value_space", 
      "to_state": "cr", 
      "event": "CR"
    }, 
    {
      "line": "  value_space --> start: NL", 
      "from_state": "value_space", 
      "to_state": "start", 
      "event": "NL"
    }, 
    {
      "line": "  value_space --> end: EOS", 
      "from_state": "value_space", 
      "to_state": "end", 
      "event": "EOS"
    }, 
    {
      "line": "  value_space --> value: ANY", 
      "from_state": "value_space", 
      "to_state": "value", 
      "event": "ANY"
    }, 
    {
      "line": "  value --> value: ANY", 
      "from_state": "value", 
      "to_state": "value", 
      "event": "ANY"
    }, 
    {
      "line": "  value --> cr: CR", 
      "from_state": "value", 
      "to_state": "cr", 
      "event": "CR"
    }, 
    {
      "line": "  value --> start: NL", 
      "from_state": "value", 
      "to_state": "start", 
      "event": "NL"
    }, 
    {
      "line": "  value --> end: EOS", 
      "from_state": "value", 
      "to_state": "end", 
      "event": "EOS"
    }, 
    {
      "line": "  end --> [*]", 
      "from_state": "end", 
      "to_state": "__end", 
      "event": ""
    }
  ]
}
'''
    doc = mermaid.state_diagram_parse_text(INI_MMD)
    actual = doc.to_json()
    self.assert_string_equal_fuzzy( expected, actual )

  def test_state_diagram_generate_code(self):
    tmp_mmd = self.make_temp_file(content = INI_MMD)
    tmp_dir = self.make_temp_dir()
    tmp_py = mermaid.state_diagram_generate_code(tmp_mmd, '_fruit', 'kiwi', tmp_dir)
    expected_code = '''\
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.text.lexer_token import lexer_token
from bes.text.text_lexer_base import text_lexer_base
from bes.text.text_lexer_char import text_lexer_char
from bes.text.text_lexer_state_base import text_lexer_state_base

class _fruit_kiwi_lexer_state_comment(text_lexer_state_base):
  def __init__(self, lexer):
    super().__init__(lexer)

  def handle_char(self, c):
    self.log_handle_char(c)

class _fruit_kiwi_lexer_state_cr(text_lexer_state_base):
  def __init__(self, lexer):
    super().__init__(lexer)

  def handle_char(self, c):
    self.log_handle_char(c)

class _fruit_kiwi_lexer_state_cr_error(text_lexer_state_base):
  def __init__(self, lexer):
    super().__init__(lexer)

  def handle_char(self, c):
    self.log_handle_char(c)

class _fruit_kiwi_lexer_state_end(text_lexer_state_base):
  def __init__(self, lexer):
    super().__init__(lexer)

  def handle_char(self, c):
    self.log_handle_char(c)

class _fruit_kiwi_lexer_state_expecting_value(text_lexer_state_base):
  def __init__(self, lexer):
    super().__init__(lexer)

  def handle_char(self, c):
    self.log_handle_char(c)

class _fruit_kiwi_lexer_state_key(text_lexer_state_base):
  def __init__(self, lexer):
    super().__init__(lexer)

  def handle_char(self, c):
    self.log_handle_char(c)

class _fruit_kiwi_lexer_state_section_name(text_lexer_state_base):
  def __init__(self, lexer):
    super().__init__(lexer)

  def handle_char(self, c):
    self.log_handle_char(c)

class _fruit_kiwi_lexer_state_section_name_error(text_lexer_state_base):
  def __init__(self, lexer):
    super().__init__(lexer)

  def handle_char(self, c):
    self.log_handle_char(c)

class _fruit_kiwi_lexer_state_space(text_lexer_state_base):
  def __init__(self, lexer):
    super().__init__(lexer)

  def handle_char(self, c):
    self.log_handle_char(c)

class _fruit_kiwi_lexer_state_start(text_lexer_state_base):
  def __init__(self, lexer):
    super().__init__(lexer)

  def handle_char(self, c):
    self.log_handle_char(c)

class _fruit_kiwi_lexer_state_start_error(text_lexer_state_base):
  def __init__(self, lexer):
    super().__init__(lexer)

  def handle_char(self, c):
    self.log_handle_char(c)

class _fruit_kiwi_lexer_state_value(text_lexer_state_base):
  def __init__(self, lexer):
    super().__init__(lexer)

  def handle_char(self, c):
    self.log_handle_char(c)

class _fruit_kiwi_lexer_state_value_space(text_lexer_state_base):
  def __init__(self, lexer):
    super().__init__(lexer)

  def handle_char(self, c):
    self.log_handle_char(c)

class _fruit_kiwi_lexer_token(object):

  def __init__(self, lexer):
    check.check_text_lexer(lexer)

    self._lexer = lexer

  COMMENT = 'comment'
  DONE = 'done'
  LINE_BREAK = 'line_break'
  SECTION_BEGIN = 'section_begin'
  SECTION_END = 'section_end'
  SPACE = 'space'
  STRING = 'string'

  def make_comment(self, value, position):
    return lexer_token(self.COMMENT, value, self._lexer.position)

  def make_done(self, value, position):
    return lexer_token(self.DONE, value, self._lexer.position)

  def make_line_break(self, value, position):
    return lexer_token(self.LINE_BREAK, value, self._lexer.position)

  def make_section_begin(self, value, position):
    return lexer_token(self.SECTION_BEGIN, value, self._lexer.position)

  def make_section_end(self, value, position):
    return lexer_token(self.SECTION_END, value, self._lexer.position)

  def make_space(self, value, position):
    return lexer_token(self.SPACE, value, self._lexer.position)

  def make_string(self, value, position):
    return lexer_token(self.STRING, value, self._lexer.position)

class _fruit_kiwi_lexer_base(text_lexer_base):

  def __init__(self, kiwi, source = None):
    super().__init__(log_tag, source = source)

    self.token = _fruit_kiwi_lexer_token(self)
    self.char = text_lexer_char

    self.comment = _fruit_kiwi_lexer_state_comment(self)
    self.cr = _fruit_kiwi_lexer_state_cr(self)
    self.cr_error = _fruit_kiwi_lexer_state_cr_error(self)
    self.end = _fruit_kiwi_lexer_state_end(self)
    self.expecting_value = _fruit_kiwi_lexer_state_expecting_value(self)
    self.key = _fruit_kiwi_lexer_state_key(self)
    self.section_name = _fruit_kiwi_lexer_state_section_name(self)
    self.section_name_error = _fruit_kiwi_lexer_state_section_name_error(self)
    self.space = _fruit_kiwi_lexer_state_space(self)
    self.start = _fruit_kiwi_lexer_state_start(self)
    self.start_error = _fruit_kiwi_lexer_state_start_error(self)
    self.value = _fruit_kiwi_lexer_state_value(self)
    self.value_space = _fruit_kiwi_lexer_state_value_space(self)
'''
    self.assert_text_file_equal_fuzzy( expected_code, tmp_py, ignore_white_space = False )

  def test__make_token_class_code_indent_0(self):
    expected = '''\
class _fruit_kiwi_lexer_token(object):

  def __init__(self, lexer):
    check.check_text_lexer(lexer)

    self._lexer = lexer

  A = 'a'
  B = 'b'
  C = 'c'

  def make_a(self, value, position):
    return lexer_token(self.A, value, self._lexer.position)

  def make_b(self, value, position):
    return lexer_token(self.B, value, self._lexer.position)

  def make_c(self, value, position):
    return lexer_token(self.C, value, self._lexer.position)
'''
    actual = mermaid._make_token_class_code('_fruit',
                                            'kiwi',
                                            [ 'a', 'b', 'c' ],
                                            indent = 0)
    self.assertEqual( expected, actual )

  def test__make_token_class_code_indent_2(self):
    expected = '''\
  class _fruit_kiwi_lexer_token(object):

    def __init__(self, lexer):
      check.check_text_lexer(lexer)

      self._lexer = lexer

    A = 'a'
    B = 'b'
    C = 'c'

    def make_a(self, value, position):
      return lexer_token(self.A, value, self._lexer.position)

    def make_b(self, value, position):
      return lexer_token(self.B, value, self._lexer.position)

    def make_c(self, value, position):
      return lexer_token(self.C, value, self._lexer.position)
'''
    actual = mermaid._make_token_class_code('_fruit',
                                            'kiwi',
                                            [ 'a', 'b', 'c' ],
                                            indent = 2)
    self.assertEqual( expected, actual )
    
if __name__ == '__main__':
  unit_test.main()
