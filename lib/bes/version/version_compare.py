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
          delta = next(delta_iter)
          new_token = lexer_token(token.token_type, token.value + delta, token.position)
        except StopIteration as ex:
          new_token = token
      else:
          new_token = token
      new_tokens.append(new_token)
    return ''.join([ str(token.value) for token in new_tokens ])

  @classmethod
  def version_range(clazz, start_version, end_version, deltas):
    if clazz.compare(start_version, end_version) > 0:
      raise ValueError('start_version \"%s\" should be smaller than end_version \"%s\"' % (start_version, end_version))
    result = []
    version = start_version
    result.append(version)
    while True:
      version = clazz.change_version(version, deltas)
      rv = clazz.compare(version, end_version)
      if rv <= 0:
        result.append(version)
      if rv >= 0:
        break
    return result

  @classmethod
  def version_to_tuple(clazz, version):
    'Parse the version and return a tuple of the numeric compoents.  Ppunctuation is stripped.'
    tokens = [ token for token in version_lexer.tokenize(version, 'compare') ]
    number_tokens = [ token for token in tokens if token.token_type == version_lexer.TOKEN_NUMBER ]
    return tuple([token.value for token in number_tokens])

  MAJOR = 0
  MINOR = 1
  REVISION = 2

  _COMPONENT_MAP = {
    'major': MAJOR,
    'minor': MINOR,
    'revision': REVISION,
    'MAJOR': MAJOR,
    'MINOR': MINOR,
    'REVISION': REVISION,
    MAJOR: MAJOR,
    MINOR: MINOR,
    REVISION: REVISION,
  }

  @classmethod
  def bump_version(clazz, version, component = None, delimiter = '.'):
    '''
    Bump a version.  If component is MAJOR or MINOR the less significant components
    will be reset to zero:

    component=REVISION 1.0.0 -> 1.0.1
    component=MINOR 1.2.3 -> 1.3.0
    component=MAJOR 1.2.3 -> 2.0.0
    '''
    t = list(clazz.version_to_tuple(version))
    if component is None:
      component = clazz.REVISION
    component = clazz._COMPONENT_MAP[component]
    if len(t) < 3:
      raise ValueError('version \"%s\" should have at least 3 components' % (version))
    if component == clazz.MAJOR:
      t[clazz.MINOR] = 0
      t[clazz.REVISION] = 0
      deltas = [ 1, 0, 0 ]
    elif component == clazz.MINOR:
      t[clazz.REVISION] = 0
      deltas = [ 0, 1, 0 ]
    elif component == clazz.REVISION:
      deltas = [ 0, 0, 1 ]
    else:
      raise ValueError('Invalid component: %s' % (component))
    rounded_version = delimiter.join([ str(c) for c in t ])
    return version_compare.change_version(rounded_version, deltas)
