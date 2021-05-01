#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path

from bes.common.check import check

from .scutil import scutil

class scutil_cli_command(object):

  @classmethod
  def handle_command(clazz, command, **kargs):
    func = getattr(scutil_cli_command, command)
    return func(**kargs)
  
  @classmethod
  def get_value(clazz, key):
    check.check_string(key)

    s = scutil.get_value(key)
    print(s)
    return 0

  @classmethod
  def set_value(clazz, key, value):
    check.check_string(key)
    check.check_string(value)

    scutil.set_value(key, value)
    return 0
