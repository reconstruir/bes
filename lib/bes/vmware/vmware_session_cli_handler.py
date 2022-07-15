#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.cli.cli_command_handler import cli_command_handler
from ..system.check import check

from .vmware_client_commands import vmware_client_commands
from .vmware_error import vmware_error
from .vmware_server import vmware_server
from .vmware_session import vmware_session
from .vmware_session_options import vmware_session_options

class vmware_session_cli_handler(cli_command_handler):
  'vmware session cli handler.'

  def __init__(self, cli_args):
    super(vmware_session_cli_handler, self).__init__(cli_args,
                                                     options_class = vmware_session_options,
                                                     delegate = self._comand_handler_delegate)
    check.check_vmware_session_options(self.options)

  def _comand_handler_delegate(self, command_name, options, *args, **kwargs):
    check.check_string(command_name)
    check.check_vmware_session_options(options)
    check.check_tuple(args)
    check.check_dict(kwargs)
    
    session = vmware_session(port = options.vmrest_port,
                             credentials = options.vmrest_credentials)
    session.start()
    commands = vmware_client_commands(session.client, options)
    func = getattr(commands, command_name)
    result = func(*args, **kwargs)
    session.stop()
    return result
