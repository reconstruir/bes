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
    b.write(f'{state.name} --> {transition.to_state}: {transition.token_name}' + os.linesep)
    return b.getvalue()
