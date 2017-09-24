#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import errno
from .criteria import criteria
from bes.fs import file_type

class file_type_criteria(criteria):
  'match the file type.'

  def __init__(self, file_type_mask):
    super(file_type_criteria, self).__init__(action = self.FILTER, target = self.ANY)
    import sys
    self.file_type_mask = file_type_mask
    sys.stderr.write('mask=%s\n' % (self.file_type_mask))
  
  def matches(self, variables):
    try:
      return file_type.matches(variables.filename, self.file_type_mask)
    except OSError, ex:
      # Sometimes os.walk() will find things that later are mysteriously missing - maybe races
      if ex.errno == errno.ENOENT:
        return False
