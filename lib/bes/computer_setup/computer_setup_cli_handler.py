#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import copy, os, pprint

from bes.cli.cli_command_handler import cli_command_handler
from ..system.check import check
from bes.key_value.key_value_list import key_value_list

from .computer_setup_error import computer_setup_error
from .computer_setup_manager import computer_setup_manager
from .computer_setup_options import computer_setup_options

from .tasks.macos import *
from .tasks.unix import *

class computer_setup_cli_handler(cli_command_handler):
  'computer_setup cli handler.'

  def __init__(self, cli_args):
    super(computer_setup_cli_handler, self).__init__(cli_args, options_class = computer_setup_options)
    check.check_computer_setup_options(self.options)
    
    self._csm = computer_setup_manager(options = self.options)
  
  def update(self, config_filename, values):
    check.check_string(config_filename)
    check.check_string_seq(values)

    parsed_values = key_value_list.parse(' '.join(values))

    self._csm.add_tasks_from_config(config_filename)
    self._csm.run(parsed_values.to_dict())

    return 0

#  @classmethod
#  def _csm_populate(clazz, csm, config_filename):
#    if config_filename == 'dev':
#      clazz._csm_populate_dev(csm, config_filename)
#    elif config_filename == 'ci':
#      clazz._csm_populate_ci(csm, config_filename)
