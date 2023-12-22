#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple
#import os
import os.path as path
#import io
import pprint
from ..common.point import point
from ..fs.file_check import file_check
from ..fs.file_util import file_util
from ..system.check import check
from ..system.log import logger
from ..text.lexer_token import lexer_token
from ..text.text_line_parser import text_line_parser
from ..text.white_space import white_space
from ..text.bindent import bindent

from .btl_code_gen_error import btl_code_gen_error
from .btl_code_gen_buffer import btl_code_gen_buffer

class btl_code_gen(object):

  _log = logger('btl')
  @classmethod
  def state_diagram_parse_file(clazz, filename, indent = 2):
    filename = file_check.check_file(filename)
    check.check_int(indent)

    text = file_util.read(filename, codec = 'utf-8')
    return clazz.state_diagram_parse_text(text, indent = indent)

  _HEADER = '''\
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.text.lexer_token import lexer_token
from bes.text.text_lexer_base import text_lexer_base
from bes.text.text_lexer_char import text_lexer_char
from bes.text.text_lexer_state_base import text_lexer_state_base
'''
  
  _LEXER_CLASS_TEMPLATE = '''\
class {namespace}_{name}_lexer_base(text_lexer_base):

  def __init__(self, {name}, source = None):
    super().__init__(log_tag, source = source)

    self.token = {namespace}_{name}_lexer_token(self)
    self.char = text_lexer_char
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
  def _make_token_class_code(clazz, namespace, name, tokens, indent = 0):
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
    return bindent.indent(stream.getvalue(), indent)

  _STATE_CLASS_TEMPLATE = '''\
class {namespace}_{name}_lexer_state_{state}(text_lexer_state_base):
  def __init__(self, lexer):
    super().__init__(lexer)

  def handle_char(self, c):
    self.log_handle_char(c)

    new_state = None
    tokens = []

    {check_event_logic_code}

    self.lexer.change_state(new_state, c)
    return tokens

'''
  @classmethod
  def make_state_class_code(clazz, desc, state):
    check.check_btl_desc(desc)
    check.check_btl_desc_state(state)

    print(f'state={state.name}')
    
    for transition in state.transitions:
      print(f'transition={transition}')

    return 'foo'
    clazz._log.log_d(f'from_transitions={pprint.pformat(from_transitions)}')
    titems = sorted(from_transitions.items())
    check_event_logic_code = ''
    for i, item in enumerate(sorted(from_transitions.items())):
      if_identifier = 'if' if i == 0 else 'elif'
      from_transition, to_transitions = item
      for j, events in enumerate(sorted(to_transitions.items())):
        print(f'events={events} - {type(events)}')
        for event in events:
          print(f'FUCK: event={event}')
#          if_code = f'{if_identifier} c in {chars}:\n  # to_state={to_state}\n'
#      print(f'{i}: from_transition={from_transition} to_transitions={to_transitions}')
    check_event_logic_code = check_event_logic_code + if_code
    state_class_code = clazz._STATE_CLASS_TEMPLATE.format(namespace = namespace,
                                                          name = name,
                                                          state = state,
                                                          check_event_logic_code = check_event_logic_code)
    return state_class_code
  

  @classmethod
  def _make_transition_code(clazz, char_map, transition):
    check.check_btl_desc_char_map(char_map)
    check.check_btl_desc_state_transition(transition)

    b = btl_code_gen_buffer()
    
    char_name = transition.char_name
    if char_name != 'default' and char_name not in char_map:
      raise btl_code_gen_error(f'char not found in char_map: "{char_name}"')
    char = char_map[char_name]

    b.write_line(f'if c in {char.chars}:')
    b.write_line(f'  new_state = {transition.to_state}')

    for command in transition.commands:
      command_code = clazz._make_state_command_code(command)
      b.write_line(command_code, indent_depth = 1)

    return b.get_value()

  @classmethod
  def _make_state_command_code(clazz, command):
    check.check_btl_desc_state_command(command)

    b = btl_code_gen_buffer()

    if command.name == 'yield':
      b.write_line(f'tokens.append(self.make_token({command.arg}, self.buffer_value(), self.position)')
    elif command.name == 'buffer':
      if command.arg == 'write':
        b.write_line(f'self.lexer.buffer_write(c)')
      elif command.arg == 'reset':
        b.write_line(f'self.lexer.buffer_reset()')
      else:
        b.write_line(f'''raise btl_lexer_error('Unknown buffer command: "{command.arg}"')''')
    
    return b.get_value()
  
