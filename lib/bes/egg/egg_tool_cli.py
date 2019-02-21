#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import argparse, os, os.path as path

from bes.fs import file_util
from bes.cli.command_cli import command_cli

from .egg import egg

class egg_tool_cli(command_cli):

  def __init__(self):
    super(egg_tool_cli, self).__init__('egg_tool_cli', 'Tool to deal with build lists.')

    # make
    self.add_command('make', 'Make an egg.')
    self.add_argument('make', 'root_dir',
                      action = 'store',
                      help = 'GIT repo root.')
    self.add_argument('make', 'setup_filename',
                      action = 'store',
                      help = 'egg description file relative to the root_dir (usually setup.py) ')
    self.add_argument('make', '-r',
                      '--revision',
                      action = 'store',
                      default = 'master',
                      help = 'Output directory [ master ]')
    
    default_output_dir = os.getcwd()
    self.add_argument('make', '-o',
                      '--output-dir',
                      action = 'store',
                      default = default_output_dir,
                      help = 'Output directory [ %s ]' % (default_output_dir))
    self.add_argument('make', '-u',
                      '--untracked',
                      action = 'store_true',
                      default = False,
                      help = 'Include untracked git files in the egg. [ False ]')
    self.add_argument('make', '-v',
                      '--verbose',
                      action = 'store_true',
                      default = False,
                      help = 'Be verbose about what is happening [ False ]')
    self.add_argument('make', '-d',
                      '--debug',
                      action = 'store_true',
                      default = False,
                      help = 'Debug mode.  Save tmp files for inspection [ False ]')
  
    # unpack
    self.add_command('unpack', 'Unpack an egg.')
    self.add_argument('unpack', 'egg_filename',
                      action = 'store',
                      help = 'What to make')
    self.add_argument('unpack', '-o',
                      '--output-dir',
                      action = 'store',
                      default = default_output_dir,
                      help = 'Output directory [ %s ]' % (default_output_dir))
    self.add_argument('unpack', '-v',
                      '--verbose',
                      action = 'store_true',
                      default = False,
                      help = 'Be verbose about what is happening [ False ]')
 
  def _command_make(self, root_dir, setup_filename, revision, output_dir, untracked, verbose, debug):
    root_dir = self.resolve_dir(root_dir)
    resolved_setup_filename = self.resolve_file(setup_filename, root_dir = root_dir)
    self.check_dir(root_dir)
    self.check_file(resolved_setup_filename)
    self.check_dir(output_dir)
    tmp_egg = egg.make(root_dir, revision, setup_filename, untracked = untracked, debug = debug)
    dst_egg = file_util.relocate_file(tmp_egg, output_dir)
    if verbose:
      print(dst_egg)
    return 0

  def _command_unpack(self, egg_filename, output_dir, verbose):
    egg_filename = self.resolve_file(egg_filename)
    self.check_file(egg_filename)
    self.check_dir(output_dir)
    egg.unpack(egg_filename, output_dir)
    return 0
