#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.system.log import log
from bes.common.size import size

class text_canvas(object):
  'text_canvas'

  ORIENTATION_VERTICAL = 'vertical'
  ORIENTATION_HORIZONTAL = 'horizontal'

  def __init__(self, width, height):
    'Create an ascii art canvas with the given dimensions.'
    log.add_logging(self, 'canvas')
    #Log.set_tag_level('canvas', log.DEBUG)
    self.width = width
    self.height = height
    self._matrix = [ ' ' ] * (width * height)

  def __str__(self):
    'Return the matrix as a string.'
    lines = self.lines()
    return '\n'.join(lines)

  def lines(self):
    'Return the text as a list of lines.'
    lines = [ self._matrix[i : i + self.width] for i in range(0, len(self._matrix), self.width) ]
    assert len(lines) == self.height
    return [ ''.join(line) for line in lines ]

  def contains_point(self, x, y):
    'Return True if the given point is contained in the canvas.'
    return x < self.width and y < self.height

  def draw_char(self, x, y, c):
    'Draw one character at x,y.'

    if x < 0 or x >= self.width:
      return
    if y < 0 or y >= self.height:
      return
    pos = y * self.width + x

    self._matrix[pos] = c

  def draw_text(self, x, y, text, orientation = ORIENTATION_HORIZONTAL):
    'Draw text at the given coordinates.'

    self.log_d('draw_text(%s, %s, "%s", %s)' % (x, y, text, orientation))

    if orientation == self.ORIENTATION_HORIZONTAL:
      truncted_text = text[0 : self.width - x]
      for c in truncted_text:
        self.draw_char(x, y, c)
        x += 1
    elif orientation == self.ORIENTATION_VERTICAL:
      truncted_text = text[0 : self.height - y]
      for c in truncted_text:
        self.draw_char(x, y, c)
        y += 1

  def draw_text_lines(self, x, y, lines):
    'Draw text lines horizontally at the given coordinates.'
    self.log_d('draw_text_lines(%s, %s, "%s")' % (x, y, lines))
    for line in lines:
      self.draw_text(x, y, line)
      y += 1
