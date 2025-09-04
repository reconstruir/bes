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
  
  def _command_set(self, filename, domain, key, value, options):
    check.check_string(filename)
    check.check_string(domain)
    check.check_string(key)
    check.check_string(value)
    check.check_bf_file_resolver_cli_options(options)

    password = options.resolve_password()

    print(f'filename={filename}')
    sv = bf_file_resolver(filename)
    sv.set_string(domain, key, value, password = options.password)
    return 0

  def _command_get(self, filename, domain, key, options):
    check.check_string(filename)
    check.check_string(domain)
    check.check_string(key)
    check.check_bf_file_resolver_cli_options(options)

    password = options.resolve_password()
    
    sv = bf_file_resolver(filename)
    value = sv.get_string(domain, key, password = options.password)
    print(value)
    return 0
  
