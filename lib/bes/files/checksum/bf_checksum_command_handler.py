#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.system.check import check
from bes.bcli.bcli_command_handler import bcli_command_handler

from ..resolve.bf_file_resolver import bf_file_resolver

from .bf_checksum_cache import bf_checksum_cache
from .bf_checksum_command_options import bf_checksum_command_options

class bf_checksum_command_handler(bcli_command_handler):

  #@abc.abstractmethod
  def name(self):
    return 'bf_checksum'

  def _command_print(self, where, options):
    check.check_string_seq(where)
    check.check_bf_checksum_command_options(options)

    resolver = bf_file_resolver()
    entries = resolver.resolve(where)
    for entry in entries:
      checksum = bf_checksum_cache.get_checksum(entry.filename, options.algorithm)
      print(f'{entry.filename}: {checksum}')
    return 0
