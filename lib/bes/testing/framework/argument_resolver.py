#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from bes.fs import file_path

from .unit_test_description import unit_test_description

class argument_resolver(object):

  def __init__(self, root_dir, arguments):
    self.root_dir = path.abspath(root_dir)
    self.arguments = arguments
    self.files, self.filters = self._separate_files_and_filters(self.root_dir, self.arguments)
    
  @classmethod
  def _separate_files_and_filters(clazz, root_dir, arguments):
    files = []
    filter_descriptions = []
    for arg in arguments:
      normalized_path = file_path.normalize(path.join(root_dir, arg))
      if not path.exists(normalized_path):
        filter_descriptions.append(arg)
      else:
        files.append(arg)
    filters = [ unit_test_description.parse(f) for f in (filter_descriptions or []) ]
    return files, filters
