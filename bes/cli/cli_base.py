#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import argparse, os, os.path as path

#from bes_network.device import device, device_type
#from bes_network.wireless import wireless#

#from bes_network.address import mac_address_lookup

from abc import abstractmethod, ABCMeta


class cli_base(object):

  __metaclass__ = ABCMeta
  
  def __init__(self):
    self._parser = argparse.ArgumentParser()
    self.add_args(self._parser)
    
  @abstractmethod
  def add_args(clazz, arg_parser):
    'Add arguments to arg_parser.'
    pass
    
#  @classmethod
#  def run(clazz):
#    raise SystemExit(cli_base().main())

  @abstractmethod
  def main(self):
    args = self._parser.parse_args()
    self._aliases = mac_address_lookup(args.aliases)
    if args.command == 'get':
      return self._command_get(args.mac_address)
    elif args.command == 'put':
      return self._command_put(args.mac_address, args.name)
    elif args.command == 'list':
      return self._command_list()

  @abstractmethod
  def main(self):
    args = self._parser.parse_args()
    self._aliases = mac_address_lookup(args.aliases)
    if args.command == 'get':
      return self._command_get(args.mac_address)
    elif args.command == 'put':
      return self._command_put(args.mac_address, args.name)
    elif args.command == 'list':
      return self._command_list()
    
