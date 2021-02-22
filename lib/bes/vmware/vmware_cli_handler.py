#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path

from bes.cli.cli_command_handler import cli_command_handler
from bes.common.check import check
from bes.system.log import logger

from .vmware import vmware
from .vmware_options import vmware_options

class vmware_cli_handler(cli_command_handler):
  'vmware cli handler.'

  _log = logger('vmware_cli_handler')
  
  def __init__(self, cli_args):
    super(vmware_cli_handler, self).__init__(cli_args,
                                             options_class = vmware_options,
                                             delegate = self._comand_handler_delegate)
    check.check_vmware_options(self.options)
    self._vmware = vmware(self.options)

  def _comand_handler_delegate(self, command_name, options, *args, **kwargs):
    check.check_string(command_name)
    check.check_vmware_options(options)
    check.check_tuple(args)
    check.check_dict(kwargs)

    func = getattr(self._vmware, command_name)
    rv = func(*args, **kwargs)
    return rv.exit_code
