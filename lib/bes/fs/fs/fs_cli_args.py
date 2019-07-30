#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os
from os import path

from bes.common.check import check
from bes.system.log import log

from .fs_cli_command import fs_cli_command
from .fs_list_options import fs_list_options

class fs_cli_args(object):

  def __init__(self):
    pass
  
  def fs_add_args(self, subparser):
    p = subparser.add_parser('ls', help = 'List files or folders.')
    p.add_argument('config_file', action = 'store', default = None, type = str,
                   help = 'The fs config file. [ None ]')
    p.add_argument('filename', action = 'store', default = None, type = str,
                   help = 'Filename or directory to list. [ None ]')
    p.add_argument('-R', '--recursive', action = 'store_true', default = False,
                   help = 'List recurisively. [ False ]')
    
  def _command_fs_ls(self, config_file, filename, recursive):
    options = fs_list_options(recursive = recursive)
    return fs_cli_command.ls(config_file, filename, options)
