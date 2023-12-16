#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from ..system.check import check

from .btl_error import btl_error

class btl_parsing(object):
  
  @classmethod
  def parse_key_value(clazz, n, source):
    check.check_node(n)
    check.check_string(source)

    key, delim, value = n.data.text.partition(':')
    if delim != ':':
      raise btl_error(f'Invalid key value "{n.data.text}" at {source}:{n.data.line_number}')
    return key.strip(), value.strip()
