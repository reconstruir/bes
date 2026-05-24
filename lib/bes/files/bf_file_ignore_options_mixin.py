#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.files.bf_check import bf_check
from bes.files.ignore.bf_file_multi_ignore import bf_file_multi_ignore

class bf_file_ignore_options_mixin(object):

  def __init__(self):
    pass

  def file_ignorer(self):
    return bf_file_multi_ignore(self.ignore_files)

  def should_ignore_file(self, ford):
    try:
      ford = bf_check.check_file_or_dir(ford)
      return self.file_ignorer().should_ignore(ford)
    except FileNotFoundError:
      return True
