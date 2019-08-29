#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import glob, os, re
from os import path

from bes.common.check import check
from bes.system.log import logger
from bes.python.code import code
from bes.fs.file_util import file_util
from bes.key_value.key_value_list import key_value_list

from .fs_registry import fs_registry
from .fs_local import fs_local
from .fs_file_info import fs_file_info
from .fs_list_options import fs_list_options
from .fs_error import fs_error

class fs_cli_command(object):
  'fs command line implementations.'

  log = logger('fs')

  _CONFIG_DIR = path.expanduser('~/.besfs/config')
  
  @classmethod
  def ls(clazz, config, filename, options):
    'ls command.'
    check.check_string(config, allow_none = True)
    check.check_string(filename)
    check.check_fs_list_options(options, allow_none = True)

    fs = clazz._create_fs_from_config(config)

    options = options or fs_list_options()
    clazz.log.log_d('ls: filename={} options={}'.format(filename, options))
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
    fields = [ path.basename(info.filename) ]
    if options.show_size:
      fields.append(clazz._format_file_size(info.size, options))
    if options.show_checksums:
      fields.append(info.checksum)
#    if options.show_attributes:
#      kvl = key_value_list.from_dict(info.attributes)
#      fields.append(kvl.to_string(delimiter = '=', value_delimiter = ' '))
    return ' '.join(fields)

  @classmethod
  def _format_file_size(clazz, size, options):
    if options.human_friendly:
      return file_util.format_size(size)
    else:
      return str(size)
  
  
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
    s = clazz._format_file_info(info, options)
    print(s)
    if options.show_attributes:
      kvl = key_value_list.from_dict(info.attributes)
      from bes.text.text_table import text_table
      t = text_table(data = kvl)
      print(t)
      #fields.append(kvl.to_string(delimiter = '=', value_delimiter = ' '))

    return 0
  
  @classmethod
  def upload(clazz, config, local_filename, remote_filename):
    'upload a file.'
    check.check_string(config, allow_none = True)
    check.check_string(local_filename)
    check.check_string(remote_filename)

    fs = clazz._create_fs_from_config(config)

    clazz.log.log_d('upload: local_filename={} remote_filename={}'.format(local_filename,
                                                                          remote_filename))
    fs.upload_file(local_filename, remote_filename)
    return 0

  @classmethod
  def download(clazz, config, remote_filename, output_filename):
    'Download a file.'
    check.check_string(config, allow_none = True)
    check.check_string(remote_filename)
    check.check_string(output_filename, allow_none = True)
    fs = clazz._create_fs_from_config(config)
    output_filename = output_filename or path.join(ow.getcwd(), path.basename(remote_filename))
    clazz.log.log_d('download: remote_filename={} output_filename={}'.format(remote_filename,
                                                                             output_filename))
    clazz.log.log_d('download: fs={}'.format(fs))
    fs.download_file(remote_filename, output_filename)
    return 0

  @classmethod
  def set_attributes(clazz, config, remote_filename, values):
    check.check_string(config, allow_none = True)
    check.check_string(remote_filename)
    check.check_key_value_list(values)
    fs = clazz._create_fs_from_config(config)
    fs.set_file_attributes(remote_filename, values.to_dict())
    return 0
    
  @classmethod
  def get_attributes(clazz, config, remote_filename, keys):
    check.check_string(config, allow_none = True)
    check.check_string(remote_filename)
    check.check_list(keys, allow_none = True)
    fs = clazz._create_fs_from_config(config)
    info = fs.file_info(remote_filename)
    if len(keys) == 1:
      key = keys[0]
      if key in info.attributes:
        clazz._print_attribute(key, info.attributes[key], False)
    else:
      for key in keys or info.attributes.keys():
        clazz._print_attribute(key, info.attributes[key], True)
    return 0
    
  @classmethod
  def _print_attribute(clazz, key, value, print_key):
    if print_key:
      print('{}={}'.format(key, value))
    else:
      print(value)
    
  @classmethod
  def config(clazz):
    for c in clazz._list_configs():
      print(c)
    return 0
    
  @classmethod
  def _resolve_config_filename(clazz, config):
    if config:
      if path.isfile(config):
        return path.abspath(config)
      possible_configs = [
        '{}/{}'.format(clazz._CONFIG_DIR, config),
        '{}/{}.besfs'.format(clazz._CONFIG_DIR, config),
      ]
      for p in possible_configs:
        if path.isfile(p):
          return p
    config = os.environ.get('BESFS_CONFIG', None)
    if path.isfile(config):
      return config
    return None
  
  @classmethod
  def _list_configs(clazz):
    files = glob.glob('{}/*.besfs'.format(clazz._CONFIG_DIR))
    return [ file_util.remove_extension(path.basename(f)) for f in files ]
  
  @classmethod
  def _create_fs_from_config(clazz, config):
    config_filename = clazz._resolve_config_filename(config)
    if not config_filename:
      raise fs_error('No config given either with --config or ~/.besfs/config or BESFS_CONFIG')
    clazz.log.log_d('_create_fs_from_config: config={}'.format(config))
    fs = fs_registry.load_from_config_file(config_filename)
    clazz.log.log_d('_create_fs_from_config: fs={}'.format(fs))
    return fs

  
