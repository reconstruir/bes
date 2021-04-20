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
    
    parsed_version = clazz.parse_version(version)
    parts = list(parsed_version.parts)
    if len(parts) == 3:
      bumped = clazz._bump_version_three_components(version, parts, component, parsed_version.delimiter, reset_lower)
    elif len(parts) == 2:
      bumped = clazz._bump_version_two_components(version, parts, component, parsed_version.delimiter, reset_lower)
    elif len(parts) == 1:
      bumped = clazz._bump_version_one_component(version, parts, component, parsed_version.delimiter)
    else:
      raise ValueError('version \"%s\" should have at least 1, 2, or 3 components' % (version))
    return bumped

  @classmethod
  def _bump_version_three_components(clazz, version_string, parts, component, delimiter, reset_lower):
    '''
    Bump a 3 component version.
    component=REVISION 1.0.0 -> 1.0.1
    component=MINOR 1.2.3 -> 1.3.0
    component=MAJOR 1.2.3 -> 2.0.0
    '''
    assert len(parts) == 3
    if component is None:
      component = clazz.REVISION
    component = clazz._COMPONENT_MAP.get(component, component)
    if component == clazz.MAJOR:
      if reset_lower:
        parts[clazz.MINOR] = 0
        parts[clazz.REVISION] = 0
      deltas = [ 1, 0, 0 ]
    elif component == clazz.MINOR:
      if reset_lower:
        parts[clazz.REVISION] = 0
      deltas = [ 0, 1, 0 ]
    elif component == clazz.REVISION:
      deltas = [ 0, 0, 1 ]
    else:
      raise ValueError('Invalid component \"{component}\" for \"{version}\"'.format(component = component,
                                                                                    version = version_string))
    string_version = delimiter.join([ str(c) for c in parts ])
    return software_version.change_version(string_version, deltas)
  
  @classmethod
  def _bump_version_two_components(clazz, version_string, parts, component, delimiter, reset_lower):
    '''
    Bump a 2 component version.
    component=MINOR 1.2 -> 1.3
    component=MAJOR 1.2 -> 2.0
    '''
    assert len(parts) == 2
    if component is None:
      component = clazz.MINOR
    component = clazz._COMPONENT_MAP.get(component, component)
    if component == clazz.MAJOR:
      if reset_lower:
        parts[clazz.MINOR] = 0
      deltas = [ 1, 0 ]
    elif component == clazz.MINOR:
      deltas = [ 0, 1 ]
    else:
      raise ValueError('Invalid component \"{component}\" for \"{version}\"'.format(component = component,
                                                                                    version = version_string))
    string_version = delimiter.join([ str(c) for c in parts ])
    return software_version.change_version(string_version, deltas)
  
  @classmethod
  def _bump_version_one_component(clazz, version_string, parts, component, delimiter):
    '''
    Bump a 1 component version.
    component=MAJOR 1 -> 2
    '''
    assert len(parts) == 1
    if component is None:
      component = clazz.MAJOR
    component = clazz._COMPONENT_MAP.get(component, component)
    if component == clazz.MAJOR:
      deltas = [ 1 ]
    else:
      raise ValueError('Invalid component \"{component}\" for \"{version}\"'.format(component = component,
                                                                                    version = version_string))
    string_version = delimiter.join([ str(c) for c in parts ])
    return software_version.change_version(string_version, deltas)
  
  @classmethod
  def change_component(clazz, version, component, value):
    'Change a component of a version to value.'
    check.check_string(version)
    component = clazz._COMPONENT_MAP.get(component, component)
    parsed_version = clazz.parse_version(version)
    parts = list(parsed_version.parts)
    num_components = len(parts)
    if component >= num_components:
      raise ValueError('Invalid component \"{}\" for \"{}\"'.format(component, version))
    parts[component] = value
    return parsed_version.delimiter.join([ str(c) for c in parts ])
