#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple
from collections import OrderedDict

from bes.common.node import node as node

from ..system.check import check
from ..version.semantic_version import semantic_version

from .btl_error import btl_error

class btl_desc_header(namedtuple('btl_desc_header', 'name, description, version, start_state, end_state')):
  
  def __new__(clazz, name, description, version, start_state, end_state):
    check.check_string(name)
    check.check_string(description)
    version = check.check_semantic_version(version)
    check.check_string(start_state)
    check.check_string(end_state)
    return clazz.__bases__[0].__new__(clazz, name, description, version, start_state, end_state)

  @classmethod
  def parse_node(clazz, n, source = '<unknown>'):
    check.check_node(n)

    d = OrderedDict([
      ( 'name', None ),
      ( 'description', None ),
      ( 'version', None ),
      ( 'start_state', None ),
      ( 'end_state', None ),
    ])
    for child in n.children:
      key, value = clazz._parse_kv(child, source)
      if key not in d:
        raise btl_error(f'Invalid header key "{key}" at {source}:{child.data.line_number}')
      d[key] = value
    for key, value in d.items():
      if value == None:
        raise btl_error(f'Missing key "{key}" at {source}:{n.data.line_number}')
    return btl_desc_header(*[ item[1] for item in d.items() ])

  @classmethod
  def _parse_kv(clazz, n, source):
    key, delim, value = n.data.text.partition(':')

    if delim != ':':
      raise btl_error(f'Invalid key value "{n.data.text}" at {source}:{n.data.line_number}')
    return key.strip(), value.strip()
    
check.register_class(btl_desc_header)
