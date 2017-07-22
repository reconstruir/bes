#!/usr/bin/env python
#-*- coding:utf-8 -*-

from collections import namedtuple
import re
from bes.common import string_util

class iwlist_line(object):
  'A single line of iwlist output.'

  def __init__(self, line_number, text):
    self.line_number = line_number
    self.original_text = text
    self.indent = self.__count_indent(text)
    self.text = text[self.indent:]

  def __str__(self):
    return '%3d:%2d:%s' % (self.line_number, self.indent, self.original_text)
    
  def __repr__(self):
    return '%3d:%2d:%s' % (self.line_number, self.indent, self.original_text)

  def __count_indent(self, s):
    indent = 0
    for c in s:
      if c in [ ' ' ]:
        indent += 1
      else:
        return indent
    return 0
    
class iwlist_scan_parser(object):
  'Parse the output of iwlist scan.'

  def __init__(self, text):
    self._text = text
    
  def parse(self):
    'Return a dictionary representation of the iwlist scan output.'
    lines = [ iwlist_line(line_number + 1, s) for line_number, s in enumerate(self._text.split('\n')) ]
    lines = [ line for line in lines if not line.text.isspace() and line.text ]

    if not lines:
      return []
    result = []
    indent = lines[0].indent
    while lines:
      line = lines.pop(0)
      if line.indent == indent:
        radio_lines = [ line ] + self.__pop_lines_with_greater_indent(lines, line.indent)
        result.append(self.__parse_radio(radio_lines))
    return result

  def __parse_radio(self, radio_lines):
    radio_name_line = radio_lines.pop(0)
    cell_lines = self.__pop_lines_with_greater_indent(radio_lines, radio_name_line.indent)
    assert len(radio_lines) == 0
    result = self.__parse_radio_name(radio_name_line)
    if result['scan_status'] != 'scan_completed':
      return result
    cells = []
    while cell_lines:
      cell_address_line = cell_lines.pop(0)
      one_cell_lines = [ cell_address_line ] + self.__pop_lines_with_greater_indent(cell_lines, cell_address_line.indent)
      cell = self.__parse_cell(one_cell_lines)
      cells.append(cell)
    result['cells'] = cells
    return result
        
  def __parse_cell(self, cell_lines):
    cell_address_line = cell_lines.pop(0)
    assert cell_address_line.text.startswith('Cell')
    result = self.__parse_cell_address(cell_address_line)
    cell_attribute_lines = self.__pop_lines_with_greater_indent(cell_lines, cell_address_line.indent)
    result.update(self.__parse_cell_attributes(cell_attribute_lines))
    assert len(cell_lines) == 0
    return result
      
  def __parse_cell_attributes(self, lines):
    result = {}
    while lines:
      line = lines.pop(0)
      extra_lines = self.__pop_lines_with_greater_indent(lines, line.indent)
      cell_attribute_dict = self.__parse_cell_attribute(line, extra_lines)
      self.__update_result(result, cell_attribute_dict)
    return result
      
  def __parse_cell_attribute(self, line, extra_lines):
    text = line.text
    if text.startswith('Channel'):
      return self.__parse_simple_key_value('Channel', 'channel', text)
    elif text.startswith('Frequency'):
      return self.__parse_frequency(text)
    elif text.startswith('Quality'):
      return self.__parse_quality(text)
    elif text.startswith('Encryption key'):
      return self.__parse_simple_key_value('Encryption key', 'encryption_key', text)
    elif text.startswith('ESSID'):
      return self.__parse_simple_key_value('ESSID', 'essid', text)
    elif text.startswith('Mode'):
      return self.__parse_simple_key_value('Mode', 'mode', text)
    elif text.startswith('Bit Rates'):
      return self.__parse_bit_rates(line, extra_lines)
    elif text.startswith('Extra'):
      return self.__parse_extra(text)
    elif text.startswith('IE'):
      return self.__parse_ie(line, extra_lines)
    else:
      raise RuntimeError('Unexpected value: %s' % (text))
    
  def __parse_bit_rates(self, line, extra_lines):
    bitrates = []
    lines = [ line ] + extra_lines
    for line in lines:
      text = line.text.replace('Bit Rates:', '')
      more_bitrates = [ bitrate.strip() for bitrate in text.split(';') ]
      bitrates.extend(more_bitrates)
    return {
      'bitrates': bitrates,
    }

  def __parse_ie(self, line, extra_lines):
    ie = {}
    _ , key = self.__partition_and_strip(line.text, ':')
    if key.startswith('Unknown'):
      return {}
    value = {}
    for extra_line in extra_lines:
      value.update(self.__parse_list(extra_line.text))
    return {
      'ie': [ ( key, value ) ],
    }

  def __parse_radio_name(self, line):
    assert isinstance(line, iwlist_line)
    parts = line.text.strip().partition(' ')
    radio = parts[0]
    status_blurb = parts[2].strip()
    if status_blurb.startswith('No scan results'):
      scan_status = 'no_scan_results'
    elif status_blurb.startswith('Scan completed'):
      scan_status = 'scan_completed'
    else:
      raise RuntimeError('%d: Unexpected scan status: %s' % (line.line_number, status_blurb))
    return {
      'radio': radio,
      'scan_status': scan_status,
    }

  def __parse_cell_address(self, line):
    groups = re.search('\s*(Cell\s*.*)\s*-\s*Address:\s*(.*)\s*', line.text).groups()
    assert len(groups) == 2
    return {
      'name': groups[0].strip(),
      'address': groups[1].strip().lower(),
    }
    
  def __update_result(self, result, new_data):
    for key, new_value in new_data.items():
      if result.has_key(key):
        old_value = result[key]
        assert type(old_value) == list
        assert type(new_value) == list
        new_value = old_value + new_value
      result[key] = new_value
        
  def __parse_frequency(self, s):
    groups = re.search('Frequency:(.*)\(Channel\s*.*\)\s*', s).groups()
    assert len(groups) == 1
    return {
      'frequency': groups[0].strip(),
    }

  def __parse_quality(self, s):
    groups = re.search('Quality=(.*)\s*Signal level=(.*)\s*', s).groups()
    assert len(groups) == 2
    return {
      'quality': groups[0].strip(),
      'signal_level': groups[1].strip(),
    }

  def __parse_extra(self, s):
    extra_data = s.replace('Extra:', '').strip()
    if extra_data.startswith('tsf'):
      return self.__partition_and_strip_as_dict(extra_data, '=')
    elif extra_data.startswith('Last beacon'):
      return self.__partition_and_strip_as_dict(extra_data, ':')
    else:
      raise RuntimeError('Unknown extra data: %s' % (extra_data))

  def __partition_and_strip(self, s, delimiter):
    parts = s.partition(delimiter)
    return ( parts[0].strip(), parts[2].strip() )

  def __partition_and_strip_as_dict(self, s, delimiter):
      key, value = self.__partition_and_strip(s, delimiter)
      return { key: value }

  def __parse_simple_key_value(self, marker, key, s):
    pattern = r'%s\s*:\s*(.*)\s*' % (marker)
    groups = re.search(pattern, s).groups()
    assert len(groups) == 1
    return {
      key: string_util.unquote(groups[0].strip()),
    }

  @classmethod
  def __parse_list(clazz, s):
    'Parse a list in the form: "this is the key" (N) : value1 value2 ... valueN'
    pattern = '(.*)\((.*)\).*'
    parts = s.partition(':')
    if parts[1] != ':':
      raise RuntimeError('Not a valid partition delimiter: %s' % (s))
    find = re.findall(pattern, parts[0])
    explicit_length = False
    if len(find) == 1 and len(find[0]) == 2:
      explicit_length = True
      key = find[0][0].strip()
      expected_length = int(find[0][1].strip())
    else:
      key = parts[0].strip()
      expected_length = 1
    values = [ s.strip() for s in string_util.split_by_white_space(parts[2]) ]
    if len(values) != expected_length:
      raise RuntimeError('Expected %d values and got %d instead: %s' % (expected_length, len(values)))
    if not explicit_length:
      values = values[0]
    return { key: values }
    
  def __pop_lines_with_greater_indent(self, lines, indent):
    result = []
    while lines and lines[0].indent > indent:
      result.append(lines.pop(0))
    return result
