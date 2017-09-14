#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import argparse, os, os.path as path

from bes.fs import file_type, file_util
from bes.fs.find import finder, file_type_criteria, max_depth_criteria, pattern_criteria

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
    
  @classmethod
  def run(clazz):
    raise SystemExit(find_cli().main())

  def main(self):
    args = self._parser.parse_args()
#    files = file_util.make_paths_absolute(args.files)
    files = args.files
    for found in self._find(files, args.name, args.file_type, args.maxdepth):
      p = './' + path.relpath(found)
      if p == './.':
        p = '.'
      print(p)
    return 0

  @classmethod
  def _find(clazz, files, name, ft, max_depth):
    if ft:
      ft = file_type.validate_file_type(ft)
    for f in files:
      if path.isdir(f):
        ff = clazz._make_finder(f, name, ft, max_depth)
        for f in ff.find():
          yield f
  
  @classmethod
  def _make_finder(clazz, d, name, ft, max_depth):
    criteria = []
    if max_depth:
      criteria.append(max_depth_criteria(max_depth))
    if name:
      criteria.append(pattern_criteria(name))
    if ft:
      criteria.append(file_type_criteria(ft))
    return finder(d, criteria = criteria)
