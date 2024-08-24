#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import argparse, os, os.path as path

from ..bf_file_type import bf_file_type
from ..match.bf_file_matcher import bf_file_matcher

from .bf_file_finder import bf_file_finder
from .bf_file_finder_options import bf_file_finder_options

class bf_file_finder_cli(object):

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
                              default = 'FILE|LINK',
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
    raise SystemExit(clazz().main())

  def main(self):
    args = self._parser.parse_args()
    files = args.files
    for found in self._find(files, args.name, args.file_type, args.mindepth, args.maxdepth, args.quit):
      if not args.quiet:
        print(found)
    return 0

  @classmethod
  def _find(clazz, files, name, ft, min_depth, max_depth, quit):
    if ft:
      ft = bf_file_type.parse(ft)
    for f in files:
      if path.isdir(f):
        ff = clazz._make_finder(f, name, ft, min_depth, max_depth, quit)
        for f in ff.find(f):
          yield f
  
  @classmethod
  def _make_finder(clazz, d, name, ft, min_depth, max_depth, quit):
    matcher = None
    if name:
      matcher = bf_file_matcher()
      matcher.add_matcher_fnmatch(name)
    options = bf_file_finder_options(min_depth = min_depth,
                                     max_depth = max_depth,
                                     file_type = ft,
                                     file_matcher = matcher,
                                     path_type = 'basename')
    finder = bf_file_finder(options = options)
    return finder
