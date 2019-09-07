#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os
from os import path

from bes.key_value.key_value_list import key_value_list
from bes.common.check import check
from bes.system.log import log

from .vfs_cli_command import vfs_cli_command
from .vfs_list_options import vfs_list_options

class vfs_cli_args(object):

  def __init__(self):
    pass
  
  def fs_add_args(self, subparser):
    p = subparser.add_parser('ls', help = 'List files or folders.')
    p.add_argument('filename', action = 'store', default = '/', type = str, nargs = '?',
                   help = 'Filename or directory to list. [ None ]')
    p.add_argument('-R', '--recursive', action = 'store_true', default = False,
                   help = 'List recurisively. [ False ]')
    p.add_argument('-l', '--show-all', action = 'store_true', default = False,
                   help = 'Show all file details. [ False ]')
    p.add_argument('-1', '--one-line', action = 'store_true', default = False,
                   help = 'Show one file per line. [ False ]')
    p.add_argument('-c', '--show-checksums', action = 'store_true', default = False,
                   help = 'Show checksums. [ False ]')
    p.add_argument('-a', '--show-attributes', action = 'store_true', default = False,
                   help = 'Show attributes. [ False ]')
    p.add_argument('-s', '--show-size', action = 'store_true', default = False,
                   help = 'Show size. [ False ]')
    p.add_argument('-f', '--flat-paths', action = 'store_true', default = False,
                   help = 'Flatten the fs tree paths. [ False ]')
    p.add_argument('-H', '--human-friendly', action = 'store_true', default = False,
                   help = 'Print data in human friendly form. [ False ]')
    
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
  
    p = subparser.add_parser('get_attributes', help = 'Get file attributes.')
    p.add_argument('remote_filename', action = 'store', default = None, type = str,
                   help = 'Remote filename to upload to. [ None ]')
    p.add_argument('keys', action = 'store', default = [], type = str, nargs = '*',
                   help = 'The keys to print or all if None [ None ]')

    p = subparser.add_parser('set_attributes', help = 'Set file attributes.')
    p.add_argument('remote_filename', action = 'store', default = None, type = str,
                   help = 'Remote filename to upload to. [ None ]')
    p.add_argument('params', action = 'store', default = [], type = str, nargs = '+',
                   help = 'The params to set in the for key1=value1 key2=value2 .... [ None ]')

    p = subparser.add_parser('cat', help = 'Cat a file.')
    p.add_argument('remote_filename', action = 'store', default = None, type = str,
                   help = 'Remote filename to upload to. [ None ]')
    
    p = subparser.add_parser('config', help = 'Show config possibilities.')
    
  def _command_fs_ls(self, config, filename, recursive, show_all, one_line,
                     show_checksums, show_attributes, show_size, flat_paths, human_friendly):
    if show_all:
      show_checksums = True
      show_size = True
      show_attributes = True
    options = vfs_list_options(recursive = recursive,
                              show_checksums = show_checksums,
                              show_size = show_size,
                              show_attributes = show_attributes,
                              one_line = one_line,
                              flat_paths = flat_paths,
                              human_friendly = human_friendly)
    return vfs_cli_command.ls(config, filename, options)

  def _command_fs_upload(self, config, local_filename, remote_filename):
    return vfs_cli_command.upload(config, local_filename, remote_filename)
  
  def _command_fs_download(self, config, remote_filename, output_filename):
    return vfs_cli_command.download(config, remote_filename, output_filename)
  
  def _command_fs_set_attributes(self, config, remote_filename, params):
    values = key_value_list.parse(' '.join(params))
    return vfs_cli_command.set_attributes(config, remote_filename, values)
  
  def _command_fs_get_attributes(self, config, remote_filename, keys):
    return vfs_cli_command.get_attributes(config, remote_filename, keys)
  
  def _command_fs_config(self):
    return vfs_cli_command.config()

  def _command_fs_cat(self, config, remote_filename):
    return vfs_cli_command.cat(config, remote_filename)
  
  
