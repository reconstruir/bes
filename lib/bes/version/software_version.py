#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.common.check import check
from bes.compat.cmp import cmp
from bes.text.lexer_token import lexer_token

from .semantic_version import semantic_version
from .semantic_version_lexer import semantic_version_lexer

from collections import namedtuple

class software_version(object):
  'Class to manipulate, sort and compare softeware versions numerically.'
  
  @classmethod
  def compare(clazz, v1, v2):
    '''
    Compare software versions taking into account punctuation using an algorithm similar to debian's
    This function should really try to match debian perfectly:
    https://manpages.debian.org/wheezy/dpkg-dev/deb-version.5.en.html#Sorting_Algorithm
    '''
    check.check_string(v1)
    check.check_string(v2)

    return semantic_version.compare(v1, v2)

  @classmethod
  def sort_versions(clazz, versions, reverse = False):
    tversions = [ ( [ p for p in semantic_version_lexer.tokenize(v, 'sort') ], i ) for i, v in enumerate(versions) ]
    tsorted = sorted(tversions, reverse = reverse)
    return [ versions[i] for _, i in tsorted ]

  @classmethod
  def change_version(clazz, version, deltas):
    sv = semantic_version(version)
    for i, delta in enumerate(deltas):
      sv = sv.change_part(i, delta)
    return str(sv)

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

  _parsed_version = namedtuple('_parsed_version', 'parts, delimiter')
  @classmethod
  def parse_version(clazz, version):
    'Parse the version and return the parts and delimiters in a _parsed_version tuple.'
    tokens = [ token for token in semantic_version_lexer.tokenize(version, 'parse_version') ]
    part_tokens = [ token for token in tokens if token.token_type == semantic_version_lexer.TOKEN_PART ]
    part_delimiter_tokens = [ token for token in tokens if token.token_type == semantic_version_lexer.TOKEN_PART_DELIMITER ]
    parts = tuple([token.value for token in part_tokens])
    delimiters = tuple([token.value for token in part_delimiter_tokens])
    return clazz._parsed_version(parts, delimiters[0] if delimiters else '')
  
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
    str(MAJOR): MAJOR,
    str(MINOR): MINOR,
    str(REVISION): REVISION,
  }

  @classmethod
  def bump_version(clazz, version, component, reset_lower = False):
    '''
    Bump a version.  If component is MAJOR or MINOR the less significant components
    will be reset to zero:

    component=REVISION 1.0.0 -> 1.0.1
    component=MINOR 1.2.3 -> 1.3.0
    component=MAJOR 1.2.3 -> 2.0.0
    '''
    check.check_string(version)
    check.check_bool(reset_lower)

    sv = semantic_version(version)
    component = clazz._COMPONENT_MAP.get(component, component or sv.num_parts - 1)
    assert component != None
    assert isinstance(component, int)
    v = sv.change_part(component, 1)
    if reset_lower:
      for i in range(component + 1, v.num_parts):
        v = v.set_part(i, 0)
    return str(v)

  @classmethod
  def change_component(clazz, version, component, value):
    'Change a component of a version to value.'
    check.check_string(version)
    
    component = clazz._COMPONENT_MAP.get(component, component)
    sv = semantic_version(version)
    return str(sv.set_part(component, int(value)))
