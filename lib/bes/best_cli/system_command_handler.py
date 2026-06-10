#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.bcli.bcli_command_handler import bcli_command_handler
from bes.system.check import check

from bes.system.process_lister import process_lister
from bes.text.text_table import text_table

class system_command_handler(bcli_command_handler):

  def name(self):
    return 'system'

  def _command_ps(self, options):
    data = []
    for process in process_lister.list_processes():
      data.append((process.command, process.pid, process.user))
    tt = text_table(data=data)
    tt.set_labels(('COMMAND', 'PID', 'USER'))
    print(tt)
    return 0

  def _command_lsof(self, pid, options):
    check.check_int(pid)

    for f in process_lister.open_files(pid):
      print(f)
    return 0
