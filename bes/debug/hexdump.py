#!/usr/bin/env python
#-*- coding:utf-8 -*-

import binascii
from cStringIO import StringIO
from collections import namedtuple

class hexdump(object):

  _item = namedtuple('_item', 'value,hexlified,printable')
  _word = namedtuple('_word', 'hexlified,asciified')

  @classmethod
  def stream(clazz, stream, wordsize = 4, columns = 8, delimiter = ' ', show_ascii = False, show_offset = False):
    'hexdump a stream to a string.'

    items = [ clazz._make_item(b) for b in iter(lambda: stream.read(1), b'') ]
    words = []
    for chunk in clazz._chunks(items, wordsize):
      word = ''.join([ item.hexlified for item in chunk ])
      ascii_word = ''.join([ item.printable for item in chunk ])
      words.append(clazz._word(word, ascii_word))
    lines = []
    hex_part_width = None
    offset = 0
    for chunk in clazz._chunks(words, columns):
      parts = []
      offset_part = hex(offset)[2:].rjust(4, '0') + '|'
      if show_offset:
        parts.append(offset_part)
      hex_part = delimiter.join([ item.hexlified for item in chunk ])
      if hex_part_width is None:
        hex_part_width = len(hex_part)
      hex_part = hex_part.ljust(hex_part_width, ' ')        
      parts.append(hex_part)
      if show_ascii:
        ascii_part = ''.join([ item.asciified for item in chunk ])
        ascii_box = '|%s|' % (ascii_part)
        parts.append(ascii_box)
      line = ' '.join(parts)
      lines.append(line)
      offset += columns
    return '\n'.join(lines)

  @classmethod
  def bytes(clazz, data, wordsize = 4, columns = 8, delimiter = ' ', show_ascii = False, show_offset = False):
    'hexdump bytes to a string.'
    return clazz.stream(StringIO(data),
                        wordsize = wordsize,
                        columns = columns,
                        delimiter = delimiter,
                        show_ascii = show_ascii,
                        show_offset = show_offset)

  @classmethod
  def file(clazz, filename, wordsize = 4, columns = 8, delimiter = ' ', show_ascii = False, show_offset = False):
    'hexdump bytes to a string.'
    with open(filename, 'r') as stream:
       return clazz.stream(stream,
                           wordsize = wordsize,
                           columns = columns,
                           delimiter = delimiter,
                           show_ascii = show_ascii,
                           show_offset = show_offset)

  # http://stackoverflow.com/questions/312443/how-do-you-split-a-list-into-evenly-sized-chunks
  @classmethod
  def _chunks(clazz, l, n):
    'Yield successive n-sized chunks from l.'
    for i in range(0, len(l), n):
      yield l[i:i + n]

  @classmethod
  def _make_item(clazz, b):
    hexlified = binascii.hexlify(b)
    value = int(hexlified, 16)
    if value >= 33 and value <= 127:
      printable = hexlified.decode('hex')
    else:
      printable = '.'
    return clazz._item(b, hexlified, printable)
