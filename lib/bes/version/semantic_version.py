#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from ..system.check import check
from bes.common.string_util import string_util
from bes.common.object_util import object_util
from bes.compat.StringIO import StringIO
from bes.compat.cmp import cmp
from bes.property.cached_property import cached_property
from bes.text.lexer_token import lexer_token

from .semantic_version_lexer import semantic_version_lexer
from .semantic_version_error import semantic_version_error

from collections import namedtuple

class semantic_version(object):
  'Class to manager a semantic version for a software package.'

  def __init__(self, version_string):
    check.check_string(version_string)
    
    self._version_string = version_string

  def __str__(self):
    return self._version_string

  def __repr__(self):
    return self._version_string
  
  def __getitem__(self, i):
    return self.parts[i]

  def __setitem__(self, i, value):
    raise AttributeError('values are read-only')

  def __len__(self):
    return len(self.parts)

  def __eq__(self, other):
    if check.is_string(other):
      other = semantic_version(other)
    return self._tokens == other._tokens

  def __ne__(self, other):
    if check.is_string(other):
      other = semantic_version(other)
    return self._tokens != other._tokens

  def __lt__(self, other):
    if check.is_string(other):
      other = semantic_version(other)
    return self._tokens < other._tokens

  def __le__(self, other):
    if check.is_string(other):
      other = semantic_version(other)
    return self._tokens <= other._tokens

  def __gt__(self, other):
    if check.is_string(other):
      other = semantic_version(other)
    return self._tokens > other._tokens

  def __ge__(self, other):
    if check.is_string(other):
      other = semantic_version(other)
    return self._tokens >= other._tokens
  
  @cached_property
  def _tokens(self):
    'Tokenize a version and return a list of tokens for it.'
    tokens = [ token for token in semantic_version_lexer.tokenize(self._version_string, 'semantic_version') ]
    assert tokens[-1].token_type == semantic_version_lexer.TOKEN_DONE
    tokens.pop(-1)
    return tokens

  @cached_property
  def _semantic_tokens(self):
    semantic_tokens = []
    for token in reversed(self._tokens):
      if token.token_type not in ( semantic_version_lexer.TOKEN_PART, semantic_version_lexer.TOKEN_PART_DELIMITER ):
        break
      semantic_tokens.append(token)
    return [ token for token in reversed(semantic_tokens) ]

  @cached_property
  def _part_tokens(self):
    return [ token for token in self._semantic_tokens if token.token_type == semantic_version_lexer.TOKEN_PART ]

  @cached_property
  def num_parts(self):
    return len(self._part_tokens)

  @cached_property
  def parts(self):
    return tuple([ token.value for token in self._part_tokens ])

  @cached_property
  def has_only_semantic_tokens(self):
    '''
    True if the tokens in version are pursely semantic such as:
      1.2.3
    but not
      1.2.3a
      1.2.alpha
    '''
    return len(self._tokens) == len(self._semantic_tokens)
    
  @classmethod
  def _tokens_to_string(clazz, tokens):
    buf = StringIO()
    for token in tokens:
      buf.write(str(token.value))
    return buf.getvalue()

  def part_value(self, part_index):
    check.check_int(part_index)

    if part_index < 0:
      raise semantic_version_error('part_index should be greater than 0: {}'.format(part_index))
    
    num_part_tokens = len(self._part_tokens)
    if part_index >= num_part_tokens:
      raise semantic_version_error('part_index should be less than {}: {}'.format(num_part_tokens,
                                                                                  part_index))
    return self._part_tokens[part_index].value
  
  def change_part(self, part_index, delta):
    check.check_int(part_index)
    check.check_int(delta)

    return self._change_part_func(part_index, lambda value: value + delta)

  def set_part(self, part_index, value):
    check.check_int(part_index)
    check.check_int(value)

    return self._change_part_func(part_index, lambda _: value)

  def _change_part_func(self, part_index, func):
    check.check_int(part_index)

    if part_index < 0:
      raise semantic_version_error('part_index should be greater than 0: {}'.format(part_index))
    
    tokens = self._tokens[:]
    part_tokens = self._part_tokens[:]
    num_part_tokens = len(part_tokens)
    if part_index >= num_part_tokens:
      raise semantic_version_error('part_index should be less than {}: {}'.format(num_part_tokens,
                                                                                  part_index))
    part_token = part_tokens[part_index]
    part_token_id = id(part_token)
    new_part_value = func(part_token.value)
    new_part_token = part_token.clone(mutations = { 'value': new_part_value })
    for i, token in enumerate(tokens):
      if id(token) == id(part_token):
        tokens[i] = new_part_token
        break
    new_version_string = self._tokens_to_string(tokens)
    return semantic_version(new_version_string)
  
  @classmethod
  def compare(clazz, v1, v2):
    '''
    Compare software versions taking into account punctuation using an algorithm similar to debian's
    This function should really try to match debian perfectly:
    https://manpages.debian.org/wheezy/dpkg-dev/deb-version.5.en.html#Sorting_Algorithm
    '''
    check.check_string(v1)
    check.check_string(v2)
    
    sv1 = semantic_version(v1)
    sv2 = semantic_version(v2)
    return cmp(sv1._tokens, sv2._tokens)

  @classmethod
  def sort_string_list(clazz, l, reverse = False):
    'Sort a string list using semantic_version'
    check.check_list(l, check.STRING_TYPES)
    return sorted(l, key = lambda v: semantic_version(v)._tokens,  reverse = reverse)

  @classmethod
  def _check_cast_func(clazz, obj):
    if check.is_string(obj):
      return semantic_version(obj)
    return obj

  _clause = namedtuple('_clause', 'operator, version')
  @classmethod
  def _parse_clause(clazz, clause):
    check.check_string(clause)

    parts = string_util.split_by_white_space(clause, strip = True)
    if len(parts) != 2:
      raise ValueError(f'Invalid clause: "{clause}"')
    operator = parts[0]
    if operator not in ( '<', '>', '==', '<=', '>=', '!=' ):
      raise ValueError(f'Invalid operator: "{operator}"')
    version = semantic_version(parts[1])
    if not version.has_only_semantic_tokens:
      raise ValueError(f'Invalid version: "{version}"')
    return clazz._clause(operator, version)

  _OPERATOR_MAP = {
    '==': '__eq__',
    '!=': '__ne__',
    '<=': '__le__',
    '>=': '__ge__',
     '>': '__gt__',
     '<': '__lt__',
  }

  def _match_one_clause(self, clause):
    parsed_clause = self._parse_clause(clause)
    assert parsed_clause.operator in self._OPERATOR_MAP
    method = getattr(self, self._OPERATOR_MAP[parsed_clause.operator])
    return method(parsed_clause.version)

  def match_clause(self, clause):
    if check.is_tuple(clause):
      clauses = list(clause)
    else:
      clauses = object_util.listify(clause)
    check.check_string_seq(clauses)

    for next_clause in clauses:
      if not self._match_one_clause(next_clause):
        return False
    return True
  
check.register_class(semantic_version, include_seq = False, cast_func = semantic_version._check_cast_func)
  
