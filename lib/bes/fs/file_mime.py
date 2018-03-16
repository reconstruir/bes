#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from __future__ import division
from bes.compat import map
from bes.system import compat, execute

class file_mime(object):

  TEXT = 'text'

  BINARY_TYPES = [
    'application/octet-stream; charset=binary',
    'application/x-executable; charset=binary',
    'application/x-mach-binary; charset=binary', # This is new in macos sierra
  ]

  # FIXME: some illegal seuqences cause this to choke: /Users/ramiro/software/tmp/builds/flex-2.6.0_rev1_2016-02-07-05-14-52-769130/deps/installation/share/gettext/po/boldquot.sed 

  @classmethod
  def mime_type(clazz, filename):
    cmd = 'file --brief --mime %s' % (filename)
    rv = execute.execute(cmd, raise_error = False)
    if rv.exit_code != 0:
      return ''
    return rv.stdout.strip()

  @classmethod
  def is_text(clazz, filename):
    return clazz.mime_type_is_text(filename) or clazz.content_is_text(filename)

  @classmethod
  def mime_type_is_text(clazz, filename):
    return clazz.mime_type(filename).startswith(clazz.TEXT)

  @classmethod
  def is_binary(clazz, filename):
    return clazz.mime_type(filename) in clazz.BINARY_TYPES

  # From http://stackoverflow.com/questions/1446549/how-to-identify-binary-and-text-files-using-python
  @classmethod
  def content_is_text(clazz, filename):
    print('content_is_text(%s)' % (filename))
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
