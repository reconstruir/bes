#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path

from bes.system.check import check
from bes.bcli.bcli_command_handler import bcli_command_handler

from .bf_metadata_command_options import bf_metadata_command_options
from .bf_metadata_file_store import bf_metadata_file_store

class bf_metadata_command_handler(bcli_command_handler):

  #@abc.abstractmethod
  def name(self):
    return 'bf_metadata'

  def _command_list(self, filename, options):
    check.check_string(filename)
    check.check_bf_metadata_command_options(options)

    store = bf_metadata_file_store()
    entries = store.get_all(path.abspath(filename))
    for key, value in sorted(entries.items()):
      print(f'{key}: {value}')
    return 0

  def _command_clear(self, filename, options):
    check.check_string(filename)
    check.check_bf_metadata_command_options(options)

    if not options.yes:
      answer = input(f'Clear all metadata for {filename}? [y/N] ').strip().lower()
      if answer not in ('y', 'yes'):
        print('Aborted.')
        return 1

    store = bf_metadata_file_store()
    store.delete(path.abspath(filename))
    return 0

  def _command_set(self, key, value, filename, options):
    check.check_string(key)
    check.check_string(value)
    check.check_string(filename)
    check.check_bf_metadata_command_options(options)

    store = bf_metadata_file_store()
    store.set(path.abspath(filename), key, value)
    return 0

  def _command_get(self, key, filename, options):
    check.check_string(key)
    check.check_string(filename)
    check.check_bf_metadata_command_options(options)

    store = bf_metadata_file_store()
    value = store.get(path.abspath(filename), key)
    if value is None:
      return 1
    print(value)
    return 0

  def _command_keys(self, filename, options):
    check.check_string(filename)
    check.check_bf_metadata_command_options(options)

    store = bf_metadata_file_store()
    for key in store.keys(path.abspath(filename)):
      print(key)
    return 0
