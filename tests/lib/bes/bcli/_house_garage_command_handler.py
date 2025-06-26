#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.system.check import check

from bes.bcli.bcli_caca_handler_i import bcli_caca_handler_i

class _house_garage_command_handler(bcli_caca_handler_i):

  def _command_house_kitchen_cook(self, method, output, what, options):
    print(f'_command_cook: method={method} output={output} what={what}')
    return 0
