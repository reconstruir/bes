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
                              dest = 'min_depth',
                              default = None,
                              type = int,
                              help = 'Min depth [ None ]')
    self._parser.add_argument('-maxdepth',
                              action = 'store',
                              dest = 'max_depth',
                              default = None,
                              type = int,
                              help = 'Max depth [ None ]')
    self._parser.add_argument('-quiet',
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
    for found in self._find(args):
      pass
    return 0

  @classmethod
  def _find(clazz, args):
    if args.file_type:
      args.file_type = bf_file_type.parse(args.file_type)
    for f in args.files:
      if path.isdir(f):
        ff = clazz._make_finder(f, args)
        for f in ff.find(f):
          yield f
  
  @classmethod
  def _make_finder(clazz, d, args):
    matcher = None
    stop_after = None
    if args.name:
      matcher = bf_file_matcher()
      matcher.add_matcher_fnmatch(args.name)
      if args.quit:
        stop_after = 1
        
    def _cb(entry):
      if not args.quiet:
        print(entry.filename, flush = True)
      
    options = bf_file_finder_options(min_depth = args.min_depth,
                                     max_depth = args.max_depth,
                                     file_type = args.file_type,
                                     file_matcher = matcher,
                                     path_type = 'basename',
                                     stop_after = stop_after,
                                     found_callback = _cb)
    finder = bf_file_finder(options = options)
    return finder
