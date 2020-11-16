#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path

from bes.cli.argparser_handler import argparser_handler
from bes.common.check import check

from .sudo_exe import sudo_exe
from .sudo_cli_options import sudo_cli_options

class sudo_cli_command(object):

  @classmethod
  def handle_command(clazz, command, **kargs):
    options = sudo_cli_options(**kargs)
    filtered_args = argparser_handler.filter_keywords_args(sudo_cli_options, kargs)
    func = getattr(sudo_cli_command, command)
    return func(options, **filtered_args)
  
  @classmethod
  def run(clazz, options, cmd):
    check.check_sudo_cli_options(options)
    check.check_string_seq(cmd)

    sudo_exe.call_sudo(cmd, options)
    return 0

  @classmethod
  def authenticate(clazz, options):
    check.check_sudo_cli_options(options)

    sudo_exe.authenticate(options)
    return 0

  @classmethod
  def is_authenticated(clazz, options):
    check.check_sudo_cli_options(options)

    if sudo_exe.is_authenticated(options):
      return 0
    else:
      return 1

  @classmethod
  def reset(clazz, options):
    check.check_sudo_cli_options(options)

    sudo_exe.reset(options)
    return 0
  
