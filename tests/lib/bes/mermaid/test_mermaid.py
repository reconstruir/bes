#!/usr/bin/env python3
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test
from bes.mermaid.mermaid import mermaid

class test_mermaid(unit_test):

  def test_parse_state_diagram_text(self):
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
    ], mermaid.parse_state_diagram_text(text) )
    
if __name__ == '__main__':
  unit_test.main()
