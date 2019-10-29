#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.common.check import check

class simple_config_error(Exception):
  def __init__(self, message, origin):
    check.check_string(message)
    check.check_simple_config_origin(origin)
    super(simple_config_error, self).__init__()
    self.message = message
    self.origin = origin

  def __str__(self):
    source = '<unknown>' if not self.origin else self.origin.source
    line_number = '<unknown>' if not self.origin else self.origin.line_number
    return '{}:{}: {}'.format(source, line_number, self.message)
