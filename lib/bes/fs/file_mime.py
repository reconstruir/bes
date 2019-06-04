#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from __future__ import division
import re
from collections import namedtuple
from bes.compat.map import map
from bes.system.compat import compat
from bes.system.execute import execute
from bes.key_value.key_value_list import key_value_list
from bes.text.text_line_parser import text_line_parser
from bes.common.algorithm import algorithm

class file_mime(object):

  TEXT = 'text'

  BINARY_TYPES = [
    'application/x-sharedlib', # -pie vs -no-pie issue in gcc 7.3
    'application/octet-stream',
    'application/x-executable',
    'application/x-pie-executable',
    'application/x-mach-binary', # This is new in macos sierra
  ]

  # FIXME: some illegal seuqences cause this to choke: /Users/ramiro/software/tmp/builds/flex-2.6.0_rev1_2016-02-07-05-14-52-769130/deps/installation/share/gettext/po/boldquot.sed 

  class _mime_type_and_charset(namedtuple('_mime_type_and_charset', 'mime_type, charset')):

    def __new__(clazz, mime_type, charset):
      return clazz.__bases__[0].__new__(clazz, mime_type, charset)
  
    def __str__(self):
      return '%s; charset=%s' % (self.mime_type, self.charset)

    def __hash__(self):
      return hash(str(self))
    
  @classmethod
  def mime_type(clazz, filename):
    cmd = 'file --brief --mime %s' % (filename)
    rv = execute.execute(cmd, raise_error = False)
    if rv.exit_code != 0:
      return clazz._mime_type_and_charset(None, None)
    text = rv.stdout.strip()
    return clazz._parse_file_output(text)
    
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

  @classmethod
  def _parse_file_output(clazz, text):
    'Parse the output of file --brief --mime {filename}'
    lines = text_line_parser.parse_lines(text, strip_text = True, remove_empties = True)
    if len(lines) == 1:
      return clazz._parse_non_fat_file_output_line(lines[0])
    entries = [ clazz._parse_fat_file_output_line(line) for line in lines ]
    entries = [ entry for entry in entries if entry ]
    entries = algorithm.unique(entries)
    if len(entries) == 1:
      return entries[0]
    return entries

  @classmethod
  def _parse_non_fat_file_output_line(clazz, line):
    'Parse one line of output from file --brief --mime {filename} for non fat failes'
    parts = line.split(';')
    parts = [ part.strip() for part in parts if part.strip() ]
    mime_type = None
    values = key_value_list()
    if len(parts) > 0:
      mime_type = parts.pop(0).strip()
    for part in parts:
      values.extend(key_value_list.parse(part, delimiter = '='))
    values.remove_dups()
    kv = values.find_by_key('charset')
    charset = kv.value if kv else None
    return clazz._mime_type_and_charset(mime_type, charset)

  @classmethod
  def _parse_fat_file_output_line(clazz, line):
    'Parse one line of output from file --brief --mime {filename} for fat files'
    r = re.findall('^.*\s\(for\sarchitecture\s(.+)\)\:\s+(.*)$', line)
    if len(r) == 1:
      arch, text = r[0]
      return clazz._parse_non_fat_file_output_line(text)
    assert len(r) == 0
    return None
