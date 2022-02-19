#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.system.check import check
from bes.compat.StringIO import StringIO

class text_insert(object):
  'Class to deal with text insert'

  @classmethod
  def insert(clazz, text, position, insert_text):
    'Insert insert_text into text at position.'
    check.check_string(text)
    check.check_int(position)
    check.check_string(insert_text)

    buf = StringIO()
    left = text[0:position]
    right = text[position:]
    buf.write(left)
    buf.write(insert_text)
    buf.write(right)
    return buf.getvalue()
