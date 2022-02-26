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

  def __str__(self):
    return self.to_string()
  
  def __repr__(self):
    return self.to_string()
  
  def clone(self, mutations = None):
    return tuple_util.clone(self, mutations = mutations)

  @classmethod
  def parse(clazz, s):
    check.check_string(s)

    pr = urllib_parse.urlparse(s)
    return clazz.__bases__[0].__new__(clazz, *pr)

  @cached_property
  def to_parse_result(self):
    return urllib_parse.ParseResult(self.scheme, self.netloc, self.path,
                                    self.params, self.query, self.fragment)
  
  @cached_property
  def query_attributes(self):
    return urllib_parse.parse_qs(self.query)

  @cached_property
  def to_string(self):
    return urllib_parse.urlunparse(self.to_parse_result())

  def normalized(self):
    if self.path == '':
      normalized_path = '/'
    else:
      normalized_path = self.path
    quoted_path = urllib_parse.quote(normalized_path)
    return self.clone(mutations = { 'path': normalized_path })
  
check.register_class(parsed_url, include_seq = False)
