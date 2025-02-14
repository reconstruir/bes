#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple

from ..common.tuple_util import tuple_util
from ..common.object_util import object_util
from ..common.string_util import string_util
from ..property.cached_property import cached_property
from ..system.check import check
from ..key_value.key_value_list import key_value_list
from ..key_value.key_value import key_value

from urllib import parse as urllib_parse
from urllib.parse import unquote as urllib_unquote

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

  @cached_property
  def query_dict(self):
    return urllib_parse.parse_qs(self.query)
  
  @cached_property
  def query_key_values(self):
    return key_value_list(urllib_parse.parse_qsl(self.query))
  
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
    if len(parts) == 2:
      return parts[0]
    return parts[-1]

  @cached_property
  def path_parts(self):
    return self.path.split('/')

  @cached_property
  def path_unquoted(self):
    return urllib_unquote(self.path)
  
  def remove_query(self):
    return self.clone(mutations = { 'query': '' })

  def remove_query_fields(self, callable_):
    check.check_callable(callable_)

    new_kvl = self.query_key_values
    new_kvl.remove_by_callable(callable_)
    query = new_kvl.to_string(delimiter = '=', value_delimiter = '&')
    return self.clone(mutations = { 'query': query })

  def keep_query_fields(self, callable_):
    check.check_callable(callable_)

    new_kvl = self.query_key_values
    new_kvl.keep_by_callable(callable_)
    query = new_kvl.to_string(delimiter = '=', value_delimiter = '&')
    return self.clone(mutations = { 'query': query })
  
  _COMMON_SUFFIXES = set([
    'ai',
    'au',
    'ca',
    'ch',
    'club',
    'com',
    'de',
    'edu',
    'es',
    'fr',
    'gov',
    'io',
    'it',
    'jp',
    'me',
    'mil',
    'net',
    'nl',
    'no',
    'org',
    'porn',
    'ru',
    'se',
    'tv',
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

  @cached_property
  def without_address(self):
    'Return the url without scheme or netloc'
    path = string_util.remove_head(self.path, '/')
    return parsed_url('', '', path, self.params, self.query, self.fragment)

  @cached_property
  def base_url(self):
    'Return just the base url without path or anything else'
    return parsed_url(self.scheme, self.netloc, '', '', '', '')

  def replace_base_url(self, url):
    check.check_string(url)

    purl = self.parse(url)
    return self.clone(mutations = {
      'scheme': purl.scheme,
      'netloc': purl.netloc,
    })

  def replace_path(self, new_path):
    check.check_string(new_path)

    self_ends_in_slash = self.path_parts[-1] == ''
    new_path_ends_in_slash = new_path.endswith('/')
    if self_ends_in_slash and not new_path_ends_in_slash:
      new_path = new_path + '/'
    if not self_ends_in_slash and new_path_ends_in_slash:
      new_path = string_util.remove_tail(new_path, '/')
    return self.clone(mutations = {
      'path': new_path,
    })
  
check.register_class(parsed_url, include_seq = False)
