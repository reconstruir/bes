#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

class btl_debug(object):

  _debug_char_map = {
    '\n': '[NL]',
    '\r': '[CR]',
    '\t': '[TAB]',
    ' ': '[SP]',
    '\0': '[EOS]',
  }
  
  @classmethod
  def make_debug_str(clazz, s):
    if s == None:
      return None
    result = []
    for c in s:
      result.append(clazz._debug_char_map.get(c, c))
    return ''.join(result)
  
