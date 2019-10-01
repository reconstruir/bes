#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import unittest
from bes.common.size import size
from bes.text.text_canvas import text_canvas

class test_text_canvas(unittest.TestCase):

  @classmethod
  def decorate_text(clazz, text):
    'Decorate text with line numbers for easier debugging.'

    vbar = ' '
    hbar = ' '
    new_line = '#'

    lines = [ '%s%s' % (line, new_line) for line in text.split('\n') ]
    vaxis_width = len(str(len(lines)))
    max_line_length = max([ len(line) for line in lines ])
    left_justified_indeces = [ str(i).ljust(vaxis_width) for i in range(0, len(lines)) ]
    right_justified_indeces = [ str(i).rjust(vaxis_width) for i in range(0, len(lines)) ]
    justified_lines = [ line.ljust(max_line_length) for line in lines ]

    lines_with_vaxis = [ '%s%s%s%s%s' % (left_index, vbar, line, vbar, right_index) for (left_index, line, right_index) in zip(right_justified_indeces, justified_lines, left_justified_indeces) ]
    haxis_digits = ''.join([ str(i % 10) for i in range(0, max_line_length) ])
    haxis = '%s %s' % (''.rjust(vaxis_width), haxis_digits)
    haxis_separator = '%s%s' % (''.rjust(vaxis_width), hbar * (len(haxis_digits) + 2))

    decorated_lines = [
      haxis,
      haxis_separator,
    ] + lines_with_vaxis + [
      haxis_separator,
      haxis,
    ]

    return '\n'.join(decorated_lines)
#    text_with_vaxis = '\n'.join(lines_with_vaxis)
#    return '\n%s\n%s' % (haxis, text_with_vaxis)

  def __parse_art(self, art):

    '''
    ++
    ++
    '''

    '''
    +--+
    |  |
    +--+
    '''
      
    STATE_BEGIN = 'begin'
    STATE_BOTTOM = 'bottom'
    STATE_END = 'end'
    STATE_EXPECTING_LINE = 'expecting_line'
    STATE_LINE = 'line'
    STATE_TOP = 'top'

    CORNER = '+'
    HBAR = '-'
    VBAR = '|'

    class State(object):
      def __init__(self, text):
        self._text = text
        self._state = STATE_BEGIN
        self._index = 0
        self._top_width = None
        self._bottom_width = None
        self._lines = []
        self._line = None
        self._x = 0
        self._y = 0

      def __save_line(self):
        'Save the current line if not None'
        if self._line != None:
          self._lines.append(self._line)
        self._line = None

      def __add_to_line(self, c):
        'Add char c to line.'
        assert self._line is not None
        self._line.append(c)

      def __unexpected_char(self, c):
        'Raise a useful exception when an unexpected char is encountered by the state machine.'
        text = test_text_canvas.decorate_text(self._text)
        line_number = len(self._lines or []) + 1
        raise RuntimeError('Unexpected input "%s" at (%s, %s) in state %s: \n%s\n' % (self.__escape_char(c),
                                                                                      self._x,
                                                                                      self._y,
                                                                                      self._state,
                                                                                      text))
      _ESCAPED_CHARS = {
        '\n': '\\n',
        '\t': '\\t',
        '\r': '\\r',
      }
      @classmethod
      def __escape_char(clazz, c):
        'Escape a char so it can be displayed in error messages.'
        return clazz._ESCAPED_CHARS.get(c, c)

      def lines(self):
        'Return lines as a list of strings.'
        return [ ''.join(line) for line in self._lines ]

      def string(self, delimiter = '\n'):
        'Return lines as a string joined with newlines.'
        return delimiter.join(self.lines())

      def width(self):
        return self._top_width

      def height(self):
        return len(self._lines)

      def size(self):
        return size(self.width(), self.height())

#      +--+
#      |fo|
#      +--+

#      +-+
#      |o|
#      +-+

#      ++
#      ++

#      ++
#      ||
#      ++

#      +-+
#      +-+

      def _handle_char(self, c):
        if self._state == STATE_BEGIN:
          if c.isspace():
            pass
          elif c == CORNER:
            self._state = STATE_TOP
            self._top_width = 0
          else:
            self.__unexpected_char(c)
        elif self._state == STATE_TOP:
          if c == HBAR:
            self._top_width += 1
          elif c == CORNER:
            self._state = STATE_EXPECTING_LINE
          else:
            self.__unexpected_char(c)
        elif self._state == STATE_EXPECTING_LINE:
          if c.isspace():
            pass
          elif c == VBAR:
            self._line = []
            self._state = STATE_LINE
          elif c == CORNER:
            self.__save_line()
            self._bottom_width = 0
            self._state = STATE_BOTTOM
          else:
            self.__unexpected_char(c)
        elif self._state == STATE_LINE:
          if c == VBAR:
            self.__save_line()
            self._state = STATE_EXPECTING_LINE
          else:
            self.__add_to_line(c)
        elif self._state == STATE_BOTTOM:
          if c == HBAR:
            self._bottom_width += 1
          elif c == CORNER:
            self._state = STATE_END
          else:
            self.__unexpected_char(c)
        if c == '\n':
          self._x = 0
          self._y += 1
        else:
          self._x += 1

      def run(self):
        while self._state != STATE_END:
          c = self._text[self._index]
          self._handle_char(c)
          self._index += 1

        if self._top_width != self._bottom_width:
          raise RuntimeError('Bottom is wider than top')

        size = self.size()

        lines = self.lines()

        # Check that each line matches the width
        for i, line in enumerate(lines):
          line_width = len(line)
          if line_width != size.width:
            raise RuntimeError('Line %d is %d wide instead of %d: "%s"' % (i + 1, line_width, size.width, line))

        return ( size, self.string() )

    state = State(art)
    return state.run()

  def test_parse_art(self):

    self.assertEqual( ( size(2, 1), 'fo' ), self.__parse_art(
      '''
      +--+
      |fo|
      +--+
      ''') )

    self.assertEqual( ( size(3, 2), 'foo\nbar' ), self.__parse_art(
      '''
      +---+
      |foo|
      |bar|
      +---+
      ''') )

    self.assertEqual( ( size(1, 1), 'f' ), self.__parse_art(
      '''
      +-+
      |f|
      +-+
      ''') )

    self.assertEqual( ( size(0, 0), '' ), self.__parse_art(
      '''
      ++
      ++
      ''') )


    self.assertEqual( ( size(0, 0), '' ), self.__parse_art(
      '''
      +-+
      +-+
      ''') )

    self.assertEqual( ( size(0, 0), '' ), self.__parse_art(
      '''
      ++
      ||
      ++
      ''') )

    self.assertRaises( RuntimeError, self.__parse_art, '''+++\n||++''' )

    self.assertRaises( RuntimeError, self.__parse_art,
      '''
      +++
      ||
      ++
      ''' )

  def assertArtEqual(self, expected, actual, msg = None):
    size, expected_art = self.__parse_art(expected)
    expected_decorated = self.decorate_text(expected_art)
    actual_decorated = self.decorate_text(actual)
#    self.assertEqual( expected_decorated, actual_decorated, msg = msg)
    self.assertMultiLineEqual( expected_decorated, actual_decorated, msg = msg)

  def __test_draw_text(self, width, height, x, y, text, orientation = text_canvas.ORIENTATION_HORIZONTAL):
    canvas = text_canvas(width, height)
    canvas.draw_text(x, y, text, orientation)
    return str(canvas)

  def test_draw_text_horizontal(self):
    self.assertArtEqual( '''
    +-----+
    |     |
    | foo |
    +-----+
    ''', self.__test_draw_text(5, 2, 1, 1, 'foo', text_canvas.ORIENTATION_HORIZONTAL) )

    self.assertArtEqual( '''
    +-----+
    |     |
    |  foo|
    +-----+
    ''', self.__test_draw_text(5, 2, 2, 1, 'foo', text_canvas.ORIENTATION_HORIZONTAL) )

    self.assertArtEqual( '''
    +-----+
    |     |
    |   fo|
    +-----+
    ''', self.__test_draw_text(5, 2, 3, 1, 'foo', text_canvas.ORIENTATION_HORIZONTAL) )

    self.assertArtEqual( '''
    +-----+
    |     |
    |    f|
    +-----+
    ''', self.__test_draw_text(5, 2, 4, 1, 'foo', text_canvas.ORIENTATION_HORIZONTAL) )

    self.assertArtEqual( '''
    +-----+
    |     |
    |     |
    +-----+
    ''', self.__test_draw_text(5, 2, 5, 1, 'foo', text_canvas.ORIENTATION_HORIZONTAL) )

  def __test_draw_text_lines(self, width, height, x, y, lines):
    canvas = text_canvas(width, height)
    canvas.draw_text_lines(x, y, lines)
    return str(canvas)

  def test_draw_text_lines(self):
    self.assertArtEqual( '''
    +-----+
    |     |
    | foo |
    | bar |
    |     |
    +-----+
    ''', self.__test_draw_text_lines(5, 4, 1, 1, [ 'foo', 'bar' ]) )

  def test_draw_text_lines(self):
    self.assertArtEqual( '''
    +-----+
    |     |
    |  foo|
    |  bar|
    |     |
    +-----+
    ''', self.__test_draw_text_lines(5, 4, 2, 1, [ 'foo', 'bar' ]) )

  def test_draw_text_lines(self):
    self.assertArtEqual( '''
    +-----+
    |     |
    |   fo|
    |   ba|
    |     |
    +-----+
    ''', self.__test_draw_text_lines(5, 4, 3, 1, [ 'foo', 'bar' ]) )

  def test_draw_text_lines(self):
    self.assertArtEqual( '''
    +-----+
    |     |
    |    f|
    |    b|
    |     |
    +-----+
    ''', self.__test_draw_text_lines(5, 4, 4, 1, [ 'foo', 'bar' ]) )

  def test_draw_text_vertical(self):
    aa = text_canvas(2, 5)
    aa.draw_text(1, 1, 'foo', text_canvas.ORIENTATION_VERTICAL)
    self.assertEqual( '  \n f\n o\n o\n  ', str(aa) )

  def xtest_draw_text_horizontal_truncated(self):
    aa = text_canvas(2, 2)
    aa.draw_text(0, 0, 'foo', text_canvas.ORIENTATION_HORIZONTAL)
    self.assertEqual( 'fo\n  ', str(aa) )

  def xtest_draw_text_vertical_truncated(self):
    aa = text_canvas(2, 2)
    aa.draw_text(0, 0, 'foo', text_canvas.ORIENTATION_VERTICAL)
    self.assertEqual( 'f \no ', str(aa) )

  def xtest_draw_text_lines(self):
    aa = text_canvas(6, 4)
    aa.draw_text_lines(1, 1, [ 'foo', 'bar' ])
    self.assertEqual( 'f \no ', str(aa) )

if __name__ == '__main__':
  unittest.main()
