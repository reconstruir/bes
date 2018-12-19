#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.common import check
from bes.compat import cmp
from bes.text import lexer_token

from .version_lexer import version_lexer
import functools
import itertools

class version_compare(object):
    
  @classmethod
  def compare(clazz, v1, v2):
    '''
    Compare software versions taking into account punctuation using an algorithm similar to debian's
    This function should really try to match debian perfectly:
    https://manpages.debian.org/wheezy/dpkg-dev/deb-version.5.en.html#Sorting_Algorithm
    '''
    check.check_string(v1)
    check.check_string(v2)
    tokens1 = [ token for token in version_lexer.tokenize(v1, 'compare') ]
    tokens2 = [ token for token in version_lexer.tokenize(v2, 'compare') ]
    return cmp(tokens1, tokens2)

  @classmethod
  def sort_versions(clazz, versions, reverse = False):
    tversions = [ ( index, version_lexer.tokenize(v, 'sort_versions') ) for index, v in enumerate(versions) ]
    tversions = [ ( [ p for p in version_lexer.tokenize(v, 'sort') ], i ) for i, v in enumerate(versions) ]
    tsorted = sorted(tversions, reverse = reverse)
    return [ versions[i] for _, i in tsorted ]

  @classmethod
  def change_version(clazz, version, deltas):
    tokens = version_lexer.tokenize(version, 'change_version')
    tokens = [ t for t in tokens if t.token_type != version_lexer.TOKEN_DONE ]
    number_tokens = [ token for token in tokens if token.token_type == version_lexer.TOKEN_NUMBER ]
    if len(deltas) > len(number_tokens):
      raise ValueError('Too many deltas (%s) for version: %s' % (str(deltas), version))
    delta_iter = iter(deltas)
    new_tokens = []
    for token in tokens:
      if token.token_type == version_lexer.TOKEN_NUMBER:
        try:
          delta = delta_iter.next()
          new_token = lexer_token(token.token_type, token.value + delta, token.position)
        except StopIteration as ex:
          new_token = token
      else:
          new_token = token
      new_tokens.append(new_token)
    return ''.join([ str(token.value) for token in new_tokens ])
