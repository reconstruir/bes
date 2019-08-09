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
    p.add_argument('filename', action = 'store', default = None, type = str, nargs = '?',
                   help = 'Filename or directory to list. [ None ]')
    p.add_argument('-R', '--recursive', action = 'store_true', default = False,
                   help = 'List recurisively. [ False ]')
    
    p = subparser.add_parser('upload', help = 'Upload a file.')
    p.add_argument('local_filename', action = 'store', default = None, type = str,
                   help = 'Local filename to upload. [ None ]')
    p.add_argument('remote_filename', action = 'store', default = None, type = str,
                   help = 'Remote filename to upload to. [ None ]')
    
    p = subparser.add_parser('download', help = 'Download a file.')
    p.add_argument('remote_filename', action = 'store', default = None, type = str,
                   help = 'Remote filename to upload to. [ None ]')
    p.add_argument('-o', '--output-filename', action = 'store', default = None, type = str,
                   help = 'Output filename to download to. [ None ]')
    
  def _command_fs_ls(self, config_file, filename, recursive):
    filename = filename or '/'
    options = fs_list_options(recursive = recursive)
    return fs_cli_command.ls(config_file, filename, options)

  def _command_fs_upload(self, config_file, local_filename, remote_filename):
    return fs_cli_command.upload(config_file, local_filename, remote_filename)
  
  def _command_fs_download(self, config_file, remote_filename, output_filename):
    return fs_cli_command.download(config_file, remote_filename, output_filename)
  
