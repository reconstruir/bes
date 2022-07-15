#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from __future__ import division

from bes.compat.map import map
from bes.system.compat import compat

class text_detect(object):

  # https://stackoverflow.com/questions/898669/how-can-i-detect-if-a-file-is-binary-non-text-in-python
  _TEXT_CHARS = bytearray({7, 8, 9, 10, 12, 13, 27} | set(range(0x20, 0x100)) - {0x7f})
  @classmethod
  def file_is_text(clazz, filename):
    with open(filename, 'rb') as f:
      head = f.read(1024)
      return not bool(head.translate(None, clazz._TEXT_CHARS))
