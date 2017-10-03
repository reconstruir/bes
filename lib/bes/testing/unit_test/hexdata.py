#!/usr/bin/env python
#-*- coding:utf-8 -*-

import codecs
from bes.compat import StringIO
from io import BytesIO

class hexdata(object):

  @classmethod
  def bytes_to_string(clazz, b):
    s = codecs.encode(b, 'hex').decode('ascii')
    assert (len(s) % 2) == 0
    buf = StringIO()
    for i in range(0, len(s), 2):
      if i != 0:
        buf.write(' ')
      buf.write(s[i])
      buf.write(s[i + 1])
    return buf.getvalue()

  @classmethod
  def string_to_bytes(clazz, s):
    buf = StringIO()
    for c in s:
      if not c.isspace():
        buf.write(c)
    return codecs.decode(buf.getvalue(), 'hex')
  
