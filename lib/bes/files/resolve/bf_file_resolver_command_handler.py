#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import getpass

from bes.system.check import check

from bes.bcli.bcli_command_handler import bcli_command_handler

from .bf_file_resolver import bf_file_resolver
from .bf_file_resolver_cli_options import bf_file_resolver_cli_options

class bf_file_resolver_command_handler(bcli_command_handler):

  #@abc.abstractmethod
  def name(self):
    return 'bf_file_resolver'
  
  def _command_files(self, where, options):
    check.check_string_seq(where)
    check.check_bf_file_resolver_cli_options(options)

    def _progress_cb(progress):
      print(progress)

    resolver_options = options.file_resolver_options.clone()
    resolver_options.progress_callback = _progress_cb
      
    resolver = bf_file_resolver(options = resolver_options)
    result = resolver.resolve(where)
    print(result)
    return 0
