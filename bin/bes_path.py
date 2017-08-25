#!/usr/bin/env python
#-*- coding:utf-8 -*-
#

# A helper script to deal with unix shell paths
# Or an excuse to avoid writing bash hackery

from collections import OrderedDict

import argparse, os, os.path as path, sys

def main():

  parser = argparse.ArgumentParser()
  subparsers = parser.add_subparsers(help = 'Command', dest = 'command')

  # append
  append_parser = subparsers.add_parser('append', help = 'Append path into parts.')
  append_parser.add_argument('path', type = str, action = 'store', help = 'The path to append.')
  append_parser.add_argument('parts', nargs = '+', type = str, action = 'store', help = 'One or more parts to append.')

  # prepend
  prepend_parser = subparsers.add_parser('prepend', help = 'Prepend path into parts.')
  prepend_parser.add_argument('path', type = str, action = 'store', help = 'The path to prepend.')
  prepend_parser.add_argument('parts', nargs = '+', type = str, action = 'store', help = 'One or more parts to prepend.')

  # Cleanup
  cleanup_parser = subparsers.add_parser('cleanup', help = 'Cleanup path into parts.')
  cleanup_parser.add_argument('path', type = str, action = 'store', help = 'The path to cleanup.')

  args = parser.parse_args()

  if args.command == 'append':
    return _command_append(args.path, args.parts)
  elif args.command == 'prepend':
    return _command_prepend(args.path, args.parts)
  elif args.command == 'cleanup':
    return _command_cleanup(args.path)

  return 0

def _path_split(p):
  return p.split(os.pathsep)

def _path_join(l):
  return os.pathsep.join(l)

def _path_cleanup(p):
  l = [ i for i in _path_split(p) if i ]
  d = OrderedDict.fromkeys(l)
  return _path_join(d)

def _command_append(p, parts):
  p =  _path_split(p)
  for part in parts:
    p.append(part)
  p = _path_cleanup(_path_join(p))
  sys.stdout.write('%s\n' % (p))
  return 0

def _command_prepend(p, parts):
  p =  _path_split(p)
  for part in parts:
    p.append(part)
  p = _path_cleanup(_path_join(p))
  sys.stdout.write('%s\n' % (p))
  return 0

def _command_cleanup(p):
  p = _path_cleanup(p)
  sys.stdout.write('%s\n' % (p))
  return 0

if __name__ == '__main__':
  raise SystemExit(main())
