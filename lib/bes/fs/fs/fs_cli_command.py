#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os
from os import path

from bes.common.check import check
from bes.system.log import logger
from bes.python.code import code

from .fs_registry import fs_registry
from .fs_local import fs_local
from .fs_file_info import fs_file_info
from .fs_list_options import fs_list_options

class fs_cli_command(object):
  'fs command line implementations.'

  log = logger('fs')
  
  @classmethod
  def ls(clazz, config_file, filename, options):
    'ls command.'
    check.check_string(config_file)
    check.check_string(filename)
    check.check_fs_list_options(options, allow_none = True)

    options = options or fs_list_options()
    clazz.log.log_d('ls: config_file={} filename={} options={}'.format(config_file, filename, options))
    fs = fs_registry.load_from_config_file(config_file)
    clazz.log.log_d('ls: fs={}'.format(fs))
    info = fs.file_info(filename)
    clazz.log.log_d('ls: info={}'.format(info))
    if info.ftype == fs_file_info.DIR:
      return clazz._ls_dir(fs, info, options)
    else:
      return clazz._ls_file(fs, info, options)
    return 0

  @classmethod
  def _ls_dir(clazz, fs, info, options):
    'list dirs.'
    clazz.log.log_d('_ls_dir: fs={} info={} options={}'.format(fs, info, options))
    assert not info.children
    listing = fs.list_dir(info.filename, options.recursive)
    clazz._print_entry(listing, options, 0)
    return 0

  @classmethod
  def _format_file_info(clazz, info, options):
    if options.show_details:
      return '{} {} {}'.format(path.basename(info.filename), info.size, info.checksum)
    else:
      return info.filename
  
  @classmethod
  def _print_entry(clazz, entry, options, depth):
    indent = '  ' * depth
    if entry.ftype == 'file':
      s = clazz._format_file_info(entry, options)
      print('{}{}'.format(indent, s))
    elif entry.ftype == 'dir':
      for child in entry:
        if child.is_dir():
          print('{}{}'.format(indent, child.display_filename))
          clazz._print_entry(child, options, depth + 1)
        else:
          s = clazz._format_file_info(child, options)
          print('{}{}'.format(indent, s))

  @classmethod
  def _ls_file(clazz, fs, info, options):
    'list files.'
    clazz.log.log_d('_ls_file: fs={} info={} options={}'.format(fs, info, options))
    if options.show_details:
      print('{} {} {}'.format(path.basename(info.filename), info.size, info.checksum))
    else:
      print(info.filename)
    return 0

  @classmethod
  def upload(clazz, config_file, local_filename, remote_filename):
    'upload a file.'
    check.check_string(config_file)
    check.check_string(local_filename)
    check.check_string(remote_filename)
    clazz.log.log_d('upload: config_file={} local_filename={} remote_filename={}'.format(config_file,
                                                                                         local_filename,
                                                                                         remote_filename))
    fs = fs_registry.load_from_config_file(config_file)
    clazz.log.log_d('upload: fs={}'.format(fs))
    fs.upload_file(local_filename, remote_filename)
    return 0

  @classmethod
  def download(clazz, config_file, remote_filename, output_filename):
    'Download a file.'
    check.check_string(config_file)
    check.check_string(remote_filename)
    check.check_string(output_filename, allow_none = True)
    output_filename = output_filename or path.join(ow.getcwd(), path.basename(remote_filename))
    clazz.log.log_d('download: config_file={} remote_filename={} output_filename={}'.format(config_file,
                                                                                            remote_filename,
                                                                                            output_filename))
    fs = fs_registry.load_from_config_file(config_file)
    clazz.log.log_d('download: fs={}'.format(fs))
    fs.download_file(remote_filename, output_filename)
    return 0

  
