#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.common.check import check
from bes.compat.cmp import cmp
from bes.text.lexer_token import lexer_token
from bes.property.cached_property import cached_property
from bes.compat.StringIO import StringIO

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
    
    tokens1 = [ token for token in semantic_version_lexer.tokenize(v1, 'semantic_version') ]
    tokens2 = [ token for token in semantic_version_lexer.tokenize(v2, 'semantic_version') ]
    return cmp(tokens1, tokens2)
