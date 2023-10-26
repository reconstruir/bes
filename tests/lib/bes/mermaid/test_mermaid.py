#!/usr/bin/env python3
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test
from bes.mermaid.mermaid import mermaid
from bes.fs.file_util import file_util

class test_mermaid(unit_test):

  def test_state_diagram_parse_text(self):
    text = '''
stateDiagram-v2
  direction LR
  
  %% start state
  [*] --> start
  start --> [*]: eos
  start --> comment: [#0059;]
  start --> space: [\t ␠]
  start --> cr: [␍]
  start --> start: [␤]
  start --> section_name: [
  start --> key: [_ a-z A-Z 0-9]
  start --> expecting_value: [=]
  start --> start_error: [.]
  note right of start_error
    Unexpected "."
  end note
  
  %% space state
  space --> space: [\t ␠]
  space --> [*]: eos
  space --> cr: [␍]
  space --> start: [␤]
  space --> key: [_ a-z A-Z 0-9]
  space --> expecting_value: [=]
  
  
  %% cr state
  cr --> start: [␤] 
  cr --> cr_error: [.] eos
  note right of cr_error
    Expecting "␤" instead of "."
  end note

  %% comment state
  comment --> comment: [.]
  comment --> cr: [␍]
  comment --> start: [␤]
  comment --> [*]: eos
  
  %% section_name state
  section_name --> section_name: [_ a-z A-Z 0-9 \.]
  section_name --> start: ]
  section_name --> section_name_error: [\t ␠ ␍ ␤] eos
  note left of section_name_error
    Unexpected char in section name
  end note
  
  %% key state
  key --> key: [_ a-z A-Z 0-9 \.]
  key --> space: [\t ␠]
  key --> cr: [␍]
  key --> start: [␤]
  key --> expecting_value: [=]
  key --> [*]: eos
  
  %% expecting_value state
  expecting_value --> value_space: [\t ␠]
  expecting_value --> cr: [␍]
  expecting_value --> start: [␤]
  expecting_value --> [*]: eos
  expecting_value --> value: [.]

  %% value_space state
  value_space --> value_space: [\t ␠]
  value_space --> cr: [␍]
  value_space --> start: [␤]
  value_space --> [*]: eos
  value_space --> value: [.]
  
  %% value state
  value --> value: [.]
%%  value --> space: [\t ␠]
  value --> cr: [␍]
  value --> start: [␤]
  value --> [*]: eos
    '''
    self.assertEqual( [
      '__end',
      '__start',
      'comment',
      'cr',
      'cr_error',
      'expecting_value',
      'key',
      'section_name',
      'section_name_error',
      'space',
      'start',
      'start_error',
      'value',
      'value_space',
    ], mermaid.state_diagram_parse_text(text) )

  def test_state_diagram_generate_code(self):
    text = '''
stateDiagram-v2
  direction LR
  
  %% start state
  [*] --> start
  start --> [*]: eos
  start --> comment: [#0059;]
  comment --> comment: [.]
  comment --> cr: [␍]
  comment --> start: [␤]
  comment --> [*]: eos
    '''

    tmp_mmd = self.make_temp_file(content = text)
    tmp_dir = self.make_temp_dir()
    tmp_py = mermaid.state_diagram_generate_code(tmp_mmd, '_fruit', 'kiwi', tmp_dir)

    expected_code = '''
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.text.text_lexer_base import text_lexer_base
from bes.text.text_lexer_state_base import text_lexer_state_base

class _fruit_kiwi_lexer_state___end(text_lexer_state_base):
  def __init__(self, lexer):
    super().__init__(lexer)

  def handle_char(self, c):
    self.log_handle_char(c)

class _fruit_kiwi_lexer_state___start(text_lexer_state_base):
  def __init__(self, lexer):
    super().__init__(lexer)

  def handle_char(self, c):
    self.log_handle_char(c)

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

class _fruit_kiwi_lexer_state_start(text_lexer_state_base):
  def __init__(self, lexer):
    super().__init__(lexer)

  def handle_char(self, c):
    self.log_handle_char(c)

class _fruit_kiwi_lexer_base(text_lexer_base):
  def __init__(self, kiwi, source = None):
    super().__init__(log_tag, source = source)


    self.__end = _fruit_kiwi_lexer_state___end(self)
    self.__start = _fruit_kiwi_lexer_state___start(self)
    self.comment = _fruit_kiwi_lexer_state_comment(self)
    self.cr = _fruit_kiwi_lexer_state_cr(self)
    self.start = _fruit_kiwi_lexer_state_start(self)
'''
    self.assert_text_file_equal_fuzzy( expected_code, tmp_py )
    
if __name__ == '__main__':
  unit_test.main()
