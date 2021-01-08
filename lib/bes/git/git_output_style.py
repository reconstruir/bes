#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

class git_output_style(object):

  STYLES = ( 'brief', 'table', 'json', 'plain' )

  @classmethod
  def check_style(clazz, style):
    if not style in clazz.STYLES:
      raise git_error('Invalid output style: "{}" - should be one of: {}'.format(style,
                                                                                 ' '.join(clazz.STYLES)))
