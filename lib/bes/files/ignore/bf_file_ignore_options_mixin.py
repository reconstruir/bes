#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from .bf_file_ignore_list import bf_file_ignore_list
from ..bf_check import bf_check

class bf_file_ignore_options_mixin(object):

  def __init__(self):
    pass

  def bf_file_ignorer(self):
    return bf_file_ignore_list(self.ignore_files)
    
  def should_ignore_file(self, ford):
    ford = bf_check.check_file_or_dir(ford)
    return self.bf_file_ignorer().should_ignore(ford)
