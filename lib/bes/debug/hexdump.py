#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import binascii, codecs
from io import BytesIO
from collections import namedtuple

from bes.text.line_break import line_break

class hexdump(object):

  _item = namedtuple('_item', 'value, hexlified, printable')
  _word = namedtuple('_word', 'hexlified, asciified')

  @classmethod
  def stream(clazz,
             stream,
             wordsize = 4,
             columns = 8,
             delimiter = None,
             show_ascii = False,
             show_offset = False,
             line_delimiter = None):
    'hexdump a stream to a string.'

    if delimiter == None:
      delimiter = ' '
    
    if line_delimiter == None:
      line_delimiter = line_break.DEFAULT_LINE_BREAK_RAW
    
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
    return line_delimiter.join(lines)

  @classmethod
  def data(clazz,
           data,
           wordsize = 4,
           columns = 8,
           delimiter = None,
           show_ascii = False,
           show_offset = False,
           line_delimiter = None):
    'hexdump bytes to a string.'
    return clazz.stream(BytesIO(data),
                        wordsize = wordsize,
                        columns = columns,
                        delimiter = delimiter,
                        show_ascii = show_ascii,
                        show_offset = show_offset,
                        line_delimiter = line_delimiter)

  @classmethod
  def filename(clazz,
               filename,
               wordsize = 4,
               columns = 8,
               delimiter = None,
               show_ascii = False,
               show_offset = False,
               line_delimiter = None):
    'hexdump bytes to a string.'
    with open(filename, 'rb') as stream:
       return clazz.stream(stream,
                           wordsize = wordsize,
                           columns = columns,
                           delimiter = delimiter,
                           show_ascii = show_ascii,
                           show_offset = show_offset,
                           line_delimiter = line_delimiter)

  # http://stackoverflow.com/questions/312443/how-do-you-split-a-list-into-evenly-sized-chunks
  @classmethod
  def _chunks(clazz, l, n):
    'Yield successive n-sized chunks from l.'
    for i in range(0, len(l), n):
      yield l[i:i + n]

  @classmethod
  def _make_item(clazz, b):
    hexlified = binascii.hexlify(b).decode('utf-8')
    value = int(hexlified, 16)
    if value >= 33 and value <= 127:
      printable = chr(value)
    else:
      printable = '.'
    item = clazz._item(b, hexlified, printable)
    return item
