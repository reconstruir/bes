#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

class file_ignore(object):
  'Decide whether to ignore a file based on scheme similar to .gitignore'
  
  def __init__(self, ignore_filename):
    self._ignore_filename = ignore_filename

  def ignore_filename(self):
    return self._ignore_filename

  def ignore(self, filename):
    pass
