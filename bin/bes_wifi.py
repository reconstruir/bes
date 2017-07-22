#!/usr/bin/env python
#-*- coding:utf-8 -*-
#

import argparse, os, os.path as path, sys
from collections import namedtuple
from bes.net.util import wireless, mac_address_lookup

Entry = namedtuple('Entry', 'ssid,address,alias,channel,signal_strength')

def main():

  parser = argparse.ArgumentParser()

  subparsers = parser.add_subparsers(help = 'commands', dest = 'command')

  # Scan
  scan_parser = subparsers.add_parser('scan', help = 'Scan for wifi networks.')
  scan_parser.add_argument('interface', action = 'store', help = 'Interface to scan')
  scan_parser.add_argument('--xml',
                           action = 'store',
                           default = False,
                           help = 'Output scan as xml [ False ]')

  ## Create
  #create_parser = subparsers.add_parser('create', help = 'Create archive')
  #create_parser.add_argument('root_dir', action = 'store', help = 'Directory to archive')
  #create_parser.add_argument('name', action = 'store', help = 'Archive name')
  #create_parser.add_argument('version', action = 'store', help = 'Archive version')
  #create_parser.add_argument('--revision',
  #                           '-r',
  #                           action = 'store',
  #                           default = '1',
  #                           help = 'Revision for archive [ 1 ]')

  args = parser.parse_args()

  if args.command == 'scan':
    return _command_scan(args.interface)

  return 0

def _command_scan(interface):
  MAC_ADDRESS_NAMES = path.expanduser('~/.bes_mac_address_names')

  networks = wireless.scan(interface)
  entries = []
  entries.append(Entry('SSID', 'ADDRESS', 'NAME', 'CHANNEL', 'SIGNAL STRENGTH'))
  for network in networks:
    alias = mac_address_lookup.get_alias(MAC_ADDRESS_NAMES, network.address) or ''
    entries.append(Entry(network.ssid, network.address, alias, network.channel, network.signal_strength))
  max_ssid_len = max([ len(entry.ssid) for entry in entries ])
  max_alias_len = max([ len(entry.alias) for entry in entries ])

  format = '%%%ds  %%-17s  %%-%ds  %%-7s  %%-4s' % (max_ssid_len, max_alias_len)

  for entry in entries:
    print format % (entry.ssid, entry.address, entry.alias, entry.channel, entry.signal_strength)
  
  return 0

if __name__ == '__main__':
  sys.exit(main())

