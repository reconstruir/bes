#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.common import check

class text_box_char(object):
  def __init__(self, name, char, width):
    self.name = name
    self.char = char
    self.width = width

class text_box(object):
  def __init__(self, chars):
    for c in chars:
      setattr(self, c.name, c)

  def write_v(self, buf):
    buf.write(self.v.char)

  def write_h(self, buf):
    buf.write(self.h.char)
    
  def write_tl(self, buf):
    buf.write(self.tl.char)
    
  def write_tr(self, buf):
    buf.write(self.tr.char)
    
  def write_bl(self, buf):
    buf.write(self.bl.char)
    
  def write_br(self, buf):
    buf.write(self.br.char)
    
  def write_top(self, buf, width):
    middle_width = width - self.tl.width - self.tr.width
    buf.write(self.tl.char)
    buf.write(self.h.char * middle_width)
    buf.write(self.tr.char)
      
  def write_bottom(self, buf, width):
    middle_width = width - self.bl.width - self.br.width
    buf.write(self.bl.char)
    buf.write(self.h.char * middle_width)
    buf.write(self.br.char)
      
  def write_middle(self, buf, width):
    middle_width = width - 2 * self.v.width
    buf.write(self.v.char)
    buf.write(self.h.char * middle_width)
    buf.write(self.v.char)
      
  def write_centered_text(self, buf, width, text):
    middle_width = width - 2 * self.v.width
    centered_text = text.center(middle_width)
    buf.write(self.v.char)
    buf.write(centered_text)
    buf.write(self.v.char)
      
check.register_class(text_box)

class text_box_unicode(text_box):
  def __init__(self):
    super(text_box_unicode, self).__init__([
      text_box_char('v', '\xe2\x94\x82', 1),
      text_box_char('h', '\xe2\x94\x80', 1),
      text_box_char('tl', '\xe2\x94\x8c', 1),
      text_box_char('tr', '\xe2\x94\x90', 1),
      text_box_char('bl', '\xe2\x94\x94', 1),
      text_box_char('br', '\xe2\x94\x98', 1),
    ])

class text_box_ascii(text_box):
  def __init__(self):
    super(text_box_ascii, self).__init__([
      text_box_char('v', '|', 1),
      text_box_char('h', '-', 1),
      text_box_char('tl', '+', 1),
      text_box_char('tr', '+', 1),
      text_box_char('bl', '+', 1),
      text_box_char('br', '+', 1),
    ])
