# -*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.system.check import check
from bes.system.log import logger

from .lsof_output_parser import lsof_output_parser
from .lsof_command import lsof_command

class lsof(object):
  'A class to abstract some lsof operations.'

  _log = logger('lsof')

  @classmethod
  def lsof(clazz, pid = None):
    'Return a list of lsof items for all process or a specific process'
    check.check_int(pid, allow_none = True)

    args = []
    if pid:
      args.extend([ '-p', str(pid)])
    rv = lsof_command.call_command(args)
    return lsof_output_parser.parse_lsof_output(rv.stdout)
