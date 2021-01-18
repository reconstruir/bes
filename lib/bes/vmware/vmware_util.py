#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.system.log import logger
from bes.system.execute import execute

class vmware_util(object):

  _log = logger('vmware_util')

  @classmethod
  def killall_vmrest(clazz):
    rv = execute.execute('killall vmrest', raise_error = False)
    if rv.exit_code == 0:
      clazz._log.log_i('killed some vmrest')
