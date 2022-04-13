#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path

from bes.system.check import check

from .shell import shell

class shell_cli_command(object):

  @classmethod
  def handle_command(clazz, command, **kargs):
    func = getattr(shell_cli_command, command)
    return func(**kargs)
  
  @classmethod
  def change(clazz, new_shell, password):
    check.check_string(new_shell)
    check.check_string(password, allow_none = True)

    shell.change_shell(new_shell, password)
    return 0
