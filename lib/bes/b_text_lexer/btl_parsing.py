#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from ..system.check import check

from .btl_error import btl_error

class btl_parsing(object):
  
  @classmethod
  def parse_key_value(clazz, n, source, delimiter = ':'):
    check.check_node(n)
    check.check_string(source)
    check.check_string(delimiter)

    key, delim, value = n.data.text.partition(delimiter)
    if delim != delimiter:
      raise btl_error(f'Invalid key value "{n.data.text}" at {source}:{n.data.line_number}')
    return key.strip(), value.strip()
