#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from ..system.check import check
from bes.fs.file_multi_ignore import file_multi_ignore
from ..bf_check import bf_check
from bes.property.cached_property import cached_property

class bf_file_ignore_options_mixin(object):

  def __init__(self):
    pass

  def bf_file_ignorer(self):
    return file_multi_ignore(self.ignore_files)
    
  def should_ignore_file(self, ford):
    ford = bf_check.check_file_or_dir(ford)
    
#    r = self.bf_file_ignorer.should_ignore(ford)
#    from bes.system.log import log
#    log.console(f'CONO: should_ignore_file({ford}) => {r}')
    return self.bf_file_ignorer().should_ignore(ford)
