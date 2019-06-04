#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import argparse

from bes.common.check import check
from bes.version.version_cli import version_cli
from bes.cli.command_cli import command_cli

import bes

class fake_cli(command_cli):

  def __init__(self):
    super(fake_cli, self).__init__('fake_cli', 'A test tool.')
    
    # foo
    self.add_command('foo', 'Do some foo.')
    
    self.add_argument('foo', 'address',
                      action = 'store',
                      default = None,
                      type = str,
                      help = 'The foo address. [ None ]')
    self.add_argument('foo', 'version',
                      action = 'store',
                      default = None,
                      type = str,
                      help = 'The foo version. [ None ]')
    self.add_argument('foo', '-d', '--debug',
                      action = 'store_true',
                      default = False)
    self.add_argument('foo', '-v', '--verbose',
                      action = 'store_true',
                      default = False,
                      help = 'Verbose debug spew [ False ]')

    # bar
    self.add_command('bar', 'Do some bar.')
    
    self.add_argument('bar', 'branch',
                      action = 'store',
                      default = None,
                      type = str,
                      help = 'The bar branch. [ None ]')
    self.add_argument('bar', '-v', '--verbose',
                      action = 'store_true',
                      default = False,
                      help = 'Verbose debug spew [ False ]')
    
    # version
    self.add_command('version', 'Print the version.')
    self.add_argument('version', '-a', '--all',
                      action = 'store_true',
                      default = False,
                      dest = 'print_all')
    self.add_argument('version', '-b', '--brief',
                      action = 'store_true',
                      default = False)

  def _command_foo(self, address, version, debug, verbose):
    check.check_string(address)
    check.check_string(version)
    check.check_bool(debug)
    check.check_bool(verbose)
    print('foo:%s:%s:%s:%s' % (address, version, int(debug), int(verbose)))
    return 0
  
  def _command_bar(self, branch, verbose):
    check.check_string(branch)
    check.check_bool(verbose)
    print('bar:%s:%s' % (branch, int(verbose)))
    return 0
  
  def _command_version(self, print_all, brief):
    version_cli.print_everything('bes', brief = brief, print_all = print_all)
    return 0
