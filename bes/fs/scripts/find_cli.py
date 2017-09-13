#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import argparse, os, os.path as path

from bes.fs import file_util
from bes.fs.find import find

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
    for found in self._find(files, args.maxdepth):
      p = './' + path.relpath(found)
      if p == './.':
        p = '.'
      #print(p)
    return 0

  @classmethod
  def _find(self, files, max_depth):
    for f in files:
      if path.isdir(f):
        for root, dirs, files in find.walk_with_poto(f, max_depth = max_depth):
          for x in files:
            yield path.join(root, x)
          for x in dirs:
            yield path.join(root, x)
      else:
        yield f
  
