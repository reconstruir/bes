#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from __future__ import division
from bes.compat import map
from bes.system import compat, execute
from bes.key_value import key_value_list
from collections import namedtuple

class file_mime(object):

  TEXT = 'text'

  BINARY_TYPES = [
    'application/x-sharedlib', # -pie vs -no-pie issue in gcc 7.3
    'application/octet-stream',
    'application/x-executable',
    'application/x-mach-binary', # This is new in macos sierra
  ]

  # FIXME: some illegal seuqences cause this to choke: /Users/ramiro/software/tmp/builds/flex-2.6.0_rev1_2016-02-07-05-14-52-769130/deps/installation/share/gettext/po/boldquot.sed 

  class _mime_type(namedtuple('_mime_type', 'mime_type, values')):

    def __new__(clazz, mime_type, values):
      return clazz.__bases__[0].__new__(clazz, mime_type, values)
  
    def __str__(self):
      return '%s; %s' % (self.mime_type, self.values.to_string())
  
  @classmethod
  def mime_type(clazz, filename):
    cmd = 'file --brief --mime %s' % (filename)
    rv = execute.execute(cmd, raise_error = False)
    if rv.exit_code != 0:
      return clazz._mime_type(None, None)
    text = rv.stdout.strip()
    mime_type, delimiter, values = text.partition(';')
    mime_type = mime_type.strip()
    values = key_value_list.parse(values, delimiter = '=')
    return clazz._mime_type(mime_type, values)
    
  @classmethod
  def is_text(clazz, filename):
    return clazz.mime_type_is_text(filename) or clazz.content_is_text(filename)

  @classmethod
  def mime_type_is_text(clazz, filename):
    return clazz.mime_type(filename).mime_type.startswith(clazz.TEXT)

  @classmethod
  def is_binary(clazz, filename):
    return clazz.mime_type(filename).mime_type in clazz.BINARY_TYPES

  # From http://stackoverflow.com/questions/1446549/how-to-identify-binary-and-text-files-using-python
  @classmethod
  def content_is_text(clazz, filename):
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
