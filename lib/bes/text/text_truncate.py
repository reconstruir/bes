#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

class text_truncate(object):
  'Truncate text.'

  @classmethod
  def truncate(clazz, text, width, ellipsis = '..'):
    text_len = len(text)
    if text_len <= width:
      return text

    delta = text_len - width + len(ellipsis)
    remainder = text_len - delta
    right_width = int(remainder / 2)
    left_width = remainder - right_width
    left = text[0:left_width]
    right = text[-right_width:]
    return f'{left}{ellipsis}{right}'
