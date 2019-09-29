#!/usr/bin/env python3
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import argparse, os, os.path as path

from bes.fs.file_type import file_type
from bes.fs.file_util import file_util
from bes.fs.find.criteria import criteria
from bes.fs.find.file_type_criteria import file_type_criteria
from bes.fs.find.finder import finder
from bes.fs.find.max_depth_criteria import max_depth_criteria
from bes.fs.find.pattern_criteria import pattern_criteria

class find_cli(object):

#             b       block special
#             c       character special
#             d       directory
#             f       regular file
#             l       symbolic link
#             p       FIFO
#             s       socket
  
  def __init__(self):
    self._parser = argparse.ArgumentParser()
    self._parser.add_argument('files', nargs = '+', action = 'store', help = 'Files or directories to find')
    self._parser.add_argument('-name',
                              action = 'store',
                              default = None,
                              help = 'Name to find [ None ]')
    self._parser.add_argument('-type',
                              '-t',
                              dest = 'file_type',
                              action = 'store',
                              default = None,
                              help = 'Type if file to find [ None ]')
    self._parser.add_argument('-mindepth',
                              action = 'store',
                              default = None,
                              type = int,
                              help = 'Min depth [ None ]')
    self._parser.add_argument('-maxdepth',
                              action = 'store',
                              default = None,
                              type = int,
                              help = 'Max depth [ None ]')
    self._parser.add_argument('--quiet',
                              '-q',
                              action = 'store_true',
                              default = False,
                              help = 'Run quietly.  Do not print out filenames [ False ]')
    self._parser.add_argument('-quit',
                              action = 'store_true',
                              default = False,
                              help = 'Quit after finding a criteria match. [ False ]')
    self._parser.add_argument('-print',
                              action = 'store_true',
                              default = True,
                              help = 'Print the files found. [ True ]')
    
  @classmethod
  def run(clazz):
    raise SystemExit(find_cli().main())

  def main(self):
    args = self._parser.parse_args()
    files = args.files
    for found in self._find(files, args.name, args.file_type, args.maxdepth, args.quit):
      if not args.quiet:
        print(found)
    return 0

  @classmethod
  def _find(clazz, files, name, ft, max_depth, quit):
    if ft:
      ft = file_type.validate_file_type(ft)
    for f in files:
      if path.isdir(f):
        ff = clazz._make_finder(f, name, ft, max_depth, quit)
        for f in ff.find():
          yield f
  
  @classmethod
  def _make_finder(clazz, d, name, ft, max_depth, quit):
    crit_list = []
    if max_depth:
      crit_list.append(max_depth_criteria(max_depth))
    if name:
      if quit:
        action = criteria.STOP
      else:
        action = criteria.FILTER
      crit_list.append(pattern_criteria(name, action = action))
    if ft:
      crit_list.append(file_type_criteria(ft))
    return finder(d, criteria = crit_list)
