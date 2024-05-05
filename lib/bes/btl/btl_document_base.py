#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os

from ..system.log import logger
from ..system.check import check
from ..property.cached_property import cached_property
from ..files.bf_file_ops import bf_file_ops
from ..files.bf_check import bf_check
from ..text.line_numbers import line_numbers

from .btl_comment_position import btl_comment_position
from .btl_debug import btl_debug
from .btl_document_error import btl_document_error
from .btl_document_insertion import btl_document_insertion
from .btl_lexer_token import btl_lexer_token
from .btl_parser_node import btl_parser_node
from .btl_parser_options import btl_parser_options

from abc import abstractmethod
from abc import ABCMeta

class btl_document_base(metaclass = ABCMeta):

  _log = logger('btl_document')
  
  def __init__(self, text = None, parser_options = None):
    check.check_string(text, allow_none = True)
    check.check_btl_parser_options(parser_options, allow_none = True)

    lexer_class = self.lexer_class()
    parser_class = self.parser_class()
    check.check_class(lexer_class)
    check.check_class(parser_class)
    
    self._lexer = lexer_class()
    self._parser_options = parser_options or btl_parser_options()
    self._parser = parser_class(self._lexer)
    self._exception_class = self.exception_class()
    self.text = text or ''
    self._root_node = None
    self._tokens = None
    self._do_parse()

  def __str__(self):
    return self.text
  
  @classmethod
  @abstractmethod
  def lexer_class(clazz):
    raise NotImplementedError(f'lexer_class')

  @classmethod
  @abstractmethod
  def parser_class(clazz):
    raise NotImplementedError(f'parser_class')

  @classmethod
  @abstractmethod
  def exception_class(clazz):
    raise NotImplementedError(f'exception_class')
  
  @abstractmethod
  def determine_insertion(self, parent_node, child_node, new_tokens):
    raise NotImplementedError(f'determine_insertion')

  @property
  def root_node(self):
    return self._root_node

  @property
  def tokens(self):
    return self._tokens
  
  def to_source_string(self):
    return self._tokens.to_source_string()

  @property
  def text(self):
    return self._text

  @text.setter
  def text(self, text):
    self._text = text
    self._line_break_str = self._determine_line_break_str(self._text)

  @property
  def lexer(self):
    return self._lexer

  @property
  def parser(self):
    return self._parser
  
  @property
  def line_break_str(self):
    return self._line_break_str

  @classmethod
  def _determine_line_break_str(clazz, text):
    if '\r\n' in text:
      return '\r\n'
    elif '\n' in text:
      return '\n'
    else:
      return os.linesep
  
  def text_to_debug_str(self):
    return line_numbers.add_line_numbers(self.text)

  def _log_nodes(self, label, name, n):
    self._log.log_d(f'{label}: {name}:\n====\n{str(n)}\n====', multi_line = True)

  def _log_tokens(self, label, name, tokens):
    self._log.log_d(f'{label}: {name}:\n====\n{tokens.to_debug_str()}\n====', multi_line = True)
    
  def _do_parse(self):
    self._root_node, self._tokens = self._parse_text(self._text)
    self._log_nodes('_do_parse', 'root_node', self._root_node)
    self._log_tokens('_do_parse', 'tokens', self._tokens)
    #self._log.log_d(f'=====:text:=====')
    #self._log.log_d(self._text)
    #self._log.log_d(f'================')
    source_string = self.to_source_string()
    #self._log.log_d(f'=====:source:=====')
    #self._log.log_d(source_string)
    #self._log.log_d(f'================')
    if self._text != source_string:
      debug_text = btl_debug.make_debug_str(self._text)
      source_text = btl_debug.make_debug_str(source_string)
      raise self._exception_class(f'Source and text do not match: text="{debug_text}" source="{source_text}"')

  def _update_text(self):
    new_text = self.to_source_string()
    self.text = new_text
    self._log.log_d(f'_update_text: new_text:\n====\n{new_text}\n====', multi_line = True)
    
  def _parse_text(self, text):
    parser_result = self._parser.parse(text, options = self._parser_options)
    assert parser_result.tokens[-1].name == 't_done'
    parser_result.tokens.pop(-1)
    return parser_result.root_node, parser_result.tokens
    
  def reitre_node(self,
                  parent_node,
                  node,
                  starting_token_name,
                  include_previous_line_break,
                  include_next_line_break):
    token_index = node.token.index

    first_token = self._tokens.find_backwards_by_name(token_index, 't_section_name_begin')
    first_index = first_token.index
    last_index = node.largest_index()
    last_token = self._tokens[last_index]
    
    if include_previous_line_break:
      new_line_before_token = self._tokens.find_backwards_by_name(first_index, 't_line_break')
      if new_line_before_token:
        first_token = new_line_before_token

    if include_next_line_break:
      new_line_after_token = self._tokens.find_forwards_by_name(last_index, 't_line_break')
      if new_line_after_token:
        last_token = new_line_after_token

    indeces_to_remove = [ i for i in reversed(range(first_token.index, last_token.index + 1)) ]
    for index_to_remove in indeces_to_remove:
      self._tokens.remove_by_index(index_to_remove)

    parent_node.remove_child(node)

    self._update_text()

  def default_insert_index(self, parent_node, tokens):
    self._log.log_d(f'default_insert_index: parent_node=\n{parent_node}\n tokens=\n{tokens.to_debug_str()}', multi_line = True)
    self._log.log_d(f'default_insert_index: self.tokens=\n{self.tokens.to_debug_str()}', multi_line = True)
    last_child = parent_node.find_last_node()
    parent_node_str = parent_node.to_string(recurse = False)
    last_child_str = last_child.to_string(recurse = False) if last_child else None
    self._log.log_d(f'default_insert_index: parent_node={parent_node_str} last_child={last_child_str}')
    self._log_nodes('default_insert_index', 'root_node', self._root_node)
    self._log_tokens('default_insert_index', 'tokens', self._tokens)

    result = None
    if len(self.tokens) == 0:
      self._log.log_d(f'default_insert_index: case 1: empty tokens')
      result = 0
    elif last_child and last_child.token:
      self._log.log_d(f'default_insert_index: case 2: last child good')
      last_child_index = last_child.token.index
      self._log.log_d(f'default_insert_index: last_child_index={last_child_index}')
      first_insert_index = last_child_index + 1
      self._log.log_d(f'default_insert_index: first_insert_index={first_insert_index}')
      skipped_insert_index = self._tokens.skip_index_by_name(first_insert_index, 'right', 't_line_break', '^')
      self._log.log_d(f'default_insert_index: skipped_insert_index={skipped_insert_index}')
      num_skipped = skipped_insert_index - first_insert_index
      self._log.log_d(f'default_insert_index: num_skipped={num_skipped}')
      if num_skipped > 1:
        skipped_insert_index -= 1
      result = skipped_insert_index
    elif parent_node.token:
      self._log.log_d(f'default_insert_index: case 3: parent token good')
      result = parent_node.token.index + 1
    else:
      self._log.log_d(f'default_insert_index: case 4: whatever')
      skipped_insert_index = self._tokens.skip_index_by_name(0, 'right', 't_line_break', '^')
      self._log.log_d(f'default_insert_index: skipped_insert_index={skipped_insert_index}')
      result = skipped_insert_index
    self._log.log_d(f'default_insert_index: result={result}')

    assert result >= 0
    assert result <= len(self._tokens)
    
    return result

  def _call_parse_text(self, parent_node, text, path):
    path_flat = '/'.join(list(path))
    new_root_node, new_tokens = self._parse_text(text)
    new_node = new_root_node.find_child_by_path(path)
    if not new_node:
      raise self._exception_class(f'Failed to find node with path: "{path_flat}"')
    insertion = self.determine_insertion(parent_node, new_node, new_tokens)

    new_text = text
    if insertion.left_line_break:
      new_text = self.line_break_str + new_text
    if insertion.right_line_break:
      new_text = new_text + self.line_break_str
    if text != new_text:
      old_text_debug = btl_debug.make_debug_str(text)
      new_text_debug = btl_debug.make_debug_str(new_text)
      self._log.log_d(f'_call_parse_text: old_text={old_text_debug} new_text={new_text_debug}')
      new_root_node, new_tokens = self._parse_text(new_text)
      new_node = new_root_node.find_child_by_path(path)
      if not new_node:
        raise self._exception_class(f'Failed to find node with path: "{path_flat}"')
    return insertion, new_node, new_tokens
  
  def add_node_from_text(self, parent_node, text, path):
    'Parse text to a node tree and add that as a child of parent_node'
    check.check_btl_parser_node(parent_node)
    check.check_string(text)
    check.check_tuple(path, check.STRING_TYPES)

    path_flat = '/'.join(list(path))
    
    self._log.log_d(f'add_node_from_text: path="{path_flat}" text:\n====\n{text}\n====', multi_line = True)
    self._log.log_d(f'add_node_from_text: root_node before insertion:\n====\n{str(self.root_node)}\n====', multi_line = True)
    self._log.log_d(f'add_node_from_text: tokens before insertion:\n====\n{self._tokens.to_debug_str()}\n====', multi_line = True)

    insertion, new_node, new_tokens = self._call_parse_text(parent_node, text, path)
    self._log.log_d(f'add_node_from_text: insertion={insertion} new_node:\n====\n{str(new_node)}\n====', multi_line = True)
    self._log.log_d(f'add_node_from_text: new_node:\n====\n{str(new_node)}\n====', multi_line = True)
    self._log.log_d(f'add_node_from_text: new_tokens:\n====\n{new_tokens.to_debug_str()}\n====', multi_line = True)
    parent_node.add_child(new_node)
    self._log.log_d(f'add_node_from_text: root_node after insertion:\n====\n{str(self.root_node)}\n====', multi_line = True)
    real_insert_index = self._tokens.insert_tokens(insertion.index, new_tokens)
    self._log.log_d(f'add_node_from_text: real_insert_index={real_insert_index} tokens after insertion:\n====\n{self._tokens.to_debug_str()}\n====', multi_line = True)
    self._update_text()
    return self._tokens[real_insert_index].position.line

  @cached_property
  def comment_begin_char(self):
    vm = self._parser.lexer.desc.variables.to_variable_manager()
    variables = self._parser_options.variables
    return variables.get('v_comment_begin', vm.variables.get('v_comment_begin'))
    
  def add_comment(self, line, comment, position):
    check.check_int(line)
    check.check_string(comment)
    position = check.check_btl_comment_position(position)

    if position == position.NEW_LINE:
      text = f'{self.comment_begin_char}{comment}{self.line_break_str}'
      insert_index = self._tokens.first_line_to_index(line)
    elif position == position.END_OF_LINE:
      text = f' {self.comment_begin_char}{comment}'
      insert_index = self._tokens.last_line_to_index(line)
    elif position == position.START_OF_LINE:
      text = f'{self.comment_begin_char}{comment}'
      insert_index = self._tokens.first_line_to_index(line)

    new_node, tokens = self._parse_text(text)
    assert insert_index >= 0
    insert_index = self._tokens.insert_tokens(insert_index, tokens)
    self.text = self.to_source_string()
    return self._tokens[insert_index].position.line

  def _make_line_break_token(self):
    return btl_lexer_token(name = 't_line_break', value = self.line_break_str)
  
  def add_line_break(self, line, count = 1):
    check.check_int(line)
    check.check_int(count)

    insert_index = self._tokens.last_line_to_index(line)
    self._log.log_d(f'add_line_break: line={line} insert_index={insert_index}')
    self._log.log_d(f'add_line_break: tokens before:\n====\n{self._tokens.to_debug_str()}\n====', multi_line = True)        
    tokens = count * [ self._make_line_break_token() ]
    self._tokens.insert_tokens(insert_index, tokens)
    
    self.text = self.to_source_string()
    self._log.log_d(f'add_line_break: tokens after:\n====\n{self._tokens.to_debug_str()}\n====', multi_line = True)
    insert_line = self._tokens[insert_index].position.line
    self._log.log_d(f'add_line_break: insert_line={insert_line}')
    return insert_line
    
  def save_file(self, filename, encoding = None, backup = True, perm = None):
    check.check_string(filename)
    check.check_string(encoding, allow_none = True)
    check.check_bool(backup)
    check.check_int(perm, allow_none = True)
    
    new_text = self.to_source_string()
    if os.path.exists(filename):
      filename = bf_check.check_file(filename)
      old_text = bf_file_ops.read_text(filename, encoding = encoding)
      if old_text == new_text:
        return
      if backup:
        bf_file_ops.backup(filename)
    else:
      filename = os.path.abspath(filename)
    bf_file_ops.save_text(filename, new_text, encoding = encoding)
    
  @classmethod
  def load_file(clazz, filename, parser_options = None, encoding = None):
    check.check_btl_parser_options(parser_options, allow_none = True)
    check.check_string(encoding, allow_none = True)
    
    if os.path.exists(filename):
      filename = bf_check.check_file(filename)
      text = bf_file_ops.read_text(filename, encoding = encoding)
    else:
      filename = os.path.abspath(filename)
      text = ''
      
    parser_options = parser_options or btl_parser_options()
    parser_options.source = filename
    return clazz(text, parser_options = parser_options)

  def insert_token(self, index, value):
    insert_index = self._tokens.insert_token(index, value)
    self.text = self.to_source_string()
    return insert_index

  def insert_tokens(self, index, values):
    insert_index = self._tokens.insert_tokens(index, values)
    self.text = self.to_source_string()
    return insert_index

  def make_insertion(self, insert_index, new_tokens):
    result = None
    self._log.log_d(f'make_insertion: insert_index={insert_index}')
    self._log_tokens('make_insertion', 'new_tokens', new_tokens)
    self._log_nodes('make_insertion', 'root_node', self._root_node)
    self._log_tokens('make_insertion', 'tokens', self._tokens)
    if insert_index == len(self._tokens):
      self._log.log_d(f'make_insertion: case 1')
      needs_left = self._need_left_line_break(insert_index, new_tokens)
      needs_right = self._need_right_line_break(insert_index, new_tokens)
      result = btl_document_insertion(insert_index, needs_left, needs_right)
    else:
      self._log.log_d(f'make_insertion: case 2')
      skipped_insert_index = self.tokens.skip_index_by_name(insert_index, 'right', 't_line_break', '*')
      self._log.log_d(f'make_insertion: skipped_insert_index={skipped_insert_index}')
      needs_left = self._need_left_line_break(skipped_insert_index, new_tokens)
      needs_right = self._need_right_line_break(skipped_insert_index, new_tokens)
      self._log.log_d(f'make_insertion: needs_left={needs_left} needs_right={needs_right}')
      result = btl_document_insertion(skipped_insert_index, needs_left, needs_right)
    self._log.log_d(f'make_insertion: result={result}')
    assert result != None
    return result
  
  def _need_left_line_break(self, insert_index, new_tokens):
    self._log.log_d(f'_need_left_line_break: insert_index={insert_index}')
    new_tokens_starts_with_line_break = new_tokens.starts_with_line_break()
    self._log.log_d(f'_need_left_line_break: new_tokens_starts_with_line_break={new_tokens_starts_with_line_break}')
    tokens_has_left_line_break = self.tokens.has_left_line_break(insert_index)
    self._log.log_d(f'_need_left_line_break: tokens_has_left_line_break={tokens_has_left_line_break}')
    if new_tokens_starts_with_line_break:
      result = False
    else:
      result = tokens_has_left_line_break == False
    self._log.log_d(f'_need_left_line_break: CACA: result={result}')
    return result

  def _need_right_line_break(self, insert_index, new_tokens):
    self._log.log_d(f'_need_right_line_break: insert_index={insert_index}')
    new_tokens_ends_with_line_break = new_tokens.ends_with_line_break()
    self._log.log_d(f'_need_right_line_break: new_tokens_ends_with_line_break={new_tokens_ends_with_line_break}')
    tokens_has_right_line_break = self.tokens.has_right_line_break(insert_index)
    self._log.log_d(f'_need_right_line_break: tokens_has_right_line_break={tokens_has_right_line_break}')
    if new_tokens_ends_with_line_break:
      result = False
    else:
      result = tokens_has_right_line_break in ( False, None )
    self._log.log_d(f'_need_right_line_break: CACA: result={result}')
    return result

  @classmethod
  def make_debug_str(clazz, text):
    return btl_debug.make_debug_str(text)
  
check.register_class(btl_document_base, include_seq = False)
