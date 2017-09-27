#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
#import argparse, os, os.path as path, re, sys
#
from bes.common import algorithm
from bes.fs import file_find, file_match
#from bes.archive import archiver
#from bes.git import git
#from bes.refactor import files as refactor_files

#log.configure('file_find=debug')

#COMMENTED_OUT_HEAD = '#####'

class script_base(object):

  def __init__(self):
    pass

  def filepath_normalize(self, filepath):
    return path.abspath(path.normpath(filepath))

  def filepaths_normalize(self, files):
    return [ self.filepath_normalize(f) for f in files ]

  def resolve_files(self, files, patterns = None, exclude_patterns = None):
    'Resolve a mixed list of files and directories into a sorted list of files.'
    result = []
    for f in files:
      if not path.exists(f):
        raise RuntimeError('Not found: %s' % (f))
      if path.isfile(f):
        result.append(self.filepath_normalize(f))
      elif path.isdir(f):
        result += file_find.find_fnmatch(f, patterns, relative = False)
      result = sorted(algorithm.unique(result))
      if not exclude_patterns:
        return result
      return file_match.match_fnmatch(result, exclude_patterns, file_match.NONE)
