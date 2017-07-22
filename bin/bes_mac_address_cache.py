#!/usr/bin/env python
#-*- coding:utf-8 -*-
#

import argparse, os, os.path as path, sys

from bes.net.util import MacAddress

def main():

  parser = argparse.ArgumentParser()

  subparsers = parser.add_subparsers(help = 'commands', dest = 'command')

  # get
  get_parser = subparsers.add_parser('get', help = 'Get')
  get_parser.add_argument('cache_filename', action = 'store', help = 'Cache filename')
  get_parser.add_argument('mac_address', action = 'store', help = 'MAC address')

  # put
  put_parser = subparsers.add_parser('put', help = 'Put')
  put_parser.add_argument('cache_filename', action = 'store', help = 'Cache filename')
  put_parser.add_argument('mac_address', action = 'store', help = 'MAC address')
  put_parser.add_argument('name', action = 'store', help = 'Name')

  args = parser.parse_args()

  if args.command == 'get':
    return _command_get(args.cache_filename, args.mac_address)
  elif args.command == 'put':
    return _command_put(args.cache_filename, args.mac_address, args.name)

  return 0

def _command_get(cache_filename, mac_address):
  name = MacAddress.cache_get(cache_filename, mac_address)
  print name or ''
  return 0

def _command_put(cache_filename, mac_address, name):
  MacAddress.cache_put(cache_filename, mac_address, name)
  return 0

if __name__ == '__main__':
  sys.exit(main())
