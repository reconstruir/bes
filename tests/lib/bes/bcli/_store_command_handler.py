#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.system.check import check

from bes.bcli.bcli_command_handler_i import bcli_command_handler_i

class _store_command_handler(bcli_command_handler_i):

  def _command_buy(self, what, verbose, options):
    print(f'_command_store_buy: what={what} verbose={verbose}')
    return 0
