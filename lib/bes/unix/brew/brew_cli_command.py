#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path

from bes.common.check import check
from bes.fs.file_util import file_util

from .brew import brew

class brew_cli_command(object):

  @classmethod
  def handle_command(clazz, command, **kargs):
    func = getattr(clazz, command)
    return func(**kargs)
  
  @classmethod
  def run_script(clazz, script_name, args, print_only):
    check.check_string(script_name)
    check.check_string_seq(args, allow_none = True)
    check.check_bool(print_only)
    if print_only:
      tmp = brew.download_script(script_name)
      file_util.page(tmp)
      return 0
    brew.run_script(script_name, args)
    return 0

  @classmethod
  def info(clazz):
    version = brew.version()
    print(version)
    return 0
  
