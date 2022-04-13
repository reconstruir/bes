#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from ..system.check import check

class text_box_char(object):
  def __init__(self, name, char, width):
    self.name = name
    self.char = char
    self.width = width

class text_box(object):
  def __init__(self, chars):
    for c in chars:
      setattr(self, c.name, c)

  def write_v_bar(self, buf):
    buf.write(self.v_bar.char)

  def write_h_bar(self, buf):
    buf.write(self.h_bar.char)
    
  def write_tl_corner(self, buf):
    buf.write(self.tl_corner.char)
    
  def write_tr_corner(self, buf):
    buf.write(self.tr_corner.char)
    
  def write_bl_corner(self, buf):
    buf.write(self.bl_corner.char)
    
  def write_br_corner(self, buf):
    buf.write(self.br_corner.char)
    
  def write_top(self, buf, width):
    middle_width = width - self.tl_corner.width - self.tr_corner.width
    buf.write(self.tl_corner.char)
    buf.write(self.h_bar.char * middle_width)
    buf.write(self.tr_corner.char)
      
  def write_bottom(self, buf, width):
    middle_width = width - self.bl_corner.width - self.br_corner.width
    buf.write(self.bl_corner.char)
    buf.write(self.h_bar.char * middle_width)
    buf.write(self.br_corner.char)
      
  def write_middle(self, buf, width):
    middle_width = width - 2 * self.v_bar.width
    buf.write(self.v_bar.char)
    buf.write(self.h_bar.char * middle_width)
    buf.write(self.v_bar.char)
      
  def write_centered_text(self, buf, width, text):
    middle_width = width - 2 * self.v_bar.width
    centered_text = text.center(middle_width)
    buf.write(self.v_bar.char)
    buf.write(centered_text)
    buf.write(self.v_bar.char)
      
check.register_class(text_box)

class text_box_unicode(text_box):
  def __init__(self):
    super(text_box_unicode, self).__init__([
      text_box_char('v_bar', '\xe2\x94\x82', 1),
      text_box_char('l_bar', '\xe2\x94\x82', 1),
      text_box_char('r_bar', '\xe2\x94\x82', 1),
      text_box_char('h_bar', '\xe2\x94\x80', 1),
      text_box_char('t_bar', '\xe2\x94\x80', 1),
      text_box_char('b_bar', '\xe2\x94\x80', 1),
      text_box_char('tl_corner', '\xe2\x94\x8c', 1),
      text_box_char('tr_corner', '\xe2\x94\x90', 1),
      text_box_char('bl_corner', '\xe2\x94\x94', 1),
      text_box_char('br_corner', '\xe2\x94\x98', 1),
    ])

class text_box_ascii(text_box):
  def __init__(self):
    super(text_box_ascii, self).__init__([
      text_box_char('v_bar', '|', 1),
      text_box_char('l_bar', '|', 1),
      text_box_char('r_bar', '|', 1),
      text_box_char('h_bar', '-', 1),
      text_box_char('t_bar', '-', 1),
      text_box_char('b_bar', '-', 1),
      text_box_char('tl_corner', '+', 1),
      text_box_char('tr_corner', '+', 1),
      text_box_char('bl_corner', '+', 1),
      text_box_char('br_corner', '+', 1),
    ])
    
class text_box_colon(text_box):
  def __init__(self):
    super(text_box_colon, self).__init__([
      text_box_char('v_bar', ':', 1),
      text_box_char('l_bar', '', 0),
      text_box_char('r_bar', '', 0),
      text_box_char('h_bar', '', 0),
      text_box_char('t_bar', '', 0),
      text_box_char('b_bar', '', 0),
      text_box_char('tl_corner', '', 0),
      text_box_char('tr_corner', '', 0),
      text_box_char('bl_corner', '', 0),
      text_box_char('br_corner', '', 0),
    ])
    
class text_box_space(text_box):
  def __init__(self):
    super(text_box_space, self).__init__([
      text_box_char('v_bar', ' ', 1),
      text_box_char('l_bar', '', 0),
      text_box_char('r_bar', '', 0),
      text_box_char('h_bar', '', 0),
      text_box_char('t_bar', '', 0),
      text_box_char('b_bar', '', 0),
      text_box_char('tl_corner', '', 0),
      text_box_char('tr_corner', '', 0),
      text_box_char('bl_corner', '', 0),
      text_box_char('br_corner', '', 0),
    ])

class text_box_csv(text_box):
  def __init__(self):
    super(text_box_csv, self).__init__([
      text_box_char('v_bar', ',', 1),
      text_box_char('l_bar', '', 0),
      text_box_char('r_bar', '', 0),
      text_box_char('h_bar', '', 0),
      text_box_char('t_bar', '', 0),
      text_box_char('b_bar', '', 0),
      text_box_char('tl_corner', '', 0),
      text_box_char('tr_corner', '', 0),
      text_box_char('bl_corner', '', 0),
      text_box_char('br_corner', '', 0),
    ])
    
