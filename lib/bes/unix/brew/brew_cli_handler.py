#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path

from bes.cli.cli_command_handler import cli_command_handler
from bes.common.check import check

from .brew import brew
from .brew_options import brew_options

class brew_cli_handler(cli_command_handler):
  'brew cli handler.'

  def __init__(self, cli_args):
    super(brew_cli_handler, self).__init__(cli_args, options_class = brew_options)
    check.check_brew_options(self.options)
    self._brew = brew(self.options)
    
  def info(self):
    version = self._brew.version()
    print('version: {}'.format(version))
    return 0

  def installed(self):
    installed = self._brew.installed()
    for p in installed:
      print(p)
    return 0
  
  def available(self):
    available = self._brew.available()
    for p in available:
      print(p)
    return 0

  def files(self, package_name, print_inode):
    check.check_string(package_name)
    check.check_bool(print_inode)
    
    files = self._brew.files(package_name)
    for f in files:
      print(f)
    return 0
  
