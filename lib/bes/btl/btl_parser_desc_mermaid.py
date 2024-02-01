#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import io
import os

from ..system.check import check
from ..text.bindent import bindent

class btl_parser_desc_mermaid(object):

  @classmethod
  def desc_to_mermain_diagram(clazz, desc):
    check.check_btl_parser_desc(desc)
    
    b = io.StringIO()
    b.write('stateDiagram-v2' + os.linesep)
    b.write('  direction LR' + os.linesep)
    b.write(os.linesep)

    for state in desc.states:
      b.write(clazz._state_to_mermaid(desc, state))
      b.write(os.linesep)

    return b.getvalue().strip() + os.linesep

  @classmethod
  def _state_to_mermaid(clazz, desc, state):
    b = io.StringIO()
    b.write(f'%% {state.name} state' + os.linesep)

    if state.name == desc.header.start_state:
      b.write(f'[*] --> {state.name}' + os.linesep)
    elif state.name == desc.header.end_state:
      b.write(f'{state.name} --> [*]' + os.linesep)

    for transition in state.transitions:
      b.write(clazz._transition_to_mermaid(desc, state, transition))
      
    return bindent.indent(b.getvalue(), 2)

  @classmethod
  def _transition_to_mermaid(clazz, desc, state, transition):
    b = io.StringIO()
    b.write(f'{state.name} --> {transition.to_state}: {transition.char_name}' + os.linesep)
    return b.getvalue()
  
'''    
  %% start state
  [*] --> start
  start --> end: EOS
  start --> comment: SEMICOLON
  start --> space: TAB SPACE
  start --> cr: CR
  start --> start: NL
  start --> section_name: OPEN_BRACKET
  start --> key: UNDERSCORE LOWER_LETTER UPPER_LETTER DIGIT
  start --> expecting_value: EQUAL
  start --> start_error: ANY
  note right of start_error
    Unexpected "."
  end note
  
  %% space state
  space --> space: TAB SPACE
  space --> end: EOS
  space --> cr: CR
  space --> start: NL
  space --> key: UNDERSCORE LOWER_LETTER UPPER_LETTER DIGIT
  space --> expecting_value: EQUAL
  
  %% cr state
  cr --> start: NL]
  cr --> cr_error: ANY EOS
  note right of cr_error
    Expecting "NL" instead of "."
  end note

  %% comment state
  comment --> comment: ANY
  comment --> cr: CR
  comment --> start: NL
  comment --> end: EOS

  %%class comment caca

  %% section_name state
  section_name --> section_name: UNDERSCORE LOWER_LETTER UPPER_LETTER DIGIT PERIOD
  section_name --> start: ]
  section_name --> section_name_error: TAB SPACE CR NL EOS
  note left of section_name_error
    Unexpected char in section name
  end note
  
  %% key state
  key --> key: UNDERSCORE LOWER_LETTER UPPER_LETTER DIGIT PERIOD
  key --> space: TAB SPACE
  key --> cr: CR
  key --> start: NL
  key --> expecting_value: EQUAL
  key --> end: EOS
  
  %% expecting_value state
  expecting_value --> value_space: TAB SPACE
  expecting_value --> cr: CR
  expecting_value --> start: NL
  expecting_value --> end: EOS
  expecting_value --> value: ANY

  %% value_space state
  value_space --> value_space: TAB SPACE
  value_space --> cr: CR
  value_space --> start: NL
  value_space --> end: EOS
  value_space --> value: ANY
  
  %% value state
  value --> value: ANY
%%  value --> space: TAB SPACE
  value --> cr: CR
  value --> start: NL
  value --> end: EOS

  %% end state
  end --> [*]
'''
