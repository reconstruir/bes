#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import argparse, os, os.path as path

from bes.cli import cli_base

from .egg import egg

class egg_tool_cli(cli_base):

  def __init__(self):
    self._parser = argparse.ArgumentParser()
    subparsers = self._parser.add_subparsers(help = 'commands', dest = 'command')
  
    # make
    make_parser = subparsers.add_parser('make', help = 'Make command')
    make_parser.add_argument('setup_filename',
                             action = 'store',
                             help = 'egg description file (usually setup.py)')
    default_output_dir = os.getcwd()
    make_parser.add_argument('-o',
                             '--output-dir',
                             action = 'store',
                             default = default_output_dir,
                             help = 'Output directory [ %s ]' % (default_output_dir))
    self.add_verbose_option(make_parser)
  
    # unpack
    unpack_parser = subparsers.add_parser('unpack', help = 'Unpack command')
    unpack_parser.add_argument('egg_filename',
                               action = 'store',
                               help = 'What to make')
    self.add_verbose_option(unpack_parser)
    unpack_parser.add_argument('-o',
                               '--output-dir',
                               action = 'store',
                               default = default_output_dir,
                               help = 'Output directory [ %s ]' % (default_output_dir))
    
  @classmethod
  def run(clazz):
    raise SystemExit(egg_tool_cli().main())

  def main(self):
    args = self._parser.parse_args()
    self.verbose = False
    if args.command == 'make':
      self.verbose = args.verbose
      return self._command_make(args.setup_filename, args.output_dir)
    elif args.command == 'unpack':
      return self._command_unpack(args.egg_filename, args.output_dir)
    else:
      raise RuntimeError('Invalid command: %s' % (args.command))
 
  def _command_make(self, setup_filename, output_dir):
    setup_filename = self.resolve_filename(setup_filename)
    self.check_file_exists(setup_filename, label = 'setup file')
    self.check_dir_exists(output_dir, label = 'output dir')
    tmp_egg = egg.make(setup_filename)
    dst_egg = file_util.relocate_file(tmp_egg, output_dir)
    if self.verbose:
      print(dst_egg)
    return 0

  def _command_unpack(self, egg_filename, output_dir):
    egg_filename = self.resolve_filename(egg_filename)
    self.check_file_exists(egg_filename, label = 'egg')
    self.check_dir_exists(output_dir, label = 'output dir')
    egg.unpack(egg_filename, output_dir)
    return 0
