#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path
import re
from bes.compat.map import map
from bes.system.execute import execute
from bes.key_value.key_value_list import key_value_list
from bes.text.text_line_parser import text_line_parser
from bes.common.algorithm import algorithm

class file_mime_type_unix_file_exe(object):
  'Detect mime types using the file utility on unix.'
    
  @classmethod
  def mime_type(clazz, filename):
    cmd = 'file --brief --mime %s' % (filename)
    if not path.isfile(filename):
      raise IOError('file not found: "{}"'.format(filename))
    rv = execute.execute(cmd, raise_error = False)
    if rv.exit_code != 0:
      return ( None, None )
    text = rv.stdout.strip()
    return clazz._parse_file_output(text)

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
    return ( mime_type, charset )

  @classmethod
  def _parse_fat_file_output_line(clazz, line):
    'Parse one line of output from file --brief --mime {filename} for fat files'
    r = re.findall(r'^.*\s\(for\sarchitecture\s(.+)\)\:\s+(.*)$', line)
    if len(r) == 1:
      arch, text = r[0]
      return clazz._parse_non_fat_file_output_line(text)
    assert len(r) == 0
    return None
