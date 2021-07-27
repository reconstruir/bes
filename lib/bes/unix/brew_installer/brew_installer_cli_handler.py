#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path

from bes.cli.cli_command_handler import cli_command_handler
from bes.common.check import check
from bes.fs.file_util import file_util

from .brew_installer import brew_installer
from .brew_installer_options import brew_installer_options

class brew_installer_cli_handler(cli_command_handler):

  def __init__(self, cli_args):
    super(brew_installer_cli_handler, self).__init__(cli_args, options_class = brew_installer_options)
    check.check_brew_installer_options(self.options)

  def run_script(self, script_name, args, print_only):
    check.check_string(script_name)
    check.check_string_seq(args, allow_none = True)
    check.check_bool(print_only)
    
    if print_only:
      tmp = brew_installer.download_script(script_name)
      file_util.page(tmp)
      return 0
    brew_installer.run_script(script_name, args, self.options)
    return 0

  def info(self):
    version = brew_installer.version()
    print(version)
    return 0

  def reinstall(self):
    brew_installer.reinstall(self.options)
    return 0
  
  def install(self):
    brew_installer.install(self.options)
    return 0

  def uninstall(self):
    brew_installer.uninstall(self.options)
    return 0

  def ensure(self):
    brew_installer.ensure(self.options)
    return 0
