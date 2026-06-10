#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.bcli.bcli_command_handler import bcli_command_handler
from bes.system.check import check

from .scutil import scutil

class scutil_command_handler(bcli_command_handler):

  def name(self):
    return 'scutil'

  def _command_get_value(self, key, options):
    check.check_string(key)

    s = scutil.get_value(key)
    print(s)
    return 0

  def _command_set_value(self, key, value, options):
    check.check_string(key)
    check.check_string(value)

    scutil.set_value(key, value)
    return 0
