#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from .process_lister_base import process_lister_base

from bes.system.execute import execute
from bes.text.text_line_parser import text_line_parser
from bes.system.process_info import process_info

from .ps_output_parser import ps_output_parser

class process_lister_macos(process_lister_base):

  @classmethod
  #@abstractmethod
  def list_processes(clazz):
    'List all processes.'
    rv = execute.execute('ps aux')
    lines = text_line_parser.parse_lines(rv.stdout, strip_comments = False, strip_text = True, remove_empties = True)
    result = []
    for i, line in enumerate(lines):
      if i == 0:
        continue
      parts = ps_output_parser.parse_ps_output_line(line, 11)
      user = parts[0]
      pid = parts[1]
      cpu = parts[2]
      mem = parts[3]
      vsz = parts[4]
      rss = parts[5]
      tty = parts[6]
      if tty.startswith('?'):
        tty = None
      else:
        tty = '/dev/tty' + tty
      command = parts[-1]
      other = {
        'vsz': vsz,
        'rss': rss,
        'tty': tty,
      }
      info = process_info(user, pid, cpu, mem, command, other)
      result.append(info)
    return result
  
