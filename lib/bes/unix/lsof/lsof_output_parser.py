#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import OrderedDict
from collections import namedtuple
import re

from bes.system.system_command import system_command

class lsof_output_parser(object):
  'Class to parse the output of "lsof" on unix'

  @classmethod
  def parse_lsof_output(clazz, text):
    'Parse one line of ps aux output.'
    lines = system_command.split_lines(text)
    header = clazz._parse_header(lines.pop(0))
    items = []
    for line in lines:
      item = clazz._parse_one_line(line, header['NAME'])
      if item:
        items.append(item)
    return items

  _item = namedtuple('_item', 'command, pid, user, fd, fd_type, name')
  @classmethod
  def _parse_one_line(clazz, line, name_index):
    'Parse one item.'
    name = line[name_index:] or None
    parts = system_command.split_by_white_space(line)
    if len(parts) < 5:
      raise ValueError('Invalid line: "{}"'.format(line))
    command = parts.pop(0)
    pid = int(parts.pop(0))
    user = parts.pop(0)
    fd = parts.pop(0)
    fd_type = parts.pop(0)
    return clazz._item(command, pid, user, fd, fd_type, name)

  @classmethod
  def _parse_header(clazz, line):
    'Parse lsof header.'
    parts = system_command.split_by_white_space(line)
    result = OrderedDict()
    for part in parts:
      result[part] = line.find(part)
    return result
