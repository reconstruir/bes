#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.system.check import check

from bes.bcli.bcli_command_handler_i import bcli_command_handler_i

class _house_kitchen_command_handler(bcli_command_handler_i):

  def _command_cook(self, method, output, what, options):
    print(f'_command_cook: method={method} output={output} what={what} options={options}')
    return 0
