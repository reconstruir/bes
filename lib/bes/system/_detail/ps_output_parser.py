#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

class ps_output_parser(object):
  'Class to parse the output of "ps aux" on unix'

  @classmethod
  def parse_ps_output_line(clazz, text, num_fields):
    'Parse one line of ps aux output.'
    parts = text.split()
    assert len(parts) >= num_fields

    cmd_field_index = num_fields - 1
    cmd_start = text.find(parts[cmd_field_index])
    assert cmd_start >= 0
    cmd = text[cmd_start:]
    parts = parts[0:cmd_field_index] + [ cmd ]
    return tuple(parts)
