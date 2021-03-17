#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple
import re

class handle_output_parser(object):
  'Class to parse the output of handle.exe on windows'

  _SECTION_DELIMITER = '------------------------------------------------------------------------------'
  @classmethod
  def parse_handle_output(clazz, text):
    'Parse handle output.'

    result = []
    if not clazz._SECTION_DELIMITER in text:
      lines = [ line for line in text.splitlines() if line ]
      items = clazz._parse_items(lines)
      section = clazz._section(None, items)
      result.append(section)
    else:
      result = []
      section_texts = [ t.strip() for t in text.split(clazz._SECTION_DELIMITER) if t.strip() ]
      for next_section_text in section_texts:
        section = clazz._parse_section(next_section_text)
        result.append(section)
    return result

  _header = namedtuple('_header', 'image_name, pid, username')
  _HEADER_PATTERN = re.compile(r'^\s*(.*)\s+pid:\s+([0-9]+)\s+(.+)\s*$')
  @classmethod
  def _parse_header(clazz, text):
    'Parse handle output.'

    f = clazz._HEADER_PATTERN.findall(text)
    if not f:
      return None
    if len(f) != 1:
      return None
    if len(f[0]) != 3:
      return None
    image_name, pid, username = f[0]
    pid = int(pid)
    if '<unable to open process>' in username:
      username = None
    return clazz._header(image_name, pid, username)

  _item = namedtuple('_item', 'handle_id, handle_type, target')
  _section = namedtuple('_section', 'header, items')
  @classmethod
  def _parse_section(clazz, text):
    'Parse handle output.'

    lines = [ line for line in text.splitlines() if line ]
    if not lines:
      return None
    header = clazz._parse_header(lines.pop(0))
    if not header:
      return None
    items = clazz._parse_items(lines)
    return clazz._section(header, items)

  _item = namedtuple('_item', 'handle_id, handle_type, target')
  @classmethod
  def _parse_items(clazz, lines):
    'Parse lines of items.'
    items = []
    for line in lines:
      parts = [ part for part in re.split(r'\s+', line) if part ]
      assert len(parts) == 3
      handle_id = clazz._parse_handle_id(parts.pop(0))
      handle_type = parts.pop(0)
      handle_target = parts.pop(0)
      item = clazz._item(handle_id, handle_type, handle_target)
      items.append(item)
    return items
  
  @classmethod
  def _parse_handle_id(clazz, s):
    return int(s.replace(':', ''), 16)
  
