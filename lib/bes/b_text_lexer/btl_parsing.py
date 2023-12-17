#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from ..system.check import check

from .btl_error import btl_error

class btl_parsing(object):
  
  @classmethod
  def parse_key_value(clazz, n, source, result_class = None, delimiter = ':'):
    check.check_node(n)
    check.check_string(source)
    check.check_string(delimiter)
    check.check_class(result_class, allow_none = True)

    key, delim, value = n.data.text.partition(delimiter)
    key = key.strip()
    value = value.strip()
    if delimiter == ' ':
      value = value or None
    else:
      #print(f'key={key} delim={delim} value={value}')
      if delim != delimiter:
        raise btl_error(f'Invalid key value "{n.data.text}" at {source}:{n.data.line_number}')
    
    if result_class:
      return result_class(key, value)
    return key, value
