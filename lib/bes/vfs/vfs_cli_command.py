#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import glob, os, re
from os import path

from datetime import datetime

from ..system.check import check
from bes.system.log import logger
from bes.python.code import code
from bes.fs.file_util import file_util
from bes.key_value.key_value_list import key_value_list
from bes.text.text_table import text_table

from .vfs_error import vfs_error
from .vfs_file_info import vfs_file_info
from .vfs_file_info import vfs_file_info_list
from .vfs_file_info_options import vfs_file_info_options
from .vfs_list_options import vfs_list_options
from .vfs_local import vfs_local
from .vfs_path_util import vfs_path_util
from .vfs_registry import vfs_registry

class vfs_cli_command(object):
  'fs command line implementations.'

  log = logger('fs')

  _CONFIG_DIR = path.expanduser('~/.bes_vfs/config')
  
  @classmethod
  def ls(clazz, config, remote_filename, options):
    'ls command.'
    check.check_string(config, allow_none = True)
    check.check_string(remote_filename)
    check.check_vfs_list_options(options, allow_none = True)

    remote_filename = vfs_path_util.normalize(remote_filename)
    
    fs = clazz._create_fs_from_config(config)

    options = options or vfs_list_options()
    clazz.log.log_d('ls: remote_filename={} options={}'.format(remote_filename, options))

    info = fs.file_info(remote_filename, vfs_file_info_options())
    clazz.log.log_d('ls: info={}'.format(info))
    if info.ftype == vfs_file_info.DIR:
      return clazz._ls_dir(fs, info, options)
    else:
      return clazz._ls_file(fs, info, options)
    return 0

  @classmethod
  def lsdir(clazz, config, remote_dir, options):
    'ls command.'
    check.check_string(config, allow_none = True)
    check.check_string(remote_dir)
    check.check_vfs_list_options(options, allow_none = True)

    remote_dir = vfs_path_util.normalize(remote_dir)
    
    fs = clazz._create_fs_from_config(config)

    options = options or vfs_list_options()
    clazz.log.log_d('lsdir: remote_dir={} options={}'.format(remote_dir, options))

    caca = fs.list_dir(remote_dir, options.recursive, vfs_file_info_options())
    for x in caca:
      print(x, type(x))
    return 0
  
  @classmethod
  def _ls_dir(clazz, fs, info, options):
    'list dirs.'
    clazz.log.log_d('_ls_dir: fs={} info={} options={}'.format(fs, info, options))
    assert not info.children
    listing = fs.list_dir(info.filename, options.recursive, vfs_file_info_options())
    clazz._print_entries(listing, options, 0)
    return 0

  @classmethod
  def _format_file_info(clazz, info, options):
    fields = [ vfs_path_util.basename(info.filename) ]
    if options.show_size:
      fields.append(clazz._format_file_size(info.size, options))
    if options.show_checksums:
      fields.append(str(info.checksums) or '')
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
  def _print_entries(clazz, entries, options, depth):
    check.check_vfs_file_info_list(entries)
    indent = '  ' * depth
    for entry in entries:
      if entry.is_dir():
        print('{}{}'.format(indent, entry.display_filename))
        clazz._print_entries(entry.children, options, depth + 1)
      else:
        s = clazz._format_file_info(entry, options)
        print('{}{}'.format(indent, s))

  @classmethod
  def _ls_file(clazz, fs, info, options):
    'list files.'
    clazz.log.log_d('_ls_file: fs={} info={} options={}'.format(fs, info, options))
    s = clazz._format_file_info(info, options)
    print(s)
    if options.show_attributes:
      kvl = key_value_list.from_dict(info.attributes)
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
    fs.download_to_file(remote_filename, output_filename)
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
        '{}/{}.bes_vfs'.format(clazz._CONFIG_DIR, config),
      ]
      for p in possible_configs:
        if path.isfile(p):
          return p
    config = os.environ.get('BES_VFS_CONFIG', None)
    if config == None:
      return None
    if path.isfile(config):
      return config
    return None
  
  @classmethod
  def _list_configs(clazz):
    files = glob.glob('{}/*.bes_vfs'.format(clazz._CONFIG_DIR))
    return [ file_util.remove_extension(path.basename(f)) for f in files ]
  
  @classmethod
  def _create_fs_from_config(clazz, config):
    config_filename = clazz._resolve_config_filename(config)
    if not config_filename:
      raise vfs_error('No config given either with --config or ~/.bes_vfs/config or BES_VFS_CONFIG')
    clazz.log.log_d('_create_fs_from_config: config={}'.format(config))
    fs = vfs_registry.load_from_config_file(config_filename)
    clazz.log.log_d('_create_fs_from_config: fs={}'.format(fs))
    return fs
  
  @classmethod
  def cat(clazz, config, remote_filename):
    'Cat a file.'
    check.check_string(config, allow_none = True)

    fs = clazz._create_fs_from_config(config)
    data = fs.download_to_bytes(remote_filename)
    print(data.decode('utf-8'))
    return 0

  @classmethod
  def rm(clazz, config, remote_filenames, recursive):
    'Remove one or more files.'
    check.check_string(config, allow_none = True)
    check.check_string_seq(remote_filenames)
    check.check_bool(recursive)

    fs = clazz._create_fs_from_config(config)
    for remote_filename in remote_filenames:
      fs.remove_file(remote_filename)
    return 0

  @classmethod
  def info(clazz, config, remote_filename):
    'info command.'
    check.check_string(config, allow_none = True)
    check.check_string(remote_filename)

    remote_filename = vfs_path_util.normalize(remote_filename)
    
    fs = clazz._create_fs_from_config(config)

    info = fs.file_info(remote_filename, vfs_file_info_options())
    clazz.log.log_d('info: info={}'.format(info))
    t = text_table(data = [ info ])
    print(t)
    return 0
  
