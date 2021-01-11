#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import copy, os, pprint

from bes.cli.cli_command_handler import cli_command_handler
from bes.common.Script import Script
from bes.common.algorithm import algorithm
from bes.common.check import check
from bes.fs.file_path import file_path
from bes.script.blurber import blurber

from .computer_setup_error import computer_setup_error
from .computer_setup_manager import computer_setup_manager
from .computer_setup_options import computer_setup_options

from .tasks.macos.cst_disable_screen_saver import cst_disable_screen_saver
from .tasks.macos.cst_install_command_line_tools import cst_install_command_line_tools
from .tasks.unix.cst_change_shell_to_bash import cst_change_shell_to_bash
from .tasks.unix.cst_install_brew import cst_install_brew

class computer_setup_cli_command(cli_command_handler):
  'computer_setup cli handler.'

  def __init__(self, cli_args):
    super(computer_setup_cli_command, self).__init__(cli_args, options_class = computer_setup_options)
    check.check_computer_setup_options(self.options)
    
    self._csm = computer_setup_manager(options = self.options)
  
###  @classmethod
###  def handle_command(clazz, command, **kargs):
###    super(vmware_client_cli_command, self).__init__(cli_args, options_class = vmware_client_options)
###    check.check_vmware_client_options(self.options)
###
###    options = computer_setup_options(**kargs)
###    csm = computer_setup_manager(options = options)
###    filtered_args = argparser_handler.filter_keywords_args(computer_setup_options, kargs)
###    func = getattr(computer_setup_cli_command, command)
###    return func(csm, **filtered_args)
#    kargs = copy.deepcopy(kargs)
#    func = getattr(computer_setup_cli_command, command)
#    bl = blurber(Script.name())
#    verbose = kargs.pop('verbose')
#    bl.set_verbose(verbose)
#    np = computer_setup(bl)
#    return func(np, **kargs)
  
  def update(self, config_filename):
    check.check_string(config_filename)

    self._csm.add_tasks_from_config(config_filename)
    self._csm.run()

    return 0

  @classmethod
  def _csm_populate(clazz, csm, config_filename):
    if config_filename == 'dev':
      clazz._csm_populate_dev(csm, config_filename)
    elif config_filename == 'ci':
      clazz._csm_populate_ci(csm, config_filename)
      
#  @classmethod
#  def _csm_populate_dev(clazz, csm, config_filename):
#from .computer_setup.tasks.macos.cst_disable_screen_saver import cst_disable_screen_saver
#from .computer_setup.tasks.macos.cst_install_command_line_tools import cst_install_command_line_tools
#from .computer_setup.tasks.unix.cst_change_shell_to_bash import cst_change_shell_to_bash
#from .computer_setup.tasks.unix.cst_install_brew import cst_install_brew#
#
#    pass
#
#  @classmethod
#  def _csm_populate_ci(clazz, csm, config_filename):
#    pass
