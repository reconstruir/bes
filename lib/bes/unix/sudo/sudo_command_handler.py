#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.bcli.bcli_command_handler import bcli_command_handler
from bes.system.check import check

from .sudo import sudo
from .sudo_cli_options import sudo_cli_options

class sudo_command_handler(bcli_command_handler):

  def name(self):
    return 'sudo'

  def _make_options(self, options, force_auth=False):
    return sudo_cli_options(verbose=options.verbose,
                            password=options.password,
                            working_dir=options.working_dir,
                            prompt=options.prompt,
                            force_auth=force_auth)

  def _command_run(self, cmd, options):
    check.check_string_seq(cmd)

    sudo.call_sudo(cmd, self._make_options(options))
    return 0

  def _command_authenticate(self, force_auth, options):
    sudo.authenticate(self._make_options(options, force_auth=force_auth))
    return 0

  def _command_is_authenticated(self, options):
    if sudo.is_authenticated(self._make_options(options)):
      return 0
    return 1

  def _command_reset(self, options):
    sudo.reset(self._make_options(options))
    return 0
