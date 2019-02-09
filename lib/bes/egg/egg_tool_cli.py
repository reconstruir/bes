#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import argparse, os, os.path as path

from bes.cli.command_cli import command_cli

from .egg import egg

class egg_tool_cli(command_cli):

  def __init__(self):
    super(build_list_cli, self).__init__('egg_tool_cli', 'Tool to deal with build lists.')

    # make
    self.add_command('make', 'Make an egg.')
    self.add_argument('make', 'setup_filename',
                      action = 'store',
                      help = 'egg description file (usually setup.py)')
    
    default_output_dir = os.getcwd()
    self.add_argument('make', '-o',
                      '--output-dir',
                      action = 'store',
                      default = default_output_dir,
                      help = 'Output directory [ %s ]' % (default_output_dir))
    self.add_argument('make', '-v',
                      '--verbose',
                      action = 'store_true',
                      default = False,
                      help = 'Be verbose about what is happening [ False ]')
  
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
 
  def _command_make(self, setup_filename, output_dir, verbose):
    setup_filename = self.resolve_filename(setup_filename)
    self.check_file_exists(setup_filename, label = 'setup file')
    self.check_dir_exists(output_dir, label = 'output dir')
    tmp_egg = egg.make(setup_filename)
    dst_egg = file_util.relocate_file(tmp_egg, output_dir)
    if verbose:
      print(dst_egg)
    return 0

  def _command_unpack(self, egg_filename, output_dir, verbose):
    egg_filename = self.resolve_filename(egg_filename)
    self.check_file_exists(egg_filename, label = 'egg')
    self.check_dir_exists(output_dir, label = 'output dir')
    egg.unpack(egg_filename, output_dir)
    return 0
