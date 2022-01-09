#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.fs.file_check import file_check
from bes.system.check import check
from bes.system.log import logger

from .reindent import main as reindent_main

class refactor_reindent(object):

  _log = logger('reindent')

  @classmethod
  def reindent_file(clazz, filename, indent, backup):
    check.check_string(filename)
    check.check_int(indent)
    check.check_bool(backup)
    file_check.check_file(filename)
    
    clazz._log.log_method_d()
    
    backup_args = [] if backup else [ '--nobackup' ]
    args = [ '--indent', str(indent) ] + backup_args + [ filename ]
    reindent_main(args)
