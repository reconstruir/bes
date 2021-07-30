#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import argparse, os, os.path as path

from bes.fs import file_util

from .egg import egg

class egg_cli_args(object):

  def __init__(self):
    pass
  
  def egg_add_args(self, subparser):
    import os
    default_output_dir = os.getcwd()
    
    # make
    p = subparser.add_parser('make', help = 'Make an egg.')
    p.add_argument('root_dir', action = 'store', default = None,
                   help = 'GIT repo root.')
    p.add_argument('setup_filename', action = 'store', default = None,
                   help = 'egg description file relative to the root_dir (usually setup.py)')
    p.add_argument('-r', '--revision', action = 'store', default = 'master',
                   help = 'Output directory [ master ]')
    default_output_dir = os.getcwd()
    p.add_argument('-o', '--output-dir', action = 'store', default = default_output_dir,
                   help = 'Output directory [ %s ]' % (default_output_dir))
    p.add_argument('-u', '--untracked', action = 'store_true', default = False,
                   help = 'Include untracked git files in the egg. [ False ]')
    p.add_argument('-v', '--verbose', action = 'store_true', default = False,
                   help = 'Be verbose about what is happening [ False ]')
    p.add_argument('-d', '--debug', action = 'store_true', default = False,
                   help = 'Debug mode.  Save tmp files for inspection [ False ]')

    # make_from_address
    p = subparser.add_parser('make_from_address', help = 'Make an from a git address.')
    p.add_argument('address', action = 'store', default = None,
                   help = 'GIT repo address.')
    p.add_argument('revision', action = 'store', default = 'master',
                   help = 'Output directory [ master ]')
    p.add_argument('--setup-filename', '-s',  action = 'store', default = 'setup.py',
                   help = 'egg setup file relative to the root_dir [ setup.py ]')
    p.add_argument('--version-filename', action = 'store', default = None,
                   help = 'Optional version filename to update [ ]')
    p.add_argument('--project-name', action = 'store', default = None,
                   help = 'The name of the project [ None ]')
    default_output_dir = os.getcwd()
    p.add_argument('-o', '--output-dir', action = 'store', default = default_output_dir,
                   help = 'Output directory [ %s ]' % (default_output_dir))
    p.add_argument('-v', '--verbose', action = 'store_true', default = False,
                   help = 'Be verbose about what is happening [ False ]')
    p.add_argument('-d', '--debug', action = 'store_true', default = False,
                   help = 'Debug mode.  Save tmp files for inspection [ False ]')
    
    # unpack
    p = subparser.add_parser('unpack', help = 'Unpack an egg.')
    p.add_argument('egg_filename', action = 'store',
                   help = 'What to make')
    p.add_argument('-o', '--output-dir', action = 'store', default = default_output_dir,
                   help = 'Output directory [ %s ]' % (default_output_dir))
    p.add_argument('-v', '--verbose', action = 'store_true', default = False,
                   help = 'Be verbose about what is happening [ False ]')

  def _command_egg(self, command, *args, **kargs):
    from .egg_cli_handler import egg_cli_handler
    return egg_cli_handler(kargs).handle_command(command)
  
