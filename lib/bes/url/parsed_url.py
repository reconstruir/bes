#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple

from bes.common.check import check
from bes.property.cached_property import cached_property
from bes.common.tuple_util import tuple_util

from urllib import parse as urllib_parse

class parsed_url(namedtuple('parsed_url', 'scheme, netloc, path, params, query, fragment')):
  
  def __new__(clazz, scheme, netloc, path, params, query, fragment):
    check.check_string(scheme)
    check.check_string(netloc)
    check.check_string(path)
    check.check_string(params)
    check.check_string(query)
    check.check_string(fragment)

    return clazz.__bases__[0].__new__(clazz, scheme, netloc, path, params, query, fragment)

  def to_dict(self):
    return dict(self._asdict())

  def to_ordered_dict(self):
    return self._asdict()
  
  def __str__(self):
    return self.to_string()
  
  def __repr__(self):
    return self.to_string()
  
  def clone(self, mutations = None):
    return tuple_util.clone(self, mutations = mutations)

  def __eq__(self, other):
    if check.is_string(other):
      other = self.parse(other)
    return super().__eq__(other)

  @classmethod
  def _resolve_entities(clazz, url):
    # return deal with all entities
    return url.replace('&amp;', '&')
  
  @classmethod
  def parse(clazz, url):
    check.check_string(url)

    resolved_url = clazz._resolve_entities(url)
    pr = urllib_parse.urlparse(resolved_url)
    return clazz.__bases__[0].__new__(clazz, *pr)

  def to_parse_result(self):
    pr = urllib_parse.ParseResult(self.scheme, self.netloc, self.path,
                                  self.params, self.query, self.fragment)
    return pr
  
  @cached_property
  def query_attributes(self):
    return urllib_parse.parse_qs(self.query)

  def to_string(self):
    return urllib_parse.urlunparse(self.to_parse_result())

  def normalized(self):
    if self.path == '':
      normalized_path = '/'
    else:
      normalized_path = self.path
    quoted_path = urllib_parse.quote(normalized_path)
    return self.clone(mutations = { 'path': normalized_path })

  @cached_property
  def netloc_name(self):
    parts = self.netloc.split('.')
    if not parts:
      return None
    if parts[-1] in self._COMMON_SUFFIXES:
      parts.pop(-1)
    if parts[0] in self._COMMON_PREFIXES:
      parts.pop(0)
    if not parts:
      return None
    return parts[-1]

  def remove_query(self):
    r = self.clone(mutations = { 'query': '' })
    return self.clone(mutations = { 'query': '' })

  _COMMON_SUFFIXES = set([
    'au',
    'ca',
    'ch',
    'com',
    'de',
    'edu',
    'es',
    'fr',
    'gov',
    'it',
    'jp',
    'mil',
    'net',
    'nl',
    'no',
    'org',
    'ru',
    'se',
    'uk',
    'us',
  ])

  _COMMON_PREFIXES = set([
    'go',
    'my',
    'super',
    'the',
    'w3',
    'web',
    'www',
  ])
  
check.register_class(parsed_url, include_seq = False)
