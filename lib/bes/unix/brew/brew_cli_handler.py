#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path

from bes.cli.cli_command_handler import cli_command_handler
from bes.system.check import check
from bes.fs.file_util import file_util

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
      if print_inode:
        inode = '{} '.format(file_util.inode_number(f))
      else:
        inode = ''
      print('{}{}'.format(inode, f))
    return 0

  def outdated(self):
    outdated = self._brew.outdated()
    for name, info in sorted(outdated.items()):
      print('{}: {}'.format(name, info))
    return 0
  
  def needs_update(self, package_name):
    check.check_string(package_name)

    result = self._brew.needs_update(package_name)
    return self.handle_boolean_result(result.needs_update,
                                      self.options.verbose)

  def install(self, package_name):
    check.check_string(package_name)
    
    self._brew.install(package_name)
    return 0

  def uninstall(self, package_name):
    check.check_string(package_name)
    
    self._brew.uninstall(package_name)
    return 0
  
  def upgrade(self, package_name):
    check.check_string(package_name)
    
    self._brew.upgrade(package_name)
    return 0
    
