#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.cli.cli_command_handler import cli_command_handler
from bes.common.check import check

from bes.system.process_lister import process_lister
from bes.text.text_table import text_table

class system_cli_handler(cli_command_handler):
  'system cli handler.'

  def __init__(self, cli_args):
    super(system_cli_handler, self).__init__(cli_args)

  def ps(self):
    data = []
    for process in process_lister.list_processes():
      data.append( ( process.command, process.pid, process.user ) )

    tt = text_table(data = data)
    tt.set_labels( ( 'COMMAND', 'PID', 'USER' ) )
    print(tt)
    return 0

  def lsof(self, pid):
    check.check_int(pid)

    for f in process_lister.open_files(pid):
      print(f)
    return 0
