#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import argparse, os
from os import path

from bes.system.log import log
from ..system.check import check
from bes.version.version_cli import version_cli
from bes.cli.argparser_handler import argparser_handler

import bes

from .vfs_cli_args import vfs_cli_args

class vfs_cli(vfs_cli_args):

  def __init__(self):
    self.parser = argparse.ArgumentParser()
    commands_subparser = self.parser.add_subparsers(help = 'commands', dest = 'command')

    self.parser.add_argument('-c', '--config', action = 'store', default = None, type = str,
                             help = 'The fs config file. [ None ]')

    self.fs_add_args(commands_subparser)
    
    # version
    version_parser = commands_subparser.add_parser('version', help = 'Version a build to a build list.')
    version_cli.arg_sub_parser_add_arguments(version_parser)
    
  def main(self):
    return argparser_handler.main('fs', self.parser, self, command_group = 'fs')

  def _command_version(self, print_all, brief):
    version_cli.print_everything('bes', dependencies = [ 'bes' ],
                                 brief = brief, print_all = print_all)
    return 0
  
  @classmethod
  def run(clazz):
    raise SystemExit(vfs_cli().main())
  
