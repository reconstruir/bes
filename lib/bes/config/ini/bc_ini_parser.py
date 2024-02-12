
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.system.check import check
from bes.btl.btl_parser_base import btl_parser_base
from bes.btl.btl_parser_runtime_error import btl_parser_runtime_error
from bes.btl.btl_parser_state_base import btl_parser_state_base

class bc_ini_parser(btl_parser_base):

  class e_unexpected_token(btl_parser_runtime_error):
    def __init__(self, message = None):
      super().__init__(message = message)

  
  class _state_s_global_start(btl_parser_state_base):
    def __init__(self, parser, log_tag):
      name = 's_global_start'
      super().__init__(parser, name, log_tag)
  
    def enter_state(self, context):
      self.log_d(f's_global_start: enter_state')
  
    def leave_state(self, context):
      self.log_d(f's_global_start: leave_state')
  
    def handle_token(self, context, token, first_time):
      self.log_handle_token(token)
      new_state_name = None
      
      if first_time:
        context.node_creator.create_root()
        context.node_creator.create('n_global_section')

      if token.name == 't_done':
        new_state_name = 's_done'
      elif token.name == 't_line_break':
        new_state_name = 's_global_start'
      elif token.name == 't_space':
        new_state_name = 's_global_start'
      elif token.name == 't_key':
        new_state_name = 's_global_expecting_delimiter'
        context.node_creator.create('n_key_value')
        context.node_creator.create('n_key')
        context.node_creator.set_token('n_key', token)
        context.node_creator.add_child('n_key_value', 'n_key')
      elif token.name == 't_comment':
        new_state_name = 's_global_start'
      elif token.name == 't_section_name_begin':
        new_state_name = 's_section_expecting_name'
      else:
        new_state_name = 's_done'
        state_name = self.name
        msg = f'In state "{state_name}" unexpected token: "{token}"'
        raise self.lexer.e_unexpected_token(message = msg)
      
      return new_state_name
  
  class _state_s_global_expecting_delimiter(btl_parser_state_base):
    def __init__(self, parser, log_tag):
      name = 's_global_expecting_delimiter'
      super().__init__(parser, name, log_tag)
  
    def enter_state(self, context):
      self.log_d(f's_global_expecting_delimiter: enter_state')
  
    def leave_state(self, context):
      self.log_d(f's_global_expecting_delimiter: leave_state')
  
    def handle_token(self, context, token, first_time):
      self.log_handle_token(token)
      new_state_name = None
      if token.name == 't_key_value_delimiter':
        new_state_name = 's_global_expecting_value'
      elif token.name == 't_space':
        new_state_name = 's_global_expecting_value'
      else:
        new_state_name = 's_done'
        state_name = self.name
        msg = f'In state "{state_name}" unexpected token: "{token}"'
        raise self.lexer.e_unexpected_token(message = msg)
      
      return new_state_name
  
  class _state_s_global_expecting_value(btl_parser_state_base):
    def __init__(self, parser, log_tag):
      name = 's_global_expecting_value'
      super().__init__(parser, name, log_tag)
  
    def enter_state(self, context):
      self.log_d(f's_global_expecting_value: enter_state')
  
    def leave_state(self, context):
      self.log_d(f's_global_expecting_value: leave_state')
  
    def handle_token(self, context, token, first_time):
      self.log_handle_token(token)
      new_state_name = None
      if token.name == 't_value':
        new_state_name = 's_global_after_value'
        context.node_creator.create('n_value')
        context.node_creator.set_token('n_value', token)
        context.node_creator.add_child('n_key_value', 'n_value')
        context.node_creator.add_child('n_global_section', 'n_key_value')
      elif token.name == 't_space':
        new_state_name = 's_global_expecting_value'
      else:
        new_state_name = 's_done'
        state_name = self.name
        msg = f'In state "{state_name}" unexpected token: "{token}"'
        raise self.lexer.e_unexpected_token(message = msg)
      
      return new_state_name
  
  class _state_s_global_after_value(btl_parser_state_base):
    def __init__(self, parser, log_tag):
      name = 's_global_after_value'
      super().__init__(parser, name, log_tag)
  
    def enter_state(self, context):
      self.log_d(f's_global_after_value: enter_state')
  
    def leave_state(self, context):
      self.log_d(f's_global_after_value: leave_state')
  
    def handle_token(self, context, token, first_time):
      self.log_handle_token(token)
      new_state_name = None
      if token.name == 't_done':
        new_state_name = 's_done'
      elif token.name == 't_space':
        new_state_name = 's_global_after_value'
      elif token.name == 't_comment':
        new_state_name = 's_global_after_value'
      elif token.name == 't_line_break':
        new_state_name = 's_global_start'
      else:
        new_state_name = 's_done'
        state_name = self.name
        msg = f'In state "{state_name}" unexpected token: "{token}"'
        raise self.lexer.e_unexpected_token(message = msg)
      
      return new_state_name
  
  class _state_s_section_expecting_key(btl_parser_state_base):
    def __init__(self, parser, log_tag):
      name = 's_section_expecting_key'
      super().__init__(parser, name, log_tag)
  
    def enter_state(self, context):
      self.log_d(f's_section_expecting_key: enter_state')
  
    def leave_state(self, context):
      self.log_d(f's_section_expecting_key: leave_state')
  
    def handle_token(self, context, token, first_time):
      self.log_handle_token(token)
      new_state_name = None
      if token.name == 't_done':
        new_state_name = 's_done'
      elif token.name == 't_line_break':
        new_state_name = 's_section_expecting_key'
      elif token.name == 't_space':
        new_state_name = 's_section_expecting_key'
      elif token.name == 't_key':
        new_state_name = 's_section_expecting_delimiter'
        context.node_creator.create('n_key_value')
        context.node_creator.create('n_key')
        context.node_creator.set_token('n_key', token)
        context.node_creator.add_child('n_key_value', 'n_key')
      elif token.name == 't_comment':
        new_state_name = 's_section_expecting_key'
      elif token.name == 't_section_name_begin':
        new_state_name = 's_section_expecting_name'
      else:
        new_state_name = 's_done'
        state_name = self.name
        msg = f'In state "{state_name}" unexpected token: "{token}"'
        raise self.lexer.e_unexpected_token(message = msg)
      
      return new_state_name
  
  class _state_s_section_expecting_name(btl_parser_state_base):
    def __init__(self, parser, log_tag):
      name = 's_section_expecting_name'
      super().__init__(parser, name, log_tag)
  
    def enter_state(self, context):
      self.log_d(f's_section_expecting_name: enter_state')
  
    def leave_state(self, context):
      self.log_d(f's_section_expecting_name: leave_state')
  
    def handle_token(self, context, token, first_time):
      self.log_handle_token(token)
      new_state_name = None
      if token.name == 't_section_name':
        new_state_name = 's_section_expecting_name_end'
        context.node_creator.create('n_section')
        context.node_creator.set_token('n_section', token)
      else:
        new_state_name = 's_done'
        state_name = self.name
        msg = f'In state "{state_name}" unexpected token: "{token}"'
        raise self.lexer.e_unexpected_token(message = msg)
      
      return new_state_name
  
  class _state_s_section_expecting_name_end(btl_parser_state_base):
    def __init__(self, parser, log_tag):
      name = 's_section_expecting_name_end'
      super().__init__(parser, name, log_tag)
  
    def enter_state(self, context):
      self.log_d(f's_section_expecting_name_end: enter_state')
  
    def leave_state(self, context):
      self.log_d(f's_section_expecting_name_end: leave_state')
  
    def handle_token(self, context, token, first_time):
      self.log_handle_token(token)
      new_state_name = None
      if token.name == 't_section_name_end':
        new_state_name = 's_section_after_section_name'
      else:
        new_state_name = 's_done'
        state_name = self.name
        msg = f'In state "{state_name}" unexpected token: "{token}"'
        raise self.lexer.e_unexpected_token(message = msg)
      
      return new_state_name
  
  class _state_s_section_after_section_name(btl_parser_state_base):
    def __init__(self, parser, log_tag):
      name = 's_section_after_section_name'
      super().__init__(parser, name, log_tag)
  
    def enter_state(self, context):
      self.log_d(f's_section_after_section_name: enter_state')
  
    def leave_state(self, context):
      self.log_d(f's_section_after_section_name: leave_state')
  
    def handle_token(self, context, token, first_time):
      self.log_handle_token(token)
      new_state_name = None
      if token.name == 't_done':
        new_state_name = 's_done'
      elif token.name == 't_space':
        new_state_name = 's_section_after_section_name'
      elif token.name == 't_comment':
        new_state_name = 's_section_after_section_name'
      elif token.name == 't_line_break':
        new_state_name = 's_section_expecting_key'
      else:
        new_state_name = 's_done'
        state_name = self.name
        msg = f'In state "{state_name}" unexpected token: "{token}"'
        raise self.lexer.e_unexpected_token(message = msg)
      
      return new_state_name
  
  class _state_s_section_expecting_delimiter(btl_parser_state_base):
    def __init__(self, parser, log_tag):
      name = 's_section_expecting_delimiter'
      super().__init__(parser, name, log_tag)
  
    def enter_state(self, context):
      self.log_d(f's_section_expecting_delimiter: enter_state')
  
    def leave_state(self, context):
      self.log_d(f's_section_expecting_delimiter: leave_state')
  
    def handle_token(self, context, token, first_time):
      self.log_handle_token(token)
      new_state_name = None
      if token.name == 't_key_value_delimiter':
        new_state_name = 's_section_expecting_value'
      elif token.name == 't_space':
        new_state_name = 's_section_expecting_delimiter'
      else:
        new_state_name = 's_done'
        state_name = self.name
        msg = f'In state "{state_name}" unexpected token: "{token}"'
        raise self.lexer.e_unexpected_token(message = msg)
      
      return new_state_name
  
  class _state_s_section_expecting_value(btl_parser_state_base):
    def __init__(self, parser, log_tag):
      name = 's_section_expecting_value'
      super().__init__(parser, name, log_tag)
  
    def enter_state(self, context):
      self.log_d(f's_section_expecting_value: enter_state')
  
    def leave_state(self, context):
      self.log_d(f's_section_expecting_value: leave_state')
  
    def handle_token(self, context, token, first_time):
      self.log_handle_token(token)
      new_state_name = None
      if token.name == 't_value':
        new_state_name = 's_section_after_value'
        context.node_creator.create('n_value')
        context.node_creator.set_token('n_value', token)
        context.node_creator.add_child('n_key_value', 'n_value')
        context.node_creator.add_child('n_root', 'n_key_value')
      elif token.name == 't_space':
        new_state_name = 's_section_expecting_value'
      else:
        new_state_name = 's_done'
        state_name = self.name
        msg = f'In state "{state_name}" unexpected token: "{token}"'
        raise self.lexer.e_unexpected_token(message = msg)
      
      return new_state_name
  
  class _state_s_section_after_value(btl_parser_state_base):
    def __init__(self, parser, log_tag):
      name = 's_section_after_value'
      super().__init__(parser, name, log_tag)
  
    def enter_state(self, context):
      self.log_d(f's_section_after_value: enter_state')
  
    def leave_state(self, context):
      self.log_d(f's_section_after_value: leave_state')
  
    def handle_token(self, context, token, first_time):
      self.log_handle_token(token)
      new_state_name = None
      if token.name == 't_done':
        new_state_name = 's_done'
      elif token.name == 't_space':
        new_state_name = 's_section_after_value'
      elif token.name == 't_comment':
        new_state_name = 's_section_after_value'
      elif token.name == 't_line_break':
        new_state_name = 's_section_expecting_key'
      else:
        new_state_name = 's_done'
        state_name = self.name
        msg = f'In state "{state_name}" unexpected token: "{token}"'
        raise self.lexer.e_unexpected_token(message = msg)
      
      return new_state_name
  
  class _state_s_done(btl_parser_state_base):
    def __init__(self, parser, log_tag):
      name = 's_done'
      super().__init__(parser, name, log_tag)
  
    def enter_state(self, context):
      self.log_d(f's_done: enter_state')
  
    def leave_state(self, context):
      self.log_d(f's_done: leave_state')
  
    def handle_token(self, context, token, first_time):
      self.log_handle_token(token)
      new_state_name = None
      
      return new_state_name

  def __init__(self, lexer):
    check.check_btl_lexer(lexer)
    states = {
      's_global_start': self._state_s_global_start(self, lexer.log_tag),
      's_global_expecting_delimiter': self._state_s_global_expecting_delimiter(self, lexer.log_tag),
      's_global_expecting_value': self._state_s_global_expecting_value(self, lexer.log_tag),
      's_global_after_value': self._state_s_global_after_value(self, lexer.log_tag),
      's_section_expecting_key': self._state_s_section_expecting_key(self, lexer.log_tag),
      's_section_expecting_name': self._state_s_section_expecting_name(self, lexer.log_tag),
      's_section_expecting_name_end': self._state_s_section_expecting_name_end(self, lexer.log_tag),
      's_section_after_section_name': self._state_s_section_after_section_name(self, lexer.log_tag),
      's_section_expecting_delimiter': self._state_s_section_expecting_delimiter(self, lexer.log_tag),
      's_section_expecting_value': self._state_s_section_expecting_value(self, lexer.log_tag),
      's_section_after_value': self._state_s_section_after_value(self, lexer.log_tag),
      's_done': self._state_s_done(self, lexer.log_tag),
    }
    super().__init__(lexer, self._DESC_TEXT, states)
  _DESC_TEXT = """
#BTL
#
parser
  name: bc_ini_parser
  description: A ini style config file parser
  version: 1.0
  start_state: s_global_start
  end_state: s_done

errors
  e_unexpected_token: In state "{state_name}" unexpected token: "{token}"

states

  s_global_start
    transitions
      t_done: s_done
      t_line_break: s_global_start
      t_space: s_global_start
      t_key: s_global_expecting_delimiter
        node create n_key_value
        node create n_key
        node set_token n_key
        node add_child n_key_value n_key
      t_comment: s_global_start
      t_section_name_begin: s_section_expecting_name
      default: s_done
        error e_unexpected_token
    one_time_commands
      node create_root n_root
      node create n_global_section

  s_global_expecting_delimiter
    transitions
      t_key_value_delimiter: s_global_expecting_value
      t_space: s_global_expecting_value
      default: s_done
        error e_unexpected_token

  s_global_expecting_value
    transitions
      t_value: s_global_after_value
        node create n_value
        node set_token n_value
        node add_child n_key_value n_value
        node add_child n_global_section n_key_value
      t_space: s_global_expecting_value
      default: s_done
        error e_unexpected_token

  s_global_after_value
    transitions
      t_done: s_done
      t_space: s_global_after_value
      t_comment: s_global_after_value
      t_line_break: s_global_start
      default: s_done
        error e_unexpected_token

  s_section_expecting_key
    transitions
      t_done: s_done
      t_line_break: s_section_expecting_key
      t_space: s_section_expecting_key
      t_key: s_section_expecting_delimiter
        node create n_key_value
        node create n_key
        node set_token n_key
        node add_child n_key_value n_key
      t_comment: s_section_expecting_key
      t_section_name_begin: s_section_expecting_name
      default: s_done
        error e_unexpected_token

  s_section_expecting_name
    transitions
      t_section_name: s_section_expecting_name_end
        node create n_section
        node set_token n_section
      default: s_done
        error e_unexpected_token

  s_section_expecting_name_end
    transitions
      t_section_name_end: s_section_after_section_name
      default: s_done
        error e_unexpected_token

  s_section_after_section_name
    transitions
      t_done: s_done
      t_space: s_section_after_section_name
      t_comment: s_section_after_section_name
      t_line_break: s_section_expecting_key
      default: s_done
        error e_unexpected_token

  s_section_expecting_delimiter
    transitions
      t_key_value_delimiter: s_section_expecting_value
      t_space: s_section_expecting_delimiter
      default: s_done
        error e_unexpected_token

  s_section_expecting_value
    transitions
      t_value: s_section_after_value
        node create n_value
        node set_token n_value
        node add_child n_key_value n_value
        node add_child n_root n_key_value
      t_space: s_section_expecting_value
      default: s_done
        error e_unexpected_token

  s_section_after_value
    transitions
      t_done: s_done
      t_space: s_section_after_value
      t_comment: s_section_after_value
      t_line_break: s_section_expecting_key
      default: s_done
        error e_unexpected_token

  s_done

start_commands
  node create_root n_root
  node create n_global_section

end_commands
  node add_child n_root n_global_section

"""
check.register_class(bc_ini_parser, include_seq = False)
