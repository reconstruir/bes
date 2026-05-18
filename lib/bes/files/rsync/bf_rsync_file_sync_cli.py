#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import argparse
import sys

from .bf_rsync_file_sync import bf_rsync_file_sync

class bf_rsync_file_sync_cli(object):

  @classmethod
  def run(clazz):
    parser = argparse.ArgumentParser(
      prog='bfile-sync',
      description='Sync large files to a NAS over rsync+SSH with retry and checksum verification.',
    )
    parser.add_argument('ssh_key', help='Path to SSH private key')
    parser.add_argument('destination', help='Remote destination in host:path form')
    parser.add_argument('source_dirs', nargs='+', metavar='source_dir',
                        help='One or more local directories to sync from')
    parser.add_argument('--log-file', default=None, metavar='PATH',
                        help='Write operational log to this file (default: stdout only)')
    parser.add_argument('--dry-run', action='store_true', default=False,
                        help='Show what would be transferred without moving any data')
    mode_group = parser.add_mutually_exclusive_group()
    mode_group.add_argument('--compact', action='store_true', default=False,
                            help='One line per file with in-place overwrite (default on TTY)')
    mode_group.add_argument('--verbose', action='store_true', default=False,
                            help='Two lines plus blank separator per file (default when not a TTY)')
    args = parser.parse_args()

    if args.compact:
      compact = True
    elif args.verbose:
      compact = False
    else:
      compact = None

    syncer = bf_rsync_file_sync(
      args.ssh_key,
      args.destination,
      args.source_dirs,
      log_file=args.log_file,
      dry_run=args.dry_run,
      compact=compact,
    )
    syncer.run()
