#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple
import os
import os.path as path
import io
from ..common.point import point
from ..fs.file_check import file_check
from ..fs.file_util import file_util
from ..system.check import check
from ..text.lexer_token import lexer_token
from ..text.text_line_parser import text_line_parser
from ..text.white_space import white_space

from .mmd_document import mmd_document
from .mmd_transition_list import mmd_transition_list
from .mmd_transition import mmd_transition

class mermaid(object):

  @classmethod
  def state_diagram_parse_file(clazz, filename, indent = 2):
    filename = file_check.check_file(filename)
    check.check_int(indent)

    text = file_util.read(filename, codec = 'utf-8')
    return clazz.state_diagram_parse_text(text, indent = indent)

  _HEADER = '''\
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.text.text_lexer_base import text_lexer_base
from bes.text.lexer_token import lexer_token
from bes.text.text_lexer_state_base import text_lexer_state_base
'''
  
  _LEXER_CLASS_TEMPLATE = '''\
class {namespace}_{name}_lexer_base(text_lexer_base):

  def __init__(self, {name}, source = None):
    super().__init__(log_tag, source = source)

    self.token = {namespace}_{name}_lexer_token(self)
'''

  @classmethod
  def state_diagram_generate_code(clazz, filename, namespace, name, output_directory,
                                  indent = 2, skip_start_state = True, skip_end_state = True):
    filename = file_check.check_file(filename)
    check.check_string(namespace)
    check.check_string(name)
    check.check_string(output_directory)
    check.check_int(indent)

    mmd_doc = clazz.state_diagram_parse_file(filename, indent = indent)
    basename = f'{namespace}_{name}_lexer_detail.py'
    output_filename = path.join(output_directory, basename)
    file_util.mkdir(output_directory)
    with open(output_filename, 'w') as stream:
      stream.write(clazz._HEADER)
      stream.write(os.linesep)
      state_instance_code_list = []
      for state in mmd_doc.states:
        if skip_start_state and state == '__start':
          continue
        if skip_end_state and state == '__end':
          continue
        state_class_code = clazz._make_state_class_code(namespace,
                                                        name,
                                                        state,
                                                        mmd_doc.transitions.from_transitions())
        stream.write(state_class_code)
        stream.write(os.linesep)
        state_class_name = f'{namespace}_{name}_lexer_state_{state}'
        state_instance_code = f'self.{state} = {state_class_name}(self)'
        state_instance_code_list.append(state_instance_code)
      token_class_code = clazz._make_token_class_code(namespace,
                                                      name,
                                                      mmd_doc.tokens)
      stream.write(token_class_code)
      stream.write(os.linesep)
      lexer_class_code = clazz._LEXER_CLASS_TEMPLATE.format(namespace = namespace,
                                                            name = name,
                                                            state = state)
      stream.write(lexer_class_code)
      stream.write(os.linesep)
      for state_instance_code in state_instance_code_list:
        stream.write('    ')
        stream.write(state_instance_code)
        stream.write(os.linesep)
    return output_filename

  @classmethod
  def state_diagram_parse_text(clazz, text, indent = 2):
    check.check_string(text)
    check.check_int(indent)

    tokens = clazz._state_diagram_tokenize(text, indent)
    states = set()
    lexer_tokens = set()
    transitions = mmd_transition_list()
    for token in tokens:
      if token.token_type == 'transition':
        to_state = token.value.to_state
        from_state = token.value.from_state
#        if to_state == '[*]':
#          to_state = '__end'
#        if from_state == '[*]':
#          from_state = '__start'
        #print(f'{from_state} --> {to_state}')
        states.add(to_state)
        states.add(from_state)
        transitions.append(token.value)
      elif token.token_type == 'comment':
        value = token.value.strip()
        if value.startswith('%%LEXER_TOKEN'):
          _, _, lexer_token_name = value.partition(' ')
          lexer_token_name = lexer_token_name.strip()
          lexer_tokens.add(lexer_token_name)
    mmd_states = sorted(list(states))
    mmd_tokens = sorted(list(lexer_tokens))
    return mmd_document(mmd_states, mmd_tokens, transitions)

  @classmethod
  def _state_diagram_tokenize(clazz, text, indent):
    check.check_string(text)
    check.check_int(indent)

    lines = text_line_parser.parse_lines(text,
                                         strip_comments = False,
                                         strip_text = False,
                                         remove_empties = False)
    tokens = []
    for line_number, line in enumerate(lines, start = 1):
      token = clazz._state_diagram_parse_line(line, line_number, indent)
      tokens.append(token)  
    return tokens
  
  @classmethod
  def _state_diagram_parse_line(clazz, line, line_number, indent):
    count = white_space.count_leading_spaces(line)
    sline = line.strip()
    #print(f'line="{line}" sline="{sline}" count={count}')

    if len(sline) == 0:
      return lexer_token(token_type = 'empty_line',
                         value = line,
                         position = point(count, line_number))

    elif sline.startswith('%%'):
      return lexer_token(token_type = 'comment',
                         value = line,
                         position = point(count, line_number))
    elif count == 0:
      if sline == 'stateDiagram-v2':
        return lexer_token(token_type = 'diagram_type',
                           value = 'stateDiagram-v2',
                           position = point(0, line_number))
    elif (count % indent) == 0:
      return clazz._state_diagram_parse_directive(count, line, sline, line_number)
    else:
      raise RuntimeError(f'Invalid indent: "{line}"')

  @classmethod
  def _state_diagram_parse_directive(clazz, count, line, sline, line_number):
    if '-->' in line:
      transition = clazz._state_diagram_parse_transition(line)
      return lexer_token(token_type = 'transition',
                         value = transition,
                         position = point(count, line_number))
    else:
      return lexer_token(token_type = 'unknown',
                         value = line,
                         position = point(count, line_number))
    
  @classmethod
  def _state_diagram_parse_transition(clazz, line):
    left, delimiter, right = line.partition('-->')
    assert delimiter == '-->'
    from_state = left.strip()
    to_state, event = clazz._state_diagram_parse_transition_to_state(right)
    return mmd_transition(line, from_state, to_state, event)

  @classmethod
  def _state_diagram_parse_transition_to_state(clazz, line):
    left, delimiter, right = line.partition(':')
    assert delimiter in ( ':' )
    return left.strip(), right.strip()

  _TOKEN_CLASS_TEMPLATE = '''\
class {namespace}_{name}_lexer_token(object):

  def __init__(self, lexer):
    check.check_text_lexer(lexer)

    self._lexer = lexer
'''

  _MAKE_TOKEN_METHOD_TEMPLATE = '''\
  def make_{token_name}(self, value, position):
    return lexer_token(self.{token_name_upper}, value, self._lexer.position)
'''
  
  @classmethod
  def _make_token_class_code(clazz, namespace, name, tokens):
    token_class_code = clazz._TOKEN_CLASS_TEMPLATE.format(namespace = namespace,
                                                          name = name)
    stream = io.StringIO()
    stream.write(token_class_code)
    stream.write(os.linesep)
    for i, token_name in enumerate(tokens):
      if i != 0:
        stream.write(os.linesep)
      stream.write(f"  {token_name.upper()} = '{token_name}'")
    stream.write(2 * os.linesep)
    for i, token_name in enumerate(tokens):
      if i != 0:
        stream.write(os.linesep)
      method_code = clazz._MAKE_TOKEN_METHOD_TEMPLATE.format(token_name = token_name,
                                                             token_name_upper = token_name.upper())
      stream.write(method_code)
    return stream.getvalue()

  _STATE_CLASS_TEMPLATE = '''\
class {namespace}_{name}_lexer_state_{state}(text_lexer_state_base):
  def __init__(self, lexer):
    super().__init__(lexer)

  def handle_char(self, c):
    self.log_handle_char(c)
'''
  @classmethod
  def _make_state_class_code(clazz, namespace, name, state, from_transitions):
    state_class_code = clazz._STATE_CLASS_TEMPLATE.format(namespace = namespace,
                                                          name = name,
                                                          state = state)
    for from_transition, to_transitions in sorted(from_transitions.items()):
      print(f'from_transition={from_transition} to_transitions={to_transitions}')
    return state_class_code
  
