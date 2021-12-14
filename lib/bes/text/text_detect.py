#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from __future__ import division

from bes.compat.map import map
from bes.system.compat import compat

class text_detect(object):

  @classmethod
  def file_is_text(clazz, filename):
    if compat.IS_PYTHON2:
      return clazz._file_is_text_py2(filename)
    else:
      return clazz._file_is_text_py3(filename)

  # From https://stackoverflow.com/questions/898669/how-can-i-detect-if-a-file-is-binary-non-text-in-python
  @classmethod
  def _file_is_text_py3(clazz, filename):
    try:
      with open(filename, "r") as f:
        for l in f:
          pass
      return True
    except UnicodeDecodeError as ex:
      return False

  @classmethod
  def _file_is_text_py2(clazz, filename):
    with open(filename, 'rb') as fin:
      s = fin.read(512)
      text_characters = ''.join(list(map(chr, range(32, 127))) + list('\n\r\t\b'))
      if compat.IS_PYTHON2:
        import string
        _null_trans = string.maketrans('', '')
      else:
        _null_trans = bytes.maketrans(b'', b'')
        
      if not s:
        # Empty files are considered text
        return True
      if b'\0' in s:
        # Files with null bytes are likely binary
        return False
      # Get the non-text characters (maps a character to itself then
      # use the 'remove' option to get rid of the text characters.)
      t = s.translate(_null_trans, text_characters)
      # If more than 30% non-text characters, then
      # this is considered a binary file
      if float(len(t))/float(len(s)) > 0.30:
        return False
      return True  
